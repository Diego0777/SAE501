#!/bin/bash

# Vérifier si la base existe et n'est pas vide
if [ ! -f "data/tvseries.db" ] || [ ! -s "data/tvseries.db" ]; then
    echo "🔄 Création de la base de données..."
    python database/import_data_sqlite.py
else
    echo "✅ Base de données déjà présente"
fi

# Démarrer le serveur
echo "🚀 Démarrage du serveur..."
gunicorn serve_api_sqlite:app --bind 0.0.0.0:$PORT
