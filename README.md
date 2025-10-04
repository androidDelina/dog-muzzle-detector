# Проект: Dog Muzzle Detector (YOLOv8)

## Кратко

Приложение решает задачу детекции собак с/без намордника с использованием дообученной модели **YOLOv8**.
Состоит из локального веб-приложения на Flask для загрузки изображений и инференса модели, а также утилиты для генерации отчётов (PDF/Excel) и ведения истории запросов в SQLite.

---

## Структура проекта

```plaintext
cv-practice/
├─ app.py                 # Flask-приложение (эндпоинты: / и /process)
├─ reports.py             # генерация PDF/Excel-отчётов
├─ requirements.txt       # зависимости
├─ README.md              # документация (этот файл)
├─ .gitignore
├─ .venv/                 # локальное виртуальное окружение (не хранится в репозитории)
├─ models/
│  └─ best.pt             # обученная модель (не хранится в репозитории)
├─ static/                # результаты инференса (result_*.jpg)
├─ reports/               # сгенерированные отчёты (PDF, XLSX)
└─ history.db             # SQLite-база истории запросов (не хранится в репозитории)
```

⚠️ **Внимание**: файл `models/best.pt` не включён в репозиторий.
Его необходимо скачать и поместить вручную в `models/best.pt` либо указать путь через переменную окружения `MODEL_PATH`.
[Скачать модель](https://drive.google.com/file/d/1aI73TGqNy64kOoblPvUHmo3zwVG29frW/view?usp=sharing).

---

## Установка

1. Клонировать репозиторий и перейти в папку:

   ```bash
   git clone <URL-репозитория>
   cd cv-practice
   ```

2. Создать и активировать виртуальное окружение:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Поместить модель `best.pt` в папку `models/` или указать путь через переменную окружения `MODEL_PATH`.

---

## Запуск приложения

Запустить Flask (пример на порту 8000):

```bash
python -m flask --app app run --host 0.0.0.0 --port 8000 --debug
```

или:

```bash
python app.py
```

После запуска открыть в браузере:

```
http://localhost:8000
```

Загрузите изображение → результат отобразится в браузере и сохранится в `static/result_*.jpg`.
Информация о запросе будет записана в `history.db`.

---

## Генерация отчётов

PDF-отчёт по последнему запросу и Excel-история:

```bash
python reports.py
```

Результаты сохраняются в папке `reports/`:

* `report_YYYYMMDD_HHMMSS.pdf`
* `history_YYYYMMDD_HHMMSS.xlsx`

