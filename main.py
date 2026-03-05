from fastapi import FastAPI, Request
import math

app = FastAPI()

# Telegram Bot Token
BOT_TOKEN = "AAG-TJ4pkExgKRxKuCOP7X_TIpYaBqtQJa0"

# Telegram API URL
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


# Material Strength (Approximate values in MPa)
material_strength = {
    "concrete": 25,
    "steel": 250,
    "wood": 40
}


def calculate_beam_capacity(length, width, depth, material):
    
    # Convert mm to meters
    width = width / 1000
    depth = depth / 1000

    # Section modulus
    Z = (width * depth**2) / 6

    # Material strength
    f = material_strength.get(material.lower(), 25)

    # Bending Moment Capacity
    M = f * Z

    # Uniform Load (approx formula)
    w = (8 * M) / (length**2)

    return round(w, 2)


@app.get("/")
def home():
    return {"message": "Beam Load Estimator Telegram Bot Running"}


@app.post("/webhook")
async def telegram_webhook(request: Request):

    data = await request.json()

    try:
        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        # Expected Input Format
        # length,width,depth,material
        # Example: 5,300,450,concrete

        values = message.split(",")

        length = float(values[0])
        width = float(values[1])
        depth = float(values[2])
        material = values[3]

        capacity = calculate_beam_capacity(length, width, depth, material)

        reply = f"""
Beam Load Estimation

Length: {length} m
Width: {width} mm
Depth: {depth} mm
Material: {material}

Estimated Safe Load: {capacity} kN/m
"""

    except:
        reply = """
Invalid input.

Use format:
length,width,depth,material

Example:
5,300,450,concrete
"""

    import requests

    requests.post(
        TELEGRAM_API,
        json={
            "chat_id": chat_id,
            "text": reply
        }
    )

    return {"status": "ok"}