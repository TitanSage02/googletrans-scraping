import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random
from tqdm import tqdm
import logging

# Configuration
SOURCE = "fr"
TARGET = "fon"
INPUT_CSV = "input.csv"
OUTPUT_CSV = "output.csv"
MAX_RETRIES = 3
SLEEP_RANGE = (1, 3)  # Secondes entre les requêtes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_driver():
    """Initialise le driver Firefox et ouvre Google Traduction."""
    options = Options()
    options.headless = True  # Mettre True pour exécuter sans ouvrir la fenêtre
    options.set_preference("intl.accept_languages", "fr-FR,fr")
    options.set_preference("general.useragent.override", 
                           "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0")
    
    driver = webdriver.Firefox(service=Service(), options=options)
    
    driver.get(f"https://translate.google.com/?hl={SOURCE}&sl=auto&tl={TARGET}&op=translate")
    
    return driver


def translate_text(driver, text: str, timeout: int = 10) -> str:
    """
    Envoie le texte à traduire dans Google Traduction et récupère la traduction.
    
    :param driver: Instance du driver Selenium.
    :param text: Texte à traduire.
    :param timeout: Temps maximum d'attente en secondes.
    :return: Texte traduit.
    """

    if pd.isna(text) or not text.strip():
        return ""
    
    for attempt in range(MAX_RETRIES):
        try:
            # Récupérer le champ de saisie
            input_box = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "er8xn"))
            )
            input_box.clear()
            input_box.send_keys(text)

            # Récupérer l'ancien élément contenant la traduction (s'il existe)
            try:
                old_translation = driver.find_element(By.CLASS_NAME, "HwtZe")
            except:
                old_translation = None  # Pas d'ancienne traduction

            # Attendre la mise à jour du texte (éviter les résultats obsolètes)
            if old_translation:
                WebDriverWait(driver, timeout).until(
                    EC.staleness_of(old_translation)
                )

            # Récupérer la nouvelle traduction
            new_translation = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "HwtZe"))
            )

            return new_translation.text  # Renvoyer la traduction

        except Exception as e:
            logger.warning(f"Tentative {attempt + 1} échouée pour : '{text}'. Erreur : {str(e)}")
            driver.refresh()
            time.sleep(2)

    logger.error(f"Échec de traduction après {MAX_RETRIES} tentatives pour : '{text}'")
    return ""

def process_csv():
    """Traitement du fichier CSV."""
    # Charger les données
    df = pd.read_csv(INPUT_CSV)
    df["translate"] = ""  # Ajout colonne vide

    # Initialiser le driver
    driver = setup_driver()

    try:
        # Traduction avec barre de progression
        for idx in tqdm(df.index, desc="Traduction des utterances"):
            text = df.at[idx, "utterance"]
            
            # Traduire seulement si non vide
            if pd.notna(text) and str(text).strip():
                df.at[idx, "translate"] = translate_text(driver, str(text))
                time.sleep(random.uniform(*SLEEP_RANGE))
            else:
                df.at[idx, "translate"] = ""
                
    except KeyboardInterrupt:
        logger.info("Interruption utilisateur - Sauvegarde des résultats partiels...")
    
    finally:
        driver.quit()
        # Sauvegarder les résultats
        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"Fichier sauvegardé : {OUTPUT_CSV}")



if __name__ == '__main__':
    process_csv()
    # driver = setup_driver()

    # try:
    #     textes = ["Cache toi", "Bonjour", "Comment allez-vous ?"]
    #     traductions = []
    #     for texte in tqdm(textes, desc="Traduction en cours"):
    #         traduction = translate_text(driver, texte)
    #         traductions.append(traduction)

    #         # Temps de pause aléatoire [1, 3] entre chaque traduction pour éviter d'être bloqué par Google
    #         time.sleep(random.uniform(1, 3))

    #     traductions = dict(zip(textes, traductions))
    #     print(traductions)
    
    # except Exception as e:
    #     print("Erreur lors de la traduction :", e)
   
    # finally:
    #     driver.quit()