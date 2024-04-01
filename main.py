import discord
import asyncio
from discord.ext import commands
import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Constants
VAGUELY_OKAY_WEBSITES = [
    "github.com",
    "bitbucket.com",
    "stackoverflow.com",
    "pastebin.com",
    "kaggle.com",
    "mit.edu",
    "usc.edu",
]

BOT_CHANNEL = 1091681853603324047
HONEY_POT_CHANNEL = 889466095810011137
SPAM_EATER_ID = 1213171019838128128
#TEST_CHANNEL = 1074146361001386014


# Initialize bot
intents = discord.Intents.all()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
user_join_dates = defaultdict(lambda: None)

def is_suspicious_url(content):
    return "http" in content and not any(website in content for website in VAGUELY_OKAY_WEBSITES)

def has_mention(message):
    return message.mention_everyone

def is_new_user(guild,user_id):
    member = guild.get_member(user_id)
    if member and member.joined_at:
        current_time_utc = datetime.now(timezone.utc)
        is_new_user = (current_time_utc - member.joined_at).total_seconds() <= timedelta(hours=1).total_seconds()
        return is_new_user
    else:
        return True

async def warn_user(channel, member):
    await channel.send(f"Hi {member.mention}, please wait a while after joining before sharing links or mentioning people.")

async def log_actions(content, author_name):
    bot_channel = bot.get_channel(BOT_CHANNEL)
    if bot_channel:
        await bot_channel.send(f"Hey bot team! I found '{content}' from {author_name} suspicious, so I deleted it. :)")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot_channel = bot.get_channel(BOT_CHANNEL)
    if bot_channel:
        await bot_channel.send(f"Hi Friends! I'm online and ready to eat some spam! :D")

@bot.event
async def on_message(message):
    # Check if the message is from the honey pot channel.
    if message.channel.id == HONEY_POT_CHANNEL:
        # Check if the author is not the spam eater.
        if message.author.id != SPAM_EATER_ID:
            await message.delete()  # Delete the message.
            await message.guild.ban(message.author, reason="Ban by bot: Honey pot interaction")  # Ban the user.
            return  # Stop further processing to avoid processing commands or other conditions.
    
    # For other channels, apply different checks.
    else:
        # Check for suspicious URLs or mentions in the message.
        if is_suspicious_url(message.content) or has_mention(message):
            server_guild = bot.get_guild(message.guild.id)
            # Check if the author is a new user.
            if is_new_user(server_guild, message.author.id):
                await warn_user(message.channel, message.author)  # Warn the user.
                await message.delete()  # Delete the message.
                await log_actions(message.content, message.author.name)  # Log the action.
    
    # Process commands if any. This is outside the 'else' block to ensure commands are processed even if the message is from the honey pot channel but by an allowed user (e.g., SPAM_EATER_ID).
    await bot.process_commands(message)

## testing function for additional debugging 
# @bot.event
# async def on_message(message):
#     if message.channel.id == TEST_CHANNEL:
#         if message.author.id != SPAM_EATER_ID:
#             bot_channel = bot.get_channel(BOT_CHANNEL)
#             if bot_channel:
#                 server_guild = bot.get_guild(message.guild.id)
#                 time_bool=show_new_user(server_guild,message.author.id)
#                 await bot_channel.send(f"{message.author.name} typed out this {message.content} and the join date is {time_bool}")

# Start the bot
bot.run(os.getenv('DISCORD_TOKEN'))
