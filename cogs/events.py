import discord
import os
import json
import io
import aiohttp
import time
import requests
import asyncio
from discord.ext import commands, tasks
from cogs.stats import load_stats, save_stats
from datetime import datetime
from dotenv import load_dotenv

LOG_FILE = "json/server_log_channels.json"

def load_log_channels():
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r") as f:
        return json.load(f)
    





class InviteDeleteView(discord.ui.View):
    def __init__(self, invite, embed, message):
        super().__init__(timeout=None)
        self.invite = invite
        self.embed = embed
        self.message = message

    @discord.ui.button(label="Delete Invite", style=discord.ButtonStyle.danger)
    async def delete_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return

        try:
            await self.invite.delete()

            # updtae embed to reflect deletion
            self.embed.color = discord.Color.red()
            self.embed.set_field_at(0, name="Status", value=f"🔴 **Invite Deleted** `@` {datetime.now().strftime('%m-%d %I:%M %p')}", inline=False)

            for child in self.children:
                child.disabled = True

            await self.message.edit(embed=self.embed, view=self)
            await interaction.response.defer()
            self.stop()
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass



class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verified_role_id = 1137277669445206036
        self.ban_announcement_channel_id = 7587736469776630274
        self.log_channels = load_log_channels()

    def get_log_channel(self, guild: discord.Guild):
        """Retrieve the log channel for a guild."""
        if not guild:
            return None

        channel_id = self.log_channels.get(str(guild.id))
        return self.bot.get_channel(channel_id) if channel_id else None

    # ------------------ Member Join/Leave Events ------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        log_channel = self.get_log_channel(member.guild)
        if not log_channel:
            return

        verified_role = discord.Object(id=self.verified_role_id)
        await member.add_roles(verified_role)

        embed = discord.Embed(
            title="Member Joined",
            description=f"{member.mention} ({member}) has joined the server.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"User ID: {member.id}")
        embed.set_thumbnail(url=member.display_avatar.url)

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        log_channel = self.get_log_channel(member.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Member Left",
            description=f"{member.mention} ({member}) has left the server.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"User ID: {member.id}")
        embed.set_thumbnail(url=member.display_avatar.url)

        await log_channel.send(embed=embed)

    # ------------------ Message Events ------------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):


        unfocused = 301512451453616128
        unfocusedKeywords = ["hi"]
        #responseMessage = "<@&1283543487190405160>"
        responseEmbed = discord.Embed(title="It's booping time!", description="Use </boop:1140024685845823650> to boop the server! 🎉", color=0xde9cff)
        returnEmbed = discord.Embed(description="Come back to boop in 2 hours 🕒", color=0xffcc00)


        if message.author.id == unfocused:
            if any(keyword in message.content.lower() for keyword in unfocusedKeywords):
                await message.channel.send(embed=returnEmbed)
                await asyncio.sleep(20)
                #await message.channel.send(responseMessage)
                await message.channel.send(embed=responseEmbed)

        if message.mention_everyone:
            return
        if message.author.bot:
            return
        self.bot.stats = getattr(self.bot, "stats", load_stats())
        self.bot.stats["messages_processed"] = self.bot.stats.get("messages_processed", 0) + 1
        save_stats(self.bot.stats)
        
        await self.bot.process_commands(message)


    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        self.bot.stats = self.bot.stats if hasattr(self.bot, "stats") else load_stats()
        self.bot.stats["interaction_commands_executed"] = self.bot.stats.get("interaction_commands_executed", 0) + 1
        save_stats(self.bot.stats)


    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content:
            return

        log_channel = self.get_log_channel(before.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Message Edited",
            description=f"**Author:** {before.author.mention} ({before.author})\n"
                        f"**Channel:** {before.channel.mention}",
            color=discord.Color.yellow(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Before:", value=before.content[:1000], inline=False)
        embed.add_field(name="After:", value=after.content[:1000], inline=False)
        embed.set_footer(text=f"Message ID: {before.id}")

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        log_channel = self.get_log_channel(message.guild)
        if not log_channel:
            return

        # Process text message logging
        if message.content:
            text_embed = discord.Embed(
                description=f"**Message by {message.author.mention} deleted in {message.channel.mention}**\n{message.content}",
                timestamp=datetime.now(),
                color=0xff2222,
            )
            text_embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            text_embed.set_footer(text=f"Author ID: {message.author.id} | Message ID: {message.id}")

            await log_channel.send(embed=text_embed)

        # Process attachments
        files = []
        image_embeds = []

        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    # Create a new embed for each image
                    embed = discord.Embed(
                        description=f"**Message by {message.author.mention} deleted in {message.channel.mention}**",
                        timestamp=datetime.now(),
                        color=0xff2222,
                    )
                    embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                    embed.set_footer(text=f"Author ID: {message.author.id} | Message ID: {message.id}")

                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:
                            if resp.status == 200:
                                file_data = await resp.read()
                                file = discord.File(io.BytesIO(file_data), filename=attachment.filename)
                                embed.set_image(url=f"attachment://{attachment.filename}")

                                image_embeds.append((embed, file))

                else:
                    # Handle non image attachments
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:
                            if resp.status == 200:
                                file_data = await resp.read()
                                file = discord.File(io.BytesIO(file_data), filename=attachment.filename)
                                files.append(file)

        for embed, file in image_embeds:
            await log_channel.send(embed=embed, file=file)

        if files:
            await log_channel.send(files=files)
    

    # ------------------ Ban/Unban Events ------------------

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        log_channel = self.get_log_channel(guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Member Banned",
            description=f"{member.mention} ({member}) was banned.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"User ID: {member.id}")
        embed.set_thumbnail(url=member.display_avatar.url)

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        log_channel = self.get_log_channel(guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Member Unbanned",
            description=f"{user.mention} ({user}) was unbanned.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"User ID: {user.id}")

        await log_channel.send(embed=embed)

    # ------------------ Role Events ------------------

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        log_channel = self.get_log_channel(role.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Role Created",
            description=f"**Role:** {role.mention} ({role.name})",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Role ID: {role.id}")

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        log_channel = self.get_log_channel(role.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Role Deleted",
            description=f"**Role:** {role.name}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Role ID: {role.id}")

        await log_channel.send(embed=embed)

    # ------------------ Voice Channel Events ------------------

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log_channel = self.get_log_channel(member.guild)
        if not log_channel:
            return

        if before.channel != after.channel:
            if after.channel:
                description = f"{member.mention} joined {after.channel.mention}"
            else:
                description = f"{member.mention} left {before.channel.mention}"

            embed = discord.Embed(
                title="Voice Channel Update",
                description=description,
                color=discord.Color.yellow(),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"User ID: {member.id}")

            await log_channel.send(embed=embed)

    # ------------------ Invite Events ------------------

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        log_channel = self.get_log_channel(invite.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Invite Created",
            description=f"**Inviter:** {invite.inviter.mention}\n"
                        f"**URL:** {invite.url}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Status", value="🟢 **Invite Active**", inline=False)

        message = await log_channel.send(embed=embed)
        view = InviteDeleteView(invite, embed, message)
        await message.edit(view=view)







load_dotenv()


TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Split the channels string into a list
TWITCH_CHANNELS = os.getenv("TWITCH_CHANNELS").split(",")

TWITCH_TOKEN_URL = os.getenv("TWITCH_TOKEN_URL")
TWITCH_STREAMS_URL = os.getenv("TWITCH_STREAMS_URL")

STREAMS_FILE = "json/live_streams.json"





def load_live_streams():
    if os.path.exists(STREAMS_FILE):
        with open(STREAMS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_live_streams(data):
    with open(STREAMS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class TwitchNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live_streams = load_live_streams()  # Load from JSON on startup
        self.twitch_headers = self.get_twitch_headers()
        self.check_twitch.start()
        self.twitch_logo_url = "https://i.imgur.com/V4j59Ad.png"

    def get_twitch_headers(self):
        response = requests.post(TWITCH_TOKEN_URL, {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        })
        data = response.json()
        return {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {data['access_token']}"
        }

    async def get_profile_image(self, twitch_username):
        user_url = f"https://api.twitch.tv/helix/users?login={twitch_username}"
        async with aiohttp.ClientSession() as session:
            async with session.get(user_url, headers=self.twitch_headers) as response:
                if response.status != 200:
                    print(f"Error fetching profile image: {response.status}, {await response.text()}")
                    return None
                user_data = await response.json()
                return user_data.get("data", [{}])[0].get("profile_image_url", None)

    @tasks.loop(minutes=1)
    async def check_twitch(self):
        if not TWITCH_CHANNELS:
            return

        query = "&user_login=".join(TWITCH_CHANNELS)
        url = f"{TWITCH_STREAMS_URL}?user_login={query}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.twitch_headers) as response:
                if response.status != 200:
                    print(f"Twitch API Error: {response.status}, {await response.text()}")
                    return

                data = (await response.json()).get("data", [])

        currently_live = set()

        # Check for online streamers
        for stream in data:
            twitch_username = stream["user_login"]
            twitch_display_name = stream["user_name"]
            game_name = stream.get("game_name", "Unknown Game")
            viewer_count = stream.get("viewer_count", 0)
            stream_title = stream.get("title", "No title available")
            stream_thumbnail = stream.get("thumbnail_url", "").replace("{width}x{height}", "400x225")
            stream_thumbnail += f"?t={int(time.time())}"

            currently_live.add(twitch_username)

            # If the streamer is not in live_streams, add them
            # If the streamer is not in live_streams OR message hasn't been sent yet
            if twitch_username not in self.live_streams or self.live_streams[twitch_username].get("message_id") is None:
                profile_image_url = await self.get_profile_image(twitch_username)

                # If not already stored, create entry
                if twitch_username not in self.live_streams:
                    self.live_streams[twitch_username] = {
                        "message_id": None,
                        "last_title": stream_title,
                        "profile_image": profile_image_url,
                        "display_name": twitch_display_name
                    }

                channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
                if channel:
                    embed = discord.Embed(
                        description=f"## **[{twitch_display_name}]({f'https://www.twitch.tv/{twitch_username}'})** is now live!\n{stream_title}",
                        color=0x9146ff,
                        timestamp=datetime.now()
                    )

                    embed.add_field(name="Game 🎮", value=game_name, inline=True)
                    embed.add_field(name="Current Viewers 👥", value=viewer_count, inline=True)
                    embed.set_image(url=stream_thumbnail)
                    embed.set_thumbnail(url=profile_image_url)
                    embed.set_footer(text="Started Streaming")
                    embed.set_author(name="Streaming on Twitch!", icon_url=self.twitch_logo_url)

                    message = await channel.send(embed=embed)

                    self.live_streams[twitch_username]["message_id"] = message.id
                    self.live_streams[twitch_username]["start_time"] = datetime.now().isoformat()

                    save_live_streams(self.live_streams)


            else:
                # Update stream data for live streamers
                stored_stream = self.live_streams[twitch_username]
                current_title = stored_stream.get("last_title", "")
                last_viewer_count = stored_stream.get("last_viewer_count", 0)

                if stream_title != current_title or last_viewer_count != viewer_count:
                    # Update the stored values
                    stored_stream["last_title"] = stream_title
                    stored_stream["last_viewer_count"] = viewer_count

                    channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
                    message_id = stored_stream.get("message_id")
                    if channel and message_id:
                        try:
                            message = await channel.fetch_message(message_id)
                            embed = message.embeds[0]

                            # Update the fields with the latets data
                            embed.description = f"## **[{twitch_display_name}]({f'https://www.twitch.tv/{twitch_username}'})** is now live!\n{stream_title}"
                            embed.clear_fields()
                            embed.add_field(name="Game 🎮", value=game_name, inline=True)
                            embed.add_field(name="Current Viewers 👥", value=viewer_count, inline=True)
                            embed.set_image(url=stream_thumbnail)

                            embed.set_footer(text="Started Streaming")

                            await message.edit(embed=embed)

                        except discord.NotFound:
                            print(f"Message {message_id} not found for {twitch_username}, removing from tracking.")

            save_live_streams(self.live_streams)

        # Detect offline users
        offline_users = [username for username in self.live_streams.keys() if username not in currently_live]

        for username in offline_users:
            stream_data = self.live_streams.get(username)
            if not stream_data:
                continue

            channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
            message_id = stream_data.get("message_id")
            start_time = stream_data.get("start_time", None)
            twitch_display_name = stream_data.get("display_name", username)

            del self.live_streams[username]  # Remove before attempting edits

            try:
                message = await channel.fetch_message(message_id)
                embed = message.embeds[0]

                # Calculate stream duration
                if start_time:
                    start_time = datetime.fromisoformat(start_time)
                    stream_duration = datetime.now() - start_time
                    hours, remainder = divmod(stream_duration.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                else:
                    duration_str = "Unknown"

                if "Stream has ended" in embed.description:
                    continue  # Avoid stupid updates

                embed.url = None  # Remove twitch link
                embed.title = None
                embed.description = f"## **[{twitch_display_name}]({f'https://www.twitch.tv/{username}'})** was live.\nStream has ended.\n**Duration:** {duration_str}"
                embed.color = 0x9146ff
                embed.clear_fields()
                embed.set_image(url=None)
                embed.set_footer(text=f"Started Stream")
                embed.set_author(name="Streamed on Twitch!", icon_url="https://i.imgur.com/V4j59Ad.png")

                await message.edit(embed=embed)

            except discord.NotFound:
                print(f"Message {message_id} not found for {username}, removing from tracking.")

        save_live_streams(self.live_streams)


async def setup(bot):
    await bot.add_cog(Events(bot))
    await bot.add_cog(TwitchNotifier(bot))
