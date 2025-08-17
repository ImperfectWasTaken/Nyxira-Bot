import discord
from discord.ext import commands, tasks
import json
import random
import asyncio
import pytz
import webcolors
from datetime import datetime

COLOR_FILE = "json\colors.json"
SCHEDULE_FILE = "json\scheduled_roles.json"

with open(COLOR_FILE, "r") as file:
    CSS3_COLORS = json.load(file)

def load_schedules():
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_schedules(schedules):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedules, file, indent=4)

def load_colors():
    try:
        with open(COLOR_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}

class RoleColorChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color_tasks = {}
        self.schedules = load_schedules()
        self.start_scheduled_tasks()
    
    def cog_unload(self):
        for task in self.color_tasks.values():
            task.cancel()   
    
    def start_scheduled_tasks(self):
        for role_id, time in self.schedules.items():
            role_id = int(role_id)
            if role_id not in self.color_tasks:
                for guild in self.bot.guilds:
                    role = guild.get_role(role_id)
                    if role:
                        task = asyncio.create_task(self.change_color_task(role, time["hour"], time["minute"]))
                        self.color_tasks[role_id] = task
                        break
                else:
                    print(f"[ERROR] Role {role_id} not found in the guild!")



    async def schedule_role_color_change(self, role: discord.Role, hour: int, minute: int):
        role_id = str(role.id)

        # Save new time to file
        self.schedules[role_id] = {"hour": hour, "minute": minute}
        save_schedules(self.schedules)

        # Cancel existing task if running
        if role_id in self.color_tasks:
            self.color_tasks[role_id].cancel()
            del self.color_tasks[role_id]

        # Start new task with updated time
        task = asyncio.create_task(self.change_color_task(role, hour, minute))
        self.color_tasks[role_id] = task


    
    async def change_color_task(self, role, hour, minute):
        colors = load_colors()
        tz = pytz.timezone("America/New_York")
        
        while True:
            now = datetime.now(tz)
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if now >= target_time:
                target_time = target_time.replace(day=now.day + 1)  # move to the next day
            
            sleep_seconds = (target_time - now).total_seconds()
            
            await asyncio.sleep(sleep_seconds)

            color_name, hex_color = random.choice(list(colors.items()))
            rgb_color = discord.Color(int(hex_color.strip("#"), 16))

            try:
                await role.edit(color=rgb_color, name=f"{color_name.title()} 🎲", reason="Scheduled color change")
            except discord.Forbidden:
                print("[ERROR] Bot does not have permission to edit roles.")
                break
            except Exception as e:
                print(f"[ERROR] Error changing role color: {e}")
                break


async def setup(bot):
    await bot.add_cog(RoleColorChanger(bot))
