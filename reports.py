import os, sqlite3
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from openpyxl import Workbook

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "history.db"
STATIC_DIR = BASE_DIR / "static"
OUT_DIR = BASE_DIR / "reports"
OUT_DIR.mkdir(exist_ok=True)

def fetch_last_n(n=20):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, ts, filename, objects_count FROM requests ORDER BY id DESC LIMIT ?", (n,))
        rows = c.fetchall()
    return rows

def pdf_latest():
    rows = fetch_last_n(1)
    if not rows:
        raise SystemExit("Нет записей в БД для PDF.")
    _id, ts, filename, count = rows[0]
    img_path = STATIC_DIR / filename
    out_pdf = OUT_DIR / f"report_{ts}.pdf"

    c = canvas.Canvas(str(out_pdf), pagesize=A4)
    w, h = A4

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, h - 2*cm, "Dog Muzzle Detector — Отчёт (YOLOv8)")

    # Метаданные
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, h - 3.0*cm, f"Дата/время обработки: {ts}")
    c.drawString(2*cm, h - 3.7*cm, f"Имя файла: {filename}")
    c.drawString(2*cm, h - 4.4*cm, f"Обнаружено объектов: {count}")

    # Картинка (если есть)
    y_img = h - 5.0*cm
    if img_path.exists():
        try:
            img = ImageReader(str(img_path))
            # посчитаем размер под ширину страницы с полями
            max_w = w - 4*cm
            iw, ih = img.getSize()
            scale = min(max_w/iw, (y_img - 2*cm)/ih)
            c.drawImage(img, 2*cm, 2*cm, iw*scale, ih*scale, preserveAspectRatio=True, anchor='sw')
        except Exception as e:
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(2*cm, 2*cm, f"[!] Не удалось встроить изображение: {e}")
    else:
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(2*cm, 2*cm, "[!] Изображение не найдено в static/")

    c.showPage()
    c.save()
    return out_pdf

def excel_history():
    rows = fetch_last_n(200)  # выгрузим до 200 последних
    if not rows:
        raise SystemExit("Нет записей в БД для Excel.")
    ts_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_xlsx = OUT_DIR / f"history_{ts_now}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "history"
    ws.append(["id", "timestamp", "filename", "objects_count"])
    for r in rows[::-1]:  # от старых к новым
        ws.append(list(r))
    # немного ширины
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 36
    ws.column_dimensions["D"].width = 16

    wb.save(str(out_xlsx))
    return out_xlsx

if __name__ == "__main__":
    pdf_path = pdf_latest()
    xlsx_path = excel_history()
    print("PDF:", pdf_path)
    print("Excel:", xlsx_path)
