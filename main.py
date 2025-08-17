import discord
import logging
import os
import datetime
import sys
import io
import json
from discord.ext import commands
from cogs.general import ImagePagination
from dotenv import load_dotenv

load_dotenv()

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, reconnect=True)
bot.launch_time = datetime.datetime.now()
PERSISTENT_STORAGE = "json/image_data.json"

# Create log directory if it doesn't exist
log_folder = "logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# File paths
error_log_file = os.path.join(log_folder, "error_logs.txt")
interaction_log_file = os.path.join(log_folder, "interactions_log.txt")

# Custom logging formatter with color and timestamps
class ColorFormatter(logging.Formatter):
    COLORS = {
        "INFO": "\033[1;32m",  # Green
        "ERROR": "\033[1;31m",  # Red
        "WARNING": "\033[1;33m",  # Yellow
        "DEBUG": "\033[1;34m",  # Blue
        "RESET": "\033[0m"  # Reset color
    }

    def format(self, record):
        log_time = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
        levelname = record.levelname
        message = super().format(record)
        return f"{self.COLORS.get(levelname, self.COLORS['RESET'])}{log_time} - {message}{self.COLORS['RESET']}"

# Function to log interactions
def log_interaction(interaction):
    timestamp = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
    with open(interaction_log_file, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] User: {interaction.user} | Command: {interaction.command.name}\n")

# Log interaction commands separately
@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.application_command:
        log_interaction(interaction)






# Unicode-safe stream for console logs
utf8_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Avoid debug logs in console

# Console handler with colors
console_handler = logging.StreamHandler(utf8_stream)
console_handler.setFormatter(ColorFormatter("%(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# File handler (logs all errors)
file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%m-%d %H:%M:%S"))
logger.addHandler(file_handler)

# Suppress discord debug logs
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.client").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# Suppress reconnect errors
class SuppressReconnectErrors(logging.Filter):
    def filter(self, record):
        if "Attempting a reconnect" in record.getMessage() or "getaddrinfo failed" in record.getMessage():
            print(f"[{datetime.datetime.now().strftime('%m-%d %H:%M:%S')}] ⚠️  Reconnecting...")
            return False  # Don't log it in the console
        return True  # Allow other logs

# Apply filter
for logger_name in ["discord.client", "discord.gateway"]:
    logger = logging.getLogger(logger_name)
    logger.addFilter(SuppressReconnectErrors())







def load_pagination_data():
    """Load pagination data from a JSON file."""
    try:
        with open(PERSISTENT_STORAGE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}




@bot.event
async def on_ready():
    print("\n       /\\                 /\\")
    print("      / \\'._   (\\_/)   _.'/ \\")
    print(f"     /_.''._'--('.')--'_.''._\\      {bot.user.name}")
    print("     | \\_ / `;=/ \" \\=;` \\ _/ |       reporting")
    print("      \\/ `\\__|`\\___/`|__/`  \\/        for")
    print("           _/  _| |_  \\_             duty! ❤️")
    print("          / `./     \\.' \\ \n")

    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.listening, name="the weak..."))

    # Load cogs dynamically
    cog_paths = ["./cogs"]
    for cog_path in cog_paths:
        for filename in os.listdir(cog_path):
            if filename.endswith(".py"):
                cog_name = f"cogs.{filename[:-3]}"  
                try:
                    await bot.load_extension(cog_name)
                    print(f"✅ Loaded {cog_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {cog_name}: {e}")

    # Sync slash commands
    data = load_pagination_data()
    for message_id, view_data in data.items():
        view = ImagePagination(view_data["image_urls"], view_data["current_index"])
        bot.add_view(view)  # Register persistent view


    total_slash_commands = len(bot.tree.get_commands())
    await bot.tree.sync()
    logger.info(f"🔁 Synced {total_slash_commands} command(s).\n")

# Global error handler
@bot.event
async def on_command_error(ctx, error):
    timestamp = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
    logger.error(f"[{timestamp}] Error occurred during command execution.")

    with open(error_log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ERROR: {str(error)}\n")
        f.write(f"Traceback:\n{logging.formatException(error)}\n\n")

    await ctx.send("An error occurred while executing the command. The bot owner has been notified.")

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

