import discord
from discord import app_commands
from discord.ext import commands

class HelpView(discord.ui.View):
    def __init__(self, pages, user):
        super().__init__(timeout=None)
        self.pages = pages
        self.current_page = 0
        self.user = user

        self.previous_page.disabled = True
        if len(pages) == 1:
            self.next_page.disabled = True


    async def update_message(self, interaction: discord.Interaction):
        embed = self.pages[self.current_page]
        embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.pages)}")
        await interaction.response.edit_message(embed=embed, view=self)


    @discord.ui.button(label="↩", style=discord.ButtonStyle.red, disabled=True)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("❌ You can't use these buttons.", ephemeral=True)

        self.current_page -= 1
        self.next_page.disabled = False

        if self.current_page == 0:
            self.previous_page.disabled = True

        await self.update_message(interaction)


    @discord.ui.button(label="↪", style=discord.ButtonStyle.red)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("❌ You can't use these buttons.", ephemeral=True)

        self.current_page += 1
        self.previous_page.disabled = False

        if self.current_page == len(self.pages) - 1:
            self.next_page.disabled = True

        await self.update_message(interaction)






class SuggestionModal(discord.ui.Modal, title="Submit a Suggestion"):
    suggestion = discord.ui.TextInput(
        label="Your Suggestion",
        style=discord.TextStyle.paragraph,
        placeholder="Describe your suggestion here...",
        required=True,
        max_length=500
    )

    def __init__(self, bot, suggestion_channel: discord.TextChannel):
        super().__init__()
        self.bot = bot
        self.suggestion_channel = suggestion_channel

    async def on_submit(self, interaction: discord.Interaction):
        """Handles the suggestion submission."""
        embed = discord.Embed(
            title="📩 New Suggestion!",
            description=f"Submitted by: {interaction.user.mention}\n\n{self.suggestion.value}",
            color=discord.Color.green(),
            timestamp=interaction.created_at
        )
        embed.set_author(name=f"Suggested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await self.suggestion_channel.send(embed=embed)
        await interaction.response.send_message("✅ Your suggestion has been submitted!", ephemeral=True)







class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays all available commands.")
    async def help(self, interaction: discord.Interaction):
        # Shows only commands the user has permission to use, grouped by cog, with command IDs
        
        registered_commands = {cmd.name: cmd for cmd in await self.bot.tree.fetch_commands()}
        embeds = []

        embed_template = lambda title: discord.Embed(
            title=title, 
            description="‎\n💎 = **Bot Owner**\n👑 = **Admin**\n⭐ = **Mod**\n-# If you dont see a command, it means you dont have access\n‎",
            color=0xff0c0d
        ).set_thumbnail(url=self.bot.user.avatar.url)  # Adding a beautiful, stunning thumbnail of our overlord

        current_embed = embed_template("<:nyxiraIcon:1350910504725516359> Nyxira Help Menu")
        field_count = 0

        for cog_name, cog in self.bot.cogs.items():
            commands_list = []

            for cmd in cog.walk_app_commands():
                if not await self.can_use(interaction, cmd):
                    continue

                cmd_id = registered_commands.get(cmd.name, {}).id if cmd.name in registered_commands else "Unknown ID"
                description = cmd.description if cmd.description else "No description available"

                commands_list.append(f"♡ </{cmd.name}:{cmd_id}> → *{description}*")

            if commands_list:
                current_embed.add_field(name=f"❤️ {cog_name}", value="\n".join(commands_list), inline=False)
                field_count += 1

                # If too many fields, create a new embed
                if field_count >= 5:
                    embeds.append(current_embed)
                    current_embed = embed_template("<:nyxiraIcon:1350910504725516359> Nyxira Help Menu (Continued)")
                    field_count = 0

        if field_count > 0:
            embeds.append(current_embed)

        for index, embed in enumerate(embeds):
            embed.set_footer(text=f"Page {index + 1} of {len(embeds)}")

        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            view = HelpView(embeds, interaction.user)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    async def can_use(self, interaction: discord.Interaction, command: app_commands.Command) -> bool:
        if "ownercommands" in command.module:
            return await self.bot.is_owner(interaction.user)

        if command.default_permissions is None:
            return True  

        user_perms = interaction.channel.permissions_for(interaction.user)
        return user_perms.is_superset(command.default_permissions)









    @app_commands.command(name="suggest", description="Submit a suggestion for the server.")
    async def suggest(self, interaction: discord.Interaction):
        suggestion_channel_id = 745873644378390558
        suggestion_channel = interaction.guild.get_channel(suggestion_channel_id)

        if not suggestion_channel:
            return await interaction.response.send_message("❌ Suggestion channel not found!", ephemeral=True)

        await interaction.response.send_modal(SuggestionModal(self.bot, suggestion_channel))


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
