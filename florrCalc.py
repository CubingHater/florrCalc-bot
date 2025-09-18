import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import os   
from discord import app_commands

GUILD_ID = [1360136587723145307] 
COMMAND_FILE = "bot_command.txt"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TRIGGERS = ["manfred", "pehiley", "magic stick", "unique"]
EMOJI = "💲"

probabilities = {
    "common": 0.64,
    "unusual": 0.32,
    "rare": 0.16,
    "epic": 0.08,
    "legendary": 0.04,
    "mythic": 0.02,
    "ultra": 0.01
}

rarity_order = ["common", "unusual", "rare", "epic", "legendary", "mythic", "ultra"]

next_rarity_colors = {
    "common": 0xFFE65D,
    "unusual": 0x4D52E3,
    "rare": 0x861FDE,
    "epic": 0xDE1F1F,
    "legendary": 0x1FDBDD,
    "mythic": 0xFF2B75,
    "ultra": 0x2BFFA3
}

def expected_successes(petals: int, chance: float) -> float:
    if petals < 5:
        return 0.0
    return (petals - 2.5 * (1 - chance)) / ((2.5 / chance) + 2.5)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    embed = discord.Embed(
        title="Server is ready!",
        description="florrCalc is online and ready to assist you.",
        color=discord.Color.purple()
    )
    embed.add_field(name="Commands", value="Here are the available commands:", inline=False)
    embed.add_field(name="/help", value="Shows this help message", inline=False)
    embed.add_field(name="/craft", value="Calculate crafting averages to the next rarity", inline=False)
    embed.add_field(name="/guessgame", value="Guess crafting averages for a random rarity and amount", inline=False)
    embed.add_field(
        name="Available rarities",
        value=", ".join([r.capitalize() for r in rarity_order]) + ", Super",
        inline=False
    )
    embed.set_footer(text="florrCalc 26.0 beta")

    for guild in bot.guilds:  # loop over alle servers waar de bot in zit
        channel = discord.utils.get(guild.text_channels, name="bot-commands")
        if channel:
            await channel.send(embed=embed)
        else:
            print(f"No #bot-commands channel found in {guild.name}")

    try:
        synced = await bot.tree.sync()  # sync ALLE commands naar ALLE servers
        print(f"Synced {len(synced)} command(s) globally.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    await AAA(guild)

async def AAA(guild):
    try:
        await bot.tree.sync(guild=discord.Object(GUILD_ID))
        print(f"Synced commands for guild: {guild.name} ({GUILD_ID})")
    except Exception as e:
        print(f"Error syncing commands for guild {guild.name} ({GUILD_ID}): {e}")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.bot:
        return
    
    content = message.content.lower()
    
    if any(trigger in content for trigger in TRIGGERS):
        try:
            await message.add_reaction(EMOJI)
        except Exception as e:
            print("Reaction failed:", e)

    if random.randint(1, 100) == 1:
        await message.channel.send("Fun fact: Manfred is p2w")
    
    await bot.process_commands(message)

@bot.tree.command(name="help", description="Show bot information")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="florrCalc Bot Help",
        description="Available commands and features",
        color=discord.Color.purple()
    )
    embed.add_field(name="/help", value="Shows this help message", inline=False)
    embed.add_field(name="/craft", value="Calculate crafting averages to the next rarity", inline=False)
    embed.add_field(name="/guessgame", value="Guess crafting averages for a random rarity and amount", inline=False)
    embed.add_field(
        name="Available rarities",
        value=", ".join([r.capitalize() for r in rarity_order]) + ", Super",
        inline=False
    )
    embed.set_footer(text="florrCalc 26.0 beta")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="craft", description="Calculate crafting averages to the next rarity")
@app_commands.describe(
    rarity="Choose the current rarity",
    petals="Number of petals you want to use"
)
@app_commands.choices(
    rarity=[
        app_commands.Choice(name="Common", value="common"),
        app_commands.Choice(name="Unusual", value="unusual"),
        app_commands.Choice(name="Rare", value="rare"),
        app_commands.Choice(name="Epic", value="epic"),
        app_commands.Choice(name="Legendary", value="legendary"),
        app_commands.Choice(name="Mythic", value="mythic"),
        app_commands.Choice(name="Ultra", value="ultra")
    ]
)
async def craft(interaction: discord.Interaction, rarity: app_commands.Choice[str], petals: int):
    if petals < 0:
        await interaction.response.send_message("Please enter a positive number of petals.", ephemeral=True)
        return

    current_rarity = rarity.value
    index = rarity_order.index(current_rarity)
    
    next_rarity = "Super" if index == len(rarity_order) - 1 else rarity_order[index + 1].capitalize()
    result = expected_successes(petals, probabilities[current_rarity])
    color = next_rarity_colors[current_rarity]

    embed = discord.Embed(
        title=f"Crafting Calculator: {current_rarity.capitalize()} → {next_rarity}",
        color=color
    )
    embed.add_field(name="Current Rarity", value=current_rarity.capitalize(), inline=True)
    embed.add_field(name="Next Rarity", value=next_rarity, inline=True)
    embed.add_field(name="Petals", value=str(petals), inline=True)
    embed.add_field(name="Expected Result", value=f"{result:.2f}", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="guessgame", description="Play a crafting guessing game")
async def guessgame(interaction: discord.Interaction):
    random_rarity = random.choice(rarity_order)
    random_petals = random.randint(5, 1000)
    expected = expected_successes(random_petals, probabilities[random_rarity])
    
    await interaction.response.send_message(
        f"Guess how many petals will craft from **{random_petals} {random_rarity.capitalize()} petals** to the next rarity! Type your guess as a number."
    )

    def check(m: discord.Message):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        guess_msg = await bot.wait_for("message", check=check, timeout=30.0)
        guess = float(guess_msg.content)
        difference = abs(guess - expected)
        percentage_error = (difference / expected) * 100

        if percentage_error <= 10:
            result_text = "Amazing! You were within 10% of the correct value!"
        elif percentage_error <= 25:
            result_text = "<:ahh:1414628749026005072> Not bad! You were within 25%."
        else:
            result_text = "Too far off, better luck next time."

        next_rarity = "Super" if random_rarity == "ultra" else rarity_order[rarity_order.index(random_rarity)+1]

        embed = discord.Embed(
            title="Crafting Guess Game",
            description=f"You guessed: {guess}\nActual average: {expected:.2f}\n{result_text}",
            color=next_rarity_colors[random_rarity]
        )
        embed.add_field(name="Petals", value=random_petals)
        embed.add_field(name="Rarity", value=random_rarity.capitalize())
        embed.add_field(name="Next Rarity", value=next_rarity.capitalize())
        await interaction.followup.send(embed=embed)

    except Exception:
        await interaction.followup.send("Time's up! You didn't answer in time.")

@bot.command(name="server_close")
@commands.has_any_role("Moderator", "Developer - CEO")
async def server_close(ctx: commands.Context):
    channel = discord.utils.get(ctx.guild.text_channels, name="bot-commands")
    if channel:
        embed = discord.Embed(
            title="Server Closing Soon",
            description="The server will close in 10 seconds. Please save your work.",
            color=next_rarity_colors["epic"]
        )
        await channel.send(embed=embed)
        await ctx.send("Close message sent to #bot-commands")
    else:
        await ctx.send("No #bot-commands channel found.")

@bot.tree.command(name="dm", description="Send a DM to a user (moderators only)")
@app_commands.checks.has_any_role("Moderator", "Developer - CEO")  # Alleen deze rollen
async def dm_command(interaction: discord.Interaction, member: discord.Member, message: str):
    try:
        await member.send(message)
        await interaction.response.send_message(
            f"Send message to {member.display_name}", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            f"Couldn't send a message to {member.display_name} (DM closed)", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Something went wrong <:ahh:1414628749026005072>: {e}", ephemeral=True
        )

@bot.tree.command(name="dm_embed", description="Send an embed DM to a user with fields (moderators only)")
@app_commands.checks.has_any_role("Moderator", "Developer - CEO")
@app_commands.describe(
    member="The user you want to DM",
    title="Embed title",
    description="Embed description",
    color="Hex color (e.g. FF0000 for red)",
    fields="Fields in format: name1|value1;name2|value2"
)
async def dm_embed_command(
    interaction: discord.Interaction,
    member: discord.Member,
    title: str,
    description: str,
    color: str = "5865F2",
    fields: str = None
):
    try:
        # Convert color hex string
        try:
            embed_color = int(color, 16)
        except ValueError:
            embed_color = 0x5865F2

        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        embed.set_footer(text=f"Sent by {interaction.user.display_name}")

        # Parse fields if provided
        if fields:
            try:
                for field in fields.split(";"):
                    name, value = field.split("|", 1)
                    embed.add_field(name=name.strip(), value=value.strip(), inline=False)
            except Exception:
                await interaction.response.send_message(
                    "Invalid field format. Use `name1|value1;name2|value2`", ephemeral=True
                )
                return

        await member.send(embed=embed)
        await interaction.response.send_message(
            f"Embed sent to {member.display_name}", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            f"Could not DM {member.display_name} (DMs closed)", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Something went wrong: {e}", ephemeral=True
        )

@bot.command(name="server_update")
@commands.has_any_role("Moderator", "Developer - CEO")
async def server_update(ctx: commands.Context):
    channel = discord.utils.get(ctx.guild.text_channels, name="bot-commands")
    if channel:
        embed = discord.Embed(
            title="Server Update Soon",
            description="The server will update in 10 seconds. Please save your work.",
            color=next_rarity_colors["legendary"]
        )
        await channel.send(embed=embed)
        await ctx.send(f"{ctx.author.mention}, update message sent to #bot-commands.")
    else:
        await ctx.send(f"{ctx.author.mention}, no #bot-commands channel found.")

@bot.command(name="server_restart")
@commands.has_any_role("Moderator", "Developer - CEO")
async def server_restart(ctx: commands.Context):
    channel = discord.utils.get(ctx.guild.text_channels, name="bot-commands")
    if channel:
        embed = discord.Embed(
            title="Server Restart Soon",
            description="The server will restart in 10 seconds. Please save your work.",
            color=next_rarity_colors["unusual"]
        )
        await channel.send(embed=embed)
        await ctx.send(f"{ctx.author.mention}, restart message sent to #bot-commands.")
    else:
        await ctx.send(f"{ctx.author.mention}, no #bot-commands channel found.")

@bot.command(name="sync")
@commands.has_permissions(administrator=True)
async def sync_command(ctx: commands.Context):
    try:
        print(f"Syncing commands for guild: {ctx.guild.name} ({ctx.guild.id})")
        # Sync alleen voor de huidige server
        guild = ctx.guild
        synced = await bot.tree.sync(guild=guild)
        await ctx.send(f"Slash commands synced! Synced {len(synced)} commands in this server.")
        print(f"Synced {len(synced)} command(s) in guild {guild.name} ({guild.id})")
    except Exception as e:
        await ctx.send(f"Failed to sync slash commands: {e}")
        print(f"Error syncing commands: {e}")


bot.run(TOKEN)
