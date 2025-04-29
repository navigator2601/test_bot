from telethon import TelegramClient, events, utils
import asyncio
from bot_test.config import API_ID, API_HASH, TELEGRAM_PHONE, TELETHON_SESSION_NAME
client = TelegramClient(TELETHON_SESSION_NAME, API_ID, API_HASH)
phone = TELEGRAM_PHONE

async def connect():
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        await client.sign_in(phone, input('Введіть код: '))

async def disconnect():
    await client.disconnect()

async def get_chat_messages(chat_id, limit=10):
    await connect()
    try:
        messages = await client.get_messages(chat_id, limit=limit)
        return messages
    finally:
        await disconnect()

async def main():
    target_chat_id = 525974549  # Замініть на потрібний ID

    messages = await get_chat_messages(target_chat_id)

    if messages:
        print(f"Останні {len(messages)} повідомлень з чату {target_chat_id}:")
        for message in messages:
            sender = await client.get_entity(message.sender_id)
            print(f"{sender.first_name}: {message.text}")
    else:
        print(f"Не вдалося отримати повідомлення з чату {target_chat_id}.")

if __name__ == '__main__':
    asyncio.run(main())