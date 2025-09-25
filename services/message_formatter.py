# відносний шлях до файлу: services/message_formatter.py

from typing import Dict, Any

def get_model_word_form(number: int) -> str:
    """
    Повертає правильну форму слова 'модель' залежно від числа.
    """
    if number % 10 == 1 and number % 100 != 11:
        return "модель"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return "моделі"
    else:
        return "моделей"

def format_model_details_message(model_details: Dict[str, Any]) -> str:
    """
    Форматує повідомлення про модель з конкретними даними, отриманими з БД.
    """
    if not model_details:
        return "❌ Деталі моделі не знайдено."
        
    model_name = model_details.get("Модель", "N/A")
    internal_unit = model_details.get("InternalUnit", "N/A")
    external_unit = model_details.get("ExternalUnit", "N/A")
    recommended_area = model_details.get("RecommendedArea", "N/A")
    power_supply = model_details.get("PowerSupply", "N/A")
    power_connection = model_details.get("PowerConnection", "N/A")
    pipe_diameters = model_details.get("PipeDiameters", "N/A")
    min_max_route = model_details.get("MinMaxRoute", "N/A")
    
    formatted_message = (
        f"<b>Модель:</b> {model_name}\n"
        f"<b>Маркування блоків:</b> {internal_unit}/{external_unit}\n"
        f"<b>Рекомендована площа:</b> {recommended_area} м²\n"
        f"<b>Живлення:</b> {power_supply}\n"
        f"<b>Кабель живлення:</b> {power_connection}\n"
        f"<b>Сполучні труби:</b> {pipe_diameters}\n"
        f"<b>Мінімальна / максимальна траса:</b> {min_max_route}"
    )
    
    return formatted_message

def format_description(model_details: Dict[str, Any]) -> str:
    """
    Форматує опис моделі, використовуючи шаблон та відповідні дані.
    """
    model_template = model_details.get("model_template", None)
    
    if not model_template:
        return "<b>Опис:</b>\n<i>Опис відсутній.</i>"

    formatted_description = model_template.format(
        TypeSeries=f"<b>{model_details.get('TypeSeries', 'N/A')}</b>",
        Brand=f"<b>{model_details.get('Brand', 'N/A')}</b>",
        Series=f"<b>{model_details.get('Series', 'N/A')}</b>",
        InternalUnit=f"<b>{model_details.get('InternalUnit', 'N/A')}</b>",
        ExternalUnit=f"<b>{model_details.get('ExternalUnit', 'N/A')}</b>",
        RecommendedArea=f"<b>{model_details.get('RecommendedArea', 'N/A')}</b>"
    )

    formatted_description = formatted_description.replace("\\n", "\n")

    return f"<b>Опис:</b>\n{formatted_description}"

def format_general_characteristics(model_details: Dict[str, Any]) -> str:
    return "<b>Загальні характеристики:</b>\n<i>Функціонал буде додано пізніше.</i>"

def format_functions(model_details: Dict[str, Any]) -> str:
    return "<b>Функції:</b>\n<i>Функціонал буде додано пізніше.</i>"

def format_technical_parameters(model_details: Dict[str, Any]) -> str:
    return "<b>Технічні параметри:</b>\n<i>Функціонал буде додано пізніше.</i>"

def format_installation_parameters(model_details: Dict[str, Any]) -> str:
    return "<b>Монтажні параметри:</b>\n<i>Функціонал буде додано пізніше.</i>"