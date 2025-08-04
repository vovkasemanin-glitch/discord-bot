from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080, debug=False)


def keep_alive():
    t = Thread(target=run)
    t.start()


import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CREATE_ROOM_CHANNEL_ID = 1401849232054554674
SEARCH_TEAM_CHANNEL_ID = 1401294465385365574
JABUKA_ROLE_ID = 1398370197936804001
RULES_CHANNEL_ID = 1401864792167284846

# --- Для временных комнат ---
temp_channels = {}  # {voice_channel_id: room_number}
used_numbers = set()
max_rooms = 100  # Максимальное количество комнат


def get_free_room_number():
    for i in range(1, max_rooms + 1):
        if i not in used_numbers:
            return i
    return None  # Если все заняты


# --- Класс для кнопок поиска тиммейтов ---
class TeamSearchView(discord.ui.View):

    def __init__(self, room_owner, room_name):
        super().__init__(timeout=None)
        self.room_owner = room_owner
        self.room_name = room_name

    @discord.ui.button(label='1',
                       style=discord.ButtonStyle.secondary,
                       emoji='1️⃣')
    async def one_player(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        if interaction.user.id != self.room_owner.id:
            await interaction.response.send_message(
                "Только создатель комнаты может использовать эту функцию!",
                ephemeral=True)
            return
        search_channel = bot.get_channel(SEARCH_TEAM_CHANNEL_ID)
        if search_channel:
            await search_channel.send(
                f"<@&{JABUKA_ROLE_ID}> {self.room_name} +1")
            await interaction.response.send_message(
                "Запрос на поиск 1 игрока отправлен!", ephemeral=True)

    @discord.ui.button(label='2',
                       style=discord.ButtonStyle.secondary,
                       emoji='2️⃣')
    async def two_players(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if interaction.user.id != self.room_owner.id:
            await interaction.response.send_message(
                "Только создатель комнаты может использовать эту функцию!",
                ephemeral=True)
            return
        search_channel = bot.get_channel(SEARCH_TEAM_CHANNEL_ID)
        if search_channel:
            await search_channel.send(
                f"<@&{JABUKA_ROLE_ID}> {self.room_name} +2")
            await interaction.response.send_message(
                "Запрос на поиск 2 игроков отправлен!", ephemeral=True)

    @discord.ui.button(label='3',
                       style=discord.ButtonStyle.secondary,
                       emoji='3️⃣')
    async def three_players(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        if interaction.user.id != self.room_owner.id:
            await interaction.response.send_message(
                "Только создатель комнаты может использовать эту функцию!",
                ephemeral=True)
            return
        search_channel = bot.get_channel(SEARCH_TEAM_CHANNEL_ID)
        if search_channel:
            await search_channel.send(
                f"<@&{JABUKA_ROLE_ID}> {self.room_name} +3")
            await interaction.response.send_message(
                "Запрос на поиск 3 игроков отправлен!", ephemeral=True)

    @discord.ui.button(label='4',
                       style=discord.ButtonStyle.secondary,
                       emoji='4️⃣')
    async def four_players(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        if interaction.user.id != self.room_owner.id:
            await interaction.response.send_message(
                "Только создатель комнаты может использовать эту функцию!",
                ephemeral=True)
            return
        search_channel = bot.get_channel(SEARCH_TEAM_CHANNEL_ID)
        if search_channel:
            await search_channel.send(
                f"<@&{JABUKA_ROLE_ID}> {self.room_name} +4")
            await interaction.response.send_message(
                "Запрос на поиск 4 игроков отправлен!", ephemeral=True)


# --- Класс для кнопки согласия с правилами с обработкой ошибок ---
class AgreeView(discord.ui.View):

    @discord.ui.button(label="Я ознакомился и согласен",
                       style=discord.ButtonStyle.success)
    async def agree_button(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        try:
            role = interaction.guild.get_role(JABUKA_ROLE_ID)
            if role in interaction.user.roles:
                await interaction.response.send_message(
                    "У тебя уже есть эта роль!", ephemeral=True)
                return
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                "Роль 'Джабука' выдана! Добро пожаловать на сервер!",
                ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Произошла ошибка: {e}",
                                                    ephemeral=True)


@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен и готов к работе!')


# --- Обработка создания временных голосовых комнат ---
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == CREATE_ROOM_CHANNEL_ID:
        guild = after.channel.guild
        category = after.channel.category

        room_number = get_free_room_number()
        if room_number is None:
            return  # Лимит комнат достигнут

        channel_name = f"🔥 Room #{room_number}"

        temp_voice_channel = await guild.create_voice_channel(
            name=channel_name, category=category)

        # Получаем связанный текстовый канал (если есть)
        temp_text_channel = temp_voice_channel.guild.get_channel(
            temp_voice_channel.id)

        if temp_text_channel:
            embed = discord.Embed(
                title="🔍 Поиск тиммейтов",
                description="Выберите количество игроков, которых нужно найти:",
                color=0xff6b35)
            view = TeamSearchView(member, channel_name)
            await temp_text_channel.send(embed=embed, view=view)

        await member.move_to(temp_voice_channel)
        temp_channels[temp_voice_channel.id] = room_number
        used_numbers.add(room_number)

    # Удаляем пустые комнаты и освобождаем номера
    for channel_id in list(temp_channels):
        channel = bot.get_channel(channel_id)
        if channel is None or len(channel.members) == 0:
            room_number = temp_channels[channel_id]
            used_numbers.remove(room_number)
            if channel is not None:
                await channel.delete()
            del temp_channels[channel_id]


# --- Команда для отправки сообщения с правилами и кнопкой ---
@bot.command()
@commands.has_permissions(administrator=True)
async def send_rules(ctx):
    if ctx.channel.id != RULES_CHANNEL_ID:
        await ctx.send(
            f"Эту команду можно использовать только в канале с правилами (ID: {RULES_CHANNEL_ID})"
        )
        return

    embed = discord.Embed(
        title="Правила сервера",
        description=
        "Пожалуйста, прочитай правила и нажми кнопку ниже, чтобы получить роль.",
        color=0x00ff00)
    view = AgreeView()
    await ctx.send(embed=embed, view=view)


import os

keep_alive()

bot.run(os.getenv('DISCORD_TOKEN'))
