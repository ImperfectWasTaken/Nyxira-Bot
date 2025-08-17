import discord
import datetime
import randfacts
import aiohttp
import os
import json
import random
import spotipy
import colorsys
import requests
import io
import re
from PIL import Image, ImageDraw, ImageFont
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from dadjokes import Dadjoke
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from dotenv import load_dotenv




load_dotenv()


TRACK_LOG_FILE = "json/added_songs.json"



class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_file = "json/ow_role_queue.json"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("client_id"),
            client_secret=os.getenv("client_secret"),
            redirect_uri=os.getenv("redirect_uri"),
            scope="playlist-modify-public"
        ))
        self.playlist_id = "2e8ewMesew3AlAh3X54skb"

        if not os.path.isfile(TRACK_LOG_FILE):
            with open(TRACK_LOG_FILE, "w") as f:
                json.dump({}, f, indent=4)



    @app_commands.command(name="randomfact", description="Get a random yet, interesting fact")
    async def randomfact(self, interaction: discord.Interaction):
        randfact = randfacts.get_fact()
        embed = discord.Embed(title=randfact, description="", color=0xff0c0d)
        await interaction.response.send_message(embed=embed)




    @app_commands.command(name="dadjoke", description="Tells a dad joke")
    async def dadjoked(self, interaction: discord.Interaction):
        dadjoke = Dadjoke()
        embed = discord.Embed(title=dadjoke.joke, description="", color=0xff0c0d)
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name = "stinkrate", description = "Rates you or a users stinkiness")
    async def stinkychance(self, interaction: discord.Interaction, member: str):
        percentage = (random.randint(0, 100))
        if percentage == 0:
            await interaction.response.send_message(f"{member} has a **{percentage}/100** stinky rating, squeaky clean mf 🧼🫧")
        elif percentage <= 20:
            await interaction.response.send_message(f"{member} has a **{percentage}/100** stinky rating, smells like, nothing? Ig?")
        elif percentage <= 50:
            await interaction.response.send_message(f"{member} has quite a stench on them, with a **{percentage}/100** stinky rating. I'd recommend taking a shower pronto 🚿")
        elif percentage <= 80:
            await interaction.response.send_message(f"{member} is starting to smell putrid, with a **{percentage}/100** stinky rating. You musty dusty crusty person, it's been **MONTHS** since you've cleaned yourself, what are you even doing?")
        elif percentage <= 99:
            await interaction.response.send_message(f"🤢 {member} has such an abhorent stench to them holyyy, with a **{percentage}/100** stinky rating going for them. You'd be considered biohazard waste with the amount of my nostril hairs that are burning from your chemically corroded smelly self")
        elif percentage == 100:
            await interaction.response.send_message(f"🤮 EVERYONE STAY AWAY FROM {member}, THEY HAVE A **{percentage}/100** STINKY RATING AAHHHHH. RUN FROM THEM, THEY'RE AN AMALGAMATION OF ALL THINGS STINKY")
        else:
            await interaction.response.send_message(f"You're so stinky you broke the command, good job")



    def load_json(self, file_path):
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


    @app_commands.command(name="randomowcharacter", description="Generates a random overwatch character")
    @app_commands.describe(amount="Choose the amount of characters to generate (Max: 5)")
    async def randomOWcharacter(self, interaction: discord.Interaction, amount: int):
        data = self.load_json(self.roles_file)
        
        # Define role emojis
        role_emojis = {
            "tank": "<:Tank:1349762410600202352>",
            "damage": "<:Damage:1349762380321656874>",
            "support": "<:Support:1349762397786607666>"
        }

        character_emojis = {char: role_emojis["tank"] for char in data.get("tank", [])}
        character_emojis.update({char: role_emojis["damage"] for char in data.get("damage", [])})
        character_emojis.update({char: role_emojis["support"] for char in data.get("support", [])})

        characters = list(character_emojis.keys())

        app_info = await self.bot.application_info()
        ownerID = app_info.owner.id

        if not characters:
            await interaction.response.send_message(f"❌ Character list is missing or corrupted! (Contact <@{ownerID}>)", ephemeral=True)
            return

        if amount > 5:
            await interaction.response.send_message("⚠️ You cannot select a number higher than 5!", ephemeral=True)
            return

        selected = random.sample(characters, min(amount, len(characters)))

        # Format response with correct emoji
        response = "\n".join(f"# {character_emojis[char]}  **{char}**" for char in selected)

        await interaction.response.send_message(response)











    def get_roles(self):
        try:
            with open(self.roles_file, encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "tank": data.get("tank", []),
                    "damage": data.get("damage", []),
                    "support": data.get("support", [])
                }
        except (FileNotFoundError, json.JSONDecodeError):
            return {"tank": [], "damage": [], "support": []}
        

    @app_commands.command(name="randomrolequeue", description="Generates a Random team for overwatch role queue")
    async def randomrolequeue(self, interaction: discord.Interaction):
        roles = self.get_roles()

        if not roles["tank"] or len(roles["damage"]) < 2 or len(roles["support"]) < 2:
            await interaction.response.send_message("❌ Role queue data is missing or corrupted!", ephemeral=True)
            return

        selected_team = {
            "tank1": None,
            "tank2": None,
            "damage1": None,
            "damage2": None,
            "support1": None,
            "support2": None
        }

        selected_team["tank1"], selected_team["tank2"] = random.sample(roles["tank"], 2)
        selected_team["damage1"], selected_team["damage2"] = random.sample(roles["damage"], 2)
        selected_team["support1"], selected_team["support2"] = random.sample(roles["support"], 2)

        response = (
            f"# <:Tank:1349762410600202352> **Tank 1**: {selected_team['tank1']}\n"
            f"# <:Tank:1349762410600202352> **Tank 2**: {selected_team['tank2']}\n"
            f"# <:Damage:1349762380321656874> **Damage 1**: {selected_team['damage1']}\n"
            f"# <:Damage:1349762380321656874> **Damage 2**: {selected_team['damage2']}\n"
            f"# <:Support:1349762397786607666> **Support 1**: {selected_team['support1']}\n"
            f"# <:Support:1349762397786607666> **Support 2**: {selected_team['support2']}"
        )

        await interaction.response.send_message(response)














    @app_commands.command(name="randomsong", description="Random song from my playlists")
    async def playlistrandom(self, interaction: discord.Interaction):
        await interaction.response.send_message("Generating random song...", ephemeral=True)

        PLAYLIST_IDS = [
            "0gj2xlGWjXi91kwXpNC5uB",
            "0VoBSoJLIHjjh3nAvmtjwE",
            "1ZBQrO8KkyLR1NYIsGlmX2",
            "3squE6DbohtP5J9Zv7DYpP",
            "3MbMawwh3KgubVGoUREFi2",
            "0LLThk9H98R0K6V7Il7ywC",
            "3I5imHdRJOVdYtDS6VFJCR",
            "1UxVuim5Y3NPJFgmfBvQmu",
            "684AaYjZD1iXpMJBXQ4B1R",
            "0zYwQlI1XwEDjLL7ahAtAa",
            "3BBhqfrZcGEh5p4zkhUmw9",
            "1Pa6xEjM25E2thiBzKdS2q",
            "2Lflr08zmbYFWnVBaoTRPj",
            "3AV9oj6jMkkYzeBm55cuMj"
        ]

        def generate_random_song():
            SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
            SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

            client_credentials_manager = SpotifyClientCredentials(
                client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
            )
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

            random_playlist_id = random.choice(PLAYLIST_IDS)
            playlist_link = f"https://open.spotify.com/playlist/{random_playlist_id}"

            results = sp.playlist_tracks(random_playlist_id)
            tracks = results['items']

            playlist_info = sp.playlist(random_playlist_id)
            playlist_name = playlist_info['name']
            playlist_creator = playlist_info['owner']['display_name']

            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])

            random_track = random.choice(tracks)
            track_name = random_track['track']['name']
            artist = random_track['track']['artists'][0]['name']
            album_name = random_track['track']['album']['name']
            album_image_url = random_track['track']['album']['images'][0]['url']
            track_id = random_track['track']['id']
            track_https_link = f"https://open.spotify.com/track/{track_id}"
            
            # Fetch artist details for profile image
            artist_id = random_track['track']['artists'][0]['id']
            artist_info = sp.artist(artist_id)
            artist_image_url = artist_info['images'][0]['url'] if artist_info['images'] else None

            return track_https_link, album_image_url, album_name, track_name, artist, playlist_creator, playlist_name, playlist_link, artist_image_url

        # Get random song details
        track_link, album_image_url, album_name, track_name, artist, playlist_creator, playlist_name, playlist_link, artist_image_url = generate_random_song()





        def get_dominant_color(image_url):
            """Fetches the image and determines the dominant color."""
            response = requests.get(image_url)
            img = Image.open(io.BytesIO(response.content))
            img = img.resize((50, 50))
            pixels = list(img.getdata())
            
            # Convert RGB to HSV and sort by saturation
            hsv_pixels = [(colorsys.rgb_to_hsv(r/255, g/255, b/255), (r, g, b)) for r, g, b in pixels]
            hsv_pixels.sort(key=lambda x: x[0][1], reverse=True)  # Sort

            dominant_color = hsv_pixels[0][1]
            
            # Convert RGB to HEX
            return int(f'0x{dominant_color[0]:02X}{dominant_color[1]:02X}{dominant_color[2]:02X}', 16)

            # Get the dominant color from the album image
        dominant_color = get_dominant_color(album_image_url)




        if playlist_creator == "Impy":
            user = await self.bot.fetch_user(301512451453616128)


            embed = discord.Embed(
                title="Random Track", 
                description=f"🎤 Track: **{track_name}**\n\n👤 Artist: **{artist}**\n\n📀 Album: **{album_name}**\n\n🎵 Playlist: [{playlist_name}]({playlist_link}) (by <@301512451453616128>)",
                color=dominant_color
            )
            embed.set_image(url=album_image_url)
            embed.set_thumbnail(url=artist_image_url)

            await interaction.delete_original_response()
            await interaction.channel.send(embed=embed)

            msg = await interaction.channel.send(f"[⠀]({track_link})")
            await msg.add_reaction("❤️")

        elif playlist_creator == "Rynn <3":
            user = await self.bot.fetch_user(493105382932086803)

            embed = discord.Embed(
                title="Random Track", 
                description=f"🎤 Track: **{track_name}**\n\n👤 Artist: **{artist}**\n\n📀 Album: **{album_name}**\n\n🎵 Playlist: [{playlist_name}]({playlist_link}) (by <@301512451453616128>)",
                color=dominant_color
            )
            embed.set_image(url=album_image_url)
            embed.set_thumbnail(url=artist_image_url)

            await interaction.response.send_message(embed=embed)

            msg = await interaction.channel.send(f"[⠀]({track_link})")
            await msg.add_reaction("❤️")






    @app_commands.command(name="addsong", description="Add a Spotify track URL to the playlist")
    @app_commands.describe(url="Spotify track URL (e.g. https://open.spotify.com/track/...)")
    async def addsong(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()

        # extract track ID from URL
        match = re.match(r'https?://open\.spotify\.com/track/([a-zA-Z0-9]+)', url)
        if not match:
            await interaction.followup.send("❌ Invalid Spotify track URL.")
            return

        track_id = match.group(1)

        try:
            track = self.sp.track(track_id)
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            track_url = track['external_urls']['spotify']

            self.sp.playlist_add_items(self.playlist_id, [track_id])

            self.log_user_addition(
                user_name=str(interaction.user.id),
                track_id=track_id,
                track_name=track_name,
                artist_name=artist_name,
                track_url=track_url
            )

            await interaction.followup.send(
                f"✅ Added **{track_name}** by **{artist_name}** to the playlist!\n{track_url}"
            )
        except spotipy.SpotifyException as e:
            await interaction.followup.send(f"⚠️ Spotify API error: {e}")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {e}")

    def log_user_addition(self, user_name, track_id, track_name, artist_name, track_url):
        with open(TRACK_LOG_FILE, "r") as f:
            data = json.load(f)

        if user_name not in data:
            data[user_name] = []

        # Avoid duplicate track logging for same user
        if not any(entry["track_id"] == track_id for entry in data[user_name]):
            data[user_name].append({
                "track_id": track_id,
                "track_name": track_name,
                "artist_name": artist_name,
                "track_url": track_url
            })

            with open(TRACK_LOG_FILE, "w") as f:
                json.dump(data, f, indent=4)






    @app_commands.command(name="playlistsongs", description="View all members and the songs they've added")
    async def songlog(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not os.path.exists(TRACK_LOG_FILE):
            await interaction.followup.send("❌ No song log file found.")
            return

        with open(TRACK_LOG_FILE, "r") as f:
            data = json.load(f)

        if not data:
            await interaction.followup.send("📭 No songs have been logged yet.")
            return

        embed = discord.Embed(
            description="# 🎶 Server Song List\n### Below are the awesome people and the songs they've added to the playlist! 💜\n### [Click here to view the playlist!](https://open.spotify.com/playlist/2e8ewMesew3AlAh3X54skb?si=a2d6b4f71b8e4672)",
            color=0x503c91
        )

        pfpPath = "images/SOULpfp.png"
        pfpFile = discord.File(pfpPath, filename="ServerPfp.png")

        embed.set_thumbnail(url="attachment://ServerPfp.png")

        for user_id, songs in data.items():
            try:
                user = await self.bot.fetch_user(int(user_id))
                field_title = f"‎"
                user_mention = user.mention
            except:
                field_title = f"‎"
                user_mention = f"<@{user_id}>"

            song_lines = [
                f"> - [{s['track_name']} - {s['artist_name']}]({s['track_url']})"
                for s in songs
            ]
            field_value = f"{user_mention}\n" + "\n".join(song_lines[:10])
            if len(song_lines) > 10:
                field_value += f"\n...and {len(song_lines) - 10} more."

            embed.add_field(name=field_title, value=field_value, inline=False)


        await interaction.followup.send(embed=embed, file=pfpFile)


async def setup(bot):
    await bot.add_cog(Fun(bot))