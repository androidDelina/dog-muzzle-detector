# Проект: Dog Muzzle Detector (YOLOv8)
## Коротко
Проект реализует задачу детекции собак с/без намордника с использованием дообученной модели YOLOv8. Включает: локальное веб-приложение на Flask для приёма изображений, инференса модели и сохранения результатов; утилиту генерации отчётов (PDF/Excel); SQLite-базу истории запросов.

## Структура проекта
cv-practice/
├─ app.py                 # Flask-приложение (эндпоинты: / и /process)
├─ reports.py             # формирование PDF/Excel-отчётов
├─ requirements.txt       # зависимости
├─ README.md              # этот файл
├─ .gitignore
├─ .venv/                 # (локально) виртуальное окружение — не в репо
├─ models/
│  └─ best.pt             # обученная модель (НЕ хранится в репозитории)
├─ static/                # результаты инференса (result_*.jpg)
├─ reports/               # сгенерированные отчёты (PDF, XLSX)
└─ history.db             # SQLite с историей запросов (не в репо)


ВАЖНО: файл models/best.pt не включён в репозиторий (обычно слишком большой). Пожалуйста, скачайте файл с Google Drive (папка dog-muzzle-project/runs/.../best.pt) и поместите вручную в models/best.pt, либо укажите путь через переменную окружения MODEL_PATH.

## Установка (локально)

Клонировать репозиторий и перейти в папку:

git clone <URL-репозитория>
cd cv-practice


Создать и активировать виртуальное окружение:

python3 -m venv .venv
source .venv/bin/activate


Установить зависимости:

pip install -r requirements.txt


Положить модель best.pt в папку models/ (или экспортировать путь через MODEL_PATH).

## Запуск приложения (локально)

Запустить Flask (пример на порту 8000, если 5000 занят):

python -m flask --app app run --host 0.0.0.0 --port 8000 --debug


или

python app.py


Открыть браузер:

http://localhost:8000


Загрузить изображение — результат отобразится в браузере и сохранится в static/result_*.jpg. Запись о запросе добавится в history.db.

## Генерация отчётов
PDF-отчёт по последнему запросу и Excel-история:
python reports.py

Результаты сохраняются в папке reports/ (файлы: report_YYYYMMDD_HHMMSS.pdf и history_YYYYMMDD_HHMMSS.xlsx).
