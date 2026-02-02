from django.urls import path
from equipment_api.views import (
    UploadCSVView,
    DatasetHistoryView,
    DatasetDetailView,
    DatasetDeleteView,
    GeneratePDFView,
)

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='upload-csv'),
    path('history/', DatasetHistoryView.as_view(), name='dataset-history'),
    path('dataset/<int:dataset_id>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('dataset/<int:dataset_id>/delete/', DatasetDeleteView.as_view(), name='dataset-delete'),
    path('dataset/<int:dataset_id>/report/', GeneratePDFView.as_view(), name='dataset-report'),
]
