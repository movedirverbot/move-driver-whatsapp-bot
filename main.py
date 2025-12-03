import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# ───────────────────────────────────────────────
# Carrega variáveis do Render (Environment vars)
# ───────────────────────────────────────────────
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

# Rota básica (opcional, só para teste)
@app.route("/", methods=["GET"])
def home():
    return "Bot ON - Move Driver", 200


# ───────────────────────────────────────────────
# VERIFICAÇÃO DO WEBHOOK (GET)
# Meta chama isso somente na configuração
# ───────────────────────────────────────────────
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Erro de verificação", 403


# ───────────────────────────────────────────────
# RECEBIMENTO DE MENSAGENS DO WHATSAPP (POST)
# ───────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.json
    print("💬 Mensagem recebida:", data)
    return jsonify({"status": "ok"}), 200


# ───────────────────────────────────────────────
# Iniciar servidor no Render
# ───────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
