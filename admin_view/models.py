from django.db import models
from sign.models import User


class AdminLogs(models.Model):
    log_id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=100)
    action_date = models.DateTimeField()
    ip_address = models.CharField(max_length=50)
    def __str__(self):
        return self.ip_address