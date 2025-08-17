import json
import os
import discord
import sys
from datetime import datetime
from discord import app_commands
from discord.ext import commands

STATS_FILE = "json/stats.json"


def load_stats():
    default_stats = {
        "messages_processed": 0,
        "interaction_commands_executed": 0
    }


    with open(STATS_FILE, "r") as f:
        stats = json.load(f)

    for key, value in default_stats.items():
        if key not in stats:
            stats[key] = value

    return stats

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)











class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = datetime.now()
        self.bot.stats = load_stats()

    @app_commands.command(name="botinfo", description="Displays bot information")
    async def info(self, interaction: discord.Interaction):

        # Set bot's start time
        uptime_seconds = (datetime.now() - self.bot.launch_time).total_seconds()
        formatted_uptime = f"{int(uptime_seconds // 3600):02}:{int((uptime_seconds % 3600) // 60):02}:{int(uptime_seconds % 60):02}"

        py_version = sys.version.split()[0]
        
        # Format the uptime
        latency = round(self.bot.latency * 1000)

        app_info = await self.bot.application_info()
        ownerID = app_info.owner.id
        nyxiraBannerPath = r"C:\Users\Mason C\Downloads\Nyxira-1.0\images\nyxiraBannerCentered.png"
        bannerFile = discord.File(nyxiraBannerPath, filename="nyxiraBanner.png")
        
        infoEmbed = discord.Embed(color=0xff0c0d)
        infoEmbed.set_author(name=f"{self.bot.user.name}", icon_url=self.bot.user.avatar.url)
        infoEmbed.add_field(name="Version ⚙️", value="1.0", inline=True)
        infoEmbed.add_field(name="Python 🐍", value=f"{py_version}", inline=True)
        infoEmbed.add_field(name="Library 📖", value="[discord.py](https://github.com/Rapptz/discord.py)", inline=True)
        infoEmbed.add_field(name="Latency 🛜", value=f"{latency} ms", inline=True)
        infoEmbed.add_field(name="Messages Processed 📄", value=f"{self.bot.stats['messages_processed']}", inline=True)
        infoEmbed.add_field(name="Commands Executed 🛠️", value=f"{self.bot.stats['interaction_commands_executed']}", inline=True)
        infoEmbed.add_field(name="Uptime 🕒", value=f"{formatted_uptime}", inline=True)
        infoEmbed.add_field(name="Developer 🧑‍💻", value=f"<@{ownerID}>", inline=True)
        infoEmbed.set_footer(text="This bot is still under construction! 🚧")
        infoEmbed.set_image(url=f"attachment://nyxiraBanner.png")

        if self.bot.user.avatar:
            infoEmbed.set_author(name=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar.url)
        else:
            infoEmbed.set_author(name=f"{self.bot.user.name}#{self.bot.user.discriminator}")

        await interaction.response.send_message(embed=infoEmbed, file=bannerFile)



    @app_commands.command(name="serverinfo", description="Displays information about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"🌍 Server Info",
            color=0xff0c0d,
            timestamp=interaction.created_at
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Created On", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="userinfo", description="Displays information about a user.")
    @app_commands.describe(member="The user you want information on")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(
            title=f"👤 User Info",
            color=member.color,
            timestamp=interaction.created_at
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Username", value=member, inline=True)
        embed.add_field(name="Mention", value=member.mention, inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Roles", value=", ".join([role.mention for role in member.roles if role != interaction.guild.default_role]) or "None", inline=False)
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="channelinfo", description="Displays information about the current channel.")
    async def channelinfo(self, interaction: discord.Interaction):
        channel = interaction.channel
        embed = discord.Embed(
            title=f"📢 Channel Info",
            color=0xff0c0d,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Channel ID", value=channel.id, inline=True)
        embed.add_field(name="Category", value=channel.category.name if channel.category else "None", inline=True)
        embed.add_field(name="Channel Type", value=str(channel.type).title(), inline=True)
        embed.add_field(name="Created On", value=channel.created_at.strftime("%B %d, %Y"), inline=True)
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="roleinfo", description="Displays information about a specific role.")
    @app_commands.describe(role="The role you want information on")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        embed = discord.Embed(
            title=f"🏷️ Role Info",
            color=role.color,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Role ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Created On", value=role.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
