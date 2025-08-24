# Usa un'immagine ufficiale di Python
FROM python:3.11

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di requirements
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gevent

# Copia il resto del codice
COPY . .

# Espone la porta su cui gira Django
EXPOSE 8000

# Comando per avviare Django
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Comando di avvio
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "cocci.wsgi"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "gevent", "--timeout", "240", "--graceful-timeout", "240", "--keep-alive", "5", "cocci.wsgi"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--worker-class", "gevent", "--timeout", "240", "--graceful-timeout", "240", "--keep-alive", "5", "cocci.wsgi"]
