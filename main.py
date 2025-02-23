from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random
from tqdm import tqdm


def setup_driver():
    """Initialise le driver Firefox et ouvre Google Traduction."""
    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(f"https://translate.google.com/details?hl={SOURCE}&sl=auto&tl={TARGET}&op=translate")
    
    return driver

def translate_to_fon(driver, text: str, timeout: int = 10) -> str:
    """
    Envoie le texte à traduire dans Google Traduction et récupère la traduction.
    
    :param driver: Instance du driver Selenium.
    :param text: Texte à traduire.
    :param timeout: Temps maximum d'attente en secondes.
    :return: Texte traduit.
    """
    # Récupérer le champ de saisie et effacer le contenu précédent
    input_box = driver.find_element(By.CLASS_NAME, "er8xn")
    input_box.clear()
    input_box.send_keys(text)

    # Attendre que l'élément contenant la traduction soit présent
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, "HwtZe"))
    )
    # Pause courte pour s'assurer que la traduction est affichée
    time.sleep(2)
    return element.text


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
            time.sleep(random.randint(1, 3))

        traductions = dict(zip(textes, traductions))
        print(traductions)
    
    except Exception as e:
        print("Erreur lors de la traduction :", e)
   
    finally:
        driver.quit()
