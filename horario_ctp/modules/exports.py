import streamlit as st # type: ignore
import pandas as pd # type: ignore
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch # type: ignore
from io import BytesIO
import base64

def create_pdf_download_link(df, filename, title):
    """Crea un enlace de descarga para un DataFrame en formato PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )

    # Título
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))

    # Convertir DataFrame a lista de listas para la tabla
    data = [df.columns.tolist()] + df.values.tolist()

    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements)

    # Crear enlace de descarga
    pdf = buffer.getvalue()
    b64 = base64.b64encode(pdf).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf">📥 Descargar PDF</a>'
    return href

def export_schedule_to_pdf(df, filename, title):
    """Exporta un horario a PDF"""
    return create_pdf_download_link(df, filename, title)

def export_teacher_schedule_to_pdf(df, teacher_name):
    """Exporta el horario de un profesor a PDF"""
    title = f"Horario del Profesor: {teacher_name}"
    return export_schedule_to_pdf(df, f"horario_{teacher_name}", title)

def export_classroom_schedule_to_pdf(df, classroom, day):
    """Exporta el horario de un aula a PDF"""
    title = f"Ocupación del Aula {classroom} - {day}"
    return export_schedule_to_pdf(df, f"ocupacion_{classroom}_{day}", title)
