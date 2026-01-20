import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURATION ---
API_URL = "https://api.spacexdata.com/v4/launches"
RAW_FILE = "raw_spacex.json"
PROCESSED_FILE = "processed_spacex.json"

def fetch_data():
    """Étape 1 : Récupération des données brutes (Extract)"""
    print(f" Connexion à SpaceX ({API_URL})...")
    try:
        # On ajoute un User-Agent pour éviter d'être bloqué
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Sauvegarde brute
        with open(RAW_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"✅ {len(data)} lancements récupérés et sauvegardés dans {RAW_FILE}")
        return data
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return None

def process_data():
    """Étape 2 : Nettoyage (Transform)"""
    print("🧹 Nettoyage des données...")
    
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    clean_list = []
    
    for launch in raw_data:
        # On ignore les lancements futurs (où 'success' est null)
        if launch.get("success") is None:
            continue
            
        # Extraction de l'année (la date est au format "2020-10-24T...")
        date_utc = launch.get("date_utc", "0000")
        year = date_utc[:4] # On garde juste les 4 premiers caractères
        
        info = {
            "name": launch.get("name"),
            "year": int(year),
            "success": "Réussi" if launch.get("success") else "Échec",
            "details": launch.get("details", "Pas de détails")
        }
        clean_list.append(info)
            
    # Sauvegarde propre
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_list, f, indent=4)
    
    print(f"✅ Données nettoyées ({len(clean_list)} lancements passés) sauvegardées.")
    return clean_list

def visualize_data():
    """Étape 3 : Visualisation (Viz)"""
    print("📊 Génération des graphiques...")
    
    # Chargement avec Pandas
    df = pd.read_json(PROCESSED_FILE)
    
    # Configuration du style visuel
    sns.set_theme(style="darkgrid")
    
    # --- GRAPHIQUE 1 : Nombre de lancements par année ---
    plt.figure(figsize=(12, 6))
    
    # On compte le nombre de lignes par année
    ax = sns.countplot(data=df, x="year", color="#3498db")
    
    plt.title("Nombre de lancements SpaceX par Année", fontsize=16)
    plt.xlabel("Année")
    plt.ylabel("Nombre de lancements")
    plt.xticks(rotation=45) # Penche les dates pour lire
    plt.tight_layout()
    plt.show()
    
    # --- GRAPHIQUE 2 : Taux de réussite (Camembert/Pie Chart) ---
    plt.figure(figsize=(8, 8))
    
    # On compte combien de réussites vs échecs
    success_counts = df["success"].value_counts()
    
    plt.pie(success_counts, labels=success_counts.index, autopct='%1.1f%%', 
            colors=["#2ecc71", "#e74c3c"], startangle=90, explode=(0.1, 0))
            
    plt.title("Taux de Réussite Global des Missions SpaceX", fontsize=16)
    plt.show()

# --- LANCEMENT ---
if __name__ == "__main__":
    data = fetch_data()
    if data:
        process_data()
        visualize_data()