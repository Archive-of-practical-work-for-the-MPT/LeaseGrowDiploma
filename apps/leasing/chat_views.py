"""Чат по заявке на лизинг — доступен клиенту и менеджеру."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.accounts.views import get_current_account
from .models import LeaseRequest, ChatMessage


def _can_access_chat(account, lease_request):
    """Проверка доступа: владелец заявки или менеджер."""
    if not account:
        return False
    if lease_request.account_id == account.id:
        return True
    if account.role and account.role.name == 'manager':
        return True
    if account.role and account.role.name == 'admin':
        return True
    return False


def chat_thread(request, request_id):
    """Страница чата по заявке."""
    account = get_current_account(request)
    if not account:
        messages.error(request, 'Войдите в систему.')
        return redirect('accounts:login')

    lease_req = get_object_or_404(LeaseRequest, pk=request_id)
    if not _can_access_chat(account, lease_req):
        messages.error(request, 'Нет доступа к этому чату.')
        return redirect('core:leasing')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm' and _can_access_chat(account, lease_req):
            if account.role and account.role.name in ('manager', 'admin') and lease_req.status == 'pending':
                lease_req.status = 'confirmed'
                lease_req.confirmed_by = account
                lease_req.save()
                messages.success(request, 'Заявка подтверждена.')
                return redirect('chat:thread', request_id=lease_req.id)
        elif action == 'reject' and _can_access_chat(account, lease_req):
            if account.role and account.role.name in ('manager', 'admin') and lease_req.status == 'pending':
                notes = (request.POST.get('manager_notes', '') or '').strip()
                lease_req.status = 'rejected'
                lease_req.manager_notes = notes
                lease_req.confirmed_by = account
                lease_req.save()
                messages.success(request, 'Заявка отклонена.')
                return redirect('chat:thread', request_id=lease_req.id)

        text = (request.POST.get('text', '') or '').strip()
        if text:
            ChatMessage.objects.create(
                lease_request=lease_req,
                sender=account,
                text=text,
            )
            return redirect('chat:thread', request_id=lease_req.id)

    messages_list = lease_req.messages.select_related('sender', 'sender__profile').all()
    is_manager = account.role and account.role.name in ('manager', 'admin')

    return render(request, 'leasing/chat_thread.html', {
        'lease_request': lease_req,
        'messages_list': messages_list,
        'current_account': account,
        'is_manager': is_manager,
    })
