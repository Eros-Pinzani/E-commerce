import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ecommerce.settings")  # Cambia con il tuo progetto
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "eros.pinzani@edu.unifi.it"
password = "190568Ab@"
first_name = "Eros"
last_name = "Pinzani"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    with open("superuser_created.txt", "w") as f:
        f.write("✅ Superuser creato.\n")
else:
    with open("superuser_created.txt", "w") as f:
        f.write("⚠️ Superuser già esistente.\n")
