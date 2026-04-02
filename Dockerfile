FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y alsa-utils
RUN apt-get update && apt-get install -y tzdata
ENV TZ=America/Sao_Paulo
COPY monitor.py .

#VOLUME ["/data"]

CMD ["python", "monitor.py"]
