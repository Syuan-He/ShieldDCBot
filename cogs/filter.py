import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from model.MyTrainer import MyTrainer

LABEL_MAP = ["Dangerous", "Harassment", "Hate", "Sexually"]

class Filter(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        print("Fliter Cog Loaded")
        self.bot = bot
        self.senstive = {"Dangerous":0.5, "Harassment": 0.5, "Hate": 0.5, "Sexually": 0.5}
        self.switch = {"Dangerous":True, "Harassment": True, "Hate": True, "Sexually": True}
        self.trainer = MyTrainer(4)
        self.trainer.load('weights/myModel.pth')

    @commands.hybrid_command()
    @app_commands.choices(
        index = [
            Choice(name="Dangerous", value="Dangerous"),
            Choice(name="Harassment", value="Harassment"),
            Choice(name="Hate", value="Hate"),
            Choice(name="Sexually", value="Sexually")
        ]
    )
    async def set_senstive(self, ctx, index: Choice[str], value: float):
        self.senstive[index.value] = value
        await ctx.send(f'Set {index.value} to {value}')

    @commands.hybrid_command()
    async def get_senstive_setting(self, ctx):
        msg = [f'{label}: {self.senstive[label]}' for label in LABEL_MAP]
        await ctx.send('\n'.join(msg))
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        result = self.trainer.inference(message.content)
        for i, label in enumerate(LABEL_MAP):
            if self.switch[label] and result[i] >= self.senstive[label]:
                await message.delete()
                await message.channel.send(label, delete_after=3)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Filter(bot))