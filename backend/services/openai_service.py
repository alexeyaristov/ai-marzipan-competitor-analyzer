"""
Сервис для работы с ProxyAPI (OpenAI-совместимый API)
https://proxyapi.ru/docs/openai-text-generation
"""
import base64
import json
import re
import time
import logging
from typing import Optional

from openai import OpenAI

from backend.config import settings
from backend.models.schemas import CompetitorAnalysis, ImageAnalysis

# Логгер для сервиса
logger = logging.getLogger("competitor_monitor.openai")


class OpenAIService:
    """Сервис для анализа через ProxyAPI"""
    
    def __init__(self):
        logger.info("=" * 50)
        logger.info("Инициализация OpenAI сервиса")
        logger.info(f"  Base URL: {settings.proxy_api_base_url}")
        logger.info(f"  Модель текста: {settings.openai_model}")
        logger.info(f"  Модель vision: {settings.openai_vision_model}")
        logger.info(f"  API ключ: {'*' * 10}...{settings.proxy_api_key[-4:] if settings.proxy_api_key else 'НЕ ЗАДАН'}")
        
        # ProxyAPI - OpenAI-совместимый API для России
        self.client = OpenAI(
            api_key=settings.proxy_api_key,
            base_url=settings.proxy_api_base_url
        )
        self.model = settings.openai_model
        self.vision_model = settings.openai_vision_model
        
        logger.info("OpenAI сервис инициализирован успешно ✓")
        logger.info("=" * 50)
    
    def _parse_json_response(self, content: str) -> dict:
        """Извлечь JSON из ответа модели"""
        logger.debug(f"Парсинг JSON ответа, длина: {len(content)} символов")
        
        # Пробуем найти JSON в markdown блоке
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
            logger.debug("JSON найден в markdown блоке")
        
        # Пробуем найти JSON объект
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)
            logger.debug("JSON объект извлечён")
        
        try:
            result = json.loads(content)
            logger.debug(f"JSON успешно распарсен, ключей: {len(result)}")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Ошибка парсинга JSON: {e}")
            logger.debug(f"Проблемный контент: {content[:200]}...")
            return {}

    def _clamp_score(self, value, default: int = 0) -> int:
        """Безопасно привести оценку к целому числу 0-10"""
        try:
            score = int(value)
        except (TypeError, ValueError):
            return default
        return max(0, min(10, score))

    def _get_recommendations(self, data: dict) -> list:
        """Извлечь 3-5 рекомендаций, отбросив пустые значения"""
        recs = data.get("recommendations") or []
        if not isinstance(recs, list):
            recs = []
        recs = [str(item).strip() for item in recs if str(item).strip()]
        return recs[:5]

    def _get_string_list(self, data: dict, key: str) -> list:
        """Безопасно извлечь список строк"""
        items = data.get(key) or []
        if not isinstance(items, list):
            return []
        return [str(item).strip() for item in items if str(item).strip()]

    def _build_competitor_analysis(self, data: dict) -> CompetitorAnalysis:
        """Собрать CompetitorAnalysis из JSON модели"""
        return CompetitorAnalysis(
            strengths=self._get_string_list(data, "strengths"),
            weaknesses=self._get_string_list(data, "weaknesses"),
            unique_offers=self._get_string_list(data, "unique_offers"),
            recommendations=self._get_recommendations(data),
            summary=str(data.get("summary") or ""),
            design_score=self._clamp_score(data.get("design_score")),
            packaging_score=self._clamp_score(data.get("packaging_score")),
            souvenir_potential=self._clamp_score(data.get("souvenir_potential")),
            regional_identity_score=self._clamp_score(data.get("regional_identity_score")),
            market_positioning=str(data.get("market_positioning") or ""),
        )
    
    async def analyze_text(self, text: str) -> CompetitorAnalysis:
        """Анализ текста конкурента"""
        logger.info("=" * 50)
        logger.info("📝 АНАЛИЗ ТЕКСТА КОНКУРЕНТА")
        logger.info(f"  Длина текста: {len(text)} символов")
        logger.info(f"  Превью: {text[:100]}...")
        logger.info(f"  Модель: {self.model}")
        
        system_prompt = """Ты — эксперт по конкурентному анализу рынка марципановых изделий и сувенирных сладостей (туристические подарки, региональные десерты, подарочные наборы).

Проанализируй текст конкурента и верни ТОЛЬКО валидный JSON без markdown-обёртки и без комментариев. Все текстовые значения — на русском языке.

Формат ответа (строго JSON):
{
    "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2", "слабая сторона 3"],
    "unique_offers": ["уникальное предложение 1", "уникальное предложение 2", "уникальное предложение 3"],
    "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"],
    "summary": "Краткое резюме анализа конкурента",
    "design_score": 7,
    "packaging_score": 6,
    "souvenir_potential": 8,
    "regional_identity_score": 5,
    "market_positioning": "Краткое описание позиционирования бренда на рынке марципана и сувенирных сладостей"
}

Оценивай конкурента по критериям:
- визуальный стиль бренда (цвета, типографика, характер коммуникации);
- дизайн упаковки (подарочность, читаемость, премиальность);
- ассортимент (марципан, фигурки, наборы, сезонные и туристические позиции);
- использование истории бренда и региональной тематики;
- пригодность продукции как туристического сувенира;
- сильные и слабые стороны относительно рынка сувенирных сладостей.

Важно:
- strengths, weaknesses, unique_offers — по 3-5 конкретных пунктов;
- recommendations — ровно 3-5 практических рекомендаций для собственного проекта;
- все оценки — целые числа от 0 до 10;
- если данных мало, ставь осторожную оценку и явно отрази это в тексте;
- не добавляй поля вне схемы, не пиши текст вне JSON."""

        start_time = time.time()
        logger.info("  Отправка запроса к API...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Проанализируй текст конкурента на рынке марципановых изделий и сувенирных сладостей:\n\n{text}"}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            elapsed = time.time() - start_time
            logger.info(f"  ✓ Ответ получен за {elapsed:.2f} сек")
            
            content = response.choices[0].message.content
            logger.info(f"  Длина ответа: {len(content)} символов")
            logger.debug(f"  Использовано токенов: {response.usage.total_tokens if response.usage else 'N/A'}")
            
            data = self._parse_json_response(content)
            result = self._build_competitor_analysis(data)
            
            logger.info(f"  Результат: {len(result.strengths)} сильных, {len(result.weaknesses)} слабых сторон")
            logger.info(f"  Оценки: дизайн {result.design_score}, упаковка {result.packaging_score}, сувенир {result.souvenir_potential}, регион {result.regional_identity_score}")
            logger.info("=" * 50)
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"  ✗ Ошибка API за {elapsed:.2f} сек: {e}")
            logger.error("=" * 50)
            raise
    
    async def analyze_image(self, image_base64: str, mime_type: str = "image/jpeg") -> ImageAnalysis:
        """Анализ изображения (баннер, сайт, упаковка)"""
        logger.info("=" * 50)
        logger.info("🖼️ АНАЛИЗ ИЗОБРАЖЕНИЯ")
        logger.info(f"  Размер base64: {len(image_base64)} символов")
        logger.info(f"  MIME тип: {mime_type}")
        logger.info(f"  Модель: {self.vision_model}")
        
        system_prompt = """Ты — эксперт по визуальному маркетингу марципановых изделий и сувенирных сладостей. Проанализируй изображение конкурента (сайт, баннер, витрина, упаковка, продукт) и верни ТОЛЬКО валидный JSON без markdown-обёртки. Все текстовые значения — на русском языке.

Формат ответа (строго JSON):
{
    "description": "Детальное описание того, что изображено",
    "marketing_insights": ["инсайт 1", "инсайт 2", "инсайт 3"],
    "visual_style_score": 7,
    "visual_style_analysis": "Анализ визуального стиля конкурента",
    "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"],
    "design_score": 7,
    "packaging_score": 6,
    "souvenir_potential": 8,
    "regional_identity_score": 5,
    "market_positioning": "Краткое описание позиционирования бренда, которое считывается с изображения"
}

Оценивай:
- визуальный стиль бренда (цвета, композиция, характер, премиальность);
- дизайн упаковки (если упаковка не видна — оцени по подарочности и оформлению продукта);
- ассортимент и подачу сладостей;
- историю бренда и региональную тематику (гербы, архитектура, локальные сюжеты, традиции);
- пригодность как туристического сувенира;
- сильные и слабые стороны визуальной коммуникации.

Важно:
- все оценки — целые числа от 0 до 10;
- marketing_insights — 3-5 пунктов;
- recommendations — ровно 3-5 практических рекомендаций;
- visual_style_score сохраняй как общую оценку визуала, design_score — стиль бренда, packaging_score — упаковку;
- не добавляй поля вне схемы, не пиши текст вне JSON."""

        start_time = time.time()
        logger.info("  Отправка запроса к Vision API...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Проанализируй это изображение конкурента на рынке марципана и сувенирных сладостей:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            elapsed = time.time() - start_time
            logger.info(f"  ✓ Ответ получен за {elapsed:.2f} сек")
            
            content = response.choices[0].message.content
            logger.info(f"  Длина ответа: {len(content)} символов")
            
            data = self._parse_json_response(content)
            
            result = ImageAnalysis(
                description=str(data.get("description") or ""),
                marketing_insights=self._get_string_list(data, "marketing_insights"),
                visual_style_score=self._clamp_score(data.get("visual_style_score")),
                visual_style_analysis=str(data.get("visual_style_analysis") or ""),
                recommendations=self._get_recommendations(data),
                design_score=self._clamp_score(data.get("design_score")),
                packaging_score=self._clamp_score(data.get("packaging_score")),
                souvenir_potential=self._clamp_score(data.get("souvenir_potential")),
                regional_identity_score=self._clamp_score(data.get("regional_identity_score")),
                market_positioning=str(data.get("market_positioning") or ""),
            )
            
            logger.info(f"  Результат: оценка стиля {result.visual_style_score}/10")
            logger.info(f"  Оценки: дизайн {result.design_score}, упаковка {result.packaging_score}, сувенир {result.souvenir_potential}, регион {result.regional_identity_score}")
            logger.info(f"  Инсайтов: {len(result.marketing_insights)}, рекомендаций: {len(result.recommendations)}")
            logger.info("=" * 50)
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"  ✗ Ошибка Vision API за {elapsed:.2f} сек: {e}")
            logger.error("=" * 50)
            raise
    
    async def analyze_parsed_content(
        self, 
        title: Optional[str], 
        h1: Optional[str], 
        paragraph: Optional[str]
    ) -> CompetitorAnalysis:
        """Анализ распарсенного контента сайта"""
        logger.info("📄 Анализ распарсенного контента")
        logger.info(f"  Title: {title[:50] if title else 'N/A'}...")
        logger.info(f"  H1: {h1[:50] if h1 else 'N/A'}...")
        logger.info(f"  Абзац: {paragraph[:50] if paragraph else 'N/A'}...")
        
        content_parts = []
        if title:
            content_parts.append(f"Заголовок страницы (title): {title}")
        if h1:
            content_parts.append(f"Главный заголовок (H1): {h1}")
        if paragraph:
            content_parts.append(f"Первый абзац: {paragraph}")
        
        combined_text = "\n\n".join(content_parts)
        
        if not combined_text.strip():
            logger.warning("  ⚠ Контент пустой, возвращаем пустой анализ")
            return CompetitorAnalysis(
                summary="Не удалось извлечь контент для анализа"
            )
        
        return await self.analyze_text(combined_text)
    
    async def analyze_website_screenshot(
        self,
        screenshot_base64: str,
        url: str,
        title: Optional[str] = None,
        h1: Optional[str] = None,
        first_paragraph: Optional[str] = None
    ) -> CompetitorAnalysis:
        """Комплексный анализ сайта конкурента по скриншоту"""
        logger.info("=" * 50)
        logger.info("🌐 КОМПЛЕКСНЫЙ АНАЛИЗ САЙТА")
        logger.info(f"  URL: {url}")
        logger.info(f"  Title: {title[:50] if title else 'N/A'}...")
        logger.info(f"  H1: {h1[:50] if h1 else 'N/A'}...")
        logger.info(f"  Размер скриншота: {len(screenshot_base64)} символов base64")
        logger.info(f"  Модель: {self.vision_model}")
        
        # Формируем контекст из извлечённых данных
        context_parts = [f"URL сайта: {url}"]
        if title:
            context_parts.append(f"Title страницы: {title}")
        if h1:
            context_parts.append(f"Главный заголовок (H1): {h1}")
        if first_paragraph:
            context_parts.append(f"Текст на странице: {first_paragraph[:300]}")
        
        context = "\n".join(context_parts)
        logger.debug(f"  Контекст:\n{context}")
        
        system_prompt = """Ты — эксперт по конкурентному анализу рынка марципановых изделий и сувенирных сладостей, а также по UX/UI сайтов брендов сладостей.

Проанализируй скриншот сайта конкурента и верни ТОЛЬКО валидный JSON без markdown-обёртки. Все текстовые значения — на русском языке.

Формат ответа (строго JSON):
{
    "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2", "слабая сторона 3"],
    "unique_offers": ["уникальное предложение 1", "уникальное предложение 2", "уникальное предложение 3"],
    "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"],
    "summary": "Комплексное резюме анализа сайта конкурента",
    "design_score": 7,
    "packaging_score": 6,
    "souvenir_potential": 8,
    "regional_identity_score": 5,
    "market_positioning": "Краткое описание позиционирования бренда на рынке марципана и сувенирных сладостей"
}

При анализе обращай внимание на:
- визуальный стиль бренда (цвета, шрифты, композиция, характер сайта);
- дизайн упаковки и подачу продуктов на сайте;
- ассортимент: марципан, фигурки, наборы, сезонные и туристические позиции;
- историю бренда и региональную тематику;
- пригодность продукции как туристического сувенира;
- сильные и слабые стороны конкурента;
- UX/UI: навигация, CTA, доверие, удобство покупки подарка.

Важно:
- strengths, weaknesses, unique_offers — по 3-5 конкретных пунктов;
- recommendations — ровно 3-5 практических рекомендаций;
- все оценки — целые числа от 0 до 10;
- если упаковка или регион слабо видны, ставь осторожную оценку и объясни это в текстах;
- не добавляй поля вне схемы, не пиши текст вне JSON."""

        start_time = time.time()
        logger.info("  Отправка скриншота в Vision API...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Проведи конкурентный анализ этого сайта бренда марципана и сувенирных сладостей:\n\n{context}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{screenshot_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            elapsed = time.time() - start_time
            logger.info(f"  ✓ Ответ получен за {elapsed:.2f} сек")
            
            content = response.choices[0].message.content
            logger.info(f"  Длина ответа: {len(content)} символов")
            
            data = self._parse_json_response(content)
            result = self._build_competitor_analysis(data)
            
            logger.info(f"  Результат:")
            logger.info(f"    - Сильных сторон: {len(result.strengths)}")
            logger.info(f"    - Слабых сторон: {len(result.weaknesses)}")
            logger.info(f"    - УТП: {len(result.unique_offers)}")
            logger.info(f"    - Рекомендаций: {len(result.recommendations)}")
            logger.info(f"    - Оценки: дизайн {result.design_score}, упаковка {result.packaging_score}, сувенир {result.souvenir_potential}, регион {result.regional_identity_score}")
            logger.info(f"  Резюме: {result.summary[:100]}...")
            logger.info("=" * 50)
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"  ✗ Ошибка Vision API за {elapsed:.2f} сек: {e}")
            logger.error("=" * 50)
            raise


# Глобальный экземпляр
logger.info("Создание глобального экземпляра OpenAI сервиса...")
openai_service = OpenAIService()
