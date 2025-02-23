import psycopg2
from telegram import Bot
from telegram.ext import CommandHandler, Application
import urllib.parse as up

# Підключення до бази даних
def connect_db():
    url = "postgresql://neondb_owner:npg_dhwrDX6O1keB@ep-round-star-a9r38wl3-pooler.gwc.azure.neon.tech/neondb"
    result = up.urlparse(url)

    conn = psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    return conn

# Команда /start для бота
async def start(update, context):
    await update.message.reply_text("Чіназес! Просто імбово що ти підключився. Будемо чілитися разом")

# Команда /db для виконання запиту до бази даних
async def db(update, context):
    conn = connect_db()
    cursor = conn.cursor()

    # Виконуємо простий запит до бази даних (приклад)
    cursor.execute("SELECT * FROM freons;")  # замініть на реальний запит
    rows = cursor.fetchall()

    # Відправляємо результат користувачу
    message = "\n".join([str(row) for row in rows])
    await update.message.reply_text(message)

    cursor.close()
    conn.close()

# Основна функція для запуску бота
def main():
    # Ваш Telegram Token
    token = '8177185933:AAGvnm0JmuTxucr8VqU0nzGd4WrNkn5VHpU'
    
    # Створення об'єкта Application
    application = Application.builder().token(token).build()

    # Додаємо хендлери для команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('db', db))

    # Запускаємо бота
    application.run_polling()

if __name__ == '__main__':
    main()
