import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Variáveis de ambiente
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "move_driver_bot")


@app.route("/", methods=["GET"])
def home():
    return "Move Driver WhatsApp Bot ON", 200


# Webhook do WhatsApp (verificação + mensagens)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verificação do webhook pelo painel do Meta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token de verificação inválido", 403

    if request.method == "POST":
        data = request.get_json()
        print("Webhook recebido:", data)

        # Pega a mensagem de texto recebida
        try:
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            messages = value.get("messages", [])

            if messages:
                message = messages[0]
                from_number = message["from"]  # telefone do cliente
                message_type = message["type"]

                if message_type == "text":
                    text = message["text"]["body"]
                    responder_mensagem(from_number, text)
        except Exception as e:
            print("Erro ao processar webhook:", e)

        return jsonify({"status": "ok"}), 200


def responder_mensagem(to_number: str, texto_recebido: str):
    """
    Responde uma mensagem simples pelo WhatsApp Cloud API.
    Por enquanto só manda um texto de confirmação.
    """
    if not WHATSAPP_TOKEN or not PHONE_ID:
        print("Token ou PHONE_ID não configurados.")
        return

    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"

    resposta = f"Recebi sua mensagem: {texto_recebido}\n\nBot Move Driver online ✅"

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": resposta},
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    r = requests.post(url, json=payload, headers=headers)
    print("Resposta da API do WhatsApp:", r.status_code, r.text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
