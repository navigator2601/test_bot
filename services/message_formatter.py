# відносний шлях до файлу: services/message_formatter.py
# Призначення та функціонал файлу: Функції для форматування повідомлень.

from typing import Dict, Any

def format_model_details_message(model_details: Dict[str, Any]) -> str:
    """
    Тимчасова функція для форматування. Виводить лише бренд та модель для перевірки.
    """
    if not model_details:
        return "❌ Деталі моделі не знайдено."
        
    model_name = model_details.get("Model", "N/A")
    brand_name = model_details.get("Brand", "N/A")
    
    return f"ℹ️ Деталі моделі:\nБренд: {brand_name}\nМодель: {model_name}"