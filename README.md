# AI-анализатор рынка марципана

Кейс: анализ конкурентов **Mzappa**, **Pomatti**, **Rosenau** и **Schaakendorf** на рынке марципановых изделий и сувенирных сладостей. Приложение разбирает тексты, изображения и сайты брендов: визуальный стиль, упаковку, ассортимент, региональную идентичность и пригодность продукции как туристического сувенира.

## Основные функции

- анализ текста конкурента;
- анализ изображений (упаковка, витрина, скриншот сайта);
- Selenium-парсинг сайтов конкурентов;
- оценки `design_score`, `packaging_score`, `souvenir_potential`, `regional_identity_score` (целые числа от 0 до 10);
- описание позиционирования (`market_positioning`) и практические рекомендации;
- история последних запросов;
- Web UI на `http://localhost:8000`;
- desktop-клиент на PyQt6.

## Архитектура

- **FastAPI** — backend и REST API;
- **ProxyAPI** — OpenAI-совместимый доступ к языковой и vision-модели;
- **HTML / CSS / JavaScript** — веб-интерфейс;
- **Selenium** — загрузка страницы, извлечение title/H1/абзаца и скриншот;
- **PyQt6** — desktop-клиент к тому же API;
- **PyInstaller** — сборка `competition_monitor.exe`.

Desktop и exe не содержат backend и не читают `.env` самостоятельно. Они обращаются к уже запущенному серверу на `http://localhost:8000`.

## Структура проекта

```
pem08-master/
├── backend/                 # FastAPI: схемы, сервисы AI, парсер, история
│   ├── main.py              # эндпоинты API
│   ├── config.py            # настройки и список конкурентов
│   ├── models/schemas.py    # Pydantic-модели ответа
│   └── services/            # OpenAI/ProxyAPI, Selenium, история
├── frontend/                # Web UI
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── desktop/                 # PyQt6-клиент и сборка exe
│   ├── main.py
│   ├── api_client.py
│   ├── build.py
│   ├── CompetitorMonitor.spec
│   └── requirements.txt
├── data/                    # материалы по четырём конкурентам (notes.txt, скриншоты)
│   ├── mzappa/
│   ├── pomatti/
│   ├── rosenau/
│   └── schaakendorf/
├── env.example.txt          # шаблон переменных окружения без секрета
├── requirements.txt         # зависимости backend
├── run.py                   # запуск сервера
└── README.md
```

Файл `.env` создаётся локально из шаблона и в репозиторий не входит.

## Установка (Windows)

Из корня проекта:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy env.example.txt .env
```

Откройте `.env` и подставьте свой ключ ProxyAPI вместо заглушки.

Зависимости desktop-клиента:

```powershell
cd desktop
pip install -r requirements.txt
cd ..
```

Корневой `requirements.txt` не включает PyQt6 и PyInstaller. Они ставятся только из `desktop/requirements.txt`.

## Пример `.env`

Используйте только заглушку. Настоящий ключ в репозиторий не кладите.

```env
PROXY_API_KEY=your_proxy_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_VISION_MODEL=gpt-4o-mini
WDM_SSL_VERIFY=0
```

## Запуск

Backend из корня проекта:

```powershell
python run.py
```

Веб-интерфейс: [http://localhost:8000](http://localhost:8000)

Документация API: [http://localhost:8000/docs](http://localhost:8000/docs)

Desktop-клиент (backend уже должен работать):

```powershell
python desktop/main.py
```

## Сборка desktop-приложения

```powershell
cd desktop
python build.py
```

Результат: `desktop/dist/competition_monitor.exe`

Очистка артефактов сборки (spec-файл не удаляется):

```powershell
python build.py clean
```

## Важное ограничение

Desktop-клиент и `competition_monitor.exe` требуют **отдельно запущенный backend** на `http://localhost:8000`.

Файл `.env` хранится только в корне проекта. **`.env` и API-ключ не входят в exe.**

## Тестирование

Перед проверками запустите `python run.py`.

1. **Mzappa** — вкладка «Парсинг сайта», выберите Mzappa (хост `mzappa.ru`) и запустите анализ. Проверьте оценки, позиционирование и рекомендации.
2. **Pomatti** — то же для `pomatti.ru`.
3. **Rosenau** — то же для `rosenau.store`.
4. **Schaakendorf** — то же для `schaaken-dorf.ru` (домен с дефисом).

Дополнительно:

- анализ текста — вставьте описание бренда из `data/<конкурент>/notes.txt`;
- анализ изображения — загрузите скриншот из соответствующей папки в `data/`;
- «Другой сайт» — ручной URL без второго `https://`;
- вкладка «История» — записи всех запросов.

## Безопасность

- `.env` не публикуется: он указан в `.gitignore`.
- `env.example.txt` содержит только шаблон (`your_proxy_api_key_here`), без настоящего ключа.
- Ключ читается backend-ом во время запуска и не должен попадать в README, исходный код или exe.
## Скриншоты работы

### Результат анализа учебного примера

![Результат анализа](<Снимок экрана (2185).png>)

### История запросов

![История запросов](<Снимок экрана (2186).png>)

## Статус и ограничения

Учебный прототип. Проверены локальный запуск, анализ текста и отображение истории запросов.

На скриншоте показан анализ вымышленного бренда «Балтийский миндаль».

Оценки модели являются предварительными и требуют проверки человеком. При тестировании модель выставила оценки дизайну без изображения и сделала неподтверждённый вывод о качестве продукции. Требуется доработка правил оценки при недостатке данных.
