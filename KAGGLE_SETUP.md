# 🎄 Configuration Kaggle pour Santa 2025

## ✅ Étapes pour utiliser le notebook sur Kaggle

### 1. Préparer le repository GitHub

Votre `solution.py` doit être accessible publiquement sur GitHub :

```bash
# Dans votre terminal local
cd "/Users/vincentr/Desktop/Kaggle Compétitions"

# Ajouter solution.py au repository
git add solution.py
git commit -m "Add solution.py for Kaggle competition"
git push origin main
```

**Vérifiez que le fichier est accessible ici :**
```
https://raw.githubusercontent.com/meiilia/finance-notebooks/main/solution.py
```

### 2. Uploader le notebook sur Kaggle

1. Allez sur : https://www.kaggle.com/competitions/santa-2024/code
2. Cliquez sur **"New Notebook"**
3. En haut à droite, cliquez sur **"File" → "Import Notebook"**
4. Uploadez `Santa.ipynb` depuis votre dossier local

### 3. Configurer les données sur Kaggle

Dans le notebook Kaggle, ajoutez les données de compétition :

1. Cliquez sur **"Add Data"** (à droite)
2. Cherchez **"Santa 2024"** 
3. Ajoutez le dataset de la compétition

### 4. Exécuter le notebook

Le notebook va automatiquement :
- ✅ Détecter qu'il tourne sur Kaggle
- ✅ Télécharger `solution.py` depuis GitHub
- ✅ Utiliser les bons chemins (`/kaggle/input/santa-2024/`)
- ✅ Générer `submission.csv` dans `/kaggle/working/`

### 5. Soumettre le résultat

Une fois l'exécution terminée :
1. Le fichier `submission.csv` sera dans la section **"Output"**
2. Cliquez sur **"Submit to Competition"**
3. Votre score apparaîtra sur le leaderboard !

---

## 🔧 Configuration automatique dans le notebook

Le notebook détecte automatiquement l'environnement :

```python
# Détection Kaggle
is_kaggle = os.path.exists("/kaggle/working")

if is_kaggle:
    # Télécharge solution.py depuis GitHub
    urllib.request.urlretrieve(GITHUB_SOLUTION_URL, "/kaggle/working/solution.py")
    INPUT_DIR = Path("/kaggle/input/santa-2024")
    OUTPUT_PATH = Path("/kaggle/working/submission.csv")
else:
    # Mode local
    INPUT_DIR = Path("/Users/vincentr/Desktop/Kaggle Compétitions")
    OUTPUT_PATH = INPUT_DIR / "submission.csv"
```

---

## 📝 Mise à jour de solution.py

Chaque fois que vous modifiez `solution.py` localement :

```bash
# 1. Testez localement
cd "/Users/vincentr/Desktop/Kaggle Compétitions"
jupyter notebook Santa.ipynb  # Vérifiez que ça marche

# 2. Commitez sur GitHub
git add solution.py
git commit -m "Update optimization parameters"
git push origin main

# 3. Sur Kaggle
# Cliquez sur "Run All" - le nouveau code sera téléchargé automatiquement
```

---

## ⚠️ Troubleshooting

### Erreur : "Cannot download solution.py"
- Vérifiez que le repo est **public** sur GitHub
- Testez l'URL dans un navigateur : https://raw.githubusercontent.com/meiilia/finance-notebooks/main/solution.py

### Erreur : "Module solution not found"
- Le téléchargement a échoué, vérifiez la connexion GitHub
- Alternative : Uploadez `solution.py` manuellement comme "Utility Script" dans Kaggle

### Timeout Kaggle (>9 heures)
- Réduisez les iterations dans la cellule 46 :
  ```python
  final_params = Params(
      iterations_small=200,   # Au lieu de 300
      iterations_medium=400,  # Au lieu de 500
      iterations_large=600    # Au lieu de 800
  )
  ```

---

## 🚀 Workflow complet

1. **Développement local** : Testez et améliorez le code
2. **Push sur GitHub** : `git push origin main`
3. **Run sur Kaggle** : Le notebook télécharge automatiquement la dernière version
4. **Soumission** : Le `submission.csv` est généré automatiquement

**Avantage** : Vous pouvez modifier `solution.py` sans re-uploader le notebook à chaque fois !

---

## 📊 URLs importantes

- **Repository GitHub** : https://github.com/meiilia/finance-notebooks
- **solution.py (raw)** : https://raw.githubusercontent.com/meiilia/finance-notebooks/main/solution.py
- **Competition Kaggle** : https://www.kaggle.com/competitions/santa-2024

Bonne chance ! 🎄🎅
