from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sessions_data import sessions
import os
import io

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from reportlab.lib.colors import HexColor

# === Реєстрація шрифтів ===
FONT_REGULAR = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
FONT_BOLD = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Bold.ttf")
pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_REGULAR))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", FONT_BOLD))

router = APIRouter()

@router.get("/api/results/{session_id}/pdf")
async def generate_pdf(session_id: str):
    result = sessions.get(session_id, {}).get("result")
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    y = h - 50

    # === Кольоровий заголовок з фоном ===
    c.setFillColor(HexColor("#2B6CB0"))
    c.rect(0, h - 100, w, 100, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("DejaVuSans-Bold", 24)
    title = f"ТИП {result['personality_type']}: {result.get('type_name', '')}"
    c.drawString(50, h - 60, title)
    c.setFont("DejaVuSans", 14)
    c.drawString(50, h - 85, result.get("subtitle", ""))

    # === Розділова лінія ===
    y = h - 120
    c.setStrokeColor(HexColor("#CBD5E0"))
    c.setLineWidth(1)
    c.line(40, y, w - 40, y)
    y -= 30

    # === full_description білим блоком із стилями ===
    full_desc = result.get('full_description', '')

    c.setFillColor(HexColor("#2D3748"))
    c.setFont("DejaVuSans", 12)
    for line in full_desc.split("\n"):
        if y < 50:
            c.showPage()
            y = h - 50
            c.setFont("DejaVuSans", 12)
            c.setFillColor(HexColor("#2D3748"))

        # --- Виділення жирного (заголовки/емодзі) ---
        if line.strip().startswith("🔹") or line.strip().startswith("💪") or line.strip().startswith("🌱") \
           or line.strip().startswith("❤️") or line.strip().startswith("😨") or line.strip().startswith("🎯"):
            c.setFont("DejaVuSans-Bold", 13)
            c.setFillColor(HexColor("#2B6CB0"))
        else:
            c.setFont("DejaVuSans", 12)
            c.setFillColor(HexColor("#2D3748"))

        # --- Колір для елементів списку ---
        if line.strip().startswith("•"):
            c.setFillColor(HexColor("#3182CE"))
            c.setFont("DejaVuSans", 12)

        # Перенос рядка при довжині
        wrapped = simpleSplit(line, c._fontname, c._fontsize, w - 80)
        for wrapped_line in wrapped:
            c.drawString(50, y, wrapped_line)
            y -= 16

        y -= 2  # Міжряддя

    # --- Розділова лінія внизу ---
    c.setStrokeColor(HexColor("#CBD5E0"))
    c.setLineWidth(1)
    if y > 80:
        c.line(40, y, w - 40, y)

    # --- Мінімальний водяний знак/логотип ---
    # c.setFillAlpha(0.15)
    # c.setFont("DejaVuSans-Bold", 60)
    # c.drawString(80, 200, "ENNEAGRAM")

    c.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=Enneagram_Type_{result['personality_type']}.pdf"
    })
