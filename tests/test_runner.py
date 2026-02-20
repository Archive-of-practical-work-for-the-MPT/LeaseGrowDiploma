"""
Кастомный тест-раннер с подробным выводом на русском.
Подключается в settings.py: TEST_RUNNER = 'tests.test_runner.RussianDiscoverRunner'
"""
import unittest
from django.test.runner import DiscoverRunner


# Краткие описания тестов (fallback, если нет docstring)
ОПИСАНИЯ_ТЕСТОВ = {
    # test_crud
    'test_role_crud': 'CRUD для роли (Role)',
    'test_account_crud': 'CRUD для аккаунта (Account)',
    'test_equipment_crud': 'CRUD для техники (Equipment)',
    'test_lease_request_crud': 'CRUD для заявки на лизинг (LeaseRequest)',
    # test_api
    'test_api_root_ok': 'Корень API (/api/)',
    'test_equipment_list_and_detail': 'API техники: список и чтение по id',
    'test_companies_list': 'API компаний: список',
    'test_invalid_token_rejected': 'API: неверный токен отклонён',
    'test_valid_token_accepted': 'API: верный токен принят',
    # test_export
    'test_export_without_login_redirects': 'Экспорт без логина: редирект',
    'test_export_excel_as_manager': 'Экспорт Excel для менеджера',
    'test_export_pdf_as_manager': 'Экспорт PDF для менеджера',
    # test_views
    'test_home_returns_200': 'Главная страница возвращает 200',
    'test_home_contains_leasing_link': 'Главная содержит ссылку на лизинг',
    'test_login_page_ok': 'Страница логина доступна',
    'test_login_success': 'Успешный вход сохраняет сессию',
    'test_logout_clears_session': 'Выход очищает сессию',
    'test_leasing_page_ok': 'Страница лизинга доступна',
    'test_leasing_shows_equipment': 'Лизинг отображает технику',
    'test_profile_redirects_if_not_logged_in': 'Профиль без логина: редирект',
    'test_profile_ok_when_logged_in': 'Профиль доступен после входа',
    'test_lease_request_requires_login': 'Заявка на лизинг требует логин',
    'test_lease_request_creates_record': 'Заявка на лизинг создаёт запись',
    'test_chat_requires_login': 'Чат без логина: редирект',
    'test_chat_accessible_by_request_owner': 'Чат доступен владельцу заявки',
}


class RussianTextTestResult(unittest.TextTestResult):
    """Результат тестов с выводом на русском и подробным логом."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, max(2, verbosity))
        self._test_index = 0

    def _description(self, test):
        """Краткое описание теста на русском."""
        desc = test.shortDescription()
        if desc:
            return desc.strip()
        method_name = getattr(test, '_testMethodName', '') or str(test)
        return ОПИСАНИЯ_ТЕСТОВ.get(method_name, method_name)

    def startTest(self, test):
        self._test_index += 1
        if self.showAll:
            desc = self._description(test)
            self.stream.write(f"  [{self._test_index}] {desc} ... ")
            self.stream.flush()
        super().startTest(test)

    def addSuccess(self, test):
        if self.showAll:
            self.stream.writeln("пройден")
            self.stream.flush()
        else:
            self.stream.write('.')
            self.stream.flush()
        unittest.TestResult.addSuccess(self, test)

    def addFailure(self, test, err):
        if self.showAll:
            self.stream.writeln("ПРОВАЛ")
            self.stream.flush()
        else:
            self.stream.write('F')
            self.stream.flush()
        super().addFailure(test, err)

    def addError(self, test, err):
        if self.showAll:
            self.stream.writeln("ОШИБКА")
            self.stream.flush()
        else:
            self.stream.write('E')
            self.stream.flush()
        super().addError(test, err)

    def addSkip(self, test, reason):
        if self.showAll:
            self.stream.writeln(f"пропущен ({reason})")
            self.stream.flush()
        super().addSkip(test, reason)

    def printErrors(self):
        """Вывод провалов и ошибок на русском."""
        if not self.failures and not self.errors:
            return
        self.stream.writeln()
        if self.failures:
            self.stream.writeln(self.separator1)
            self.stream.writeln("ПРОВАЛЫ ТЕСТОВ")
            self.stream.writeln(self.separator2)
            for test, err in self.failures:
                self.stream.writeln(f"  Тест: {self._description(test)}")
                self.stream.writeln(self.separator2)
                self.stream.writeln(err)
                self.stream.writeln()
        if self.errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("ОШИБКИ ВЫПОЛНЕНИЯ")
            self.stream.writeln(self.separator2)
            for test, err in self.errors:
                self.stream.writeln(f"  Тест: {self._description(test)}")
                self.stream.writeln(self.separator2)
                self.stream.writeln(err)
                self.stream.writeln()
        self.stream.flush()


class RussianTextTestRunner(unittest.TextTestRunner):
    """Запуск тестов с результатом на русском."""

    resultclass = RussianTextTestResult

    def __init__(self, verbosity=1, resultclass=None, **kwargs):
        super().__init__(
            verbosity=max(2, verbosity),
            resultclass=resultclass or RussianTextTestResult,
            **kwargs
        )

    def run(self, test):
        result = super().run(test)
        self.stream.writeln('-' * 70)
        if result.wasSuccessful():
            self.stream.writeln(
                f"Выполнено тестов: {result.testsRun}, все пройдены успешно."
            )
        else:
            failed = len(result.failures) + len(result.errors)
            self.stream.writeln(
                f"Выполнено тестов: {result.testsRun}, "
                f"провалов/ошибок: {failed}."
            )
        self.stream.writeln()
        self.stream.flush()
        return result


class RussianDiscoverRunner(DiscoverRunner):
    """
    Django DiscoverRunner с подробным выводом на русском.
    Устанавливает verbosity=2 и свой класс результата.
    """

    test_runner = RussianTextTestRunner
    resultclass = RussianTextTestResult

    def __init__(self, verbosity=1, **kwargs):
        super().__init__(verbosity=max(2, verbosity), **kwargs)

    def run_tests(self, test_labels=None, extra_tests=None, **kwargs):
        """Запуск тестов с заголовком и итогом на русском."""
        import sys
        stream = sys.stderr
        stream.write("\n" + "=" * 70 + "\n")
        stream.write("        LeaseGrow — автоматизированные тесты\n")
        stream.write("=" * 70 + "\n\n")
        stream.flush()
        return super().run_tests(test_labels, **kwargs)

    def run_suite(self, suite, **kwargs):
        """Запуск набора тестов с нашим runner и result class."""
        runner = self.test_runner(
            verbosity=self.verbosity,
            failfast=self.failfast,
            buffer=False,
            resultclass=self.resultclass,
        )
        return runner.run(suite)
