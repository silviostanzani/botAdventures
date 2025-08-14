import os, httpx
from fastapi import FastAPI, Request, Header, BackgroundTasks

BOT_TOKEN = os.environ["BOT_TOKEN"]          # set in Railway
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") # optional

app = FastAPI()

@app.get("/")
def health():
    return {"ok": True}

async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )

@app.post("/webhook")
async def webhook(
    request: Request,
    background: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None)
):
    # (optional) verify Telegram's secret header if you set one
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        return {"ok": True}

    update = await request.json()
    msg = update.get("message") or update.get("edited_message")
    if msg:
        chat_id = msg["chat"]["id"]
        text = msg.get("text") or "👋"
        background.add_task(send_message, chat_id, f"You said: {text}")

    # Respond fast; do the heavy work in background
    return {"ok": True}