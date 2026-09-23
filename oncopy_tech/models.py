from django.db import models


class RepairRequest(models.Model):
    phone = models.CharField('Телефон', max_length=20)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на ремонт'
        verbose_name_plural = 'Заявки на ремонт'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка от {self.phone}'