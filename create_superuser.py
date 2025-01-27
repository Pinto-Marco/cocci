# create_superuser.py
import os
from django.contrib.auth import get_user_model

User = get_user_model()

# Prendi i dati dell'utente dalle variabili di ambiente
username = os.getenv("SUPERUSER_USERNAME", "admin")
email = os.getenv("SUPERUSER_EMAIL", "admin@admin.com")
password = os.getenv("SUPERUSER_PASSWORD", "admin")

# Crea il superuser solo se non esiste
if not User.objects.filter(username=username).exists():
    print(f"Creazione del superuser: {username}")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print(f"Superuser {username} esiste già.")
