# Desktop-приложение: анализ рынка марципана

PyQt6-клиент к backend. Сам по себе exe **не** содержит AI, Selenium и API-ключ: он обращается к серверу на `http://localhost:8000`.

## Что нужно перед запуском

1. Файл `.env` лежит **только в корне проекта**. Он не входит в exe.
2. Backend должен быть запущен из корня:

```bash
python run.py
```

3. Зависимости desktop ставятся отдельно, из папки `desktop`:

```bash
cd desktop
pip install -r requirements.txt
```

Корневой `requirements.txt` для desktop не используется.

## Режим разработки

Терминал 1 — корень проекта:

```bash
python run.py
```

Терминал 2:

```bash
python desktop/main.py
```

Если backend не запущен, приложение покажет сообщение, что `localhost:8000` недоступен.

## Сборка exe

Сборка выполняется **из папки `desktop`**:

```bash
cd desktop
python build.py
```

Итоговый файл:

```
desktop/dist/competition_monitor.exe
```

Сборка использует `CompetitorMonitor.spec` (имя файла историческое). Внутри spec задано имя exe: `competition_monitor`.

В exe **не** попадают: `.env`, `PROXY_API_KEY`, `backend/`, `data/`.

Очистка артефактов сборки (spec не удаляется):

```bash
python build.py clean
```

## Запуск готового exe

1. Из корня: `python run.py` (ключ читается из корневого `.env`).
2. Запустить `desktop/dist/competition_monitor.exe`.

## Функции клиента

- анализ текста конкурента;
- анализ изображений упаковки и сайта;
- парсинг четырёх конкурентов (Mzappa, Pomatti, Rosenau, Schaakendorf) или другого URL;
- оценки рынка марципана и позиционирование;
- история последних запросов.
