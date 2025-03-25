from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CallbackContext
from handlers.db_queries import fetch_brands, fetch_types

async def info(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Кондиціонери", callback_data="info_air_conditioners")],
        [InlineKeyboardButton("Фреони", callback_data="info_freons")],
        [InlineKeyboardButton("Типові помилки", callback_data="info_errors")],
        [InlineKeyboardButton("Діагностика", callback_data="info_diagnostics")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ℹ️ Оберіть категорію інформації:", reply_markup=reply_markup)

async def show_brands(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    brands = fetch_brands()

    if brands:
        keyboard = [[InlineKeyboardButton(f"{brand_name} ({model_count} моделей)", callback_data=f"brand_{brand_name}")] for brand_name, model_count in brands]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("📋 **Оберіть бренд кондиціонерів:**", reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await query.message.reply_text("ℹ️ Немає доступної інформації про бренди.")

async def show_types(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    brand_name = query.data.split("_")[1]
    types = fetch_types(brand_name)

    if types:
        keyboard = [[InlineKeyboardButton(f"{type_name} ({model_count} моделей)", callback_data=f"type_{type_name}")] for type_name, model_count in types]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"📋 **Типи кондиціонерів для бренду {brand_name}:**", reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await query.message.reply_text(f"ℹ️ Для бренду {brand_name} немає доступної інформації про типи кондиціонерів.")

async def callback_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    if query.data == "info_air_conditioners":
        await show_brands(update, context)
    elif query.data.startswith("brand_"):
        await show_types(update, context)
    else:
        await query.answer("Невідома команда.")

info_handler = CallbackQueryHandler(info)
callback_handler = CallbackQueryHandler(callback_handler)
