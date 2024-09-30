import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from datetime import datetime
from typing import Optional

from model.MyTrainer import MyTrainer
from src.type import ModelType
from src.utils import SwitchManager

LABEL_MAP = [ModelType.Dangerous.value, ModelType.Harassment.value, ModelType.Hate_Speech.value, ModelType.Sexually.value]
REASON = {ModelType.Dangerous.value: "危險言論", ModelType.Harassment.value: "騷擾言論", ModelType.Hate_Speech.value: "仇恨言論", ModelType.Sexually.value: "淫穢言論"}
class Filter(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        print("Fliter Cog Loaded")
        self.bot = bot
        self.switch = SwitchManager()
        self.trainer = MyTrainer(4)
        self.trainer.load('weights/myModel.pth')

    @commands.hybrid_command()
    @app_commands.choices(
        index = [
            Choice(name="Dangerous", value=ModelType.Dangerous.value),
            Choice(name="Harassment", value=ModelType.Harassment.value),
            Choice(name="Hate", value=ModelType.Hate_Speech.value),
            Choice(name="Sexually", value=ModelType.Sexually.value)
        ]
    )
    async def set_senstive(self, ctx: commands.Context, index: Choice[str], value: float):
        self.switch.set_threshold(ctx.guild.id, index.value, value)
        await ctx.send(f'Set {index.value} to {value}')

    @commands.hybrid_command()
    async def get_senstive_setting(self, ctx: commands.Context):
        msg = [f'{label}: {self.switch.get_threshold(ctx.guild.id, label)}' for label in LABEL_MAP]
        await ctx.send('\n'.join(msg))
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if (not self.switch.is_open(message.guild.id, message.channel.id)):
            return
        result = self.trainer.inference(message.content)
        reasons = []
        for i, label in enumerate(LABEL_MAP):
            if self.switch.get_switch(message.guild.id, message.channel.id, label) and result[i] >= self.switch.get_threshold(message.guild.id, label):
                reasons.append(REASON[label])
        if (len(reasons) > 0):
            await message.delete()
            embed=discord.Embed(description=f"已刪除 {message.author.mention} 的訊息", color=0xf70202)
            embed.add_field(name="違規內容", value=f"涉及 {reasons}", inline=True)
            embed.set_footer(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            await message.channel.send(embed=embed)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Filter(bot))