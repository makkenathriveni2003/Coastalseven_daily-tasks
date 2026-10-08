from __future__ import annotations
import csv
import io
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from celery_app import celery_app
from database import database_connection

logger = logging.getLogger("shopzone_tasks")

INVOICE_DIR = Path(__file__).resolve().parent / "generated_invoices"
INVOICE_DIR.mkdir(parents=True, exist_ok=True)


def _safe_update_state(task_self: Any, state: str = "PROGRESS", meta: dict[str, Any] | None = None) -> None:
    req = getattr(task_self, "request", None)
    if req and getattr(req, "id", None):
        try:
            task_self.update_state(state=state, meta=meta)
        except Exception as err:
            logger.debug("Failed updating task state: %s", err)


@celery_app.task(bind=True)
def sample_background_job_task(self, total_steps: int = 10, step_delay: float = 0.5) -> dict[str, Any]:
    """Sample Celery background task for testing task lifecycle."""
    logger.info("Starting sample background job: %s steps", total_steps)
    for i in range(1, total_steps + 1):
        time.sleep(step_delay)
        percent = int((i / total_steps) * 100)
        _safe_update_state(
            self,
            state="PROGRESS",
            meta={
                "current": i,
                "total": total_steps,
                "percent": percent,
                "message": f"Processing step {i} of {total_steps}...",
                "status": "PROGRESS",
            },
        )
    return {
        "status": "SUCCESS",
        "percent": 100,
        "message": "Sample background task completed successfully!",
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


@celery_app.task(bind=True)
def generate_invoice_pdf_task(self, order_id: int, user_email: str | None = None) -> dict[str, Any]:
    """Asynchronously generates a PDF invoice for a given order using ReportLab."""
    logger.info("Generating invoice for order_id=%s", order_id)
    _safe_update_state(
        self,
        state="PROGRESS",
        meta={
            "current": 10,
            "total": 100,
            "percent": 10,
            "message": "Querying order and customer details from database...",
            "status": "PROGRESS",
        },
    )

    # 1. Fetch order details from PostgreSQL
    with database_connection() as conn:
        order_row = conn.execute(
            """
            SELECT id, user_id, email, total, status, full_name, phone,
                   address, city, state, pincode, payment_method, created_at
            FROM orders
            WHERE id = %s
            """,
            (order_id,),
        ).fetchone()

        if not order_row:
            raise ValueError(f"Order #{order_id} not found")

        order = dict(order_row)

        _safe_update_state(
            self,
            state="PROGRESS",
            meta={
                "current": 35,
                "total": 100,
                "percent": 35,
                "message": "Fetching purchased items and pricing...",
                "status": "PROGRESS",
            },
        )

        items_rows = conn.execute(
            """
            SELECT item.id, item.product_id,
                   COALESCE(item.product_name, product.name, 'Product #' || item.product_id) AS product_name,
                   item.quantity, item.unit_price
            FROM order_items AS item
            LEFT JOIN products AS product ON product.id = item.product_id
            WHERE item.order_id = %s
            ORDER BY item.id ASC
            """,
            (order_id,),
        ).fetchall()

        items = [dict(r) for r in items_rows]

    _safe_update_state(
        self,
        state="PROGRESS",
        meta={
            "current": 60,
            "total": 100,
            "percent": 60,
            "message": "Rendering PDF layout and styling...",
            "status": "PROGRESS",
        },
    )

    # 2. Build PDF Document
    filename = f"ShopZone_Invoice_{order_id}.pdf"
    file_path = INVOICE_DIR / filename

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
    )
    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#334155"),
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
    )
    body_muted = ParagraphStyle(
        "BodyMuted",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748b"),
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.white,
        fontName="Helvetica-Bold",
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
    )
    table_cell_right = ParagraphStyle(
        "TableCellRight",
        parent=table_cell_style,
        alignment=2,  # Align right
    )

    story = []

    # Header section
    header_data = [
        [
            Paragraph("<b>SHOPZONE</b><br/><font size=8 color='#64748b'>E-Commerce Platform</font>", title_style),
            Paragraph(
                f"<b>TAX INVOICE</b><br/>"
                f"Invoice No: <b>INV-{order_id:06d}</b><br/>"
                f"Date: {str(order.get('created_at', ''))[:19]}<br/>"
                f"Status: <font color='{'#16a34a' if order.get('status') == 'delivered' else '#2563eb'}'><b>{str(order.get('status', 'PENDING')).upper()}</b></font>",
                ParagraphStyle("HeaderRight", parent=styles["Normal"], fontSize=9, leading=14, alignment=2),
            ),
        ]
    ]
    header_table = Table(header_data, colWidths=[280, 250])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=15))

    # Customer and Order Details
    cust_name = order.get("full_name") or "Valued Customer"
    cust_email = order.get("email") or "N/A"
    cust_phone = order.get("phone") or "N/A"
    address_str = f"{order.get('address') or ''}, {order.get('city') or ''}, {order.get('state') or ''} - {order.get('pincode') or ''}"
    payment_method = (order.get("payment_method") or "Credit Card").upper()

    details_data = [
        [
            Paragraph("<b>BILLED TO:</b>", section_title_style),
            Paragraph("<b>ORDER INFORMATION:</b>", section_title_style),
        ],
        [
            Paragraph(
                f"<b>{cust_name}</b><br/>"
                f"Email: {cust_email}<br/>"
                f"Phone: {cust_phone}<br/>"
                f"Address: {address_str}",
                body_style,
            ),
            Paragraph(
                f"Order ID: <b>#{order_id}</b><br/>"
                f"Payment Method: <b>{payment_method}</b><br/>"
                f"Payment Status: <b>{'PAID' if order.get('status') != 'cancelled' else 'REFUNDED'}</b><br/>"
                f"Currency: <b>INR (₹)</b>",
                body_style,
            ),
        ],
    ]
    details_table = Table(details_data, colWidths=[280, 250])
    details_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))

    # Items Table
    table_content = [
        [
            Paragraph("Item & Description", table_header_style),
            Paragraph("Unit Price (₹)", table_header_style),
            Paragraph("Qty", table_header_style),
            Paragraph("Total (₹)", table_header_style),
        ]
    ]

    subtotal = 0.0
    for it in items:
        qty = it.get("quantity", 1)
        price = it.get("unit_price", 0.0)
        line_total = qty * price
        subtotal += line_total
        p_name = it.get("product_name") or f"Item #{it.get('product_id')}"
        table_content.append([
            Paragraph(f"<b>{p_name}</b>", table_cell_style),
            Paragraph(f"₹{price:,.2f}", table_cell_right),
            Paragraph(str(qty), table_cell_right),
            Paragraph(f"₹{line_total:,.2f}", table_cell_right),
        ])

    grand_total = float(order.get("total") or subtotal)
    table_content.append([
        Paragraph("<b>Grand Total</b>", table_cell_style),
        "",
        "",
        Paragraph(f"<b>₹{grand_total:,.2f}</b>", table_cell_right),
    ])

    items_table = Table(table_content, colWidths=[260, 90, 60, 120])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#1e293b")),
        ("TOPPADDING", (0, -1), (-1, -1), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("SPAN", (0, -1), (2, -1)),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 30))

    # Footer note
    footer_text = (
        "Thank you for shopping with ShopZone! This is a system-generated electronic invoice "
        "and does not require a physical signature. For any support inquiries, contact support@shopzone.com."
    )
    story.append(Paragraph(footer_text, subtitle_style))

    _safe_update_state(
        self,
        state="PROGRESS",
        meta={
            "current": 85,
            "total": 100,
            "percent": 85,
            "message": "Writing invoice file to safe storage...",
            "status": "PROGRESS",
        },
    )

    doc.build(story)

    logger.info("Invoice generated successfully at: %s", file_path)

    return {
        "status": "SUCCESS",
        "percent": 100,
        "order_id": order_id,
        "filename": filename,
        "file_size": os.path.getsize(file_path),
        "download_url": f"/orders/{order_id}/invoice/download",
        "message": f"Invoice for order #{order_id} generated successfully.",
    }


@celery_app.task(bind=True)
def bulk_import_products_csv_task(self, file_path: str, user_email: str) -> dict[str, Any]:
    """Bulk import products from CSV into PostgreSQL database."""
    logger.info("Starting CSV product import from: %s", file_path)
    csv_path = Path(file_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Uploaded CSV file not found: {file_path}")

    _safe_update_state(
        self,
        state="PROGRESS",
        meta={
            "current": 0,
            "total": 100,
            "percent": 5,
            "message": "Reading CSV file structure...",
            "imported": 0,
            "failed": 0,
            "errors": [],
            "status": "PROGRESS",
        },
    )

    rows: List[Dict[str, str]] = []
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or missing header row")
        
        # Check required columns (case insensitive)
        normalized_headers = {h.strip().lower(): h for h in reader.fieldnames if h}
        if "name" not in normalized_headers or "price" not in normalized_headers:
            raise ValueError("CSV must contain at least 'name' and 'price' columns")

        for row in reader:
            rows.append(row)

    total_rows = len(rows)
    if total_rows == 0:
        return {
            "status": "SUCCESS",
            "percent": 100,
            "imported_count": 0,
            "failed_count": 0,
            "total_rows": 0,
            "errors": [],
            "message": "CSV file contained 0 data rows.",
        }

    imported_count = 0
    failed_count = 0
    errors: List[Dict[str, Any]] = []
    valid_products: List[Dict[str, Any]] = []

    for idx, row in enumerate(rows, start=2):  # Row 2 is first data row
        # Normalize fields
        row_clean = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
        name = row_clean.get("name", "")
        price_str = row_clean.get("price", "")
        category = row_clean.get("category", "") or "General"
        image = row_clean.get("image", "") or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
        description = row_clean.get("description", "") or f"High quality {category}: {name}"
        stock_str = row_clean.get("stock", "50")

        # Validation
        if not name:
            failed_count += 1
            errors.append({"row": idx, "reason": "Missing product name"})
            continue

        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("Price must be greater than 0")
        except Exception:
            failed_count += 1
            errors.append({"row": idx, "name": name, "reason": f"Invalid price '{price_str}' (must be positive number)"})
            continue

        try:
            stock = int(stock_str) if stock_str else 50
            if stock < 0:
                raise ValueError("Stock cannot be negative")
        except Exception:
            failed_count += 1
            errors.append({"row": idx, "name": name, "reason": f"Invalid stock '{stock_str}' (must be non-negative integer)"})
            continue

        valid_products.append({
            "name": name,
            "price": price,
            "category": category,
            "image": image,
            "description": description,
            "stock": stock,
        })

        if idx % 10 == 0 or idx == total_rows + 1:
            progress_pct = int(((idx - 1) / total_rows) * 60) + 10
            _safe_update_state(
                self,
                state="PROGRESS",
                meta={
                    "current": idx - 1,
                    "total": total_rows,
                    "percent": min(progress_pct, 70),
                    "message": f"Validating row {idx - 1} of {total_rows}...",
                    "imported": len(valid_products),
                    "failed": failed_count,
                    "errors": errors[:10],
                    "status": "PROGRESS",
                },
            )

    # Database insertion / upsert
    _safe_update_state(
        self,
        state="PROGRESS",
        meta={
            "current": total_rows,
            "total": total_rows,
            "percent": 80,
            "message": f"Inserting {len(valid_products)} valid products into PostgreSQL database...",
            "imported": len(valid_products),
            "failed": failed_count,
            "errors": errors[:10],
            "status": "PROGRESS",
        },
    )

    with database_connection() as conn:
        for p in valid_products:
            # Check if product exists by name (case-insensitive) to update or insert
            existing = conn.execute(
                "SELECT id FROM products WHERE LOWER(name) = LOWER(%s)",
                (p["name"],),
            ).fetchone()

            if existing:
                conn.execute(
                    """
                    UPDATE products
                    SET price = %s, category = %s, image = %s, description = %s, stock = %s
                    WHERE id = %s
                    """,
                    (p["price"], p["category"], p["image"], p["description"], p["stock"], existing["id"]),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO products (name, price, category, image, description, stock)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (p["name"], p["price"], p["category"], p["image"], p["description"], p["stock"]),
                )
            imported_count += 1

    # Cleanup temporary CSV file
    try:
        if csv_path.exists():
            csv_path.unlink()
    except Exception as cleanup_err:
        logger.warning("Could not delete temporary import file %s: %s", csv_path, cleanup_err)

    return {
        "status": "SUCCESS",
        "percent": 100,
        "imported_count": imported_count,
        "failed_count": failed_count,
        "total_rows": total_rows,
        "errors": errors,
        "message": f"CSV import completed: {imported_count} imported/updated, {failed_count} failed.",
    }
