import asyncio
import requests
import json
import os
import datetime
from telegram import Bot

# URL of the JSON data
url = "https://ssc.gov.in/api/general-website/portal/records?page=1&limit=10&contentType=notice-boards&key=createdAt&order=DESC&pageType=filter&isAttachment=true&attributes=id,headline,examId,contentType,redirectUrl,startDate,endDate,language,createdAt&queryKey=startDate,endDate&customKey=createdAt&language=english"

# Base URL for attachments
base_url = "https://ssc.gov.in/api/attachment/"

# Telegram Bot Token
telegram_bot_token = "6741806828:AAFcSnSJlKgfnW5gWsE7bJEitHjejZYXSL0"

# Telegram Channel ID
telegram_channel_id = "@government_job_hunter"

# File to store sent message IDs
sent_messages_file = 'sent_messages.json'

# Fetching the JSON data
response = requests.get(url)
data = response.json()

# Extracting today's date
today_date = datetime.date.today().strftime("%Y-%m-%d")

# Extracting the required information and creating valid URLs
new_data = []
for item in data.get("data", []):
    headline = item.get("headline")
    created_at = item.get("createdAt").split("T")[0]  # Extracting date only
    attachments = item.get("attachments", [])
    for attachment in attachments:
        path = attachment.get("path").replace("\\", "/").replace(" ", "%20")
        valid_url = f"{base_url}{path}"
        if created_at == today_date:  # Check if data is from today
            new_data.append({
                "title": headline,
                "Updated on": created_at,
                "link": valid_url
            })

# Load existing data if the file exists
file_path = 'ssc.json'
if os.path.exists(file_path) and os.stat(file_path).st_size != 0:
    with open(file_path, 'r') as file:
        existing_data = json.load(file)
else:
    existing_data = []

# If today's data is fetched and not already sent, send it to the Telegram channel
if new_data:
    # Save the combined data back to the JSON file
    combined_data = new_data + existing_data
    with open(file_path, 'w') as file:
        json.dump(combined_data, file, indent=4)

    # Load sent message IDs if the file exists
    if os.path.exists(sent_messages_file) and os.stat(sent_messages_file).st_size != 0:
        with open(sent_messages_file, 'r') as file:
            sent_messages = json.load(file)
    else:
        sent_messages = []

    # Send message to Telegram channel for new data
    async def send_message():
        bot = Bot(token=telegram_bot_token)
        message = "Today's Fetched Data:\n"
        for item in new_data:
            message += f"{item['title']} - {item['link']}\n"
        sent_message = await bot.send_message(chat_id=telegram_channel_id, text=message)
        print("Data successfully fetched and sent to Telegram channel.")

        # Add sent message ID to the list and save it
        sent_messages.append(sent_message.message_id)
        with open(sent_messages_file, 'w') as file:
            json.dump(sent_messages, file, indent=4)

    asyncio.run(send_message())
else:
    print("No new data fetched today.")
