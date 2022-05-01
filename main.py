import re
from typing import Optional
import os
import discord
from discord.ext import commands

from command_parser import roll, execute_dice_cmd

roll_validator = re.compile(r'[0-9d+-/*/() \\]+')
dice_mod_validator = re.compile(r'[1-9][0-9]*[bp]')

bot = commands.Bot(command_prefix="!", intents=(discord.Intents(messages=True)))


@bot.event
async def on_ready():
    print("Bot ready!")


@bot.command()
async def r(ctx: commands.Context, cmd: str):
    query_author = ctx.author

    if len(cmd) == 0:
        return

    if len(cmd) > 100:
        await ctx.send(f'{query_author.mention} Roll command can have max 100 characters.')
        return

    if roll_validator.fullmatch(cmd) is None:
        await ctx.send(f'{query_author.mention} Roll command can only contain: numbers, rolls in XdY format, +-*/()\\, space.')
        return

    try:
        result, rolls = execute_dice_cmd(cmd)
        await ctx.send(f'{query_author.mention}\n```python\n{result}\nRolls [{", ".join(str(x) for x in rolls)}]```')

    except:
        await ctx.send(f'{query_author.mention} Failed to evaluate command!')


@bot.command()
async def cr(ctx: commands.Context, skill_val: int, mod: Optional[str] = None):
    if skill_val > 100 or skill_val < 1:
        await ctx.send(f"{ctx.author.mention} Invalid skill value!")
        return

    if mod is not None and dice_mod_validator.fullmatch(mod) is None:
        await ctx.send(f"{ctx.author.mention} Invalid dice modifier!")
        return

    base_roll = roll([10, 10], start_from_zero=True)

    if mod is None:
        modifiers = []
        mod = 0
    else:
        mod_count = int(mod[:-1])
        modifiers = roll([10] * mod_count, start_from_zero=True)
        mod = -1 if mod[-1] == 'b' else 1

    units = base_roll[1]
    all_rolls = [x * 10 + units for x in [base_roll[0], *modifiers]]
    all_rolls = [100 if x == 0 else x for x in all_rolls]

    if mod == 0:
        final_roll = all_rolls[0]
    elif mod == -1:
        final_roll = min(all_rolls)
    else:
        final_roll = max(all_rolls)

    if final_roll == 100:
        result = "Fumble!"

    elif skill_val < 50 and final_roll >= 96:
        result = "Fumble!"

    elif final_roll > skill_val:
        result = "Fail"

    else:
        if final_roll == 1:
            result = "Critical Success!"
        elif final_roll <= (skill_val // 5):
            result = "Extreme Success"
        elif final_roll <= (skill_val // 2):
            result = "Hard Success"
        else:
            result = "Success"

    rolls = [t * 10 for t in [base_roll[0], *modifiers]] + [units]
    await ctx.send(f"{ctx.author.mention}\n```python\n{result} {final_roll}\nRolls: [{', '.join(str(x) for x in rolls)}]```")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
