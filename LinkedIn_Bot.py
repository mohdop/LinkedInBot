from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

# Configuration
linkedin_username = 'votre mail'
linkedin_password = 'votre mot de pass linkedin'


#ne remplacez pas [Nom] et [Nom de l'entreprise], le bot le fera de lui même
message_template = (
    "Bonjour [Nom]\n\n"
    "Je m'appelle [Remplacez par votre nom] et je cherche [remplacez par le poste auquel vous postulez]. J'aimerais discuter des opportunités chez [Nom de l'entreprise]. Merci !\n\n"
    "Cordialement,"
    "[Votre nom complet]"
)

# Initialisation du navigateur
driver = webdriver.Chrome()  # Assurez-vous que le chemin vers ChromeDriver est correct
driver.get('https://www.linkedin.com/login')

# Connexion
try:
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'username'))
    )
    password_input = driver.find_element(By.ID, 'password')
    username_input.send_keys(linkedin_username)
    password_input.send_keys(linkedin_password)
    password_input.send_keys(Keys.RETURN)
except Exception as e:
    print(f'Erreur lors de la connexion: {e}')
    driver.quit()
    exit()

# Attendre que la page se charge
time.sleep(5)

# Chercher des recruteurs
try:
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Rechercher"]'))
    )
    search_box.send_keys('Recruteur France')
    search_box.send_keys(Keys.RETURN)
except Exception as e:
    print(f'Erreur lors de la recherche: {e}')
    driver.quit()
    exit()

# Attendre que la page se charge
time.sleep(5)

# Filtrer par personnes
try:
    people_filter = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Personnes"]'))
    )
    people_filter.click()
except Exception as e:
    print(f'Erreur lors du filtrage par personnes: {e}')
    driver.quit()
    exit()

# Attendre que la page se charge
time.sleep(10)  # Augmenter le délai d'attente pour s'assurer que la page se charge complètement

def send_invitations_on_current_page():
    try:
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'reusable-search__result-container'))
        )

        print(f'Nombre de résultats trouvés: {len(results)}')  # Ajouter une impression pour vérifier le nombre de résultats trouvés
        
        for result in results:
            try:
                # Vérifier si le bouton "Message" est présent, ce qui signifie que vous êtes déjà connecté
                try:
                    message_button = result.find_element(By.XPATH, './/button//span[text()="Message"]/ancestor::button')
                    if message_button:
                        print('Bouton "Message" trouvé, passage au résultat suivant.')
                        continue
                except NoSuchElementException:
                    # Si le bouton "Message" n'est pas trouvé, c'est normal, continuez avec le processus de connexion
                    pass

                # Vérifier si le bouton est "Connecter" et non "Suivre"
                connect_button = result.find_element(By.XPATH, './/button//span[text()="Connecter"]/ancestor::button')
                if not connect_button:
                    print('Bouton "Connecter" non trouvé, passage au résultat suivant.')
                    continue

                # Récupérer le nom du recruteur
                recruiter_name = result.find_element(By.CLASS_NAME, 'entity-result__title-text').text

                # Récupérer le nom de l'entreprise
                company_name = result.find_element(By.CLASS_NAME, 'entity-result__primary-subtitle').text

                print(f'Envoi d\'une invitation à {recruiter_name} de {company_name}')  # Ajouter une impression pour chaque invitation envoyée
                
                # Cliquez sur le bouton de connexion
                connect_button.click()
                
                # Attendre que le modal de connexion apparaisse
                time.sleep(2)
                
                # Cliquez sur ajouter une note
                add_note_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//button//span[text()="Ajouter une note"]/ancestor::button'))
                )
                add_note_button.click()
                
                # Créer le message personnalisé
                personalized_message = message_template.replace('[Nom]', recruiter_name).replace("[Nom de l'entreprise]", company_name)
                
                # Remplir le message personnalisé en morceaux de 200 caractères ou moins
                message_parts = [personalized_message[i:i+200] for i in range(0, len(personalized_message), 200)]
                
                for part in message_parts:
                    # Remplir le message dans la zone de texte
                    note_textarea = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'custom-message'))
                    )
                    note_textarea.send_keys(part)
                    
                    # Envoyer l'invitation
                    send_invitation_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//button//span[text()="Envoyer"]'))
                    )
                    send_invitation_button.click()
                    
                    # Attendre un peu avant de passer à la prochaine
                    time.sleep(2)

            except Exception as e:
                print(f'Erreur lors de la connexion avec un recruteur: {e}')
                continue

    except Exception as e:
        print(f'Erreur lors de la récupération des résultats: {e}')

# Naviguer à travers les pages
while True:
    send_invitations_on_current_page()
    #avant d'appuyer sur Entrée, cliquez sur le terminal
    input("Cliquez sur le bouton 'Suivant' et appuyez sur Entrée pour continuer...")
    time.sleep(5)  # Attendre que la nouvelle page se charge

# Fermer le navigateur
driver.quit()
