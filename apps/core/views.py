from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.catalog.models import Equipment
from apps.leasing.models import LeaseRequest
from apps.accounts.views import get_current_account


def home(request):
    return render(request, 'core/home.html')


def leasing(request):
    """Страница лизинга — каталог доступной техники."""
    equipment_list = Equipment.objects.filter(
        status='available'
    ).select_related('category', 'manufacturer').order_by('category__name', 'name')

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

    return render(request, 'core/leasing.html', {
        'equipment_list': equipment_list,
        'my_requests': my_requests,
        'pending_equipment_ids': pending_equipment_ids,
        'current_account': account,
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


def privacy(request):
    return render(request, 'core/privacy.html')


def page_not_found(request, exception=None):
    """Кастомная страница 404."""
    return render(request, '404.html', status=404)


def page_404_preview(request):
    """Предпросмотр страницы 404 (для проверки в режиме DEBUG=True)."""
    return render(request, '404.html')
