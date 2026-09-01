"""
Pydantic схемы для API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# === Запросы ===

class TextAnalysisRequest(BaseModel):
    """Запрос на анализ текста"""
    text: str = Field(..., min_length=10, description="Текст для анализа")


class ParseDemoRequest(BaseModel):
    """Запрос на парсинг URL"""
    url: str = Field(..., description="URL для парсинга")


class CompetitorItem(BaseModel):
    """Конкурент из списка для парсинга"""
    id: str
    name: str
    host: str = Field(..., description="Хост без протокола, например mzappa.ru")


class CompetitorsResponse(BaseModel):
    """Список конкурентов"""
    items: List[CompetitorItem]


# === Ответы ===

class CompetitorAnalysis(BaseModel):
    """Структурированный анализ конкурента"""
    strengths: List[str] = Field(default_factory=list, description="Сильные стороны")
    weaknesses: List[str] = Field(default_factory=list, description="Слабые стороны")
    unique_offers: List[str] = Field(default_factory=list, description="Уникальные предложения")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации (3-5 пунктов)")
    summary: str = Field("", description="Общее резюме")
    design_score: int = Field(0, ge=0, le=10, description="Оценка визуального стиля бренда (0-10)")
    packaging_score: int = Field(0, ge=0, le=10, description="Оценка дизайна упаковки (0-10)")
    souvenir_potential: int = Field(0, ge=0, le=10, description="Пригодность как туристический сувенир (0-10)")
    regional_identity_score: int = Field(0, ge=0, le=10, description="Использование истории и региональной тематики (0-10)")
    market_positioning: str = Field("", description="Описание рыночного позиционирования")


class ImageAnalysis(BaseModel):
    """Анализ изображения"""
    description: str = Field("", description="Описание изображения")
    marketing_insights: List[str] = Field(default_factory=list, description="Маркетинговые инсайты")
    visual_style_score: int = Field(0, ge=0, le=10, description="Оценка визуального стиля (0-10)")
    visual_style_analysis: str = Field("", description="Анализ визуального стиля")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации (3-5 пунктов)")
    design_score: int = Field(0, ge=0, le=10, description="Оценка визуального стиля бренда (0-10)")
    packaging_score: int = Field(0, ge=0, le=10, description="Оценка дизайна упаковки (0-10)")
    souvenir_potential: int = Field(0, ge=0, le=10, description="Пригодность как туристический сувенир (0-10)")
    regional_identity_score: int = Field(0, ge=0, le=10, description="Использование истории и региональной тематики (0-10)")
    market_positioning: str = Field("", description="Описание рыночного позиционирования")


class ParsedContent(BaseModel):
    """Результат парсинга страницы"""
    url: str
    title: Optional[str] = None
    h1: Optional[str] = None
    first_paragraph: Optional[str] = None
    analysis: Optional[CompetitorAnalysis] = None
    error: Optional[str] = None


class TextAnalysisResponse(BaseModel):
    """Ответ на анализ текста"""
    success: bool
    analysis: Optional[CompetitorAnalysis] = None
    error: Optional[str] = None


class ImageAnalysisResponse(BaseModel):
    """Ответ на анализ изображения"""
    success: bool
    analysis: Optional[ImageAnalysis] = None
    error: Optional[str] = None


class ParseDemoResponse(BaseModel):
    """Ответ на парсинг"""
    success: bool
    data: Optional[ParsedContent] = None
    error: Optional[str] = None


# === История ===

class HistoryItem(BaseModel):
    """Элемент истории"""
    id: str
    timestamp: datetime
    request_type: str  # "text", "image", "parse"
    request_summary: str
    response_summary: str


class HistoryResponse(BaseModel):
    """Ответ со списком истории"""
    items: List[HistoryItem]
    total: int

