# github.com/hitem
# !enablecleaner CHANNEL_ID
# !setcleaningtime TIME
# !testcleaner TIME

import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import asyncio
import pytz
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# Define intents
intents = discord.Intents.default()
intents.message_content = True

# Retrieve bot token from environment variable
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

# Define CET timezone
CET = pytz.timezone('Europe/Stockholm')

# File to store cleaner state
STATE_FILE = '/path/to/your/bot/cleaner/cleaner_state.json'

# Load initial state
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error loading state file: {e}")
            return {}
    else:
        return {}

state = load_state()

# List of roles allowed to execute commands
MODERATOR_ROLES = ["Admins", "Super Friends"]  # Add role names as needed

# Initialize bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store cleaning tasks for each channel
cleaning_tasks = {}

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')
    for channel_id in state.keys():
        if channel_id not in cleaning_tasks:
            cleaning_tasks[channel_id] = tasks.loop(hours=1)(clean_old_messages)
        try:
            cleaning_tasks[channel_id].start(channel_id)
            logger.info(f"Started cleaner task for channel ID: {channel_id}")
        except RuntimeError:
            logger.warning(f"Task for channel ID: {channel_id} is already running")
    logger.info("Bot is ready to receive commands")

async def clean_old_messages(channel_id):
    config = state.get(str(channel_id))
    if not config:
        logger.warning(f"No configuration found for channel ID: {channel_id}")
        return

    # Find the guild and channel explicitly
    channel = None
    for guild in bot.guilds:
        for ch in guild.text_channels:
            if ch.id == int(channel_id):
                channel = ch
                break
        if channel:
            break

    if not channel:
        logger.warning(f"Channel not found: {channel_id}")
        return

    now = datetime.now(CET)  # Use timezone-aware datetime
    time_limit = now - timedelta(hours=config['time_to_keep'])

    deleted_count = await delete_messages(channel, time_limit)

    if deleted_count > 0:
        logger.info(f"Cleaned {deleted_count} messages in channel {channel_id}")
    else:
        logger.info(f"No messages to clean in channel {channel_id}")

def has_moderator_role(ctx):
    return any(role.name in MODERATOR_ROLES for role in ctx.author.roles)

@bot.command(name='enablecleaner')
async def enable_cleaner(ctx, channel_id: int):
    if has_moderator_role(ctx):
        try:
            state[str(channel_id)] = {'time_to_keep': 24}  # Default to 24 hours
            save_state()
            if channel_id not in cleaning_tasks:
                cleaning_tasks[channel_id] = tasks.loop(hours=1)(clean_old_messages)
            try:
                cleaning_tasks[channel_id].start(channel_id)
            except RuntimeError:
                logger.warning(f"Task for channel ID: {channel_id} is already running")
            await ctx.send(f"Cleaner enabled for channel ID: {channel_id}")
            logger.info(f"Cleaner enabled for channel ID: {channel_id} by {ctx.author}")
        except Exception as e:
            await ctx.send(f"Error enabling cleaner: {e}")
            logger.error(f"Error enabling cleaner for channel ID: {channel_id}: {e}")
    else:
        await ctx.send("You do not have the required permissions to use this command.")
        logger.warning(f"{ctx.author} tried to enable cleaner without required permissions")

@enable_cleaner.error
async def enable_cleaner_error(ctx, error):
    await ctx.send(f"An error occurred: {error}")
    logger.error(f"An error occurred in enable_cleaner: {error}")

@bot.command(name='setcleaningtime')
async def set_cleaning_time(ctx, hours: int):
    if has_moderator_role(ctx):
        channel_id = ctx.channel.id
        if hours not in range(1, 73):  # Allow time from 1 to 72 hours
            await ctx.send("Invalid time. Please set it to a value between 1 and 72 hours.")
            logger.warning(f"Invalid cleaning time set by {ctx.author}: {hours} hours")
            return

        if str(channel_id) in state:
            state[str(channel_id)]['time_to_keep'] = hours
            save_state()
            await ctx.send(f"Cleaning time set to {hours} hours for channel ID: {channel_id}")
            logger.info(f"Cleaning time set to {hours} hours for channel ID: {channel_id} by {ctx.author}")
        else:
            await ctx.send(f"Cleaner is not enabled for channel ID: {channel_id}")
            logger.warning(f"{ctx.author} tried to set cleaning time for a channel that is not enabled: {channel_id}")
    else:
        await ctx.send("You do not have the required permissions to use this command.")
        logger.warning(f"{ctx.author} tried to set cleaning time without required permissions")

@set_cleaning_time.error
async def set_cleaning_time_error(ctx, error):
    await ctx.send(f"An error occurred: {error}")
    logger.error(f"An error occurred in set_cleaning_time: {error}")

@bot.command(name='testcleaner')
async def test_cleaner(ctx, time: str):
    if has_moderator_role(ctx):
        channel_id = ctx.channel.id
        if str(channel_id) not in state:
            await ctx.send("Cleaner is not enabled.")
            logger.warning(f"{ctx.author} tried to test cleaner on a channel that is not enabled: {channel_id}")
            return

        channel = ctx.channel

        if time.lower() == 'all':
            time_limit = None
            await ctx.send("Deleting all messages in the channel.")
            logger.info(f"Testing cleaner: deleting all messages in channel {channel_id}")
        else:
            try:
                hours = int(time)
                now = datetime.now(CET)  # Use timezone-aware datetime
                time_limit = now - timedelta(hours=hours)
                await ctx.send(f"Deleting messages older than {hours} hours.")
                logger.info(f"Testing cleaner: deleting messages older than {hours} hours in channel {channel_id}")
            except ValueError:
                await ctx.send("Invalid time. Please specify 'all' or a number of hours.")
                logger.error(f"Invalid time specified by {ctx.author} for testcleaner: {time}")
                return

        deleted_count = await delete_messages(channel, time_limit)
        await ctx.send(f"Test complete. Deleted {deleted_count} messages.")
        logger.info(f"Test cleaner completed. Deleted {deleted_count} messages in channel {channel_id}")
    else:
        await ctx.send("You do not have the required permissions to use this command.")
        logger.warning(f"{ctx.author} tried to test cleaner without required permissions")

@test_cleaner.error
async def test_cleaner_error(ctx, error):
    await ctx.send(f"An error occurred: {error}")
    logger.error(f"An error occurred in test_cleaner: {error}")

@bot.command(name='checkpermissions')
async def check_permissions(ctx):
    permissions = ctx.author.guild_permissions
    await ctx.send(f"Your permissions: {permissions}")
    logger.info(f"{ctx.author} checked their permissions")

@bot.command(name='listchannels')
async def list_channels(ctx):
    if has_moderator_role(ctx):
        guild = ctx.guild
        channels_info = ""
        for channel in guild.text_channels:
            channels_info += f"Channel: {channel.name} (ID: {channel.id})\n"
        await ctx.send(f"Channels in this guild:\n{channels_info}")
    else:
        await ctx.send("You do not have the required permissions to use this command.")
        logger.warning(f"{ctx.author} tried to list channels without required permissions")

async def delete_messages(channel, time_limit):
    deleted_count = 0

    async for message in channel.history(limit=None, before=time_limit):
        try:
            await message.delete()
            deleted_count += 1
        except discord.Forbidden:
            logger.error(f"Forbidden error deleting message {message.id}")
        except discord.HTTPException as e:
            logger.error(f"HTTP error deleting message {message.id}: {e}")
        await asyncio.sleep(1)  # Sleep to handle rate limits

    return deleted_count

def save_state():
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
        logger.info("State saved successfully")
    except Exception as e:
        logger.error(f"Error saving state file: {e}")

# Run the bot
bot.run(TOKEN)
