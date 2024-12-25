# MADE BY Coder-Boner (https://github.com/coder-boner/)
# Repo (https://github.com/coder-boner/Poll-Bot)
# v1.0.0

import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# API Key and server IDs with nicknames
api_key = "API_KEY"
servers = {
    # Server id is found in the URL when accessing the server
    # The Nick Name can be set to anything as it is just to help people viewing it on the discord side (it can also help you identify servers)
    "SERVER_ID": "NICK NAME",
}

# Set this to your channel id
CHANNEL_ID = CHANNEL_ID

# Variable to store the status message
status_message = None
# Session for aiohttp
session = None

@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    update_server_status.start()
    print(f'{bot.user} has connected to Discord!')
    print('Fetching channel! Please wait...')

@bot.event
async def on_disconnect():
    if session:
        await session.close()

@tasks.loop(seconds=15)
async def update_server_status():
    global status_message
    embed = discord.Embed(title="Server Status", color=discord.Color.blue())

    for server_id, nickname in servers.items():
        # Change the panel.example.com to your panels address, DO NOT CHANGE ANY THING ELSE
        url = f"https://panel.example.com/api/client/servers/{server_id}/resources"
        url2 = f"https://panel.example.com/api/client/servers/{server_id}"
        headers = {
            'Accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        try:
            async with session.get(url2, headers=headers, timeout=10) as response:

                if response.status != 200:
                    raise Exception(f"Failed to fetch server info: {response.status}")

                data = await response.json()

                # TOTAL CPU
                total_cpu = data['attributes']['limits']['cpu']

                # TOTAL RAM
                MB_total_memory = data['attributes']['limits']['memory']
                total_memory = int(MB_total_memory) / 1024

                # IP AND PORT
                ip = data['attributes']['sftp_details']['ip']
                port = data['attributes']['sftp_details']['port']

            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch server resources: {response.status}")
                data = await response.json()

                # CURRENT SERVER SATE
                current_state = data['attributes']['current_state']

                #CPU USAGE
                cpu_usage = data['attributes']['resources']['cpu_absolute']

                # STORAGE TOTAL
                storage_bytes = data['attributes']['resources']['disk_bytes']
                storage_GB_total = int(storage_bytes) / 1024 / 1024 / 1024

                # RAM USAGE
                ram_usage = data['attributes']['resources']['memory_bytes']
                ram_mb_usage = int(ram_usage) / 1024 / 1024 / 1024

                # UPTIME
                uptime_milliseconds = data['attributes']['resources']['uptime']
                def convert_milliseconds(milliseconds):
                    seconds = milliseconds // 1000
                    minutes, seconds = divmod(seconds, 60)
                    hours, minutes = divmod(minutes, 60)
                    days, hours = divmod(hours, 24)
                    return f"{days}d {hours}h {minutes}m {seconds}s"

                uptime = convert_milliseconds(uptime_milliseconds)

                # Displays if hte server is up or not
                if current_state == 'running':
                    better_state = "🟢 Running"
                elif current_state == 'starting':
                    better_state = '🟡 Starting'
                elif current_state == 'stopping':
                    better_state = '🟠 Stopping'
                elif current_state == 'offline':
                    better_state = "🔴 Offline"
                else:
                    better_state = "⚪ Unknown"

                # The embed on the discord side (BE CAREFUL AS THIS CAN BREAK AND KILL THE BOTS USE)
                embed.add_field(
                    name=f"{nickname}",
                    value=(
                        f"Status: {better_state}\n"
                        f"CPU: {int(cpu_usage)}%/{total_cpu}%\n"
                        f"RAM: {int(ram_mb_usage)}GB/{total_memory:.1f}GB\n"
                        f"Storage: {storage_GB_total:.1f}GB\n"
                        f"Uptime: {uptime}\n"
                        f"IP: {ip}:{port}"
                    ),
                    inline=False
                )

        except asyncio.TimeoutError:
            embed.add_field(name=f"{nickname}", value="Timeout exceeded", inline=False)
        except Exception as e:
            embed.add_field(name=f"{nickname}", value=f"An error occurred: {str(e)}", inline=False)

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        if status_message:
            await status_message.edit(embed=embed)
        else:
            status_message = await channel.send(embed=embed)

# Replace 'BOT_TOKEN' with your actual Discord bot token
bot.run('BOT_TOKEN')
