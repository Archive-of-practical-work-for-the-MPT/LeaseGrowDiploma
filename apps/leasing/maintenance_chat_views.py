"""Чат по заявке на ТО — доступен клиенту и менеджеру."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.accounts.views import get_current_account
from .models import MaintenanceRequest, MaintenanceChatMessage


def _can_access_maintenance_chat(account, maint_req):
    """Проверка доступа: владелец компании заявки или менеджер."""
    if not account:
        return False
    if maint_req.company.account_id == account.id:
        return True
    if account.role and account.role.name in ('manager', 'admin'):
        return True
    return False


def maintenance_chat_thread(request, pk):
    """Страница чата по заявке на ТО."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')

    maint_req = get_object_or_404(MaintenanceRequest, pk=pk)
    if not _can_access_maintenance_chat(account, maint_req):
        messages.error(request, 'Нет доступа к этому чату.')
        return redirect('core:my_maintenance_requests')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action and account.role and account.role.name in ('manager', 'admin'):
            if action in ('in_progress', 'completed', 'cancelled'):
                maint_req.status = action
                if action == 'in_progress':
                    maint_req.assigned_to = account
                elif action == 'completed':
                    maint_req.completed_at = timezone.now()
                maint_req.save()
                if action == 'in_progress':
                    messages.success(request, 'Статус изменён: в работе.')
                elif action == 'completed':
                    messages.success(request, 'Заявка выполнена.')
                else:
                    messages.success(request, 'Заявка отменена.')
                return redirect('chat:maintenance_thread', pk=maint_req.id)

        text = (request.POST.get('text', '') or '').strip()
        if text and maint_req.status != 'cancelled':
            msg = MaintenanceChatMessage.objects.create(
                maintenance_request=maint_req,
                sender=account,
                text=text,
            )
            try:
                sender_name = account.profile.first_name or account.username
            except Exception:
                sender_name = account.username
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'maint_chat_{maint_req.id}',
                {
                    'type': 'chat_message',
                    'data': {
                        'id': msg.id,
                        'text': msg.text,
                        'sender_id': account.id,
                        'sender_name': sender_name,
                        'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
                    },
                },
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'ok': True,
                    'message': {
                        'id': msg.id,
                        'text': msg.text,
                        'sender_id': account.id,
                        'sender_name': sender_name,
                        'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
                    },
                })
            return redirect('chat:maintenance_thread', pk=maint_req.id)

    messages_list = maint_req.messages.select_related(
        'sender', 'sender__profile').all()
    is_manager = account.role and account.role.name in ('manager', 'admin')

    return render(request, 'leasing/maintenance_chat_thread.html', {
        'maintenance_request': maint_req,
        'messages_list': messages_list,
        'current_account': account,
        'is_manager': is_manager,
    })
