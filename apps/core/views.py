from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from django.utils import timezone

from apps.catalog.models import Equipment, EquipmentCategory, Manufacturer
from apps.leasing.models import (
    LeaseRequest, LeaseContract, Company,
    PaymentSchedule, MaintenanceRequest,
)
from apps.accounts.views import get_current_account


def home(request):
    return render(request, 'core/home.html')


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
    my_requests = []
    pending_equipment_ids = set()
    pending_lease_requests = {}
    can_cancel_ids = set()
    if account:
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

    get_copy = request.GET.copy()
    get_copy.pop('page', None)
    query_string = get_copy.urlencode()

    return render(request, 'core/leasing.html', {
        'equipment_list': equipment_list,
        'page_obj': page_obj,
        'query_string': query_string,
        'my_requests': my_requests,
        'can_cancel_ids': can_cancel_ids,
        'pending_equipment_ids': pending_equipment_ids,
        'pending_lease_requests': pending_lease_requests,
        'current_account': account,
        'categories': categories,
        'manufacturers': manufacturers,
        'search_q': q,
        'filter_category_id': category_id,
        'filter_manufacturer_id': manufacturer_id,
        'sort': sort,
    })


def leasing_request_create(request, equipment_id):
    """Создание заявки на лизинг пользователем."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему, чтобы оформить заявку.')
        return redirect('accounts:login')

    # Клиент должен быть связан с компанией
    if account.role and account.role.name not in ('admin', 'manager'):
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
    """Фейковая оплата по договору."""
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

    payments = list(contract.payment_schedule.filter(status='pending').order_by('due_date'))

    if request.method == 'POST':
        amount = request.POST.get('amount', '').strip()
        pay_id = request.POST.get('payment_id', '').strip()
        if amount:
            try:
                amount_val = float(amount.replace(',', '.'))
                if amount_val <= 0:
                    raise ValueError('Сумма должна быть больше 0')
                if pay_id:
                    ps = PaymentSchedule.objects.get(
                        contract=contract, pk=int(pay_id), status='pending'
                    )
                    ps.status = 'paid'
                    ps.paid_at = timezone.now()
                    ps.save()
                else:
                    next_num = contract.payment_schedule.count() + 1
                    from datetime import timedelta
                    due = contract.start_date + timedelta(days=30 * (next_num - 1))
                    PaymentSchedule.objects.create(
                        contract=contract,
                        payment_number=next_num,
                        due_date=due,
                        amount=amount_val,
                        status='paid',
                        paid_at=timezone.now(),
                    )
                messages.success(request, f'Оплата {amount_val:.0f} руб. проведена.')
            except (ValueError, PaymentSchedule.DoesNotExist) as e:
                messages.error(request, 'Ошибка: ' + str(e) if isinstance(e, ValueError) else 'Платёж не найден.')
        else:
            messages.error(request, 'Укажите сумму.')
        return redirect('core:contract_pay', pk=pk)

    if not payments:
        payments = None  # Показать форму произвольной оплаты

    return render(request, 'core/contract_pay.html', {
        'contract': contract,
        'payments': payments,
    })


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
