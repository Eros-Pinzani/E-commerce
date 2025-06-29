import os
import django

# Imposta la variabile d'ambiente per il settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecommerce.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "eros.pinzani@edu.unifi.it"
password = "190568Ab@"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser creato.")
else:
    print("Superuser già esistente.")
