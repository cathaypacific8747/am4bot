import discord
from discord.ext.commands import Bot, Context

import am4

from .checks import ignore_dm, ignore_pricealert
from .config import config

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix=config.COMMAND_PREFIX, intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} on {", ".join([g.name for g in bot.guilds])}')
    am4.db.init()
    print(f"am4utils ({am4.utils.__version__}), executable_path={am4.__path__[0]} loaded")


async def warn_broken(ctx: Context):
    await ctx.send(
        "We are experiencing with our hosting provider - many commands are broken right now and will be fixed hopefully <t:1694620800:R>"
    )


@bot.command(help="shows botinfo")
@ignore_pricealert()
async def botinfo(ctx: Context):
    info = "**AM4 ACDB bot (TEMPORARY)**\nMade by **favorit1** and **Cathay Express**\nDatabase and profit formula by **Scuderia Airlines**\nJoin this server: https://discord.gg/4tVQHtf"
    await ctx.send(info)
    await warn_broken(ctx)
