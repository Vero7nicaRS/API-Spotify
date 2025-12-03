import os 
import requests
import json
from dotenv import load_dotenv 

# Se cargan variables del .env
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# -------------------------------------------------------------------------------------
#                                      OBJETIVOS
#                                     -----------
# 1º Solicitar un Token a Spotify para poder realizar búsquedas con dicho token.
# 2º Usar Token para buscar canciones (tracks)
# 3º Usar Token para buscar cantantes (artist)
# -------------------------------------------------------------------------------------

# 1) Solicitar un Token a Spotify para poder realizar búsquedas con dicho token.
def get_token():
     url = "https://accounts.spotify.com/api/token"
     data = {"grant_type": "client_credentials"}
     auth = (CLIENT_ID, CLIENT_SECRET)
     try:
          response = requests.post(url=url,data=data,auth=auth)
          # Aparece un error si el código es distinto de 200 (OK)
          response.raise_for_status() 
          json_data = response.json() # Serializa el objeto a formato JSON
     #     print(f"Loaded data: {json_data}")

     # Poner que la visualización sea más agradable a la vista: ese diccionario se convierta a JSON 
          data_pretty = json.dumps(json_data, indent=4)
          print(f"Pretty Printed Data: {data_pretty}")
          # Json devolverá: "acces_token", "token_type", "expires_in"
          return json_data["access_token"]
     except:
          requests.exceptions.Timeout
          print("No se ha podido conectar con Spotify")
          return None

#2) Usar Token para buscar canciones (tracks)
#  Se encarga de buscar canciones en Spotify por el nombre de la canción
def search_track_song(query):
     token = get_token()
     url = "https://api.spotify.com/v1/search"
     params = {
          "q"       : query,
          "type"    : "track",
          "limit"   : 1 # Devuelve solo 1 resultados de la búsqueda
     }
     header = {
          "Authorization": f"Bearer {token}"
     }

     try:
          response = requests.get(url,params=params, headers=header)
     # Aparece un error si el código es distinto de 200 (OK)
          response.raise_for_status() 
          json_data = response.json()
     #    print(f"Loaded data: {json_data}")

     # Poner que la visualización sea más agradable a la vista: ese diccionario se convierta a JSON 
          data_pretty = json.dumps(json_data, indent=4) # Serializa el objeto a formato JSON
          print(f"Pretty Printed Data: {data_pretty}")
          return json_data
     except:
          requests.exceptions.Timeout
          print("No se ha podido conectar con Spotify")
          return None




#2) Usar Token para buscar canciones (tracks)
#  Se encarga de buscar canciones en Spotify por el nombre de la canción
def search_artist(query):
     token = get_token()
     url = "https://api.spotify.com/v1/search"
     params = {
          "q"       : query,
          "type"    : "artist",
          "limit"   : 1 # Devuelve solo 1 resultados de la búsqueda
     }
     header = {
          "Authorization": f"Bearer {token}"
     }
     try:
          response = requests.get(url,params=params, headers=header)
     # Aparece un error si el código es distinto de 200 (OK)
          response.raise_for_status() 
          json_data = response.json()
     #    print(f"Loaded data: {json_data}")

     # Poner que la visualización sea más agradable a la vista: ese diccionario se convierta a JSON 
          data_pretty = json.dumps(json_data, indent=4) # Serializa el objeto a formato JSON
          print(f"Pretty Printed Data: {data_pretty}")
          return json_data
     except:
          requests.exceptions.Timeout
          print("No se ha podido conectar con Spotify")
          return None





if __name__ == "__main__":
    search_track_song("La bachata")
#    search_artist("Adele")