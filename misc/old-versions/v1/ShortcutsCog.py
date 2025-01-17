info = 'Tools Shortcuts Commands Extension v1.2a'

import discord
from discord.ext import commands
from checks import *

sheetC = websiteC = 0

class ShortcutsCog(commands.Cog, name = 'Tool Shortcuts Commands'):
    def __init__(self, bot):
        self.bot = bot
        print(f'Loaded {info}!')

    '''
    Public use:
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    $website|tools|web
    $spreadsheet|excel|sheet
    '''

    @commands.command(aliases = ['tools', 'web'], help="Links to Scuderia's AM4 Tools Website", usage='$web|website|tools')
    @notPriceAlert()
    @notDM()
    async def website(self, ctx):
        global websiteC
        websiteC += 1
        await ctx.send(f"Here's the link to the AM4 Tools Website, created by Scuderia Airlines:\nhttps://am4tools.com")

    @commands.command(aliases = ['excel', 'sheet'], help='Links to the AM4 AC Spreadsheet', usage='$sheet|spreadsheet|excel')
    @notPriceAlert()
    @notDM()
    async def spreadsheet(self, ctx):
        await ctx.send(f'''Here's a link to all to all AC shortnames. They are to be used in almost all commands:
https://docs.google.com/spreadsheets/d/1xoEtXi4qibjyTHq05vh0frzWXLKXiAvXulAUB-zUW0M/edit#gid=0
To automatically search for aircraft abbreviations, use `$search`.
''')

async def setup(bot):
    await bot.add_cog(ShortcutsCog(bot))