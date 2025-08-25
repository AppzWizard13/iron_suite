import logging
import os
from django.conf import settings
from django.db.models import Max
from reportlab.pdfgen import canvas
from .models import CustomUser
import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

logger = logging.getLogger(__name__)

def generate_username():
    try:
        max_id = CustomUser.objects.aggregate(Max('member_id'))['member_id__max'] or 0
        next_id = max_id + 1
        username_prefix = getattr(settings, 'USERNAME_PREFIX', 'EMP')  # Fallback to 'EMP'
        return f"{username_prefix}{next_id:05d}"  # Format: EMP00001, EMP00002
    except Exception as e:
        logger.exception("Error generating username")
        return "EMP00001"  # Default fallback


def generate_invoice_pdf(order, output_dir='invoices'):
    invoice_number = f"INV-{order.order_number}"

    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.getcwd(), output_dir)
    file_path = os.path.join(output_dir, f"{invoice_number}.pdf")

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        BLUE = colors.HexColor("#1847B0")
        LIGHT_BLUE = colors.HexColor("#F2F6FF")
        BLACK = colors.black
        GREY = colors.HexColor("#ababab")
        PAGE_WIDTH, PAGE_HEIGHT = LETTER

        c = canvas.Canvas(file_path, pagesize=LETTER)

        # --- Header (Blue Block) ---
        c.setFillColor(BLUE)
        c.rect(0, PAGE_HEIGHT - 90, PAGE_WIDTH, 90, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(colors.white)
        c.drawString(42, PAGE_HEIGHT - 65, "INVOICE")

        # --- Gym Details (right-aligned) ---
        gym = order.gym
        c.setFont("Helvetica", 10)
        y_shop = PAGE_HEIGHT - 55
        header_details = [gym.name, gym.location, getattr(gym, 'proprietor_name', '')]
        for detail in header_details:
            c.drawRightString(PAGE_WIDTH - 42, y_shop, detail)
            y_shop -= 13

        # --- Customer Info ---
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 11)
        customer_name = getattr(order.customer, 'get_full_name', lambda: '')()
        c.drawString(42, PAGE_HEIGHT - 120, customer_name)
        c.setFont("Helvetica", 10)
        y_customer = PAGE_HEIGHT - 135
        if hasattr(order.customer, 'address'):
            c.drawString(42, y_customer, order.customer.address)
            y_customer -= 13
        c.drawString(42, y_customer, f"Phone: {getattr(order.customer, 'phone_number', 'N/A')}")

        # --- Invoice Metadata (right-aligned) ---
        info_top = PAGE_HEIGHT - 120
        meta_x = PAGE_WIDTH - 42
        c.setFont("Helvetica", 10)
        c.drawRightString(meta_x, info_top, f"Invoice#: {invoice_number}")
        c.drawRightString(meta_x, info_top - 15, f"Invoice Date: {order.start_date}")
        c.drawRightString(meta_x, info_top - 30, "Terms: Due on Receipt")
        c.drawRightString(meta_x, info_top - 45, f"Due Date: {order.end_date}")

        # --- Table Header ---
        start_y = PAGE_HEIGHT - 180
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(BLACK)
        c.drawString(42, start_y, "#")
        c.drawString(76, start_y, "ITEM & DESCRIPTION")
        c.drawCentredString(390, start_y, "QTY")
        c.drawCentredString(450, start_y, "UNIT")
        c.drawRightString(PAGE_WIDTH - 42, start_y, "AMOUNT")

        # --- Table Content ---
        y = start_y - 20
        package = order.package
        c.setFont("Helvetica", 10)
        c.drawString(42, y, "1")
        c.drawString(76, y, getattr(package, 'name', 'N/A'))
        c.drawCentredString(390, y, "1")
        c.drawCentredString(450, y, "Package")
        c.drawRightString(PAGE_WIDTH - 42, y, f"INR - {order.total:.2f}")

        # Optional: Package Description
        if hasattr(package, 'description') and package.description:
            c.setFillColor(GREY)
            c.setFont("Helvetica", 9)
            y -= 13
            c.drawString(86, y, package.description)
            c.setFillColor(BLACK)
            c.setFont("Helvetica", 10)

        # --- Summary Box ---
        box_top = y - 25
        line_spacing = 15
        box_height = 55
        c.setFillColor(LIGHT_BLUE)
        c.rect(40, box_top - box_height + 10, PAGE_WIDTH - 80, box_height, fill=1, stroke=0)

        # --- Summary Content ---
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 10)
        summary_y = box_top - 13
        c.drawString(52, summary_y, "Thanks for your business.")

        summary_y -= line_spacing
        c.drawRightString(PAGE_WIDTH - 150, summary_y, f"GST ({order.gst_percent:.2f}%)")
        c.drawRightString(PAGE_WIDTH - 42, summary_y, f"INR - {order.gst_amount:.2f}")

        summary_y -= line_spacing
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(PAGE_WIDTH - 150, summary_y, "Total Amount")
        c.drawRightString(PAGE_WIDTH - 42, summary_y, f"INR - {order.total + order.gst_amount:.2f}")

        # --- Terms & Conditions ---
        c.setFont("Helvetica", 9)
        c.setFillColor(GREY)
        c.drawString(42, 70, "Terms & Conditions")
        c.setFillColor(BLACK)
        c.drawString(42, 55, "Full payment is due upon receipt. Late payments may incur additional fees.")

        c.save()
        return invoice_number, file_path

    except Exception as e:
        print(f"Error generating invoice PDF for Order #{order.order_number}: {e}")
        raise