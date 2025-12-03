#Vamos a crear nuestro PRIMER SERVICIO en FLASK
from flask import Flask, request

from configuration.conections import DatabaseConnection
from spotify_request import search_artist, search_track_song

app = Flask(__name__)


# from configuration.conections import DatabaseConnection

# Vamos a crearnos una base de datos para almacenar información: identificador, nombre y gustos musicales del usuario.
# Para ello, se va a crear unos usuarios.
users = [
    {
        "id":1,
        "nombre": "Pepe",
        "cantantes_favoritos": ["Robbie Williams", "Melendi", "Bruno Mars"],
        "canciones_favoritas": ["Leave the Door Open", "Tocado y hundido"]
    },
    {
        "id":2,
        "nombre": "Laura",
        "cantantes_favoritos": ["Paul McCartney", "Adele", "Dua Lipa", "Ed Sheeran"],
        "canciones_favoritas": ["Angels"]
    },
    {
        "id":3,
        "nombre": "Manuel",
        "cantantes_favoritos": ["Elton John"],
        "canciones_favoritas": ["La llorona", "La bachata"]
    }
]

# Conexión con la base de datos
db = DatabaseConnection(
    host="localhost",
    user="root",
    password="mysql",
    database="bd_spotify"
)
# Crear los diferente POINTS / URLS
@app.route('/') # Vamos a crear un endpoint raíz.
def home(): # Cada vez que alguien llame a este endpoint muestre el mensaje "HEllo word"
    return "Hello world!" 

# Vamos a entrar a una API PÚBLICA desde un puerto concreto: http://127.0.0.1:5000
# Para ello, usamos POSTMAN y ponemos el path a donde queremos acceder,
#  en este caso: http://127.0.0.1:5000/  (con la barra al final).

# Ahora vamos a crear diferentes enpoints.
# Método GET --> Obtenemos los usuarios iniciales.
# 1 Creación endpoint
# 2 Debajo del enpoint, se crea la funcionalidad que se quiere.
@app.route('/users', methods=['GET'])
def get_users():
#    return {"users":users}, 200
    cursor = db.get_cursor()
    cursor.execute("SELECT * FROM usuarios;")
    users = cursor.fetchall()
    cursor.close()

    return {"users": users}, 200

# ---------------------------------------------------------- ENDPOINT USERS ----------------------------------------------------------
# Vamos a entrar en el endpoint "/users" para obtener los diferentes usuarios que hay en la base de datos.
# http://127.0.0.1:5000/users
# Método POST --> añadir usuarios
@app.route('/users', methods=['POST'])
def post_user():
    # Se obtiene los datos del JSON.
    data = request.get_json()
    new_users = data.get('users', [])

    if not isinstance(new_users, list) or not new_users:
        return {"message": "Se debe enviar una lista 'users' con usuarios"}, 400

    conn = db.get_connection()
    cursor = conn.cursor()

    inserted_ids = []
    # Se comprueba que se recibe el campo "nombre"
    for user in new_users:
        nombre = user.get("nombre")
        if not nombre:
            return {"message": "Cada usuario debe tener 'nombre'"}, 400

        sql = "INSERT INTO usuarios (nombre) VALUES (%s)"
        cursor.execute(sql, (nombre,))
        inserted_ids.append(cursor.lastrowid)

    conn.commit()
    cursor.close()

    return {
        "message": f"Usuarios añadidos correctamente",
        "ids": inserted_ids
    }, 201



# Método PUT --> modificar usuarios.
# se le indica <tipo: nombre>
@app.route('/users/<int:id>', methods=['PUT'])
def put_user(id):
    authorization = request.headers.get('Authorization')
    if authorization != "1234":
        return {"message": "Sin autorización"}, 401
    # Se obtiene los datos del JSON.
    data = request.get_json()
    nombre = data.get("nombre")
    # Se comprueba que se recibe el campo "nombre"
    if not nombre:
        return {"message": "El campo 'nombre' es obligatorio"}, 400

    conn = db.get_connection()
    cursor = conn.cursor()

    # Actualizar
    sql = "UPDATE usuarios SET nombre = %s WHERE id = %s"
    cursor.execute(sql, (nombre, id))
    conn.commit()
    # Se comprueba si ha habido alguna modificación en las filas de la tabla "usuarios".
    # En este caso, si ha sido actualizada alguna fila. 
    # Por tanto, si no se ha moficado ninguna fila, significa que el usuario no se ha encontrado.
    if cursor.rowcount == 0:
        cursor.close()
        return {"message": f"Usuario '{id}' no encontrado"}, 404

    cursor.close()
    
    return {
        "message": f"Usuarios '{id}' actualizado correctamente",
    }, 201

# Método HEADER (Metido en el PUT)--> parámetros adicionales que le podemos mandar a nuestro servicio.
# Aparte de mandarle la información del usuario, también me vas a pasar un tipo de autorización


# Método DELETE --> eliminar usuarios
@app.route('/users', methods=['DELETE'])
def delete_user():
    user_id = request.args.get("id", type=int) # "request.args" --> Sirve para los Query Params

    if not user_id:
        return {"message": "Falta el parámetro 'id'"}, 400

    conn = db.get_connection()
    cursor = conn.cursor()

    sql = "DELETE FROM usuarios WHERE id = %s"
    cursor.execute(sql, (user_id,))
    conn.commit()
    # Se comprueba si ha habido alguna modificación en las filas de la tabla "usuarios".
    # En este caso, si ha sido eliminada alguna fila. 
    # Por tanto, si no se ha eliminado ninguna fila, significa que el usuario no se ha encontrado.
    if cursor.rowcount == 0:
        cursor.close()
        return {"message": "Usuario no encontrado"}, 404

    cursor.close()
    return {"message": f"Usuario '{user_id}' eliminado correctamente"}, 200



# ---------------------------------------------------------- ENDPOINT CANTANTES FAVORITOS  ----------------------------------------------------------
# Método GET --> obtener cantantes favoritos de un usuario
@app.route('/users/<int:id>/cantantes_favoritos', methods=['GET'])
def get_cantante(id):
    cursor = db.get_cursor()

    # 1. Se comprueba que existe el usuario: 
    # para ello se hace un JOIN de las tablas Usuario y Cantantes favoritos.
    # 
    consulta_sql = """
        SELECT user.id AS usuario_id, 
               user.nombre AS usuario_nombre,
               c_f.nombre AS cantante_favorito
        FROM usuarios user
        LEFT JOIN cantantes_favoritos c_f
            ON c_f.usuario_id = user.id
        WHERE user.id = %s;
    """
    # usuario_id  nombre_usuario cantante_favorito
    # ---------- --------------- ------------------
    #  2                Laura            Dua Lipa 
    #  2                Laura           Ed Sheeran
    #  3                Pepe             Melendi
    #  5                Juan              NULL
    cursor.execute(consulta_sql,(id,))
    filas_usuarios = cursor.fetchall()
    cursor.close()
    # 2. Si no hay fila, significa que el usuario no existe.
    if not filas_usuarios:
        return{
                "message": f"Usuario '{id}' no encontrado",
        },404
    

    # 3. Hay una fila para el usuario, se extrae su información para ver si tiene
    # cantantes favoritos.
    usuario_nombre = filas_usuarios[0]["usuario_nombre"]
    cantantes_favoritos= [] 
    for fila in filas_usuarios: # Se recorren todas las filas del usuario para ver su cantante favorito
        cantante = fila["cantante_favorito"]
        if cantante is not None: 
            cantantes_favoritos.append(cantante)

    # 4. El cantante existe pero no tiene ningún cantante favorito
    if not cantantes_favoritos:
        return {
            "message": f"El usuario '{id}' ({usuario_nombre}) no tiene ningún cantante favorito",
            "cantantes_favoritos": []
        }, 200

    # 5. El cantante existe y tiene cantantes favoritos
    return {
            "cantantes_favoritos": f"Los cantantes favoritos del usuario '{id}' ({usuario_nombre})"
                                    + f" son '{cantantes_favoritos}'"
            }, 200
 
# Método POST --> añadir cantante favorito a un usuario
@app.route('/users/<int:id>/cantantes_favoritos', methods=['POST'])
def post_cantante(id):
    authorization = request.headers.get('Authorization')
    if authorization != "1234":
        return{
            "message": "Sin autorización"
        }
    
    # 1. Se obtiene los datos del JSON.
    data = request.get_json() # {cantantes_favoritos = [....]}
    new_cantantes_favoritas = data.get('cantantes_favoritos', [])

    if not isinstance(new_cantantes_favoritas, list) or not new_cantantes_favoritas:
        return {"message": "Se debe enviar una lista 'cantantes_favoritos' con canciones"}, 400

    # 2. Se conecta a la base de datos.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)

    # 3. Comprobar que el usuario existe
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone() # Devuelve la primera fila.

    if not usuario:
        cursor.close()
        return {
            "message": f"Usuario '{id}' no encontrado"
        }, 404

    # 4. Obtener cantantes favoritos ya existentes para ese usuario para no repetir cantantes en el futuro.
    cursor.execute(
        "SELECT nombre FROM cantantes_favoritos WHERE usuario_id = %s", (id,)
    )
    existentes = []
    filas_existentes = cursor.fetchall() # Devuelve toda la lista 
    #                                          --> {'nombre': 'Robbie Williams'}, 
    #                                              {'nombre': 'Melendi'}
    #  id usuario_id cancion   < < < < filas_existentes
    #   1	1	Robbie Williams
    #   2	1	Melendi
    #   3	2	Adele
    #   3	2	Ed Sheeran
    #   4	3	Elton John
    #   5	3	La bachata
    existentes = set()
    for fila in filas_existentes:
        existentes.add(fila["nombre"])  # --> ["Robbie Williams", "Melendi"]
  
    cantantes_agregados = []
    cantantes_existentes = []

    # 5. Recorrer los nuevos cantantes y decidir si insertar o marcar como repetidos
    for cantante in new_cantantes_favoritas:
        if cantante in existentes: # ¿El cantante ya está en sus cantantes favoritos?
            cantantes_existentes.append(cantante) 
        else:
            cursor.execute( # Añade el cantante a su lista de cantantes favoritos.
                "INSERT INTO cantantes_favoritos (usuario_id, nombre) VALUES (%s, %s)",
                (id, cantante)
            )
            cantantes_agregados.append(cantante)
            existentes.add(cantante)  # Actualizamos los cantantes existentes con los que se han agregado.

    conn.commit()

    # 6. Obtener la lista final de cantantes favoritos
    cursor.execute("SELECT nombre FROM cantantes_favoritos WHERE usuario_id = %s", (id,))
    filas_finales = cursor.fetchall()
    cursor.close()

    lista_final = []
    for fila in filas_finales:
        lista_final.append(fila["nombre"])

    if cantantes_agregados:
        return {
            "message": f"Añadir cantante al usuario '{id}'",
            "cantantes_agregados": cantantes_agregados,
            "cantantes_existentes": cantantes_existentes,
            "cantantes_favoritos": lista_final
        }, 201 
    else:
        return {
            "message": f"Añadir cantante al usuario '{id}'",
            "cantantes_agregados": cantantes_agregados,
            "cantantes_existentes": cantantes_existentes,
            "cantantes_favoritos": lista_final
        }, 200 

# Método PUT --> modificar gustos musicales de un usuario
@app.route('/users/<int:id>/cantantes_favoritos', methods=['PUT'])
def put_cantante(id):

    # Comprobar si el usuario es válido (HEADER)
    authorization = request.headers.get('Authorization')
    if authorization != "1234":
        return{
            "message": "Sin autorización"
        },401
    
    # 1. Se obtiene los datos del JSON.
    user_data = request.get_json() # Se obtiene el BODY del JSON
    mod_cantantes_favoritos = user_data.get('cantantes_favoritos', [])
    
    if not isinstance(mod_cantantes_favoritos, list) or not mod_cantantes_favoritos:
        return {"message": "Se debe enviar una lista 'cantantes_favoritos' con cantantes"}, 400

    # 2. Se conecta a la base de datos.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)

    # 3. Comprobar que el usuario existe
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone() # Devuelve la primera fila.

    if not usuario:
        cursor.close()
        return {
            "message": f"Usuario '{id}' no encontrado"
        }, 404

    # 4. Se eliminan los cantantes favoritos del usuario para reemplazarlos por la nueva lista.
    cursor.execute("DELETE FROM cantantes_favoritos WHERE usuario_id = %s", (id,))

    # 5. Se añaden los nuevos cantantes favoritos.
    for cantante in mod_cantantes_favoritos:
        cursor.execute(
            "INSERT INTO cantantes_favoritos (usuario_id, nombre) VALUES (%s, %s)",
            (id, cantante)
        )

    conn.commit()

    # 6. Se obtiene la lista con los cantantes favoritos.
    cursor.execute(
        "SELECT nombre FROM cantantes_favoritos WHERE usuario_id = %s",
        (id,)
    )
    filas_finales = cursor.fetchall()
    cursor.close()

    lista_final = []
    for fila in filas_finales:
        lista_final.append(fila["nombre"])
    
    return {
        "message": f"La lista de cantantes del usuario '{id}' ha sido actualizada",
        "cantantes_favoritos": lista_final
    }, 200

# Método DELETE --> eliminar gustos musicales de un usuario
@app.route('/users/<int:id>/cantantes_favoritos', methods=['DELETE'])
def delete_cantante(id):
    # Comprobar si el usuario es válido (HEADER)
    authorization = request.headers.get('Authorization')
    if authorization != "1234":
        return{
            "message": "Sin autorización"
        }
    
    # 1. Se obtiene los desde la URL (?...=....)
    nombre_cantante = request.args.get("cantante")
    if not nombre_cantante:
        return {
            "message": "Falta el parámetro 'cantante' en la URL"
        }, 400

    # 2. Se conecta a la base de datos.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)

    # 3. Comprobar que el usuario existe
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone() # Devuelve la primera fila.

    if not usuario:
        cursor.close()
        return {
            "message": f"Usuario '{id}' no encontrado"
        }, 404

    # 4. Se eliminan los cantantes favoritos del usuario para reemplazarlos por la nueva lista.
    cursor.execute("DELETE FROM cantantes_favoritos WHERE usuario_id = %s AND nombre=%s", 
                   (id,nombre_cantante))
    conn.commit()

    if cursor.rowcount == 0:
        # No se eliminó ninguna fila → ese cantante no estaba para ese usuario
        cursor.close()
        return {
            "message": f"El usuario '{id}' no tiene al cantante '{nombre_cantante}' entre sus favoritos"
        }, 404

    # 5. Se obtiene la lista con los cantantes favoritos.
    cursor.execute(
        "SELECT nombre FROM cantantes_favoritos WHERE usuario_id = %s",
        (id,)
    )
    filas_finales = cursor.fetchall()
    cursor.close()

    lista_final = []
    for fila in filas_finales:
        lista_final.append(fila["nombre"])
    
    return {
        "message": f"El cantante '{nombre_cantante}' del usuario '{id}' ha sido eliminado",
        "cantantes_favoritos": lista_final
    }, 200



#---------------------------------------------------------- ENDPOINT CANCIONES FAVORITOS  ----------------------------------------------------------
# Método GET --> obtener canciones favoritas de un usuario
@app.route('/users/<int:id>/canciones_favoritas', methods=['GET'])
def get_canciones_favoritas(id):
    cursor = db.get_cursor()

    # 1. Se comprueba que existe el usuario: 
    # para ello se hace un JOIN de las tablas Usuario y Canciones favoritas.
    # 
    consulta_sql = """
        SELECT user.id AS usuario_id, 
               user.nombre AS usuario_nombre,
               c_f.nombre AS cancion_favorita
        FROM usuarios user
        LEFT JOIN canciones_favoritas c_f
            ON c_f.usuario_id = user.id
        WHERE user.id = %s;
    """
    # usuario_id  nombre_usuario    canciones_favoritas
    # ---------- ---------------    --------------------
    #  1                Pepe            Leave the Door Open
    #  2                Laura           Tocado y Hundido
    #  2                Laura           Angels
    #  3                Pepe            La llorona
    #  3                Pepe            La bachata
    #  5                Luisito            NULL
    cursor.execute(consulta_sql,(id,))
    filas_usuarios = cursor.fetchall()
    cursor.close()
    # 2. Si no hay fila, significa que el usuario no existe.
    if not filas_usuarios:
        return{
                "message": f"Usuario '{id}' no encontrado",
        },404
    

    # 3. Hay una fila para el usuario, se extrae su información para ver si tiene
    # cantantes favoritos.
    usuario_nombre = filas_usuarios[0]["usuario_nombre"]
    canciones_favoritas= [] 
    for fila in filas_usuarios: # Se recorren todas las filas del usuario para ver su cantante favorito
        cancion = fila["cancion_favorita"]
        if cancion is not None: 
            canciones_favoritas.append(cancion)

# 4. El cantante existe pero no tiene ningún cantante favorito
    if not canciones_favoritas:
        return {
            "message": f"El usuario '{id}' ({usuario_nombre}) no tiene ninguna canción favorita",
            "canciones_favoritas": []
        }, 200

# 5. El cantante existe y tiene cantantes favoritos
    return {
            "cantantes_favoritos": f"Las canciones favoritas del usuario '{id}' ({usuario_nombre})"
                                    + f" son '{canciones_favoritas}'"
            }, 200
 
# Método POST --> añadir canción favorita a un usuario
@app.route('/users/<int:id>/canciones_favoritas', methods=['POST'])
def post_canciones_favoritas(id):

    authorization = request.headers.get('Authorization')
    if authorization != "1234":
        return{
            "message": "Sin autorización"
        }
    # 1. Se obtiene los datos del JSON
    user_data = request.get_json() # Se obtiene el BODY del JSON
    new_canciones_favoritas = user_data.get("canciones_favoritas") # Selecciono el gusto musical del JSON

    if not new_canciones_favoritas:
        return{
            "message": "Falta 'canciones_favoritas'"
        }, 400
    
    if not isinstance(new_canciones_favoritas, list) or not new_canciones_favoritas:
        return {"message": "Se debe enviar una lista 'canciones_favoritas' con canciones"}, 400

    # 2. Se conecta a la base de datos.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    
     # 3. Comprobar que el usuario existe
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone() # Devuelve la primera fila.

    if not usuario:
        cursor.close()
        return {
            "message": f"Usuario '{id}' no encontrado"
        }, 404

    # 4. Obtener canciones favoritos ya existentes para ese usuario para no repetir canciones en el futuro.
    cursor.execute(
        "SELECT nombre FROM canciones_favoritas WHERE usuario_id = %s", (id,)
    )

    existentes = []
    filas_existentes = cursor.fetchall() # Devuelve toda la lista 
    #                                          --> {'nombre': 'Leave the door'}, 
    #                                              {'nombre': 'Tocado y hundido'}
    #  id   usuario_id    cancion   < < < < filas_existentes
    #   1	    1	    Leave the Door Open
    #   2	    1	    Tocado y Hundido
    #   3	    2	    Angels
    #   4	    3	    La llorona
    #   5	    3	    La bachata

    existentes = set()
    for fila in filas_existentes:
        existentes.add(fila["nombre"])  # --> ["Leave the Door Open", "Tocado y Hundido"]
    
    canciones_agregadas = []
    canciones_existentes = []

 # 5. Recorrer las nuevas canciones y añadirla en caso de no estar repetida.
    for cancion in new_canciones_favoritas:
        if cancion in existentes: # ¿La canción ya está en sus canciones favoritas?
            canciones_existentes.append(cancion) 
        else:
            cursor.execute( # Añade la canción a su lista de canciones favoritos.
                "INSERT INTO canciones_favoritas (usuario_id, nombre) VALUES (%s, %s)",
                (id, cancion)
            )
            canciones_agregadas.append(cancion)
            existentes.add(cancion)  # Actualizamos los canciones existentes con los que se han agregado.

    conn.commit()

# 6. Obtener la lista final de cantantes favoritos
    cursor.execute("SELECT nombre FROM canciones_favoritas WHERE usuario_id = %s", (id,))
    filas_finales = cursor.fetchall()
    cursor.close()

    lista_final = []
    for fila in filas_finales:
        lista_final.append(fila["nombre"])

    if canciones_agregadas:
        return {
            "message": "Operación realizada correctamente",
            "canciones_agregadas": canciones_agregadas,
            "canciones_existentes": canciones_existentes,
            "canciones_favoritas": lista_final
        }, 201 
    else:
        return {
            "message": "Operación realizada correctamente",
            "canciones_agregadas": canciones_agregadas,
            "canciones_existentes": canciones_existentes,
            "canciones_favoritas": lista_final
        }, 200 
    

# Método PUT --> modificar gustos musicales de un usuario
@app.route('/users/<int:id>/canciones_favoritas', methods=['PUT'])
def put_canciones(id):

    # Comprobar si el usuario es válido (HEADER)
    authorization = request.headers.get('Authorization')
    if authorization != "1234":
        return{
            "message": "Sin autorización"
        }
    
    # 1. Se obtiene los datos del JSON.
    user_data = request.get_json() # Se obtiene el BODY del JSON
    mod_canciones_favoritas = user_data.get('canciones_favoritas', [])
    
    if not isinstance(mod_canciones_favoritas, list) or not mod_canciones_favoritas:
        return {"message": "Se debe enviar una lista 'canciones_favoritas' con cantantes"}, 400

    # 2. Se conecta a la base de datos.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)

    # 3. Comprobar que el usuario existe
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone() # Devuelve la primera fila.

    if not usuario:
        cursor.close()
        return {
            "message": f"Usuario '{id}' no encontrado"
        }, 404

    # 4. Se eliminan las canciones favoritas del usuario para reemplazarlos por la nueva lista.
    cursor.execute("DELETE FROM canciones_favoritas WHERE usuario_id = %s", (id,))

    # 5. Se añaden las nuevas canciones favoritas.
    for cantante in mod_canciones_favoritas:
        cursor.execute(
            "INSERT INTO canciones_favoritas (usuario_id, nombre) VALUES (%s, %s)",
            (id, cantante)
        )

    conn.commit()

    # 6. Se obtiene la lista con las canciones favoritas.
    cursor.execute(
        "SELECT nombre FROM canciones_favoritas WHERE usuario_id = %s",
        (id,)
    )
    filas_finales = cursor.fetchall()
    cursor.close()

    lista_final = []
    for fila in filas_finales:
        lista_final.append(fila["nombre"])
    
    return {
        "message": f"La lista de canciones del usuario '{id}' ha sido actualizada",
        "canciones_favoritas": lista_final
    }, 200
    

@app.route('/users/<int:id>/canciones_favoritas', methods=['DELETE'])
def delete_cancion(id):
    # Comprobar si el usuario es válido (HEADER)
    authorization = request.headers.get('Authorization')
    if authorization != "1234":
        return{
            "message": "Sin autorización"
        }
    
    # 1. Se obtiene los datos desde la URL (?... = ...)
    nombre_cancion = request.args.get("cancion")
    if not nombre_cancion:
        return {
            "message": "Falta el parámetro 'cancion' en la URL"
        }, 400

    # 2. Se conecta a la base de datos.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)

    # 3. Comprobar que el usuario existe
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone() # Devuelve la primera fila.

    if not usuario:
        cursor.close()
        return {
            "message": f"Usuario '{id}' no encontrado"
        }, 404

    # 4. Se eliminan las canciones favoritas del usuario para reemplazarlos por la nueva lista.
    cursor.execute("DELETE FROM canciones_favoritas WHERE usuario_id = %s AND nombre=%s", 
                   (id,nombre_cancion))
    conn.commit()

    if cursor.rowcount == 0:
        # No se eliminó ninguna fila → ese cantante no estaba para ese usuario
        cursor.close()
        return {
            "message": f"El usuario '{id}' no tiene la canción '{nombre_cancion}' entre sus favoritos"
        }, 404

    # 5. Se obtiene la lista con las canciones favoritas.
    cursor.execute(
        "SELECT nombre FROM canciones_favoritas WHERE usuario_id = %s",
        (id,)
    )
    filas_finales = cursor.fetchall()
    cursor.close()

    lista_final = []
    for fila in filas_finales:
        lista_final.append(fila["nombre"])
    
    return {
        "message": f"La canción '{nombre_cancion}' del usuario '{id}' ha sido eliminada",
        "canciones_favoritas": lista_final
    }, 200

    
# ----------------------------------------- ENDPOINT USUARIO + CANTANTES FAVORITOS + SPOTIFY -----------------------------------------
# Obtiene información de los artistas de un usuario dado sus cantantes favoritos
@app.route('/users/<int:id>/artistas_spotify', methods=['GET'])
def get_info_artistas_spotify(id):
    
    # 1. Se conecta a la base de datos.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)

    cantantes_favoritos = []
    resultado_spotify = []

    # 2. Comprobar que el usuario existe
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone() # Devuelve la primera fila.

    if not usuario:
        cursor.close()
        return {
            "message": f"Usuario '{id}' no encontrado"
        }, 404

    # 3. Obtener cantantes favoritos ya existentes para el usuario y recorrerlas una a una para buscar
    cursor.execute(
        "SELECT nombre FROM cantantes_favoritos WHERE usuario_id = %s", (id,)
    )

    filas_existentes = cursor.fetchall() # Devuelve toda la lista 
    #                                          --> {'nombre': 'Robbie Williams'}, 
    #                                              {'nombre': 'Melendi'}

    cantantes_usuario = set()
    for fila in filas_existentes:
        cantantes_usuario.add(fila["nombre"])  # --> ["Robbie Williams", "Melendi"]
    
    # 4. Recorremos cada cantante favorito del usuario para encontrar información acerca de ellos.
    for cantante in cantantes_usuario:
        json_artistas = search_artist(cantante)
        # Devuelve el diccionario de artistas y obten el array de "items"
        contenido_artista = json_artistas.get("artists", {}).get("items", [])
        # 5. Obtenemos información del artista
        if contenido_artista:
            # Devuelve el primer elemento de Spotify
            artista = contenido_artista[0]
            info_artista = {
                "gusto_original": cantante,
                "nombre": artista.get("name"),
                "id": artista.get("id"),
                "popularidad": artista.get("popularity"),
                "seguidores": artista.get("followers", {}).get("total"),
                "generos": artista.get("genres", []),
                "spotify_url": artista.get("external_urls", {}).get("spotify")
            }
            resultado_spotify.append(info_artista)
            cantantes_favoritos.append(info_artista["nombre"])
    if not resultado_spotify:
            mensaje = f"No se han encontrado artistas en Spotify para los gustos del usuario '{id}'",
        
    else: 
            mensaje = f"Usuario '{id}' ha encontrado información en Spotify acerca de cantantes favoritos. "
    return {
        "message": mensaje,
        "cantantes_favoritos": cantantes_favoritos, # Muestra los cantantes favoritos del usuario.
        "resultado_spotify": resultado_spotify, # Devuelve la información obtenida de Spotify
    }, 200

@app.route('/users/<int:id>/canciones_spotify', methods=['GET'])
def get_info_canciones_spotify(id):
    
    # 1. Se conecta a la base de datos.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)

    canciones_favoritas = []
    resultado_spotify = []

    # 2. Comprobar que el usuario existe
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone() # Devuelve la primera fila.

    if not usuario:
        cursor.close()
        return {
            "message": f"Usuario '{id}' no encontrado"
        }, 404

    # 3. Obtener canciones favoritos ya existentes para el usuario y recorrerlas una a una para buscar
    # información.
    cursor.execute(
        "SELECT nombre FROM canciones_favoritas WHERE usuario_id = %s", (id,)
    )

    filas_existentes = cursor.fetchall() # Devuelve toda la lista 
    #                                          --> {'nombre': 'Leave the Door Open'}, 
    #                                              {'nombre': 'Tocado y Hundido'}

    canciones_usuario = set()
    for fila in filas_existentes:
        canciones_usuario.add(fila["nombre"])  # --> ["Leave the Door Open", "Tocado y Hundido"]
    
    # 5. Recorremos cada canción favorita del usuario para encontrar información acerca de la ella.
    for cancion in canciones_usuario:
        json_canciones = search_track_song(cancion)
        # Devuelve el diccionario de canciones y obten el array de "items"
        contenido_cancion = json_canciones.get("tracks", {}).get("items", [])
        # 6. Obtenemos información de la canción
        if contenido_cancion:
            # Devuelve el primer elemento de Spotify
            canc = contenido_cancion[0]

            # Una misma canción puede tener varios cantantes, 
            # por tanto vamos a añadirlos a una lista para obtener a todos los cantantes.
            cantantes_nombres = []
            for art in canc.get("artists", []):
                cantantes_nombres.append(art.get("name"))
                             
            info_cancion = {
                "nombre": cancion,
                "nombre_album": canc.get("album",{}).get("name"),
                "tipo_album": canc.get("album",{}).get("album_type"),
                "cantantes": cantantes_nombres,
                "id": canc.get("id"),
                "popularidad": canc.get("popularity"),
                "numero_cancion": canc.get("track_number"),
                "duracion": canc.get("duration_ms"),
                "fecha_lanzamiento": canc.get("album", {}).get("release_date"),
                "spotify_url": canc.get("external_urls", {}).get("spotify"),
            }
            resultado_spotify.append(info_cancion)
            canciones_favoritas.append(info_cancion["nombre"])
    if not resultado_spotify:
            mensaje = f"No se han encontrado canciones en Spotify para los gustos del usuario '{id}'",
    else: 
            mensaje = f"Usuario '{id}' ha encontrado información en Spotify acerca de canciones favoritos. "
    return {
        "message": mensaje,
        "canciones_favoritas": canciones_favoritas, # Muestra las canciones favoritas del usuario.
        "resultado_spotify": resultado_spotify, # Devuelve la información obtenida de Spotify
    }, 200


if __name__ == '__main__':  # Va al final
    app.run(debug=True)