#!/bin/bash
# Script pour connecter au repository GitHub
# Remplacez USERNAME par votre nom d'utilisateur GitHub

cd "/Users/vincentr/Desktop/Kaggle Compétitions"

# Configuration Git (une seule fois)
git config user.name "Vincent R"
git config user.email "votre-email@example.com"  # Mettez votre vrai email GitHub

# Connecter au repository GitHub (remplacez USERNAME)
git remote add origin https://github.com/USERNAME/kaggle-santa-2025.git

# Renommer la branche en main si nécessaire
git branch -M main

# Pousser vers GitHub
git push -u origin main

echo "✓ Tout est pushé sur GitHub !"
