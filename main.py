import discord
import asyncio
from discord.ext import commands
import os
from datetime import datetime, timedelta
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

# Initialize bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
user_join_dates = defaultdict(lambda: None)

def is_suspicious_url(content):
    return "http" in content and not any(website in content for website in VAGUELY_OKAY_WEBSITES)

def has_mention(message):
    return message.mention_everyone

def is_new_user(user_id):
    join_date = user_join_dates[user_id]
    if join_date:
        return (datetime.utcnow() - join_date) <= timedelta(hours=1)
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

@bot.event
async def on_message(message):
    if message.channel.id != BOT_CHANNEL:
        if message.channel.id == HONEY_POT_CHANNEL and message.author.id != SPAM_EATER_ID:
            await message.delete()
            await message.guild.ban(message.author, reason="Ban by bot honey potted :D")
        if is_suspicious_url(message.content) or has_mention(message):
            if is_new_user(message.author.id):
                await warn_user(message.channel, message.author)
                await message.delete()
                await log_actions(message.content, message.author.name)
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    user_join_dates[member.id] = datetime.utcnow()

@bot.event
async def on_message_edit(before, after):
    await on_message(after)

# Start the bot
bot.run(os.getenv('DISCORD_TOKEN'))
