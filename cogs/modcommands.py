import discord
import json
import os
import asyncio
from datetime import datetime 
from discord import app_commands
from discord.ext import commands


LOG_FILE = "json\server_log_channels.json"
SCHEDULE_FILE = "json\scheduled_roles.json"
EVENTS_FILE = "json\live_streams.json"




def load_log_channels():
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_log_channels(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)








def load_schedules():
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_schedules(schedules):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedules, file, indent=4)








class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = load_log_channels()  

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.kick_members or await self.bot.is_owner(ctx.author)







    @app_commands.command(name="kick", description="Kicks a user from the server. ⭐")
    @app_commands.describe(member="The user to kick", reason="Reason for kicking")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} has been kicked.\n**Reason:** {reason}", ephemeral=True)



    @app_commands.command(name="ban", description="Bans a user from the server. ⭐")
    @app_commands.describe(member="The user to ban", reason="Reason for banning")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} has been banned.\n**Reason:** {reason}", ephemeral=True)



    @app_commands.command(name="unban", description="Unbans a user by their ID. ⭐")
    @app_commands.describe(user_id="The ID of the user to unban")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user_id = int(user_id)
        except ValueError:
            await interaction.response.send_message("The user ID must be a valid integer.", ephemeral=True)
            return
        
        guild = interaction.guild

        # Collect banned users by iterating over the async generator
        banned_users = []
        async for entry in guild.bans():
            banned_users.append(entry.user)
        
        # Search for the user in the banned list
        user = discord.utils.get(banned_users, id=user_id)

        if user:
            await guild.unban(user)
            await interaction.response.send_message(f"Unbanned {user.name}.")
        else:
            await interaction.response.send_message(f"No user found with the ID {user_id}.")



    @app_commands.command(name="mute", description="Mutes a user in the server. ⭐")
    @app_commands.describe(member="The user to mute", duration="Duration (e.g., 10m, 1h)", reason="Reason for muting")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        duration_seconds = self.parse_time(duration)
        if duration_seconds is None:
            await interaction.response.send_message("⚠ Invalid duration format. Use (e.g., `10m`, `1h`).", ephemeral=True)
            return

        await member.timeout(discord.utils.utcnow() + discord.timedelta(seconds=duration_seconds), reason=reason)
        await interaction.response.send_message(f"🔇 {member.mention} has been muted for {duration}.\n**Reason:** {reason}", ephemeral=True)



    @app_commands.command(name="unmute", description="Unmutes a user in the server. ⭐")
    @app_commands.describe(member="The user to unmute")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(f"✅ {member.mention} has been unmuted.", ephemeral=True)



    @app_commands.command(name="clear", description="Deletes a specified number of messages. ⭐")
    @app_commands.describe(amount="The number of messages to delete")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)

        if amount <= 0:
            return await interaction.followup.send("❌ Please enter a number greater than 0.", ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Deleted **{len(deleted)}** messages.", ephemeral=True)





    def parse_time(self, duration: str):
        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            unit = duration[-1].lower()
            if unit in time_units:
                return int(duration[:-1]) * time_units[unit]
        except ValueError:
            return None


    @app_commands.command(name="createembed", description="Creates an embedded message for the bot to send ⭐")
    @app_commands.describe(color_code="Hex code for the color of the embed")
    @app_commands.describe(below_embed="Any messages or pings below the embed")
    @app_commands.describe(channel="The channel you want this to be sent in")
    @app_commands.default_permissions(manage_messages=True)
    async def createembed(self, interaction: discord.Interaction, title: str, content: str, below_embed: str = None, color_code: str = None, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel

        await interaction.response.send_message("Creating embed...", ephemeral=True)

        if color_code is None:
            embed = discord.Embed(title=title, description=content, color=0xfcba03)
        else:
            embed = discord.Embed(title=title, description=content, color=int(color_code, 16))

        await interaction.delete_original_response()
        
        if below_embed is None:
            await channel.send(embed=embed)
        else:
            await channel.send(embed=embed)
            await channel.send(content=below_embed)






    @app_commands.command(name="random-color-role", description="Schedule a role to change random colors ⭐")
    @app_commands.describe(role="The role to change colors", time="Time in HH:MM AM/PM format (e.g., 1:30 PM)")
    async def colorrole(self, interaction: discord.Interaction, role: discord.Role, time: str):
        
        # Convert 12 hour time to 24 hour format
        try:
            dt = datetime.strptime(time, "%I:%M %p")  # Parses 12 hour format
            hour, minute = dt.hour, dt.minute  # Extracts 24hour values
        except ValueError:
            await interaction.response.send_message("❌ Invalid time format! Use `HH:MM AM/PM` (e.g., `1:30 PM`).", ephemeral=True)
            return

        role_changer = self.bot.get_cog("RoleColorChanger")
        if role_changer is None:
            await interaction.response.send_message("❌ Role color changer system is not loaded.", ephemeral=True)
            return

        await role_changer.schedule_role_color_change(role, hour, minute)

        embed = discord.Embed(description=f"✅ {role.mention} will now change color daily at {time} EST")
        await interaction.response.send_message(embed=embed)




    @app_commands.command(name="setlogchannel", description="Set the log channel ⭐")
    @app_commands.default_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.log_channels[str(interaction.guild.id)] = channel.id
        save_log_channels(self.log_channels)
        await interaction.response.send_message(f"✅ Log channel set to {channel.mention}")





async def setup(bot):
    await bot.add_cog(ModCommands(bot))
