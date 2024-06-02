# Discord Cleaner Bot

A Discord bot that automatically cleans messages in specified channels after a certain period of time.

## Features

- Automatically delete messages in specified channels after a set amount of time.
- Supports different cleaning intervals for different channels.
- Commands to enable the cleaner, set cleaning intervals, and manually test the cleaner.
- Permission checks to ensure only users with specified roles can execute commands.
- The scheduled cleanup runs once per hour.

## Prerequisites

- A server to run the bot on
- Python 3.6 or higher
- Discord.py library
- Pytz library
- Linux system to run the bot (rasberry or similiar)
- App setup in Discord Developer portal (Scroll down to bottom to see how)

## Installation

1. Update your package list and install Python and pip:
    ```sh
    sudo apt update
    sudo apt install python3 python3-pip
    ```

2. Install the required Python packages:
    ```sh
    pip3 install discord.py
    pip3 install pytz
    ```

3. Clone this repository.

   Change following lines in `CleanBotman.py`:

     - Set your timezone (the server where you are running the bot):
    ```sh
    # Define CET timezone
    CET = pytz.timezone('Europe/Stockholm')
    ```
    - Set your path to the `cleaner_state.json`
    ```sh
    # File to store cleaner state
    STATE_FILE = '/path/to/your/bot/cleaner/cleaner_state.json'
    ```
    - and set the Roles on your Discord server you want to allow using the bot commands:
    ```sh
    # List of roles allowed to execute commands
    MODERATOR_ROLES = ["Admins", "Super Friends"]  # Add role names as needed
    ```

4. Ensure the bot file and state file have the correct permissions:
    ```sh
    chmod 755 /path/to/your/CleanBotman.py
    chmod 755 /path/to/your/cleaner_state.json
    ```

5. Create a systemd service file to run the bot: (this will autostart the bot after server restart or downtime)

    ```sh
    sudo touch /etc/systemd/system/discord-cleaner-bot.service
    sudo nano /etc/systemd/system/discord-cleaner-bot.service
    ```

    Add the following content to the file:

    ```ini
    [Unit]
    Description=Discord Cleaner Bot
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 /path/to/your/CleanBotman.py
    WorkingDirectory=/path/to/your/
    Restart=always
    User=your_username
    Environment="DISCORD_BOT_TOKEN=your_bot_token_here"
    StandardOutput=journal
    StandardError=journal

    [Install]
    WantedBy=multi-user.target
    ```

    Replace `/path/to/your/` with the actual path to your bot file and state file, and `your_username` with your actual username of the account running the bot on server. And `your_bot_token_here` with your generated bot token from Discord Developer portal.

6. Reload systemd to recognize the new service and start it:
    ```sh
    sudo systemctl daemon-reload
    sudo systemctl start discord-cleaner-bot
    sudo systemctl enable discord-cleaner-bot
    ```

## Usage

### Commands

- `!enablecleaner CHANNEL_ID`  
  Enable the cleaner for a specific channel. The default cleaning interval is 24 hours.

- `!setcleaningtime HOURS`  
  Set the cleaning interval for the current channel. `HOURS` must be between 1 and 72.

- `!testcleaner TIME`  
  Manually test the cleaner in the current channel. `TIME` can be `all` to delete all messages or a number of hours.

- `!checkpermissions`  
  Check your permissions. This wont show rolename, but it will show your permission id.

- `!listchannels`  
  List all channels + channel_id on the current server (discord calls it guild).

## Logging

The bot uses systemd journal for logging. To view the logs, use:
```sh
sudo journalctl -u discord-cleaner-bot -f
```
![log](https://github.com/hitem/CleanBot/assets/8977898/7bd176cb-eaba-4bb1-b07c-1419157ce34c)

## Limitations
Discord has 14 days message time limitation. If message is older then 14 days, quotas will be enforced - be patient, the bot will retry deleting old messages untill it has completed the task (can take awhile).

## Setup on Discord Developer Portal

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click on "New Application".
3. Enter a name for your bot and click "Create".
4. Go to the "Bot" section and click "Add Bot".
5. Click "Yes, do it!" to confirm.
6. Under the "Token" section, click "Copy" to copy your bot token. This will be used as the `DISCORD_BOT_TOKEN` environment variable.
7. Under "Privileged Gateway Intents", enable "Message Content Intent".
8. Save your changes.

### Invite the Bot to Your Server

1. Go to the "OAuth2" section, then "URL Generator".
2. Under "SCOPES", select "bot".
3. Under "BOT PERMISSIONS", select the permissions your bot needs:\
    `Manage Messages`\
    `Read Messages`\
    `Send Messages`\
    `View Channels`\
    `Read Message History`
4. Copy the generated URL and open it in your browser.
5. Select the server you want to add the bot to and authorize it.


