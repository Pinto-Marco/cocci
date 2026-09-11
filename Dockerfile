FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

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

#
COPY --from=frontend-build /app/static/dist ./static/dist

# Il DB sqlite vive sul volume montato, non nell'immagine.
ENV DB_PATH=/app/db/db.sqlite3

# Static raccolti a build time: l'immagine è già completa e il deploy ha
# un passaggio in meno che può fallire. SECRET_KEY fittizia: serve solo
# perché Django si avvii, non finisce in nessun file raccolto.
RUN SECRET_KEY=build-time-only python manage.py collectstatic --noinput

# Espone la porta su cui gira Django
EXPOSE 8000

# Comando per avviare Django
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] zio pesca

# Comando di avvio
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "cocci.wsgi"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "gevent", "--timeout", "240", "--graceful-timeout", "240", "--keep-alive", "5", "cocci.wsgi"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--worker-class", "gevent", "--timeout", "240", "--graceful-timeout", "240", "--keep-alive", "5", "cocci.wsgi"]
