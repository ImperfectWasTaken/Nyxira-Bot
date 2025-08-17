import discord
from discord.ext import commands
from discord import app_commands

class BotOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    def is_owner_check(self, interaction: discord.Interaction) -> bool:
        return 301512451453616128 == interaction.user.id
    

    @app_commands.command(name="load", description="Load a cog 💎")
    @app_commands.default_permissions(administrator=False)
    async def load(self, interaction: discord.Interaction, extension: str):
        await interaction.response.defer()
        if not self.is_owner_check(interaction):
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
            return
        
        try:
            await self.bot.load_extension(f"cogs.{extension}")
            await interaction.followup.send(f"✅ Loaded `{extension}` successfully.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to load `{extension}`:\n```{e}```", ephemeral=True)


    @app_commands.command(name="unload", description="Unload a cog 💎")
    @app_commands.default_permissions(administrator=False)
    async def unload(self, interaction: discord.Interaction, extension: str):
        await interaction.response.defer()
        if not self.is_owner_check(interaction):
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
            return

        if f"cogs.{extension}" not in self.bot.extensions:
            await interaction.followup.send(f"❌ `{extension}` is not loaded.", ephemeral=True)
            return
        
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            await interaction.followup.send(f"✅ Unloaded `{extension}` successfully.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to unload `{extension}`:\n```{e}```", ephemeral=True)


    @app_commands.command(name="reload", description="Reload a cog 💎")
    @app_commands.default_permissions(administrator=False)
    async def reload(self, interaction: discord.Interaction, extension: str):
        await interaction.response.defer()
        if not self.is_owner_check(interaction):
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
            return

        if f"cogs.{extension}" not in self.bot.extensions:
            await interaction.followup.send(f"❌ `{extension}` is not loaded.", ephemeral=True)
            return

        try:
            await self.bot.reload_extension(f"cogs.{extension}")
            await self.bot.tree.sync()
            await interaction.followup.send(f"✅ Reloaded `{extension}` and synced commands!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to reload `{extension}`:\n```{e}```", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BotOwnerCommands(bot))

