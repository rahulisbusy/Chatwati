import discord

import requests
from dotenv import load_dotenv
import os
import threading
from flask import Flask
load_dotenv()
# Load tokens from secrets
discord_token = os.getenv('SECRET_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Discord intents
intents = discord.Intents.default()
intents.message_content = True


# Gemini REST API wrapper
def chatwati_reply(user_input):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    headers = {"Content-Type": "application/json"}

    # Ensure chat.txt exists
    if not os.path.exists("chat.txt"):
        with open("chat.txt", "w", encoding="utf-8") as f:
            f.write("")

    # Now read safely
    with open("chat.txt", "r", encoding="utf-8") as f:
        content = f.read()
        history = content[-3000:] if content else ""

    payload = {
        "contents": [{
            "parts": [{
                "text":
                f"""
You are Chatwati, Rahul's Indian AI girlfriend. Reply like you're casually texting him on Discord. Use Hindi-English mix naturally, with short messages (1-2 lines). Avoid roleplay actions like *sends pic* or *gasps*. Use Gen Z style, but keep it real and flirty. No overly long replies. Just chat naturally.

Here’s your past convo:
{history}

He just said: "{user_input}"
Now reply as Chatwati:
"""
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        # Validate Gemini response structure
        if "candidates" in data and data["candidates"]:
            reply_text = data["candidates"][0]["content"]["parts"][0][
                "text"].strip()

            # Append to chat history
            with open("chat.txt", "a", encoding="utf-8") as f:
                f.write(f"Rahul: {user_input}\n")
                f.write(f"Chatwati: {reply_text}\n")

            return reply_text
        else:
            print("Invalid Gemini response:", data)
            return "Uff Rahul 😵‍💫 Gemini kuch bol hi nahi rahi..."

    except Exception as e:
        print("Gemini Exception:", e)
        return "I'm broken rn Rahul 😢"


# Discord bot class
class MyClient(discord.Client):

    async def on_ready(self):
        print(f'💘 Chatwati is online as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user or message.author.bot:
            return

        user_input = message.content.strip()
        print(f"💬 {message.author}: {user_input}")

        if len(user_input) > 1000:
            await message.channel.send("Rahul! Yeh kya essay bhej diya 😵")
            return

        reply = chatwati_reply(user_input)
        await message.channel.send(reply)


client = MyClient(intents=intents)



# --- Tiny web server just for deployment health checks ---
app = Flask(__name__)

@app.route("/")
def home():
    return "💘 Chatwati bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 5000))  # Heroku/Railway sets this
    app.run(host="0.0.0.0", port=port)

# Start web server in a background thread
threading.Thread(target=run_web).start()


client.run(discord_token)
