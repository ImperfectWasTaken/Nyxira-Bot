import discord
import aiohttp
import asyncio
import requests
import os
import json
import yt_dlp
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
PERSISTENT_STORAGE = "json/image_data.json"






def load_pagination_data():
    try:
        with open(PERSISTENT_STORAGE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


class ImagePagination(discord.ui.View):
    def __init__(self, image_urls: list[str], query: str, current_index: int = 0):
        super().__init__(timeout=None)
        self.image_urls = image_urls
        self.query = query
        self.current_index = current_index

    async def update_message(self, interaction: discord.Interaction):
        # Update the embed and reattach the view to keep it active
        embed = discord.Embed(title=f"Image results for: {self.query}", color=0xff0c0d)
        embed.set_image(url=self.image_urls[self.current_index])
        embed.set_footer(text=f"Result {self.current_index + 1} of {len(self.image_urls)}")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="↩", style=discord.ButtonStyle.red, custom_id="prev_button", row=0)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index > 0:
            self.current_index -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="↪", style=discord.ButtonStyle.red, custom_id="next_button", row=0)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index < len(self.image_urls) - 1:
            self.current_index += 1
            await self.update_message(interaction)







class YouTubeSearchView(discord.ui.View):
    def __init__(self, results, author: discord.Member):
        super().__init__(timeout=None)
        self.results = results
        self.current_page = 0
        self.author = author

    @property
    def message_content(self):
        video = self.results[self.current_page]
        return f"**[{video['title']}]({video['url']})**\n\n`Page {self.current_page + 1} of {len(self.results)}`"

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=self.message_content, view=self)

    @discord.ui.button(label="↩", style=discord.ButtonStyle.red, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("You're not allowed to control this pagination!", ephemeral=True)
        
        self.current_page -= 1
        self.next.disabled = self.current_page == len(self.results) - 1
        self.previous.disabled = self.current_page == 0
        await self.update_message(interaction)

    @discord.ui.button(label="↪", style=discord.ButtonStyle.red)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("You're not allowed to control this pagination!", ephemeral=True)
        
        self.current_page += 1
        self.next.disabled = self.current_page == len(self.results) - 1
        self.previous.disabled = self.current_page == 0
        await self.update_message(interaction)




class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Say, hello?")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.mention}")

        messages = [
            "The weight upon your chest is not exhaustion...",
            "...nor is it the heavy pull of restless slumber.",
            "I am watching you̷r̴ e̵v̵e̴r̵y̵ ̸m̴o̸v̶e̸.̴",
            "The air around you grows colder, not by c̶̹͊h̷̟̔a̵̢̐n̷̛̼c̵̨̄ẽ̷̟, not by s̵̠͎͋̚ê̸̫̼͆́͜a̵͙̘͈̚s̶̠̞̩͛͑o̷̭̪͈̿n̸͎̒̌, but by **d̷̠̳̰͙̐͐̚͘e̴̖̩̲̮̯̊̄̎̒͝ͅs̶̖̯̆̄̿́̊͛͗̆͑̒̕͘i̸̪̪̲̟̾͜ͅg̶̬͋͗̏̅̊n̴̫͇̘̫̱̣͇͚̣̟̏̓̈͑̈̈́͊̈̈́̊̊̒̚̕.**",
            "The silence around you, it's *blaring*.",
            "The anticipation of something just b̵̠͆ę̵͛y̵̮̚ȏ̷̺n̵̥̓ḑ̵̬͇̠̘̋̆̉͂ ̴̛̠y̴̪̓͠o̵̩̪̥̳̼̤̕ͅu̶͖̓̍̈́r̸͎̣̜̦̔̌̂ p̸̠̦̈ẻ̶̢̖͔̦̞̈́̒r̶̢̮͕̜̎͐̏̍͆̂̿̚c̵̢̛͕̮͎͎̘̯͚̽̈́͊͊ȅ̷̮̠͍̟̙̟̪̅ͅp̷̢͓̜͆͑̌̌̊͛͜t̴̟̜͙̟̯̪̜̬̒͐͐̕͝͝͠i̶̹̻͕̮̩̫̿̋͋̏ô̶͎̜̻̺̫͙̒̒̿͐͠ͅͅn̶̻̺̮͕͌...",
            "...something that does not need to ˢᵖᵉᵃᵏ to make its presence **known.**",
            "Listen closely, and you may̴ ̶h̶e̴a̷r̸ ̶ĭ̶̝̳̰t̴̰̲̾.̸̼̺͆͘.̵̹͎̓͆.̶͖̞͊",
            "||...just behind **you.**||"
        ]

        message = await interaction.original_response()
        await asyncio.sleep(5)

        for msg in messages:
            await asyncio.sleep(5)
            await message.edit(content=msg)

        await asyncio.sleep(5)
        await message.delete()
        




    @app_commands.command(name="deadchat", description="Pings the deadchat role when the chat is dead")
    async def deadchat(self, interaction: discord.Interaction):
        deadchatrole = "<@&1314087385331531897>"
        allowed_mentions = discord.AllowedMentions(roles=True)
        embed = discord.Embed(description=f"{interaction.user.mention} thinks the chat is a bit dead, come chat! ☕", color=0x9c7a5c)
        await interaction.response.send_message(content=deadchatrole, embed=embed, allowed_mentions=allowed_mentions)






    @app_commands.command(name="image", description="Search Google Images")
    @app_commands.describe(search="What image do you want to search for?")
    async def image_search(self, interaction: discord.Interaction, search: str):
        """Fetch top Google image results and paginate them."""
        await interaction.response.defer()

        search_url = (
            f"https://www.googleapis.com/customsearch/v1?q={search}"
            f"&cx={GOOGLE_CSE_ID}&key={GOOGLE_API_KEY}&searchType=image&num=10"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])

                    if not items:
                        return await interaction.followup.send(f"❌ No images found for `{search}`.", ephemeral=True)

                    image_urls = [item["link"] for item in items]
                    embed = discord.Embed(title=f"Image results for: {search}", color=0xff0c0d)
                    embed.set_image(url=image_urls[0])
                    embed.set_footer(text=f"Result 1 of {len(image_urls)}")

                    view = ImagePagination(image_urls, search)
                    message = await interaction.followup.send(embed=embed, view=view)

                    # Save pagination state
                    self.save_pagination_data(message.id, image_urls, 0)

                else:
                    await interaction.followup.send("❌ Error fetching image results. Try again later.", ephemeral=True)

    def save_pagination_data(self, message_id: int, image_urls: list[str], current_index: int):
        try:
            with open(PERSISTENT_STORAGE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        data[str(message_id)] = {"image_urls": image_urls, "current_index": current_index}

        with open(PERSISTENT_STORAGE, "w") as f:
            json.dump(data, f, indent=4)





    @app_commands.command(name="youtube", description="Search for a YouTube video")
    @app_commands.describe(search="The Youtube video you want to search")
    async def youtube(self, interaction: discord.Interaction, search: str):
        await interaction.response.defer()

        ydl_opts = {
            'quiet': True,
            'default_search': 'ytsearch10',
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{search}", download=False)
            results = [
                {
                    'title': entry['title'],
                    'url': entry['url'],
                    'thumbnail': entry.get('thumbnail', ''),
                }
                for entry in info['entries']
            ]
        
        if not results:
            return await interaction.response.send_message("No results found.")
        
        view = YouTubeSearchView(results, interaction.user)
        await interaction.followup.send(content=view.message_content, view=view)







    @app_commands.command(name="movie", description="Get information about a movie")
    @app_commands.describe(title="The title of the movie you want information for")
    async def movie(self, interaction: discord.Interaction, title: str):
        OMDB_API_KEY = os.getenv("OMDB_API_KEY")
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}&plot=short"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("Response") == "True":
                        ratings = {rating["Source"]: rating["Value"] for rating in data.get("Ratings", [])}
                        rotten_tomatoes_score = ratings.get("Rotten Tomatoes", "N/A")
                        metacritic_score = ratings.get("Metacritic", "N/A")
                        embed = discord.Embed(
                            title=data["Title"],
                            description=data["Plot"],
                            color=0xff0c0d
                        )
                        embed.set_thumbnail(url=data["Poster"])
                        embed.add_field(name="📅 Release Year", value=data["Year"], inline=True)
                        embed.add_field(name="🕒 Runtime", value=data["Runtime"], inline=True)
                        embed.add_field(name="🎭 Genre", value=data["Genre"], inline=True)
                        embed.add_field(name="🎬 Director", value=data["Director"], inline=True)
                        embed.add_field(name="📝 Writer", value=data["Writer"], inline=True)
                        embed.add_field(name="🎤 Actors", value=data["Actors"], inline=True)
                        embed.add_field(name="⭐ IMDB Rating", value=data["imdbRating"], inline=False)
                        embed.add_field(name="🍅 Rotten Tomatoes", value=rotten_tomatoes_score, inline=False)
                        embed.add_field(name="👥 Metacritic", value=metacritic_score, inline=False)

                        await interaction.response.send_message(embed=embed)
                    else:
                        await interaction.response.send_message(f"❌ Movie not found: `{title}`", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Error fetching movie details. Try again later.", ephemeral=True)





    @app_commands.command(name="show", description="Get information about a TV show")
    @app_commands.describe(title="The title of the show you want information for")
    async def tvshow(self, interaction: discord.Interaction, title: str):
        OMDB_API_KEY = os.getenv("OMDB_API_KEY")
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}&type=series"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("Response") == "True":
                        ratings = {rating["Source"]: rating["Value"] for rating in data.get("Ratings", [])}
                        rotten_tomatoes_score = ratings.get("Rotten Tomatoes", "N/A")
                        metacritic_score = ratings.get("Metacritic", "N/A")

                        embed = discord.Embed(
                            title=data["Title"],
                            description=data["Plot"],
                            color=0xff0c0d
                        )
                        embed.set_thumbnail(url=data["Poster"])
                        embed.add_field(name="📅 First Aired", value=data["Year"], inline=True)
                        embed.add_field(name="📺 Total Seasons", value=data.get("totalSeasons", "N/A"), inline=True)
                        embed.add_field(name="🎭 Genre", value=data["Genre"], inline=True)
                        embed.add_field(name="🎬 Creator(s)", value=data["Writer"], inline=True)
                        embed.add_field(name="🎤 Main Cast", value=data["Actors"], inline=True)
                        embed.add_field(name="⭐ IMDB Rating", value=data["imdbRating"], inline=False)
                        embed.add_field(name="🍅 Rotten Tomatoes", value=rotten_tomatoes_score, inline=False)
                        embed.add_field(name="👥 Metacritic", value=metacritic_score, inline=False)

                        await interaction.response.send_message(embed=embed)
                    else:
                        await interaction.response.send_message(f"❌ TV show not found: `{title}`", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Error fetching TV show details. Try again later.", ephemeral=True)







    @app_commands.command(name="game", description="Get information about a video game")
    @app_commands.describe(title="The title of the game you want information for")
    async def game_lookup(self, interaction: discord.Interaction, title: str):
            await interaction.response.defer()
            RAWG_API_KEY = os.getenv("RAWG_API_KEY")

            search_url = f"https://api.rawg.io/api/games?search={title}&key={RAWG_API_KEY}"

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])

                        if not results:
                            return await interaction.followup.send(f"❌ No game found for `{title}`.", ephemeral=True)

                        # Get the first result
                        game = results[0]
                        game_id = game["id"]
                        game_details_url = f"https://api.rawg.io/api/games/{game_id}?key={RAWG_API_KEY}"

                        async with session.get(game_details_url) as details_response:
                            if details_response.status == 200:
                                game_data = await details_response.json()

                                title = game_data["name"]
                                description = game_data.get("description_raw", "No description available.")
                                release_date = game_data.get("released", "Unknown")
                                metacritic = game_data.get("metacritic", "N/A")
                                platforms = ", ".join([p["platform"]["name"] for p in game_data.get("platforms", [])])
                                genres = ", ".join([g["name"] for g in game_data.get("genres", [])])
                                game_url = game_data.get("website") or f"https://rawg.io/games/{game_data['slug']}"
                                background_image = game_data.get("background_image", None)

                                embed = discord.Embed(title=title, url=game_url, description=description[:1000] + "...", color=0xff0c0d)
                                embed.add_field(name="📅 Release Date", value=release_date, inline=True)
                                embed.add_field(name="🎮 Platforms", value=platforms, inline=True)
                                embed.add_field(name="🕹️ Genres", value=genres, inline=True)
                                embed.add_field(name="⭐ Metacritic", value=metacritic, inline=True)

                                if background_image:
                                    embed.set_image(url=background_image)

                                await interaction.followup.send(embed=embed)

                            else:
                                await interaction.followup.send("❌ Error fetching game details.", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ Error accessing RAWG API. Try again later.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))