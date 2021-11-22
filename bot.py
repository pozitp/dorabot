# import logging
import json

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ChatType, ContentType
from aiogram.utils.exceptions import Throttled

from config import TOKEN

# logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def setup_bot_commands(dispatcher: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand(command="/topsocial", description="Топ социального рейтинга"),
        types.BotCommand(command="/mysocial", description="Мой социальный рейтинг")
    ])
    # logging.info("Started")


@dp.message_handler(content_types=ContentType.STICKER)
async def example(message: types.Message):
    print()


@dp.message_handler(commands=['topsocial'], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def social_top(message: types.Message):
    with open('db.json', "r") as file:
        data = json.load(file)
    top = sorted(data[str(message.chat.id)].items(), key=lambda i: i[1], reverse=True)[0:10]
    top_msg = "Топ чата:\n"
    chat_id = message.chat.id
    for top_u in top:
        user_info = await bot.get_chat_member(chat_id, top_u[0])
        top_msg += f'{user_info["user"]["first_name"]}: {top_u[1]}\n'
    return await message.reply(top_msg)


@dp.message_handler(commands=['mysocial'], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def social_top(message: types.Message):
    with open('db.json', "r") as file:
        data = json.load(file)
    msg = f'Твой рейтинг: {data[str(message.chat.id)][str(message.from_user.id)]}'
    return await message.reply(msg)


@dp.message_handler(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def social_rating(message: types.Message):
    with open('db.json', "r") as file:
        data = json.load(file)
    entry1 = {
        str(message.chat.id): {}
    }
    if message.text.startswith("++") and message.reply_to_message:
        if message.reply_to_message.from_user.is_bot:
            await message.reply("Нельзя изменять рейтинг боту!")
            return
        try:
            await dp.throttle('++', rate=10)
        except Throttled:
            await message.reply('Нельзя изменять рейтинг так часто!')
        else:
            if message.from_user.id == message.reply_to_message.from_user.id:
                await message.reply("Нельзя изменять рейтинг самому себе!")
                return
            entry2 = {
                str(message.reply_to_message.from_user.id): 0
            }
            if str(message.chat.id) not in data:
                data.update(entry1)
            if str(message.reply_to_message.from_user.id) not in data[str(message.chat.id)]:
                data[str(message.chat.id)].update(entry2)

            data[str(message.chat.id)][str(message.reply_to_message.from_user.id)] += 1

            with open('db.json', "w") as file:
                json.dump(data, file)

            return await message.reply(f'Социальный рейтинг '
                                       f'{str(message.reply_to_message["from"]["first_name"])}'
                                       f' увеличен до {data[str(message.chat.id)][str(message.reply_to_message.from_user.id)]}')
    if message.text.startswith('—') or message.text.startswith('--') and message.reply_to_message:
        if message.reply_to_message.from_user.is_bot:
            await message.reply("Нельзя изменять рейтинг боту!")
            return
        try:
            await dp.throttle('++', rate=10)
        except Throttled:
            await message.reply('Нельзя изменять рейтинг так часто!')
        else:
            if message.from_user.id == message.reply_to_message.from_user.id:
                await message.reply("Нельзя изменять рейтинг самому себе!")
                return
            entry2 = {
                str(message.reply_to_message.from_user.id): 0
            }
            if str(message.chat.id) not in data:
                data.update(entry1)
            if str(message.reply_to_message.from_user.id) not in data[str(message.chat.id)]:
                data[str(message.chat.id)].update(entry2)

            data[str(message.chat.id)][str(message.reply_to_message.from_user.id)] -= 1

            with open('db.json', "w") as file:
                json.dump(data, file)

            return await message.reply(f'Социальный рейтинг '
                                       f'{str(message.reply_to_message["from"]["first_name"])}'
                                       f' уменьшен до {data[str(message.chat.id)][str(message.reply_to_message.from_user.id)]}')


@dp.message_handler(chat_type=[ChatType.PRIVATE])
async def no_private(message: types.Message):
    return message.reply('Я не работаю в личных сообщениях. Добавь меня в групповой чат.')


if __name__ == '__main__':
    # logging.info("Starting...")
    executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)
