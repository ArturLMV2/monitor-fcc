import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

URL = "https://www.concursosfcc.com.br/concursos/cpupe125/index.html"
CACHE = "/data/cache.json"
INTERVALO = 60  # 5 minutos
def alerta_visual():
    for _ in range(5):
        print("\033[1;31m")
        print("🚨🚨🚨 NOVA PUBLICAÇÃO DETECTADA 🚨🚨🚨")
        print("\033[0m")
        time.sleep(0.3)

def beep():
    open("/data/alert.txt", "w").close()

def obter_publicacoes():
    r = requests.get(URL, timeout=30)
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
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


print("��� Monitor FCC iniciado...")
print("��� Aguardando alterações...\n")

while True:
    try:
        antigos = carregar_cache()
        atuais = obter_publicacoes()

        novos = [i for i in atuais if i not in antigos]

        if novos:
            alerta_visual()
            beep()
            print("\n��������� NOVA PUBLICAÇÃO DETECTADA ���������")
            print(f"⏰ {datetime.now()}\n")

            for item in novos:
                print(f"��� {item['texto']}")
                print(f"��� {item['href']}\n")

            salvar_cache(atuais)

        else:
            print(f"✔ Sem mudanças - {datetime.now()}")

    except Exception as e:
        print(f"❌ erro: {e}")

    time.sleep(INTERVALO)
