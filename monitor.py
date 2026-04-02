import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

URL = "https://www.concursosfcc.com.br/concursos/cpupe125/index.html"
CACHE = "/data/cache.json"
INTERVALO = int(os.environ.get("TIME_INTERVAL") or 1800)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17 Safari/605.1.15"
]


def enviar_email(mensagem):
    remetente = os.environ.get("EMAIL_USER")
    senha = os.environ.get("EMAIL_PASS")
    destinatario = os.environ.get("EMAIL_TO")

    msg = MIMEText(mensagem)
    msg["Subject"] = "🚨 Nova publicação FCC"
    msg["From"] = remetente
    msg["To"] = destinatario

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remetente, senha)
        server.send_message(msg)


def alerta_visual():
    for _ in range(5):
        logger.info("\033[1;31m")
        logger.info("🚨🚨🚨 NOVA PUBLICAÇÃO DETECTADA 🚨🚨🚨")
        logger.info("\033[0m")
        time.sleep(0.3)


def beep():
    open("/data/alert.txt", "w").close()


def baixar_pagina(url, tentativas=3):
    for tentativa in range(tentativas):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
                "Connection": "keep-alive"
            }

            logger.info(f"🌐 Acessando com UA rotativo...")

            response = requests.get(
                url,
                headers=headers,
                timeout=60
            )

            response.raise_for_status()
            return response.text

        except Exception as e:
            logger.info(f"⚠️ tentativa {tentativa+1} falhou: {e}")
            time.sleep(10)

    raise Exception("Falha ao acessar página após retries")


def obter_publicacoes():
    html = baixar_pagina(URL)
    soup = BeautifulSoup(html, "html.parser")

    itens = []

    for a in soup.find_all("a"):
        texto = a.get_text(strip=True)
        href = a.get("href")

        if not texto:
            continue

        if any(x in texto.lower() for x in ["edital", "resultado", "convocação", "retificação"]):
            itens.append({
                "texto": texto,
                "href": href
            })

    return itens


def carregar_cache():
    if not os.path.exists(CACHE):
        return []
    with open(CACHE, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_cache(data):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


logger.info("🚀 Monitor FCC iniciado...")
logger.info("👀 Aguardando alterações...\n")

while True:
    try:
        antigos = carregar_cache()
        atuais = obter_publicacoes()

        novos = [i for i in atuais if i not in antigos]

        if novos:
            mensagem = "\n\n".join(
                f"{item['texto']}\n{item['href']}"
                for item in novos
            )

            enviar_email(mensagem)
            alerta_visual()
            beep()

            logger.info("\n🚨🚨🚨 NOVA PUBLICAÇÃO DETECTADA 🚨🚨🚨")
            logger.info(f"⏰ {datetime.now()}\n")

            for item in novos:
                logger.info(f"📄 {item['texto']}")
                logger.info(f"🔗 {item['href']}\n")

            salvar_cache(atuais)

        else:
            logger.info(f"✔ Sem mudanças - {datetime.now()}")

    except Exception as e:
        logger.info(f"❌ erro: {e}")

    # delay com pequena variação para evitar bloqueio
    sleep_time = INTERVALO + random.randint(-60, 60)
    logger.info(f"⏳ Aguardando {sleep_time}s...\n")
    time.sleep(sleep_time)