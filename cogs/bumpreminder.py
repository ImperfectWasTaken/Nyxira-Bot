import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
from datetime import datetime, timedelta

class BumpReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bump_file = "json\bum.json"
        self.check_pending_bump.start()

    def save_bump_time(self, timestamp: str):
        with open(self.bump_file, "w") as f:
            json.dump({"last_bump": timestamp}, f)

    def load_bump_time(self):
        try:
            with open(self.bump_file, "r") as f:
                data = json.load(f)
                if "last_bump" in data:
                    return datetime.fromisoformat(data["last_bump"])
                else:
                    return None
        except FileNotFoundError:
            return None
        


    @tasks.loop(seconds=60)
    async def check_pending_bump(self):
        last_bump_time = self.load_bump_time()
        if last_bump_time is None:
            return

        elapsed = datetime.now() - last_bump_time
        if elapsed.total_seconds() >= 5:
            channel = self.bot.get_channel(1377923706973585458)
            if channel:
                responseEmbed = discord.Embed(
                    title="It's bumping time!",
                    description="Use </bump:947088344167366698> to bump the server! 🎉",
                    color=0xde9cff
                )
                await channel.send("<@&1378468189377396846>")
                await channel.send(embed=responseEmbed)

            # Reset the timer so it doesnt trigger again until the next bump
            self.save_bump_time(datetime.now().isoformat())



    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        TARGET_BOT_ID = 301512451453616128
        TARGET_CHANNEL_ID = 1355193284913397780
        returnEmbed = discord.Embed(description="Come back to bump in 2 hours 🕒", color=0xffcc00)

        if message.author.id != TARGET_BOT_ID or message.channel.id != TARGET_CHANNEL_ID:
            return

        if not message.embeds:
            return

        embed = message.embeds[0]
        title = embed.title or "(no title)"

        if "hi" in title:
            now = datetime.now()
            self.save_bump_time(now.isoformat())
            await message.channel.send(embed=returnEmbed)

            # also start new countdown
            await asyncio.sleep(5)
            responseEmbed = discord.Embed(
                title="It's bumping time!",
                description="Use </bump:947088344167366698> to bump the server! 🎉",
                color=0xde9cff
            )
            await message.channel.send("<@&1378468189377396846>")
            await message.channel.send(embed=responseEmbed)

async def setup(bot):
    await bot.add_cog(BumpReminder(bot))