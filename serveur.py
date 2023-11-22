
import http.server
import socketserver
import requests
from simple_om2m import createContentInstance

PORT = 9999

class MyHttpRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Logique pour récupérer l'état actuel du bouton via une requête RETRIEVE
        button_state = retrieve_button_status()

        # Modifier l'état de la lumière en fonction de l'état du bouton récupéré
        if button_state:
            if button_state == 'ON':
                createContentInstance("admin:admin", "http://127.0.0.1:8080/~/in-cse/in-name/Light/DATA", "ON")
            else:
                createContentInstance("admin:admin", "http://127.0.0.1:8080/~/in-cse/in-name/Light/DATA", "OFF")
        else:
            print("Impossible de récupérer l'état du bouton. Traitement par défaut ou autre action nécessaire.")

        # Répondre au client HTTP
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Action effectuee avec succes !')

    def do_POST(self):
        try:
            # Récupérer les informations de l'en-tête et les données du contenu
            length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']
            request_id = self.headers['X-M2M-RI']
            post_data = self.rfile.read(length)

            # Traitement des données POST (exemple)
            print("Requête POST reçue avec les données suivantes :")
            print(f"Type de contenu : {content_type}")
            print(f"Identifiant de requête : {request_id}")
            print(f"Données du contenu : {post_data.decode('utf-8')}")

            # Répondre avec un code de réussite (200 OK)
            self.send_response(200)
            self.send_header('X-M2M-RSC', '2000')
            self.send_header('X-M2M-RI', request_id)
            self.end_headers()

        except Exception as e:
            # En cas d'erreur, répondre avec un code d'erreur (par exemple, 500 - Erreur interne du serveur)
            print("Une erreur s'est produite lors du traitement de la requête POST :", e)
            self.send_response(500)
            self.end_headers()

# Fonction pour effectuer une requête RETRIEVE pour obtenir l'état actuel du bouton
def retrieve_button_status():
    try:
        # Effectuer une requête RETRIEVE pour obtenir l'état du bouton
        # Assurez-vous d'utiliser les détails fournis par votre serveur OneM2M pour effectuer la requête

        # Exemple de requête RETRIEVE vers le serveur OneM2M pour récupérer l'état du bouton
        response = requests.get("http://localhost:8080/webui/index.html?ri=id-in&or=CAdmin", 
                                params={
                                    'to': '/Button/Button_Status',
                                    'originator': 'Cmyself',
                                    'requestIdentifier': '123',
                                    'releaseVersionIndicator': '3',
                                    'filterUsage': 'conditionalRetrieval',
                                    'filterCriteria': {'lbl': ['tag:greeting']},
                                    'resultContent': 'childResources'
                                })

        if response.status_code == 200:
            # Supposons que la réponse contient l'état du bouton au format texte
            return response.text
        else:
            print(f"La requête RETRIEVE pour l'état du bouton a échoué avec le code de statut : {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print("Une erreur s'est produite lors de la requête RETRIEVE :", e)
        return None

Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serveur HTTP en cours d'exécution sur le port", PORT)
    httpd.serve_forever()
