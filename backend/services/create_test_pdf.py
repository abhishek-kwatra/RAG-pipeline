from reportlab.pdfgen import canvas
from io import BytesIO

def create_test_pdf(text="This is a test PDF."):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
