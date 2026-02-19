"""
Авторизация API по токену (AccountToken).
Заголовок: Authorization: Token <key>
"""
from rest_framework import authentication
from rest_framework import exceptions

from apps.accounts.models import AccountToken


class AccountTokenAuthentication(authentication.BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode('utf-8')
        if not auth_header or not auth_header.startswith(f'{self.keyword} '):
            return None
        key = auth_header[len(self.keyword):].strip()
        if not key:
            return None
        try:
            token = AccountToken.objects.select_related('account').get(key=key)
        except AccountToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Неверный или просроченный токен.')
        account = token.account
        if not account.is_active:
            raise exceptions.AuthenticationFailed('Аккаунт деактивирован.')
        return (account, token)
