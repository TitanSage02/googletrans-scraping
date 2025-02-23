from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random
from tqdm import tqdm

def setup_driver():
    """Initialise le driver Firefox et ouvre Google Traduction."""
    options = Options()
    options.headless = True  # Mettre True pour exécuter sans ouvrir la fenêtre
    
    driver = webdriver.Firefox(service=Service(), options=options)
    
    driver.get(f"https://translate.google.com/?hl={SOURCE}&sl=auto&tl={TARGET}&op=translate")
    
    return driver


def translate_to_fon(driver, text: str, timeout: int = 10) -> str:
    """
    Envoie le texte à traduire dans Google Traduction et récupère la traduction.
    
    :param driver: Instance du driver Selenium.
    :param text: Texte à traduire.
    :param timeout: Temps maximum d'attente en secondes.
    :return: Texte traduit.
    """
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
        print(f"❌ Erreur lors de la traduction de '{text}':", e)
        return ""


SOURCE = "fr"
TARGET = "fon"

if __name__ == '__main__':
    driver = setup_driver()

    try:
        textes = ["Cache toi", "Bonjour", "Comment allez-vous ?"]
        traductions = []
        for texte in tqdm(textes, desc="Traduction en cours"):
            traduction = translate_to_fon(driver, texte)
            traductions.append(traduction)

            # Temps de pause aléatoire [1, 3] entre chaque traduction pour éviter d'être bloqué par Google
            time.sleep(random.random() % 3)

        traductions = dict(zip(textes, traductions))
        print(traductions)
    
    except Exception as e:
        print("Erreur lors de la traduction :", e)
   
    finally:
        driver.quit()