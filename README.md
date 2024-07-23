# Discord Cleaner Bot

A Discord bot that automatically cleans messages in specified channels after a certain period of time.

## Features

- Automatically delete messages in specified channels after a set amount of time.
- Supports different cleaning intervals for different channels.
- Commands to enable the cleaner, set cleaning intervals, and manually test the cleaner.
- Permission checks to ensure only users with specified roles can execute commands.
- The scheduled cleanup runs every 15 minutes (Default).
- Limit the amount of inputs to prevent spam/DoS type scenarios.

## Prerequisites

- A server to run the bot on
- Python 3.6 or higher
- Linux system to run the bot (Raspberry Pi or similar)
- App setup in Discord Developer portal (Scroll down to bottom to see how)

## Installation

1. Ensure Python and pip are installed:
    ```sh
    sudo apt update
    sudo apt install python3 python3-pip
    ```

2. Clone this repository:
    ```sh
    git clone https://github.com/hitem/CleanBot.git
    cd CleanBot
    ```

3. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Install `pipenv` within the virtual environment:
    ```sh
    pip install pipenv
    ```

5. Install the required Python packages using `pipenv`:
    ```sh
    pipenv install
    ```

6. Create a `.env` file following the format of `.env_example`. Add your DISCORD_BOT_TOKEN accordingly (make sure you have completed the Prerequisites)

7. Run the bot:
    ```sh
    pipenv run python3 CleanBotman.py
    ```

## Running as a Service
Here are some extra step to run your bot as a service on the server incase of reboot or similiar scenarios.

1. Create a systemd service file:
    ```sh
    sudo nano /etc/systemd/system/discord-cleaner-bot.service
    ```

2. Add the following content to the file, make sure you change `/path/to/your/` to correct directory.
    ```ini
    [Unit]
    Description=Discord Cleaner Bot
    After=network.target
    
    [Service]
    Type=simple
    User=your_username
    WorkingDirectory=/path/to/your/CleanBot
    ExecStart=/bin/bash -c 'source /path/to/your/CleanBot/venv/bin/activate && pipenv run python3 /path/to/your/CleanBot/CleanBotman.py'
    Restart=on-failure
    StandardOutput=journal
    StandardError=journal
    
    [Install]
    WantedBy=multi-user.target
    ```

3. Reload systemd to recognize the new service:
    ```sh
    sudo systemctl daemon-reload
    ```

4. Enable the service to start on boot:
    ```sh
    sudo systemctl enable discord-cleaner-bot
    ```

5. Start the service:
    ```sh
    sudo systemctl start discord-cleaner-bot
    ```

6. Check the service status:
    ```sh
    sudo systemctl status discord-cleaner-bot
    ```

## Commands

- `!enablecleaner CHANNEL_ID`  
  Enable the cleaner for a specific channel. The default cleaning interval is 24 hours.

- `!setcleaningtime HOURS`  
  Set the cleaning interval for the current channel. `HOURS` must be between 1 and 72.

- `!testcleaner TIME`  
  Manually test the cleaner in the current channel. `TIME` can be `all` to delete all messages or a number of hours.

- `!checkpermissions`  
  Check your permissions. This won't show the role name, but it will show your permission ID.

- `!listchannels`  
  List all channels + channel_id on the current server (discord calls it guild).

- `!cleanersetting`  
  Check if the cleaner is enabled and what the current timer setting is for the current channel. It returns "Cleaner is enabled and timer is set to xx hours" if enabled, otherwise it will state that the cleaner is not enabled for the channel.

- `!cleanerhelp`  
  Lists all the bot-commands available.

## Logging

The bot uses systemd journal for logging. To view the logs, use:
```sh
sudo journalctl -u discord-cleaner-bot -f
```


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
3. Under "BOT PERMISSIONS", select the permissions your bot needs:
    - `Manage Messages`
    - `Read Messages`
    - `Send Messages`
    - `View Channels`
    - `Read Message History`
4. Copy the generated URL and open it in your browser.
5. Select the server you want to add the bot to and authorize it.

