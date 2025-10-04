# app.py — минимальный Flask-сервер для детекции YOLOv8
import os
import time
import sqlite3
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from ultralytics import YOLO

# ── пути
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "history.db"
STATIC_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

MODEL_PATH = os.environ.get("MODEL_PATH", str(MODELS_DIR / "best.pt"))
if not Path(MODEL_PATH).exists():
    raise FileNotFoundError(
        f"Не найден файл модели: {MODEL_PATH}\n"
        f"Положи свой best.pt в {MODELS_DIR} (или укажи переменную окружения MODEL_PATH)"
    )
model = YOLO(MODEL_PATH)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            filename TEXT NOT NULL,
            objects_count INTEGER NOT NULL
        )
        """)
        conn.commit()
init_db()

app = Flask(__name__, static_folder=str(STATIC_DIR))

INDEX_HTML = """
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"/>
<title>Dog Muzzle Detector (YOLOv8)</title>
<style>
 body{font-family:system-ui,Arial,sans-serif;margin:24px}
 .box{max-width:720px;margin:0 auto} .row{margin:12px 0}
 img{max-width:100%;border:1px solid #ddd;border-radius:8px}
 button{padding:8px 12px;cursor:pointer}
 #stats{margin-top:8px;font-weight:600}
 code{background:#f6f8fa;padding:2px 4px;border-radius:4px}
</style></head><body>
<div class="box">
  <h2>Dog Muzzle Detector (YOLOv8)</h2>
  <p>Загрузите изображение — модель отметит намордник/его отсутствие.</p>
  <div class="row">
    <input id="imageInput" type="file" accept="image/*"/>
    <button onclick="processImage()">Запустить обработку</button>
  </div>
  <div class="row">
    <img id="resultImage" src="" alt="Результат появится здесь"/>
    <div id="stats"></div>
  </div>
  <p>Файлы сохраняются в <code>/static</code>.</p>
</div>
<script>
async function processImage(){
  const file=document.getElementById('imageInput').files[0];
  if(!file){alert('Выберите файл');return;}
  const formData=new FormData(); formData.append('image',file);
  const resp=await fetch('/process',{method:'POST',body:formData});
  if(!resp.ok){alert('Ошибка: '+await resp.text());return;}
  const data=await resp.json();
  document.getElementById('stats').innerText='Обнаружено объектов: '+data.count;
  document.getElementById('resultImage').src='/static/'+data.filename+'?'+Date.now();
}
</script></body></html>
"""

@app.get("/")
def index():
    return render_template_string(INDEX_HTML)

@app.post("/process")
def process_image():
    if 'image' not in request.files:
        return "Файл 'image' обязателен", 400
    raw = request.files['image'].read()
    if not raw:
        return "Пустой файл", 400
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return "Не удалось прочитать изображение", 400

    results = model(img)           # инференс
    vis = results[0].plot()        # визуализация боксов (BGR)

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_name = f"result_{ts}.jpg"
    out_path = STATIC_DIR / out_name
    cv2.imwrite(str(out_path), vis)

    count = len(results[0].boxes) if hasattr(results[0], "boxes") else 0
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO requests (ts, filename, objects_count) VALUES (?, ?, ?)",
                  (ts, out_name, int(count)))
        conn.commit()

    return jsonify({"count": int(count), "filename": out_name})

@app.get("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(str(STATIC_DIR), filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
