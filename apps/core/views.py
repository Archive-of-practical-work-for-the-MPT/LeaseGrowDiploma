from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from django.db import transaction
from django.db.models import Sum

from django.utils import timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from datetime import timedelta
import json

from apps.catalog.models import Equipment, EquipmentCategory, Manufacturer
from apps.leasing.models import (
    LeaseRequest, LeaseContract, Company,
    PaymentSchedule, MaintenanceRequest,
)
from apps.accounts.views import get_current_account
from yookassa import Configuration, Payment


def _extract_first_image_url(images_value):
    """Возвращает первый URL изображения из JSONField (list/str/json-string)."""
    if not images_value:
        return ''
    if isinstance(images_value, (list, tuple)):
        return str(images_value[0]).strip() if images_value else ''
    if isinstance(images_value, str):
        text = images_value.strip()
        if not text:
            return ''
        try:
            parsed = json.loads(text)
            if isinstance(parsed, (list, tuple)):
                return str(parsed[0]).strip() if parsed else ''
            if isinstance(parsed, str):
                return parsed.strip()
        except json.JSONDecodeError:
            pass
        return text
    return str(images_value).strip()


def _can_create_leasing_request(account):
    if not account:
        return False
    role_name = getattr(getattr(account, 'role', None), 'name', '')
    return role_name not in ('admin', 'manager')


def _get_leasing_request_context(account):
    my_requests = []
    pending_equipment_ids = set()
    pending_lease_requests = {}
    can_cancel_ids = set()

    if not account:
        return {
            'my_requests': my_requests,
            'can_cancel_ids': can_cancel_ids,
            'pending_equipment_ids': pending_equipment_ids,
            'pending_lease_requests': pending_lease_requests,
        }

    my_requests = list(
        LeaseRequest.objects.filter(account=account)
        .select_related('equipment', 'lease_contract')
        .order_by('-created_at')
    )
    for req in my_requests:
        if req.status in ('pending', 'confirmed'):
            c = getattr(req, 'lease_contract', None)
            if not c or not c.signed_at:
                can_cancel_ids.add(req.id)

    pending_lease_requests = dict(
        LeaseRequest.objects.filter(
            account=account, status='pending'
        ).values_list('equipment_id', 'id')
    )
    pending_equipment_ids = set(pending_lease_requests.keys())

    return {
        'my_requests': my_requests,
        'can_cancel_ids': can_cancel_ids,
        'pending_equipment_ids': pending_equipment_ids,
        'pending_lease_requests': pending_lease_requests,
    }


def home(request):
    show_company_bind_prompt = bool(request.session.pop('show_company_bind_prompt', False))
    return render(request, 'core/home.html', {
        'show_company_bind_prompt': show_company_bind_prompt,
    })


def leasing(request):
    """Страница лизинга — каталог доступной техники с поиском и фильтрами."""
    qs = Equipment.objects.filter(status='available').select_related('category', 'manufacturer')

    q = (request.GET.get('q') or '').strip()
    category_id = None
    manufacturer_id = None
    try:
        cid = request.GET.get('category')
        if cid:
            category_id = int(cid)
    except (ValueError, TypeError):
        pass
    try:
        mid = request.GET.get('manufacturer')
        if mid:
            manufacturer_id = int(mid)
    except (ValueError, TypeError):
        pass
    sort = request.GET.get('sort', 'name')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(model__icontains=q) | Q(category__name__icontains=q)
        )
    if category_id:
        qs = qs.filter(category_id=category_id)
    if manufacturer_id:
        qs = qs.filter(manufacturer_id=manufacturer_id)

    if sort == 'price':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'rate':
        qs = qs.order_by('monthly_lease_rate')
    else:
        qs = qs.order_by('category__name', 'name')

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    equipment_list = page_obj.object_list

    categories = EquipmentCategory.objects.filter(
        equipment__status='available'
    ).distinct().order_by('name')
    manufacturers = Manufacturer.objects.filter(
        equipment__status='available'
    ).distinct().order_by('name')

    account = get_current_account(request)
    request_context = _get_leasing_request_context(account)

    get_copy = request.GET.copy()
    get_copy.pop('page', None)
    query_string = get_copy.urlencode()

    return render(request, 'core/leasing.html', {
        'equipment_list': equipment_list,
        'page_obj': page_obj,
        'query_string': query_string,
        'current_account': account,
        'can_create_leasing_request': _can_create_leasing_request(account),
        'categories': categories,
        'manufacturers': manufacturers,
        'search_q': q,
        'filter_category_id': category_id,
        'filter_manufacturer_id': manufacturer_id,
        'sort': sort,
        **request_context,
    })


def leasing_detail(request, equipment_id):
    equipment = get_object_or_404(
        Equipment.objects.select_related('category', 'manufacturer'),
        pk=equipment_id,
        status='available',
    )
    account = get_current_account(request)
    request_context = _get_leasing_request_context(account)

    return render(request, 'core/leasing_detail.html', {
        'equipment': equipment,
        'current_account': account,
        'can_create_leasing_request': _can_create_leasing_request(account),
        **request_context,
    })


def leasing_request_create(request, equipment_id):
    """Создание заявки на лизинг пользователем."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему, чтобы оформить заявку.')
        return redirect('accounts:login')
    if not _can_create_leasing_request(account):
        messages.error(request, 'Оформление заявок доступно только клиентам.')
        return redirect('core:leasing_detail', equipment_id=equipment_id)

    # Клиент должен быть связан с компанией
    has_company = Company.objects.filter(account=account).exists()
    if not has_company:
        messages.warning(
            request,
            'Для оформления заявки укажите данные компании в профиле.'
        )
        return redirect(reverse('accounts:profile') + '?need_company=1')

    equipment = get_object_or_404(Equipment, pk=equipment_id, status='available')

    if request.method == 'POST':
        existing = LeaseRequest.objects.filter(
            equipment=equipment, account=account, status='pending'
        ).first()
        if existing:
            messages.warning(request, 'У вас уже есть активная заявка на эту технику.')
            return redirect('chat:thread', request_id=existing.id)
        message = (request.POST.get('message', '') or '').strip()
        lease_req = LeaseRequest.objects.create(
            equipment=equipment,
            account=account,
            message=message,
        )
        messages.success(
            request,
            f'Заявка на {equipment.name} ({equipment.model}) отправлена. '
            'Менеджер свяжется с вами для подтверждения.'
        )
        return redirect('chat:thread', request_id=lease_req.id)

    return redirect('core:leasing')


def my_equipment(request):
    """Страница «Моя техника» — техника, взятая пользователем в лизинг (только для обычных пользователей).
    Показывает: 1) договоры (LeaseContract) по компаниям пользователя;
    2) подтверждённые заявки (LeaseRequest), когда договор ещё не оформлен."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')
    if account.role and account.role.name in ('admin', 'manager'):
        messages.error(request, 'Эта страница доступна только клиентам.')
        return redirect('core:home')

    contracts = LeaseContract.objects.filter(
        company__account=account
    ).select_related(
        'equipment', 'equipment__category', 'equipment__manufacturer',
        'company', 'lease_request'
    ).prefetch_related('payment_schedule').order_by('-start_date')

    # Подтверждённые заявки — техника, по которой менеджер подтвердил заявку (договор может быть ещё не создан)
    confirmed_requests_qs = LeaseRequest.objects.filter(
        account=account,
        status='confirmed'
    ).select_related('equipment', 'equipment__category', 'equipment__manufacturer').order_by('-updated_at')

    # Есть ли у пользователя техника вообще (до поиска и фильтров) — для отображения поиска и фильтров
    has_any_equipment = contracts.exists() or confirmed_requests_qs.exists()

    # Поиск
    search_q = (request.GET.get('q', '') or '').strip()
    if search_q:
        contracts = contracts.filter(
            Q(equipment__name__icontains=search_q)
            | Q(equipment__model__icontains=search_q)
            | Q(equipment__category__name__icontains=search_q)
            | Q(equipment__manufacturer__name__icontains=search_q)
            | Q(contract_number__icontains=search_q)
            | Q(company__name__icontains=search_q)
        )
        confirmed_requests_qs = confirmed_requests_qs.filter(
            Q(equipment__name__icontains=search_q)
            | Q(equipment__model__icontains=search_q)
            | Q(equipment__category__name__icontains=search_q)
            | Q(equipment__manufacturer__name__icontains=search_q)
        )

    # Исключаем технику, которая уже есть в договорах (чтобы не дублировать)
    contract_equipment_ids = set(contracts.values_list('equipment_id', flat=True))
    confirmed_requests = [r for r in confirmed_requests_qs if r.equipment_id not in contract_equipment_ids]

    # Фильтр по статусу
    status_filter = request.GET.get('status', '')
    if status_filter == 'confirmed':
        contracts = contracts.none()
    elif status_filter in ('active', 'completed', 'terminated', 'draft'):
        contracts = contracts.filter(status=status_filter)

    if status_filter and status_filter != 'confirmed':
        confirmed_requests = []

    contracts = list(contracts)
    for contract in contracts:
        image_urls = getattr(contract.equipment, 'images_urls', []) or []
        contract.preview_image_url = _extract_first_image_url(image_urls)

    for req in confirmed_requests:
        image_urls = getattr(req.equipment, 'images_urls', []) or []
        req.preview_image_url = _extract_first_image_url(image_urls)

    return render(request, 'core/my_equipment.html', {
        'contracts': contracts,
        'confirmed_requests': confirmed_requests,
        'status_filter': status_filter,
        'search_q': search_q,
        'has_any_equipment': has_any_equipment,
        'current_account': account,
    })


def contract_sign(request, pk):
    """Подписание договора пользователем (подтверждение)."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')
    if account.role and account.role.name in ('admin', 'manager'):
        messages.error(request, 'Договор подписывает клиент.')
        return redirect('core:my_equipment')

    contract = get_object_or_404(LeaseContract, pk=pk)
    if contract.company.account_id != account.id:
        messages.error(request, 'Нет доступа к этому договору.')
        return redirect('core:my_equipment')
    if contract.signed_at:
        messages.info(request, 'Договор уже подписан.')
        return redirect('core:my_equipment')
    if contract.status != 'draft':
        messages.info(request, 'Договор уже обработан.')
        return redirect('core:my_equipment')

    if request.method == 'POST':
        contract.status = 'active'
        contract.signed_at = timezone.now()
        contract.signed_by = account
        contract.save()
        messages.success(request, f'Договор {contract.contract_number} подписан. Техника доступна в «Моя техника».')
        return redirect('core:my_equipment')

    return render(request, 'core/contract_sign.html', {'contract': contract})


def contract_pay(request, pk):
    """Создание платежа в ЮKassa и редирект на страницу подтверждения."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')
    if account.role and account.role.name in ('admin', 'manager'):
        return redirect('core:my_equipment')

    contract = get_object_or_404(LeaseContract, pk=pk)
    if contract.company.account_id != account.id:
        messages.error(request, 'Нет доступа.')
        return redirect('core:my_equipment')

    pending_qs = contract.payment_schedule.filter(status='pending').order_by('due_date')
    payments = list(pending_qs)

    if request.method == 'POST':
        shop_id = getattr(settings, 'YOOKASSA_SHOP_ID', '')
        secret_key = getattr(settings, 'YOOKASSA_SECRET_KEY', '')
        if not shop_id or not secret_key:
            messages.error(request, 'Не настроены YOOKASSA_SHOP_ID/YOOKASSA_SECRET_KEY в .env.')
            return redirect('core:contract_pay', pk=pk)

        amount_raw = request.POST.get('amount', '').strip()
        pay_id = request.POST.get('payment_id', '').strip()
        if not amount_raw:
            messages.error(request, 'Укажите сумму.')
            return redirect('core:contract_pay', pk=pk)

        try:
            amount_val = Decimal(amount_raw.replace(',', '.'))
        except (InvalidOperation, AttributeError):
            messages.error(request, 'Некорректная сумма.')
            return redirect('core:contract_pay', pk=pk)

        if amount_val <= Decimal('0'):
            messages.error(request, 'Сумма должна быть больше 0.')
            return redirect('core:contract_pay', pk=pk)

        pending_payment = None
        if pay_id:
            try:
                pending_payment = PaymentSchedule.objects.get(
                    contract=contract, pk=int(pay_id), status='pending'
                )
            except (ValueError, PaymentSchedule.DoesNotExist):
                messages.error(request, 'Платёж по графику не найден.')
                return redirect('core:contract_pay', pk=pk)
            amount_val = pending_payment.amount

        Configuration.configure(shop_id, secret_key)
        return_url = request.build_absolute_uri(
            reverse('core:contract_pay_return', kwargs={'pk': contract.pk})
        )

        metadata = {
            'contract_id': str(contract.id),
            'account_id': str(account.id),
        }
        if pending_payment:
            metadata['payment_schedule_id'] = str(pending_payment.id)

        try:
            yk_payment = Payment.create(
                {
                    'amount': {
                        'value': str(amount_val.quantize(Decimal('0.01'))),
                        'currency': 'RUB',
                    },
                    'capture': True,
                    'confirmation': {
                        'type': 'redirect',
                        'return_url': return_url,
                    },
                    'description': f'Оплата по договору {contract.contract_number}',
                    'metadata': metadata,
                },
                str(uuid4()),
            )
        except Exception:
            messages.error(request, 'Не удалось создать платёж в ЮKassa.')
            return redirect('core:contract_pay', pk=pk)

        confirmation = getattr(yk_payment, 'confirmation', None)
        confirmation_url = getattr(confirmation, 'confirmation_url', None)
        if not confirmation_url:
            messages.error(request, 'ЮKassa не вернула ссылку для подтверждения платежа.')
            return redirect('core:contract_pay', pk=pk)

        # payment_id не всегда приходит обратно в return_url query params,
        # поэтому сохраняем его в сессию как fallback.
        pending_ids = request.session.get('yookassa_pending_payments', {})
        pending_ids[str(contract.id)] = str(yk_payment.id)
        request.session['yookassa_pending_payments'] = pending_ids
        request.session.modified = True

        return redirect(confirmation_url)

    paid_qs = contract.payment_schedule.filter(status='paid')
    paid_total = paid_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_amount = contract.total_amount or Decimal('0')
    remaining_total = max(total_amount - paid_total, Decimal('0'))
    progress_percent = 0
    if total_amount > 0:
        progress_percent = min(100, int((paid_total / total_amount) * 100))

    today = timezone.localdate()
    current_month_payment = pending_qs.filter(
        due_date__year=today.year,
        due_date__month=today.month,
    ).first()
    next_payment = payments[0] if payments else None
    quick_month_payment = current_month_payment or next_payment
    remaining_this_month = quick_month_payment.amount if quick_month_payment else Decimal('0')

    pending_count = len(payments)
    paid_count = paid_qs.count()
    month_status = 'none'
    month_status_label = 'Нет платежа в этом месяце'
    month_status_class = 'neutral'
    if current_month_payment:
        if current_month_payment.due_date < today:
            month_status = 'overdue'
            month_status_label = 'Просрочен'
            month_status_class = 'danger'
        elif current_month_payment.due_date == today:
            month_status = 'today'
            month_status_label = 'Оплата сегодня'
            month_status_class = 'warning'
        else:
            month_status = 'upcoming'
            month_status_label = 'В срок'
            month_status_class = 'success'

    return render(request, 'core/contract_pay.html', {
        'contract': contract,
        'payments': payments,
        'paid_total': paid_total,
        'remaining_total': remaining_total,
        'remaining_this_month': remaining_this_month,
        'current_month_payment': current_month_payment,
        'next_payment': next_payment,
        'quick_month_payment': quick_month_payment,
        'pending_count': pending_count,
        'paid_count': paid_count,
        'progress_percent': progress_percent,
        'month_status': month_status,
        'month_status_label': month_status_label,
        'month_status_class': month_status_class,
    })


def contract_pay_return(request, pk):
    """Обработка возврата пользователя после оплаты в ЮKassa."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')

    contract = get_object_or_404(LeaseContract, pk=pk)
    if contract.company.account_id != account.id:
        messages.error(request, 'Нет доступа.')
        return redirect('core:my_equipment')

    payment_id = (request.GET.get('paymentId') or request.GET.get('payment_id') or '').strip()
    if not payment_id:
        pending_ids = request.session.get('yookassa_pending_payments', {})
        payment_id = (pending_ids.get(str(contract.id)) or '').strip()
    if not payment_id:
        messages.error(request, 'Не найден идентификатор платежа.')
        return redirect('core:contract_pay', pk=pk)

    shop_id = getattr(settings, 'YOOKASSA_SHOP_ID', '')
    secret_key = getattr(settings, 'YOOKASSA_SECRET_KEY', '')
    if not shop_id or not secret_key:
        messages.error(request, 'Не настроены YOOKASSA_SHOP_ID/YOOKASSA_SECRET_KEY в .env.')
        return redirect('core:contract_pay', pk=pk)

    Configuration.configure(shop_id, secret_key)
    try:
        yk_payment = Payment.find_one(payment_id)
    except Exception:
        messages.error(request, 'Не удалось получить статус платежа в ЮKassa.')
        return redirect('core:contract_pay', pk=pk)

    if getattr(yk_payment, 'status', '') != 'succeeded':
        messages.warning(request, 'Платёж еще не завершен. Попробуйте проверить позже.')
        return redirect('core:contract_pay', pk=pk)

    metadata = getattr(yk_payment, 'metadata', {}) or {}
    if str(metadata.get('contract_id', '')) != str(contract.id):
        messages.error(request, 'Платёж не относится к этому договору.')
        return redirect('core:contract_pay', pk=pk)

    amount_obj = getattr(yk_payment, 'amount', None)
    amount_val = Decimal(str(getattr(amount_obj, 'value', '0')))

    with transaction.atomic():
        already_processed = PaymentSchedule.objects.filter(external_payment_id=payment_id).exists()
        if already_processed:
            messages.info(request, 'Этот платёж уже учтен в графике.')
            return redirect('core:contract_pay', pk=pk)

        payment_schedule_id = metadata.get('payment_schedule_id')
        if payment_schedule_id:
            try:
                ps = PaymentSchedule.objects.select_for_update().get(
                    contract=contract,
                    pk=int(payment_schedule_id),
                )
            except (ValueError, PaymentSchedule.DoesNotExist):
                messages.error(request, 'Платёж по графику не найден.')
                return redirect('core:contract_pay', pk=pk)

            if ps.status != 'paid':
                ps.status = 'paid'
                ps.paid_at = timezone.now()
                ps.external_payment_id = payment_id
                ps.save(update_fields=['status', 'paid_at', 'external_payment_id'])
                messages.success(request, f'Платёж #{ps.payment_number} успешно оплачен.')
            else:
                messages.info(request, 'Этот платёж по графику уже был оплачен ранее.')
            return redirect('core:contract_pay', pk=pk)

        next_num = contract.payment_schedule.count() + 1
        due = contract.start_date + timedelta(days=30 * (next_num - 1))
        PaymentSchedule.objects.create(
            contract=contract,
            payment_number=next_num,
            due_date=due,
            amount=amount_val,
            status='paid',
            paid_at=timezone.now(),
            external_payment_id=payment_id,
        )

    messages.success(request, f'Оплата {amount_val:.2f} руб. успешно проведена.')
    pending_ids = request.session.get('yookassa_pending_payments', {})
    if str(contract.id) in pending_ids:
        pending_ids.pop(str(contract.id), None)
        request.session['yookassa_pending_payments'] = pending_ids
        request.session.modified = True
    return redirect('core:contract_pay', pk=pk)


def my_maintenance_requests(request):
    """Список заявок на ТО пользователя."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')
    if account.role and account.role.name in ('admin', 'manager'):
        return redirect('core:my_equipment')

    requests_list = MaintenanceRequest.objects.filter(
        company__account=account
    ).select_related('equipment', 'equipment__category', 'equipment__manufacturer').order_by('-created_at')

    return render(request, 'core/my_maintenance_requests.html', {
        'maintenance_requests': requests_list,
        'current_account': account,
    })


def maintenance_request_create(request, pk):
    """Создание заявки на ТО по технике из договора."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')
    if account.role and account.role.name in ('admin', 'manager'):
        return redirect('core:my_equipment')

    contract = get_object_or_404(LeaseContract, pk=pk)
    if contract.company.account_id != account.id:
        messages.error(request, 'Нет доступа.')
        return redirect('core:my_equipment')

    if request.method == 'POST':
        description = (request.POST.get('description') or '').strip()
        urgency = request.POST.get('urgency', 'normal')
        if not description:
            messages.error(request, 'Опишите проблему.')
        else:
            maint_req = MaintenanceRequest.objects.create(
                equipment=contract.equipment,
                company=contract.company,
                description=description,
                urgency=urgency,
                status='new',
            )
            messages.success(
                request,
                'Заявка на ТО создана. Чат с менеджером открыт.'
            )
            return redirect('chat:maintenance_thread', pk=maint_req.id)

    return render(request, 'core/maintenance_request_form.html', {
        'contract': contract,
    })


def privacy(request):
    return render(request, 'core/privacy.html')


def about(request):
    return render(request, 'core/about.html')


def page_not_found(request, exception=None):
    """Кастомная страница 404."""
    return render(request, '404.html', status=404)


def page_404_preview(request):
    """Предпросмотр страницы 404 (для проверки в режиме DEBUG=True)."""
    return render(request, '404.html')
