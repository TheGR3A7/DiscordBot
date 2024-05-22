import disnake
import asyncio
import random
from disnake.ext import commands
from datetime import datetime
from typing import Optional

bot = commands.Bot(command_prefix="!", help_command=None, intents=disnake.Intents.all(), test_guilds=[1215750949587521677])

# Глобальные переменные


CENSORED_WORDS = ["fook", "karas"]
WARN_THRESHOLD = 3
warnings = {}


# События


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")

    await bot.change_presence(
        status=disnake.Status.online,
        activity=disnake.Game(name="GTA IRL")
    )


@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    role = disnake.utils.get(member.guild.roles, id=1215791141778362500)

    embed = disnake.Embed(
        title="Новый участник!",
        description=f"{member.name}",
        color=0xffffff
    )

    await member.add_roles(role)
    await channel.send(embed=embed)


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    for content in message.content.split():
        for censored_word in CENSORED_WORDS:
            if content.lower() == censored_word:
                await message.delete()
                await message.channel.send(f"{message.author.mention} такие слова запрещены!",delete_after=2)

                user_id = message.author.id
                warnings[user_id] = warnings.get(user_id, 0) + 1

                if warnings[user_id] >= WARN_THRESHOLD:
                    await message.author.add_roles(disnake.utils.get(message.author.guild.roles, id=1215792832577671249))
                    mute_msg = await message.channel.send(f"{message.author.mention} получил мут на 1 минуту за нарушение правил.")
                    await asyncio.sleep(60)
                    await message.author.remove_roles(disnake.utils.get(message.author.guild.roles, id=1215792832577671249))
                    warnings[user_id] = 0
                    await mute_msg.delete()

                break


@bot.event
async def on_command_error(ctx, error):
    print(error)

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author}, у вас недостаточно прав для выполнения данной команды!")
    elif isinstance(error, commands.UserInputError):
        await ctx.send(embed=disnake.Embed(
            description=f"Правильное использование команды: '{ctx.prefix}{ctx.command.name}' ({ctx.command.brief})\nExample: {ctx.prefix}{ctx.command.usage}"
        ))


@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == 1215958366648799323 and payload.message_id == 1215959244113838150:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if not member.bot:
            role_id = None

            if str(payload.emoji) == "👊":
                role_id = 1215790416855699456

            if role_id:
                role = guild.get_role(role_id)
                await member.add_roles(role)


# Команды через '!'


@bot.command(usage="kick <@user> <reason=None>")
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: disnake.Member, *, reason="Нарушение правил."):
    await ctx.send(f"Администратор {ctx.author.mention} исключил пользователя {member.mention}", delete_after=2)
    await member.kick(reason=reason)
    await ctx.message.delete()


@bot.command(name="бан", aliases=["ban"])
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: disnake.Member, *, reason="Нарушение правил."):
    try:
        await ctx.send(f"Администратор {ctx.author.mention} забанил пользователя {member.mention}", delete_after=2)
        await member.ban(reason=reason)
        await ctx.message.delete()
    except Exception as e:
        print(f"Ошибка при бане пользователя: {e}")


@bot.command(name="разбан", aliases=["unban"])
@commands.has_permissions(ban_members=True, administrator=True)
async def unban(ctx, user: disnake.User):
    await ctx.guild.unban(user)
    await ctx.send(f"Разбанен {user.mention}")


@bot.command()
async def hello(ctx):
    await ctx.send(f"Aloha, {ctx.author.mention}!")


@bot.command()
async def time(ctx):
    current_time = datetime.now().strftime("%H:%M:%S")
    await ctx.send(f"Текущее время: {current_time}")


@bot.command()
async def date(ctx):
    current_date = datetime.now().strftime("%d/%m/%Y")
    await ctx.send(f"Текущая дата: {current_date}")


@bot.command(name="squad")
async def ask_squad(ctx):
    view = Confirm()

    await ctx.send("Приглашение на вступление в Hustler University, вы согласны?", view=view)
    await view.wait()

    if view.value is None:
        await ctx.send("Ты упустил свой шанс! Какой же ты Bottom G...")
    elif view.value:
        await ctx.send("Отлично! Это первый шаг к становлению Top G", view=LinkToSquad())
    else:
        await ctx.send("Ты упустил свой шанс! Какой же ты Bottom G...")


@bot.command()
async def transport(ctx):
    await ctx.send("Выберите транспорт:", view=DropDownView())


@bot.command()
async def info(ctx):
    embed = disnake.Embed(
        title="Информация о боте",
        description="Этот бот предназначен для курсовой работы.",
        color=0x3498db
    )

    embed.add_field(name="Версия", value="1.0")
    embed.add_field(name="Разработчик", value="Логвинов Алексей")
    embed.add_field(name="Github", value="[https://github.com/TheGR3A7]")

    await ctx.send(embed=embed)


@bot.command()
async def help(ctx):
    embed = disnake.Embed(
        title="Помощь по командам",
        color=0x00ff00
    )

    embed.add_field(name="!info", value="Отображение информации о боте")
    embed.add_field(name="!hello", value="Приветствие от бота")
    embed.add_field(name="!time", value="Отображение текущего времени")
    embed.add_field(name="!date", value="Отображение текущей даты")
    embed.add_field(name="!squad", value="Вступить в сквад")
    embed.add_field(name="!uinfo пользователь", value="Информация о пользователе")
    embed.add_field(name="!transport", value="Выберите транспорт")
    embed.add_field(name="!rps выбор", value="Игра камень-ножницы-бумага")
    embed.add_field(name="/calc", value="Калькулятор")
    embed.add_field(name="/avatar", value="Выдает аватарку выбранного пользователя")
    embed.add_field(name="/random_role", value="Выдает случайную роль")
    embed.add_field(name="/clear", value="Удаляет введенное количество сообщений(Только для администратора)")
    embed.add_field(name="!kick", value="Кикает с сервера(Только для администратора)")
    embed.add_field(name="!ban", value="Банит с сервера(Только для администратора)")
    embed.add_field(name="!ping", value="Проверка пинга бота(Только для администратора)")

    await ctx.send(embed=embed)


@bot.command(name="rock_paper_scissors", aliases=["rps"])
async def rock_paper_scissors(ctx, player_choice: str):
    game = RockPaperScissors()

    if player_choice.lower() not in game.choices:
        await ctx.send("Неверный ответ! Пожалуйста, выберите 'камень', 'ножницы' или 'бумагу'.")
        return

    bot_choice = random.choice(game.choices)
    result = game.determine_winner(player_choice.lower(), bot_choice)

    embed = disnake.Embed(
        title="Камень-Ножницы-Бумага",
        color=0x3498db
    )
    embed.add_field(name="Ваш выбор", value=player_choice.capitalize(), inline=False)
    embed.add_field(name="Выбор бота", value=bot_choice.capitalize(), inline=False)
    embed.add_field(name="Результат", value=result, inline=False)

    await ctx.send(embed=embed)


@bot.command(name="userinfo", aliases=["uinfo"])
async def user_info(ctx, member: disnake.Member = None):
    member = member or ctx.author
    embed = disnake.Embed(title=f"Информация о {member.display_name}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Имя", value=member.name, inline=True)
    embed.add_field(name="Никнейм", value=member.nick, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Статус", value=str(member.status).capitalize(), inline=True)
    embed.add_field(name="Дата присоединения", value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
    embed.add_field(name="Дата создания аккаунта", value=member.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
    embed.add_field(name="Роли", value=", ".join([role.name for role in member.roles[1:]]), inline=True)
    embed.add_field(name="Высшая роль", value=member.top_role.name, inline=True)
    await ctx.send(embed=embed)


@bot.command(name="ping")
async def ping(ctx):
    latency = bot.latency * 1000  # Пинг в миллисекундах
    embed = disnake.Embed(
        title="Проверка пинга",
        description=f"Пинг бота: {latency:.2f} мс",
        color=0x3498db
    )
    await ctx.send(embed=embed)


# Команды через '/'


@bot.slash_command(description="'+' - для сложения, '-' - для вычитания, '*' - для умножения, '/' - для деления")
async def calc(inter, a: int, oper: str, b: int):
    if oper == "+":
        result = a+b
    elif oper == "-":
        result = a-b
    elif oper == "*":
        result = a*b
    elif oper == "/":
        result = a/b
    else:
        result = "Неверный оператор!"

    await inter.send(str(result), delete_after=5)


@bot.slash_command(description="Выдает случайную роль")
async def random_role(inter):
    await inter.response.defer()

    guild = inter.guild
    roles_to_include = [1215961567196352522, 1215961664621379685, 1215961763091189780]

    all_roles = guild.roles

    eligible_roles = [role for role in all_roles if role.id in roles_to_include and not role.is_default()]

    if eligible_roles:
        random_role = random.choice(eligible_roles)
        member = inter.author

        await member.add_roles(random_role)
        await inter.edit_original_response(content=f"Поздравляю! Вы получили случайную роль: {random_role.mention}")
        await asyncio.sleep(2)
        await inter.delete_original_response()
    else:
        await inter.edit_original_response(content="На сервере нет доступных ролей для этой команды.")
        await asyncio.sleep(2)
        await inter.delete_original_response()


@bot.slash_command()
@commands.has_permissions(administrator=True)
async def clear(inter, amount: int):
    if not 1 <= amount <= 100:
        await inter.response.send_message("Пожалуйста, введите число от 1 до 100", ephemeral=True)
        return

    await inter.channel.purge(limit=amount + 1)
    await inter.response.send_message(f"Удалено {amount} сообщений!", ephemeral=True)


@bot.slash_command()
async def avatar(inter, member:disnake.Member = None):
    user = member or inter.author
    embed = disnake.Embed(title="Аватарка", color=0x2f3136)
    embed.set_image(url=user.display_avatar.url)
    await inter.response.send_message(embed=embed)


# Приглашение в сквад


class Confirm(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=10.0)
        self.value = Optional[bool]

    @disnake.ui.button(label="Confirm", style=disnake.ButtonStyle.green, emoji="😎")
    async def confirm(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.send_message("Отлично, теперь жди сообщения!")
        self.value = True
        self.stop()

    @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.red, emoji="💀")
    async def cancel(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.send_message("Роковая ошибка")
        self.value = False
        self.stop()


class LinkToSquad(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(label="Sign the contract, BIG BOY!", url="https://github.com/TheGR3A7"))


# Выпадающее меню


class DropDown(disnake.ui.StringSelect):
    def __init__(self):
        options = [
            disnake.SelectOption(label="Bugatti", description="Розовый бугатти", emoji="🏎️"),
            disnake.SelectOption(label="Bicycle", description="Трехколесный велосипед", emoji="🚲"),
            disnake.SelectOption(label="Plane", description="Бизнес-джет", emoji="✈️"),
            disnake.SelectOption(label="Yacht", description="Личная яхта", emoji="⛵")
        ]

        super().__init__(
            placeholder="Transports",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.send_message(f"Вы выбрали {self.values[0]}. Отличный выбор!")


class DropDownView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DropDown())


class RockPaperScissors:
    def __init__(self):
        self.choices = ["камень", "бумага", "ножницы"]

    def determine_winner(self, player_choice, bot_choice):
        if player_choice == bot_choice:
            return "Ничья!"
        elif (
            (player_choice == "камень" and bot_choice == "ножницы") or
            (player_choice == "бумага" and bot_choice == "камень") or
            (player_choice == "ножницы" and bot_choice == "бумага")
        ):
            return "Ты выиграл!"
        else:
            return "Ты проиграл!"


token = open('token.txt', 'r').readline()
bot.run(token)