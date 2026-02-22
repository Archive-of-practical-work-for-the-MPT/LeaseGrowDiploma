from django.db import models

from apps.accounts.models import Account


class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changed_fields = models.JSONField(default=list, blank=True)
    performed_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_log'
        verbose_name = 'запись аудита'
        verbose_name_plural = 'журнал аудита'
        indexes = [
            models.Index(fields=['table_name', 'record_id'], name='idx_audit_table_record'),
            models.Index(fields=['performed_at'], name='idx_audit_performed_at'),
        ]
        ordering = ['-performed_at']

    def __str__(self):
        return f'{self.action} {self.table_name}.{self.record_id}'
