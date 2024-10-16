import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from model.MyTrainer import MyTrainer

LABEL_MAP = ["Dangerous", "Harassment", "Hate", "Sexually"]

class Filter(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        print("Filter Cog Loaded")
        self.bot = bot
        self.senstive = {"Dangerous": 0.5, "Harassment": 0.5, "Hate": 0.5, "Sexually": 0.5}
        self.trainer = MyTrainer(4)
        self.trainer.load('weights/myModel.pth')

        self.channel_filter_status = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.channel_filter_status[channel.id] = {label: True for label in LABEL_MAP}
        print("所有頻道的過濾功能已啟用")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.TextChannel):
            self.channel_filter_status[channel.id] = {label: True for label in LABEL_MAP}
            print(f"新頻道 {channel.name} 的過濾功能已啟用")

    @commands.hybrid_command()
    @app_commands.choices(
        status=[
            Choice(name="開啟", value="on"),
            Choice(name="關閉", value="off")
        ]
    )
    async def set_filter_channel(self, ctx, channel: discord.TextChannel, status: Choice[str]):
        if channel.id not in self.channel_filter_status:
            self.channel_filter_status[channel.id] = {label: True for label in LABEL_MAP}

        new_status = (status.value == "on")
        for label in LABEL_MAP:
            self.channel_filter_status[channel.id][label] = new_status

        status_text = "開啟" if new_status else "關閉"

        embed = discord.Embed(
            title="過濾狀態已更新",
            description=f"已將頻道 {channel.mention} 的所有過濾設為「{status_text}」",
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.choices(
        category=[Choice(name=label, value=label) for label in LABEL_MAP],
        status=[
            Choice(name="開啟", value="on"),
            Choice(name="關閉", value="off")
        ]
    )
    async def set_filter_category(self, ctx, channel: discord.TextChannel, category: Choice[str], status: Choice[str]):
        if channel.id not in self.channel_filter_status:
            self.channel_filter_status[channel.id] = {label: True for label in LABEL_MAP}

        self.channel_filter_status[channel.id][category.value] = (status.value == "on")
        status_text = "開啟" if status.value == "on" else "關閉"

        embed = discord.Embed(
            title="過濾類別狀態已更新",
            description=f"已將頻道 {channel.mention} 的「{category.value}」過濾設為「{status_text}」",
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def get_filter_setting(self, ctx):
        embed = discord.Embed(
            title="當前過濾器限制",
            description="顯示當前伺服器所有頻道的狀態",
            color=discord.Color.green()
        )

        guild_channels = ctx.guild.text_channels

        if not guild_channels:
            embed.add_field(name="没有频道", value="當前服務器沒有文本頻道", inline=False)
        else:
            for channel in guild_channels:
                channel_id = channel.id
                if channel_id not in self.channel_filter_status:
                    self.channel_filter_status[channel_id] = {label: True for label in LABEL_MAP}

                categories = self.channel_filter_status[channel_id]
                channel_mention = channel.mention
                status_lines = []
                for label, status in categories.items():
                    status_text = "開啟" if status else "關閉"
                    status_lines.append(f"{label}: {status_text}")
                embed.add_field(name=f"频道: {channel_mention}", value="\n".join(status_lines), inline=False)

        await ctx.send(embed=embed)


    @commands.hybrid_command()
    @app_commands.choices(
        index=[Choice(name=label, value=label) for label in LABEL_MAP]
    )
    async def set_senstive(self, ctx, index: Choice[str], value: float):
        self.senstive[index.value] = value

        embed = discord.Embed(
            title="敏感度已更新",
            description=f"敏感度設定已更新",
            color=discord.Color.blue()
        )

        embed.add_field(name="分類", value=f"{index.value}", inline=True)
        embed.add_field(name="新敏感度", value=f"{value}", inline=True)

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def get_senstive_setting(self, ctx):
        embed = discord.Embed(
            title="當前敏感度設定",
            description="顯示所有分類的敏感度設定",
            color=discord.Color.green()
        )

        for i, label in enumerate(LABEL_MAP):
            inline = (i % 2 == 0)
            embed.add_field(name=label, value=str(self.senstive[label]), inline=inline)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if message.channel.id not in self.channel_filter_status:
            self.channel_filter_status[message.channel.id] = {label: True for label in LABEL_MAP}

        channel_settings = self.channel_filter_status[message.channel.id]

        result = self.trainer.inference(message.content)
        for i, label in enumerate(LABEL_MAP):
            if channel_settings[label] and result[i] >= self.senstive[label]:
                await message.delete()

                embed = discord.Embed(
                    title="已刪除訊息",
                    description=f"已刪除 {message.author.mention} 的訊息",
                    color=discord.Color.red(),
                    timestamp=message.created_at
                )
                embed.add_field(name="違規內容", value=f"涉及「{label}言論」", inline=False)

                await message.channel.send(embed=embed)
                break

async def setup(bot: commands.Bot):
    await bot.add_cog(Filter(bot))
