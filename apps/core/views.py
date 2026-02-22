from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from apps.catalog.models import Equipment, EquipmentCategory, Manufacturer
from apps.leasing.models import LeaseRequest, LeaseContract
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
    if account:
        my_requests = LeaseRequest.objects.filter(
            account=account
        ).select_related('equipment').order_by('-created_at')
        pending_equipment_ids = set(
            LeaseRequest.objects.filter(
                account=account, status='pending'
            ).values_list('equipment_id', flat=True)
        )

    get_copy = request.GET.copy()
    get_copy.pop('page', None)
    query_string = get_copy.urlencode()

    return render(request, 'core/leasing.html', {
        'equipment_list': equipment_list,
        'page_obj': page_obj,
        'query_string': query_string,
        'my_requests': my_requests,
        'pending_equipment_ids': pending_equipment_ids,
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

    equipment = get_object_or_404(Equipment, pk=equipment_id, status='available')

    if request.method == 'POST':
        existing = LeaseRequest.objects.filter(
            equipment=equipment, account=account, status='pending'
        ).exists()
        if existing:
            messages.warning(request, 'У вас уже есть активная заявка на эту технику.')
        else:
            message = (request.POST.get('message', '') or '').strip()
            LeaseRequest.objects.create(
                equipment=equipment,
                account=account,
                message=message,
            )
            messages.success(
                request,
                f'Заявка на {equipment.name} ({equipment.model}) отправлена. '
                'Менеджер свяжется с вами для подтверждения.'
            )
        return redirect('core:leasing')

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
    ).select_related('equipment', 'equipment__category', 'equipment__manufacturer', 'company').order_by('-start_date')

    # Подтверждённые заявки — техника, по которой менеджер подтвердил заявку (договор может быть ещё не создан)
    confirmed_requests = LeaseRequest.objects.filter(
        account=account,
        status='confirmed'
    ).select_related('equipment', 'equipment__category', 'equipment__manufacturer').order_by('-updated_at')

    # Исключаем технику, которая уже есть в договорах (чтобы не дублировать)
    contract_equipment_ids = set(contracts.values_list('equipment_id', flat=True))
    confirmed_requests = [r for r in confirmed_requests if r.equipment_id not in contract_equipment_ids]

    return render(request, 'core/my_equipment.html', {
        'contracts': contracts,
        'confirmed_requests': confirmed_requests,
        'current_account': account,
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
