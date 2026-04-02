import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText


URL = "https://www.concursosfcc.com.br/concursos/cpupe125/index.html"
CACHE = "cache.json"   # <-- sem /data
INTERVALO = int(os.environ.get("TIME_INTERVAL") or 1800)


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


def obter_publicacoes():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=60)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

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
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    print("🚀 Monitor FCC iniciado...")
    print(f"⏰ {datetime.now()}")

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

            print("🚨 NOVA PUBLICAÇÃO DETECTADA!")

            for item in novos:
                print(f"📄 {item['texto']}")
                print(f"🔗 {item['href']}")

            salvar_cache(atuais)

        else:
            print("✔ Sem mudanças")

    except Exception as e:
        print(f"❌ erro: {e}")


if __name__ == "__main__":
    main()