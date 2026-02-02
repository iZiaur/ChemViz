from django.db import models
from django.contrib.auth.models import User
import binascii
import os


class Token(models.Model):
    """Token model for API authentication."""
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_token')
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


class EquipmentDataset(models.Model):
    """Stores metadata and summary for each uploaded CSV dataset. Max 5 kept."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(default=0.0)
    avg_pressure = models.FloatField(default=0.0)
    avg_temperature = models.FloatField(default=0.0)
    type_distribution = models.JSONField(default=dict)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"


class EquipmentRecord(models.Model):
    """Individual equipment record linked to a dataset."""
    dataset = models.ForeignKey(EquipmentDataset, on_delete=models.CASCADE, related_name='records')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField(default=0.0)
    pressure = models.FloatField(default=0.0)
    temperature = models.FloatField(default=0.0)

    class Meta:
        ordering = ['equipment_name']

    def __str__(self):
        return self.equipment_name
