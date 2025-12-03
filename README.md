# API Usuarios, Gustos musicales y Spotify
# ----------------------------------------

# ----------
#  OBJETIVOS
# ----------
Desarollar una API que permita gestionar los usuarios y sus gustos musicales (cantantes y canciones favoritas), los cuales están almacenados en una base de datos MySQL.

Además, se puede consultar más información acerca de sus gustos musicales en Spotify.

Este proyecto se ha implementando utilizando Flask, Python y MySQL.

# -----------
# INSTALACIÓN
# -----------

1. Crear un entorno virtual (recomendado)

python -m venv venv

2. Activarlo

venv\Scripts\activate

3. Instalar dependencias

pip install -r requirements.txt

4. Configurar variables de Spotify

SPOTIFY_CLIENT_ID= ...

SPOTIFY_CLIENT_SECRET= ...

5. Ejecutarlo

python app.py

Se obtiene como resultado: http://127.0.0.1:5000/

----------------------------------------

# -----------
#  ENDPOINTS
# -----------
# Usuarios
# --------
- GET /users: 

Obtiene la lista de todos los usuarios.

- POST /users
    
Crea uno o varios usuarios.
    
    Body:
    	
        users: lista de objetos con el campo:
        
            nombre (string, obligatorio)

- PUT /users/<id>

Modifica el nombre del usuario existente.
Se requiere de autorización para realizar la modificación del usuario.

    Headers:
	    Authorization: 1234
    Body:
        nombre (string, obligatorio)

- DELETE /users

Elimina un usuario por ID.

    Query params:
        id (entero, obligatorio)

 
# Cantantes favoritos
# -------------------
Ruta de cantantes favoritos de un determinado usuario: /users/{id}cantantes_favoritos

- GET /users/{id}/cantantes_favoritos

Obtiene la lista de cantantes favoritos del usuario.

- POST /users/{id}/cantantes_favoritos

Añade uno o varios cantantes favoritos al usuario.

Se requiere de autorización para añadir cantantes favoritos a un usuario.
    
    Headers:
        Authorization: 1234
    
    Body:
        cantantes_favoritos: lista de nombres (obligatorio)

- PUT /users/{id}/cantantes_favoritos

  Reemplaza completamente la lista de cantantes favoritos del usuario.

  Se requiere de autorización para realizar la modificación de los cantantes favoritos de un usuario.

    	Headers:
        	Authorization: 1234
  
    	Body:
        	cantantes_favoritos: lista de nombres (obligatorio)

- DELETE /users/{id}/cantantes_favoritos

  Elimina un cantante favorito concreto del usuario.

  Se requiere de autorización para realizar la eliminación de los cantantes favoritos de un usuario.

    	Headers:
        	Authorization: 1234

    	Query params:
        	cantante: nombre del cantante (obligatorio)


# -------------------
# Canciones favoritas
# -------------------

Ruta de canciones favoritas de un determinado usuario: /users/{id}/canciones_favoritas

- GET /users/{id}/canciones_favoritas
  
  Obtiene la lista de canciones favoritas del usuario.

- POST /users/{id}/canciones_favoritas
  
  Añade una o varias canciones favoritas al usuario.

  Se requiere de autorización para añadir canciones favoritas a un usuario.

    	Headers:
        	Authorization: 1234
    	Body:
        	canciones_favoritas: lista de nombres (obligatorio)


- PUT /users/{id}/canciones_favoritas
    
  Reemplaza completamente las canciones favoritas del usuario.

  Se requiere de autorización para realizar la modificación de las canciones favoritas de un usuario.
    
    	Headers:
        	Authorization: 1234

    	Body:
        	canciones_favoritas: lista de nombres (obligatorio)

- DELETE /users/{id}/canciones_favoritas
    
  Elimina una canción favorita concreta del usuario.

  Se requiere de autorización para realizar la eliminación de las canciones favoritas de un usuario.
    
    	Headers:
        	Authorization: 1234

    	Query params:
       	 	cancion: nombre de la canción (obligatorio)

# -----------------------
# Integración con spotify
# -----------------------

- GET /users/{id}/artistas_spotify

  Obtiene información de Spotify acerca de los cantantes favoritos del usuario.

  La llamada a la API de Spotify se realiza con “search_artist()”.

- GET /users/{id}/canciones_spotify

  Obtiene información de Spotify acerca de las canciones favoritas del usuario.

  La llamada a la API de Spotify se realiza con “search_artist()”.
 
