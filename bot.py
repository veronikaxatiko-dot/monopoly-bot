import asyncio
import random
import os

TOKEN = os.getenv("TOKEN")

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


# ==========================================
# CONFIG
# ==========================================


START_MONEY = 1500
PASS_START = 200
JAIL_POSITION = 10

# ==========================================
# BOARD
# ==========================================

BOARD = [
    {"type": "start", "name": "СТАРТ"},

    {"type": "property", "name": "Анклав морозной луны", "price": 60, "rent": 2},
    
    {"type": "chance", "name": "Задание мира"},

    {"type": "property", "name": "Нашгород", "price": 60, "rent": 4},

    {"type": "tax", "name": "Налог", "amount": 200},

    {"type": "railroad", "name": "Море древности", "price": 200, "rent": 25},

    {"type": "property", "name": "Деревня Пуассон", "price": 100, "rent": 6},

    {"type": "chance", "name": "Задание легенд"},

    {"type": "property", "name": "Оперный театр Эпиклез", "price": 100, "rent": 6},

    {"type": "property", "name": "Кур-де-Фонтейн", "price": 120, "rent": 8},

    {"type": "jail", "name": "Опыты Дотторе"},

    {"type": "property", "name": "Цуруми", "price": 140, "rent": 10},

    {"type": "utility", "name": "Охота за грозами", "price": 150, "rent": 20},

    {"type": "property", "name": "Ватацуми", "price": 140, "rent": 10},

    {"type": "property", "name": "Остров Наруками", "price": 160, "rent": 12},

    {"type": "railroad", "name": "Энканомия", "price": 200, "rent": 25},

    {"type": "property", "name": "Земля верхнего Сетеха", "price": 180, "rent": 14},

    {"type": "chance", "name": "Задание мира"},

    {"type": "property", "name": "Царство Фаракхерт", "price": 180, "rent": 14},

    {"type": "property", "name": "Пустыня Колоннад", "price": 200, "rent": 16},

    {"type": "rest", "name": "Чайник безмятежности"},

    {"type": "property", "name": "Атокпан", "price": 220, "rent": 18},

    {"type": "chance", "name": "Задание легенд"},

    {"type": "property", "name": "Ручьи Тойек", "price": 220, "rent": 18},

    {"type": "property", "name": "Очканатлан", "price": 240, "rent": 20},

    {"type": "railroad", "name": "Разлом", "price": 200, "rent": 25},

    {"type": "property", "name": "Долина Бишуй", "price": 260, "rent": 22},

    {"type": "property", "name": "Долина Ченьюй", "price": 260, "rent": 22},

    {"type": "utility", "name": "Пророчество Фонтейна", "price": 150, "rent": 20},

    {"type": "property", "name": "Гавань Ли Юэ", "price": 280, "rent": 24},

    {"type": "go_to_jail", "name": "На Опыты"},

    {"type": "property", "name": "Логово Ужаса Бури", "price": 300, "rent": 26},

    {"type": "property", "name": "Драконий хребет", "price": 300, "rent": 26},

    {"type": "chance", "name": "Задание мира"},

    {"type": "property", "name": "Долина Звездопада", "price": 320, "rent": 28},

    {"type": "railroad", "name": "Храм Асмодей", "price": 200, "rent": 25},

    {"type": "chance", "name": "Задание легенд"},

    {"type": "property", "name": "Морепесок", "price": 350, "rent": 35},

    {"type": "expensive_buy", "name": "Покупка Луны", "amount": 100},

    {"type": "property", "name": "Заполярный дворец", "price": 400, "rent": 50},
]

# ==========================================
# CHANCE CARDS
# ==========================================

CHANCE = [
    {"text": "💰 Донат на вайфу: +200$", "money": 200},

    {"text": "💸 Проиграл 50 на 50: -50$", "money": -50},

    {"text": "🏦 Промокод успешно применён: +150$", "money": 150},

    {"text": "😭 Ци Ци сбила гарант: -100$", "money": -100},

    {
        "text": "🗝 Карточка освобождения от тюрьмы",
        "action": "free_jail"
    },

    {
        "text": "♨️ Отправляйтесь в Атокпан",
        "action": "move",
        "position": 21
    },

    {
        "text": "🏁 Пройдите на старт",
        "action": "move_start"
    },

    {
        "text": "🚔 Вас украли на опыты",
        "action": "go_to_jail"
    },

    {
        "text": "⛩ Отправляйтесь в Храм Асмодей",
        "action": "move",
        "position": 35
    },

    {
        "text": "⬅️ Вернитесь на 3 клетки назад",
        "action": "back",
        "steps": 3
    },
]

# ==========================================
# GAME STORAGE
# ==========================================

games = {}

# ==========================================
# GAME CLASS
# ==========================================


class MonopolyGame:

    def __init__(self):
        self.players = {}
        self.turn_order = []
        self.current_turn = 0
        self.properties = {}

    def add_player(self, user_id, name):

        if user_id in self.players:
            return False

        self.players[user_id] = {
            "name": name,
            "money": START_MONEY,
            "position": 0,
            "jail": 0,
            "bankrupt": False,
            "free_jail_card": 0,
        }

        self.turn_order.append(user_id)

        return True

    def current_player(self):
        return self.turn_order[self.current_turn]

    def next_turn(self):

        alive = [
            p for p in self.turn_order
            if not self.players[p]["bankrupt"]
        ]

        self.turn_order = alive

        if len(self.turn_order) <= 1:
            return

        self.current_turn += 1

        if self.current_turn >= len(self.turn_order):
            self.current_turn = 0

    def roll_dice(self):
        return random.randint(1, 6)

    def move_player(self, user_id, steps):

        player = self.players[user_id]

        old = player["position"]

        new = (old + steps) % len(BOARD)

        if new < old:
            player["money"] += PASS_START

        player["position"] = new

        return BOARD[new]

    def player_info(self, user_id):

        p = self.players[user_id]

        return (
            f"👤 {p['name']}\n"
            f"💰 {p['money']}$\n"
            f"📍 {BOARD[p['position']]['name']}\n"
            f"🗝 Карты выхода: {p['free_jail_card']}\n"
        )

    def buy_property(self, user_id):

        player = self.players[user_id]

        pos = player["position"]

        if pos in self.properties:
            return "❌ Уже куплено"

        cell = BOARD[pos]

        if cell["type"] not in [
            "property",
            "railroad",
            "utility"
        ]:
            return "❌ Это нельзя купить"

        if player["money"] < cell["price"]:
            return "❌ Недостаточно денег"

        player["money"] -= cell["price"]

        self.properties[pos] = user_id

        return f"🏠 {player['name']} купил {cell['name']}"

    def pay_rent(self, user_id):

        player = self.players[user_id]

        pos = player["position"]

        if pos not in self.properties:
            return None

        owner_id = self.properties[pos]

        if owner_id == user_id:
            return None

        owner = self.players[owner_id]

        rent = BOARD[pos]["rent"]

        player["money"] -= rent
        owner["money"] += rent

        if player["money"] <= 0:
            player["bankrupt"] = True

        return (
            f"💸 {player['name']} заплатил "
            f"{rent}$ игроку {owner['name']}"
        )

    def process_cell(self, user_id):

        player = self.players[user_id]

        cell = BOARD[player["position"]]

        # НАЛОГ

        if cell["type"] == "tax":

            player["money"] -= cell["amount"]

            return f"💸 Налог: -{cell['amount']}$"

        # ОТДЫХ

        if cell["type"] == "rest":

            player["money"] += 50

            return (
                "🛌 Чайник безмятежности\n"
                "💰 Восстановление: +50$"
            )

        # ДОРОГАЯ ПОКУПКА

        if cell["type"] == "expensive_buy":

            amount = cell["amount"]

            player["money"] -= amount

            if player["money"] <= 0:

                player["bankrupt"] = True

                return (
                    f"💸 Покупка Луны: -{amount}$\n"
                    f"☠️ БАНКРОТ"
                )

            return (
                f"🛒 Дорогая покупка!\n"
                f"💸 Потрачено: {amount}$"
            )

        # ШАНС

        if cell["type"] == "chance":

            card = random.choice(CHANCE)

            text = f"🎴 {card['text']}"

            # ДЕНЬГИ

            if "money" in card:
                player["money"] += card["money"]

            # КАРТА ВЫХОДА

            if card.get("action") == "free_jail":

                player["free_jail_card"] += 1

                text += "\n🗝 Получена карта выхода"

            # ПЕРЕМЕЩЕНИЕ

            if card.get("action") == "move":

                player["position"] = card["position"]

                new_cell = BOARD[player["position"]]

                text += (
                    f"\n📍 Игрок перемещён:"
                    f" {new_cell['name']}"
                )

            # НА СТАРТ

            if card.get("action") == "move_start":

                player["position"] = 0
                player["money"] += PASS_START

                text += (
                    f"\n🏁 Игрок отправлен на старт"
                    f"\n💰 +{PASS_START}$"
                )

            # НАЗАД

            if card.get("action") == "back":

                player["position"] -= card["steps"]

                if player["position"] < 0:
                    player["position"] += len(BOARD)

                text += (
                    f"\n⬅️ Игрок вернулся "
                    f"на {card['steps']} клетки"
                )

            # В ТЮРЬМУ

            if card.get("action") == "go_to_jail":

                player["position"] = JAIL_POSITION
                player["jail"] = 2

                text += "\n🚔 Игрок отправлен в тюрьму"

            return text

        # В ТЮРЬМУ

        if cell["type"] == "go_to_jail":

            player["position"] = JAIL_POSITION
            player["jail"] = 2

            return "🚔 Игрок отправлен в тюрьму"

        return None


# ==========================================
# BOT
# ==========================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==========================================
# COMMANDS
# ==========================================

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Бот запущен")

@dp.message(Command("newgame"))
async def new_game(message: Message):

    chat_id = message.chat.id

    games[chat_id] = MonopolyGame()

    await message.answer(
        "🎮 Новая игра создана\n"
        "Игроки могут входить через /join"
    )


@dp.message(Command("join"))
async def join(message: Message):

    chat_id = message.chat.id

    if chat_id not in games:
        await message.answer("❌ Сначала /newgame")
        return

    game = games[chat_id]

    user_id = message.from_user.id
    name = message.from_user.first_name

    result = game.add_player(user_id, name)

    if result:
        await message.answer(f"✅ {name} вошёл в игру")
    else:
        await message.answer("❌ Ты уже в игре")


@dp.message(Command("players"))
async def players(message: Message):

    chat_id = message.chat.id

    if chat_id not in games:
        return

    game = games[chat_id]

    text = "📋 Игроки:\n\n"

    for uid in game.players:
        text += game.player_info(uid)
        text += "\n"

    await message.answer(text)


# ==========================================
# ROLL
# ==========================================


@dp.message(Command("roll"))
async def roll(message: Message):

    chat_id = message.chat.id

    if chat_id not in games:
        return

    game = games[chat_id]

    user_id = message.from_user.id

    if user_id not in game.players:
        await message.answer("❌ Ты не в игре")
        return

    current = game.current_player()

    if current != user_id:

        name = game.players[current]["name"]

        await message.answer(
            f"⏳ Сейчас ход игрока {name}"
        )

        return

    player = game.players[user_id]

    # ТЮРЬМА

    if player["jail"] > 0:

        if player["free_jail_card"] > 0:

            player["free_jail_card"] -= 1
            player["jail"] = 0

            await message.answer(
                "🗝 Использована карта "
                "освобождения!"
            )

        else:

            player["jail"] -= 1

            await message.answer(
                f"🚔 Ты в тюрьме ещё "
                f"{player['jail']} ходов"
            )

            game.next_turn()

            return

    # КУБИК

    dice = game.roll_dice()

    cell = game.move_player(user_id, dice)

    text = (
        f"🎲 Выпало: {dice}\n"
        f"📍 Клетка: {cell['name']}\n"
    )

    # ОБРАБОТКА КЛЕТКИ

    extra = game.process_cell(user_id)

    if extra:
        text += f"\n{extra}"

    # АРЕНДА

    rent = game.pay_rent(user_id)

    if rent:
        text += f"\n{rent}"

    # КНОПКА ПОКУПКИ

    keyboard = None

    pos = player["position"]

    if (
        cell["type"] in
        ["property", "railroad", "utility"]
        and pos not in game.properties
    ):

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Купить за {cell['price']}$",
                        callback_data=f"buy_{pos}"
                    )
                ]
            ]
        )

    text += (
        f"\n\n💰 Баланс: "
        f"{player['money']}$"
    )

    if player["bankrupt"]:
        text += "\n☠️ БАНКРОТ"

    await message.answer(
        text,
        reply_markup=keyboard
    )

    # ПОБЕДА

    alive = [
        p for p in game.players.values()
        if not p["bankrupt"]
    ]

    if len(alive) == 1:

        await message.answer(
            f"🏆 Победил {alive[0]['name']}!"
        )

        del games[chat_id]

        return

    game.next_turn()

    next_player = game.players[
        game.current_player()
    ]["name"]

    await message.answer(
        f"➡️ Ход игрока: {next_player}"
    )


# ==========================================
# BUY PROPERTY
# ==========================================


@dp.callback_query(F.data.startswith("buy_"))
async def buy_property(callback: CallbackQuery):

    chat_id = callback.message.chat.id

    if chat_id not in games:
        return

    game = games[chat_id]

    user_id = callback.from_user.id

    result = game.buy_property(user_id)

    add_player(user_id, name)

    await callback.message.answer(result)

    await callback.answer()


# ==========================================
# MAIN
# ==========================================


async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())