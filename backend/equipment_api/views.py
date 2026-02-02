import pandas as pd
import io
import os
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.http import HttpResponse
from django.db import transaction

from equipment_api.models import EquipmentDataset, EquipmentRecord
from equipment_api.serializers import (
    EquipmentDatasetSerializer,
    DatasetSummarySerializer,
)


def parse_csv(file_content: str) -> pd.DataFrame:
    """Parse CSV content into a cleaned DataFrame."""
    df = pd.read_csv(io.StringIO(file_content))
    # Normalize column names
    df.columns = df.columns.str.strip()
    # Map expected columns (flexible matching)
    col_map = {}
    for col in df.columns:
        lower = col.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('°c', '').replace('l/min', '').replace('bar', '').strip('_')
        if 'equipment_name' in lower or 'name' in lower:
            col_map[col] = 'equipment_name'
        elif 'type' in lower:
            col_map[col] = 'equipment_type'
        elif 'flowrate' in lower or 'flow' in lower:
            col_map[col] = 'flowrate'
        elif 'pressure' in lower:
            col_map[col] = 'pressure'
        elif 'temperature' in lower or 'temp' in lower:
            col_map[col] = 'temperature'
    df.rename(columns=col_map, inplace=True)

    required = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    df[['flowrate', 'pressure', 'temperature']] = df[['flowrate', 'pressure', 'temperature']].apply(
        pd.to_numeric, errors='coerce'
    ).fillna(0.0)
    df['equipment_name'] = df['equipment_name'].astype(str).str.strip()
    df['equipment_type'] = df['equipment_type'].astype(str).str.strip()

    return df


def compute_summary(df: pd.DataFrame) -> dict:
    """Compute summary statistics from the parsed DataFrame."""
    type_dist = df['equipment_type'].value_counts().to_dict()
    return {
        'total_records': len(df),
        'avg_flowrate': round(df['flowrate'].mean(), 2),
        'avg_pressure': round(df['pressure'].mean(), 2),
        'avg_temperature': round(df['temperature'].mean(), 2),
        'type_distribution': type_dist,
    }


def enforce_max_datasets(user, max_count=5):
    """Keep only the last N datasets for a user, deleting oldest if needed."""
    datasets = EquipmentDataset.objects.filter(user=user).order_by('-uploaded_at')
    count = datasets.count()
    if count >= max_count:
        to_delete = datasets[max_count - 1:]
        for ds in to_delete:
            ds.delete()


class UploadCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith('.csv'):
            return Response({'error': 'Only .csv files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content = file.read().decode('utf-8')
            df = parse_csv(content)
            summary = compute_summary(df)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce max 5 datasets
        enforce_max_datasets(request.user, max_count=5)

        try:
            with transaction.atomic():
                dataset = EquipmentDataset.objects.create(
                    user=request.user,
                    name=file.name,
                    total_records=summary['total_records'],
                    avg_flowrate=summary['avg_flowrate'],
                    avg_pressure=summary['avg_pressure'],
                    avg_temperature=summary['avg_temperature'],
                    type_distribution=summary['type_distribution'],
                )
                records = [
                    EquipmentRecord(
                        dataset=dataset,
                        equipment_name=row['equipment_name'],
                        equipment_type=row['equipment_type'],
                        flowrate=row['flowrate'],
                        pressure=row['pressure'],
                        temperature=row['temperature'],
                    )
                    for _, row in df.iterrows()
                ]
                EquipmentRecord.objects.bulk_create(records)
        except Exception as e:
            return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = EquipmentDatasetSerializer(dataset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DatasetHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datasets = EquipmentDataset.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
        serializer = DatasetSummarySerializer(datasets, many=True)
        return Response(serializer.data)


class DatasetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dataset_id):
        try:
            dataset = EquipmentDataset.objects.get(id=dataset_id, user=request.user)
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EquipmentDatasetSerializer(dataset)
        return Response(serializer.data)


class DatasetDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, dataset_id):
        try:
            dataset = EquipmentDataset.objects.get(id=dataset_id, user=request.user)
            dataset.delete()
            return Response({'message': 'Dataset deleted successfully.'}, status=status.HTTP_200_OK)
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found.'}, status=status.HTTP_404_NOT_FOUND)


class GeneratePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dataset_id):
        try:
            dataset = EquipmentDataset.objects.get(id=dataset_id, user=request.user)
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            # Fallback: generate a simple text-based PDF using basic bytes
            return self._generate_simple_pdf(dataset)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.6 * inch,
            leftMargin=0.6 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=22,
            textColor=HexColor('#1a2332'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#5a6a7a'),
            spaceAfter=16,
            alignment=TA_CENTER,
        )
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#2c5f8a'),
            spaceBefore=18,
            spaceAfter=8,
            fontName='Helvetica-Bold',
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#333333'),
            spaceAfter=4,
        )

        story = []

        # Title
        story.append(Paragraph("Chemical Equipment Parameter Report", title_style))
        story.append(Paragraph(f"Dataset: {dataset.name} &nbsp;|&nbsp; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp; User: {request.user.username}", subtitle_style))
        story.append(Spacer(1, 8))

        # Summary Section
        story.append(Paragraph("Summary Statistics", section_style))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Equipment', str(dataset.total_records)],
            ['Avg Flowrate', f"{dataset.avg_flowrate} L/min"],
            ['Avg Pressure', f"{dataset.avg_pressure} bar"],
            ['Avg Temperature', f"{dataset.avg_temperature} °C"],
        ]
        summary_table = Table(summary_data, colWidths=[2.5 * inch, 2.5 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c5f8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f0f4f8')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#c8d6e0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 12))

        # Type Distribution
        story.append(Paragraph("Equipment Type Distribution", section_style))
        dist_data = [['Equipment Type', 'Count', 'Percentage']]
        total = dataset.total_records or 1
        for etype, count in sorted(dataset.type_distribution.items()):
            pct = round((count / total) * 100, 1)
            dist_data.append([etype, str(count), f"{pct}%"])
        dist_table = Table(dist_data, colWidths=[2.8 * inch, 1.0 * inch, 1.2 * inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c5f8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f0f4f8')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f0f4f8'), HexColor('#ffffff')]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9.5),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#c8d6e0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 1), (0, -1), 8),
        ]))
        story.append(dist_table)

        # Equipment Records Table
        story.append(PageBreak())
        story.append(Paragraph("Equipment Records", section_style))

        records = dataset.records.all()
        header = ['#', 'Equipment Name', 'Type', 'Flowrate (L/min)', 'Pressure (bar)', 'Temp (°C)']
        table_data = [header]
        for i, rec in enumerate(records, 1):
            table_data.append([
                str(i),
                rec.equipment_name,
                rec.equipment_type,
                f"{rec.flowrate:.1f}",
                f"{rec.pressure:.1f}",
                f"{rec.temperature:.1f}",
            ])

        col_widths = [0.4 * inch, 2.2 * inch, 1.2 * inch, 1.1 * inch, 1.1 * inch, 1.0 * inch]
        rec_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c5f8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f7f9fb'), HexColor('#ffffff')]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.4, HexColor('#c8d6e0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (1, 1), (1, -1), 6),
        ]))
        story.append(rec_table)

        doc.build(story)
        buffer.seek(0)

        filename = f"report_{dataset.name.replace('.csv', '')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _generate_simple_pdf(self, dataset):
        """Fallback plain-text PDF if reportlab is not installed."""
        lines = []
        lines.append("Chemical Equipment Parameter Report")
        lines.append(f"Dataset: {dataset.name}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        lines.append("=== Summary ===")
        lines.append(f"Total Records: {dataset.total_records}")
        lines.append(f"Avg Flowrate: {dataset.avg_flowrate} L/min")
        lines.append(f"Avg Pressure: {dataset.avg_pressure} bar")
        lines.append(f"Avg Temperature: {dataset.avg_temperature} °C")
        lines.append("")
        lines.append("=== Type Distribution ===")
        for t, c in dataset.type_distribution.items():
            lines.append(f"  {t}: {c}")
        lines.append("")
        lines.append("=== Records ===")
        for rec in dataset.records.all():
            lines.append(f"  {rec.equipment_name} | {rec.equipment_type} | Flow: {rec.flowrate} | Press: {rec.pressure} | Temp: {rec.temperature}")

        content = "\n".join(lines)
        filename = f"report_{dataset.name.replace('.csv', '')}.txt"
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
