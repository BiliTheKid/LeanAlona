from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import qrcode
from io import BytesIO

def generate_qr_code(data):
    # Generate a QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert the image to a format ReportLab can use (ImageReader)
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return ImageReader(img_byte_arr)

def create_pdf(file_name, fields, qr_code_data):
    # Create a canvas for the PDF
    pdf = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter

    # Set the title of the PDF
    pdf.setTitle("Dynamic PDF with QR Code")

    # Add dynamic fields
    y_position = height - 100  # Start position for the fields
    for field_name, field_value in fields.items():
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, y_position, f"{field_name}: {field_value}")
        y_position -= 20  # Adjust position for next field

    # Generate QR code
    qr_code_img = generate_qr_code(qr_code_data)

    # Draw the QR code on the PDF
    pdf.drawImage(qr_code_img, 100, y_position - 150, width=1.5*inch, height=1.5*inch)

    # Save the PDF
    pdf.showPage()
    pdf.save()

if __name__ == "__main__":
    # Define dynamic fields
    dynamic_fields = {
        "Name": "John Doe",
        "Email": "john.doe@example.com",
        "Phone": "123-456-7890",
        "Address": "1234 Main St, City, State"
    }

    # Define QR code data
    qr_code_data = "https://www.example.com"

    # Generate the PDF
    create_pdf("output.pdf", dynamic_fields, qr_code_data)
