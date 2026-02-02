from django.contrib import admin
from equipment_api.models import EquipmentDataset, EquipmentRecord, Token


class EquipmentRecordInline(admin.TabularInline):
    model = EquipmentRecord
    extra = 0
    readonly_fields = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


@admin.register(EquipmentDataset)
class EquipmentDatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'uploaded_at', 'total_records', 'avg_flowrate', 'avg_pressure', 'avg_temperature']
    list_filter = ['user', 'uploaded_at']
    search_fields = ['name', 'user__username']
    inlines = [EquipmentRecordInline]
    readonly_fields = ['uploaded_at', 'total_records', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution']


@admin.register(EquipmentRecord)
class EquipmentRecordAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['equipment_name']


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', 'created']
    readonly_fields = ['key', 'created']
