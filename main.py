from fastapi import FastAPI
import requests
import time
import math
import os
from dotenv import load_dotenv
import threading

# ---------------- ENV SETUP ----------------
load_dotenv()

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

GET_UPDATES = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
SEND_MESSAGE = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ---------------- MATERIAL DATA ----------------
material_strength = {
    "concrete": 25,
    "steel": 250,
    "wood": 40
}

# ---------------- CALCULATION FUNCTION ----------------
def calculate_beam_capacity(length, width, depth, material):

    width = width / 1000
    depth = depth / 1000

    Z = (width * depth**2) / 6

    f = material_strength.get(material.lower(), 25)

    M = f * Z

    w = (8 * M) / (length**2)

    return round(w, 2)


# ---------------- TELEGRAM SEND MESSAGE ----------------
def send_message(chat_id, text):

    requests.post(
        SEND_MESSAGE,
        json={
            "chat_id": chat_id,
            "text": text
        }
    )


# ---------------- BOT LISTENER ----------------
def telegram_listener():

    print("Bot Started Listening...")

    offset = None

    while True:

        params = {"timeout": 100}

        if offset:
            params["offset"] = offset

        response = requests.get(GET_UPDATES, params=params).json()

        if "result" in response:

            for update in response["result"]:

                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"].get("text", "")
                chat_id = update["message"]["chat"]["id"]

                # Welcome message
                if message.lower() in ["/start", "hi", "hello"]:
                    reply = """
👷 Welcome to Beam Load Estimator Bot

Send beam details in this format:

length,width,depth,material

Example:
5,300,450,concrete

Units:
Length → meters
Width → mm
Depth → mm
"""
                    send_message(chat_id, reply)
                    continue

                # Calculation
                try:

                    values = message.split(",")

                    length = float(values[0])
                    width = float(values[1])
                    depth = float(values[2])
                    material = values[3]

                    capacity = calculate_beam_capacity(
                        length, width, depth, material
                    )

                    reply = f"""
🏗 Beam Load Estimation

Length: {length} m
Width: {width} mm
Depth: {depth} mm
Material: {material}

Estimated Safe Load:
{capacity} kN/m
"""

                except:
                    reply = """
❌ Invalid input.

Use format:
length,width,depth,material

Example:
5,300,450,concrete
"""

                send_message(chat_id, reply)

        time.sleep(1)


# ---------------- START LISTENER THREAD ----------------
@app.on_event("startup")
def start_bot():

    thread = threading.Thread(target=telegram_listener)
    thread.start()


# ---------------- ROOT ----------------
@app.get("/")
def home():
    return {"message": "Beam Load Estimator Telegram Bot Running"}