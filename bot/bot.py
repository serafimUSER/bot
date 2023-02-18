from aiogram import Bot, Dispatcher, executor, types
from html import escape

import core.config as config
import logging

import random


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

database = {}


def random_task(id_session):
    mode = config.modes[database[id_session]["game"]["status_game"]]
    mode_tags = mode["tags"]

    tasks = config.tasks_data
    mode_tasks = []
    for key in tasks:
        for mode_tag in mode_tags:
            if mode_tag in tasks[key]["tags"] and tasks[key] not in mode_tasks:
                mode_tasks.append(tasks[key])
    
    game_task = mode_tasks[random.randint(0, len(mode_tasks)-1)]
    
    data = database[id_session]["game"]["users"]
    user = data[random.randint(0, len(data)-1)]
    
    tags = ""
    for game_tag in game_task["tags"]:
        tags += f"#{game_tag} "
    
    return f"Задание для <b>{escape(user)}</b>\n\n{game_task['text']}\n{tags}"
    

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    play_start = types.InlineKeyboardMarkup()
    play_start.add(
        types.InlineKeyboardButton("Играть 🎲", callback_data="play")
    )
    
    database[str(message.chat.id)] = {"game": {"users": [], "status_game": ""}, "status": ""}
    
    await message.reply(
    f"""<b>{escape('Добро пожаловать,')}</b> {message.from_user.username}! 👋
    
Если ты хочешь <b>{escape('отлично')}</b> провести время в компании - ты по адресу! Мы предоставляем простую и интересную игру. Ниже можешь ознакомиться с правилами ⬇

Правила игры просты 💫:
1. Выбирай тему, количество игроков и их ники
2. Игроки по очереди отвечают на вопросы или выполняют действия
3. Всем весело и здорово
""", parse_mode="HTML", reply_markup=play_start)


@dp.message_handler(commands=['newgame'])
async def newgame(msg: types.Message):
    database[str(msg.chat.id)] = {"game": {"users": [], "status_game": ""}, "status": ""}
    class Call:
        message = msg
        
    await play(Call)

@dp.callback_query_handler(text="play")
async def play(call: types.CallbackQuery):
    team = types.ReplyKeyboardMarkup()
    num = 0
    
    def gen_tow(team):
        team.row(
                types.KeyboardButton(list(config.modes.keys())[mode_index]),
                types.KeyboardButton(list(config.modes.keys())[mode_index+1])
        )
    
    for mode_index in range(len(config.modes)):
        if len(config.modes) % 2 == 0:
            if num == 1:
                num = 0
                continue
            
            gen_tow(team)
            num = 1
        else:
            if mode_index == len(list(config.modes.keys()))-1:
                team.add(types.KeyboardButton(list(config.modes.keys())[mode_index]))
                break
            
            elif num == 1:
                num = 0
                continue
            
            gen_tow(team)
            num = 1
    
    database[str(call.message.chat.id)]["status"] = "status"
    await bot.send_message(call.message.chat.id, "Выберете режим игры: ", reply_markup=team)


@dp.message_handler(content_types=["text"])
async def echo(message: types.Message):
    if database[str(message.chat.id)]["status"] == "status":
        for i in list(config.modes.keys()):
            if message.text == i:
                database[str(message.chat.id)]["game"]["status_game"] = i
                database[str(message.chat.id)]["status"] = "users"
                
                await bot.send_message(message.chat.id, "Введите через запятую пользователей: ")
                
    elif database[str(message.chat.id)]["status"] == "users":
        database[str(message.chat.id)]["status"] = ""
        users = list(filter(lambda li: li != "", message.text.replace(" ", "").split(",")))
        database[str(message.chat.id)]["game"]["users"] = users
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Закончить игру 🚫", callback_data="game_stop"),
            types.InlineKeyboardButton("Дальше ➡", callback_data="next")
        )
        
        await bot.send_message(message.chat.id, random_task(str(message.chat.id)), parse_mode="HTML", reply_markup=markup)

@dp.callback_query_handler(text="next")
async def next(call: types.CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Закончить игру 🚫", callback_data="game_stop"),
        types.InlineKeyboardButton("Дальше ➡", callback_data="next")
    )
    await bot.send_message(call.message.chat.id, random_task(str(call.message.chat.id)), parse_mode="HTML", reply_markup=markup)

@dp.callback_query_handler(text="game_stop")
async def game_stop(call: types.CallbackQuery):
    database[str(call.message.chat.id)] = {"game": {"users": [], "status_game": ""}, "status": ""}
    await bot.send_message(call.message.chat.id, "Хорошего настроения 😇\nЧтобы начать новую игру введит /newgame")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
