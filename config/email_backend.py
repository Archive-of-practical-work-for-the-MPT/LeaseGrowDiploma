"""SMTP backend with automatic fallback port retry."""
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


class FallbackSMTPEmailBackend(SMTPEmailBackend):
    """
    SMTP backend that retries with fallback port when primary port fails.
    """

    def open(self):
        if self.connection:
            return False

        try:
            return super().open()
        except Exception:
            fallback_port = getattr(settings, "EMAIL_FALLBACK_PORT", None)
            if not fallback_port or int(fallback_port) == int(self.port):
                raise

            original_port = self.port
            self.port = int(fallback_port)
            try:
                return super().open()
            finally:
                # Keep active connection from fallback if opened.
                if not self.connection:
                    self.port = original_port
