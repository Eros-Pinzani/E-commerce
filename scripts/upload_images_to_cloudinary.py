# Script di esempio per caricare immagini su Cloudinary
import cloudinary
import cloudinary.uploader
import os
from pathlib import Path

# Configurazione Cloudinary
cloudinary.config(
    cloud_name="dlaj3hne2",
    api_key="534671878168598",
    api_secret="XUd3tiPVJlg15yVIV1EI5WGpL2A"
)

# Directory delle immagini
media_dir = Path("media")

# Carica tutte le immagini
for root, dirs, files in os.walk(media_dir):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, media_dir)

            # Carica su Cloudinary mantenendo la stessa struttura di cartelle
            folder_path = os.path.dirname(relative_path).replace("\\", "/")

            result = cloudinary.uploader.upload(
                file_path,
                folder=folder_path,
                public_id=os.path.splitext(os.path.basename(file))[0]
            )
            print(f"Caricato {file_path} come {result['secure_url']}")