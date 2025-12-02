import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ===== CONFIG =====
VERIFY_TOKEN = "move_driver_whatsapp_bot"  # mesmo token do painel Meta

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")       # vai no Render
WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID") # vai no Render


def enviar_whatsapp(to, text):
    """
    Envia mensagem de texto usando a WhatsApp Cloud API
    """
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        print("ERRO: faltando environment variables no Render")
        return

    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    r = requests.post(url, json=payload, headers=headers)
    print("Resposta do WhatsApp:", r.status_code, r.text)


@app.route("/", methods=["GET"])
def home():
    return "Bot ON - Move Driver (Render)", 200


# ===== VERIFICAÇÃO DO WEBHOOK =====
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Erro de verificação", 403


# ===== RECEBER MENSAGEM =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Webhook recebido:", data)

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]["value"]

        if "messages" in changes:
            msg = changes["messages"][0]
            number = msg["from"]
            text = msg.get("text", {}).get("body", "")

            resposta = f"Recebi sua mensagem: {text}"
            enviar_whatsapp(number, resposta)

    except Exception as e:
        print("Erro ao processar webhook:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
