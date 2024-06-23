# model.py
import json

import mysql.connector


class UserModel:
    def __init__(self):
        pass

    """
    Método que crea la conexión a la base de datos.
    
    :returns la conexión a la base de datos.
    """
    def crear_conexion(self):
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="prueba"
            )
            if conexion.is_connected():
                #print("Conexión exitosa")
                return conexion
        except mysql.connector.Error as err:
            print(f"Error al crear la conexion a la base de datos: {err}")
            return None

    """
    Método que comprueba si las credenciales son correctas
    
    :argument username, parámetro que indica el nombre de usuario
    :argument password, parámetro que indica el password del usuario
    
    :returns None en caso de que no exista ningún usuario con esas credenciales
    :returns id_usuario en caso de que sí exista el usuario con esas credenciales
    
    :exception Excepción de MySQL
    """
    def validate_user(self, username, password):
        try:
            id_usuario = None
            conexion = self.crear_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE username = '"+username+"'")
            result = cursor.fetchone()
            conexion.close()
            if result:
                id_usuario = result[0]
        except mysql.connector.Error as err:
            print(f"Error al comprobar las credenciales: {err}")
        #TODO hacer la tabla de contrasenias y validar tambien la contrasenia
        return id_usuario

    """
    Método que trae de la base de datos todos los eventos disponibles
    
    :returns Devuelve item a item todas las tuplas devueltas por la base de datos
    
    :exception Excepción de MySQL
    """
    def traer_eventos(self):
        try:
            conexion = self.crear_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM eventos")
            data = cursor.fetchall()
            conexion.close()
        except mysql.connector.Error as err:
            print(f"Error al traer toda la lista de eventos: {err}")

        return [item for item in data]

    """
    Método que trae un evento en concreto en base a un id de evento seleccionado
    
    :param id, ID del evento que queremos traer
    
    :returns Devuelve item a item todas las tuplas
    
    :exception Excepción de MySQL
    """
    def traer_evento_por_id(self, id):
        try:
            conexion = self.crear_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM eventos WHERE id='"+ str(id) +"'")
            data = cursor.fetchone()

        except mysql.connector.Error as err:
            print(f"Error al intentar trae un evento por su id: {err}")
        finally:
            cursor.close()
            conexion.close()

        return [item for item in data]

    """
    Método que introduce en la base de datos que un usuario a realizado una reserva de un envento
    
    :param id_usuario, ID del usuario que hace la reserva
    :param id_evento, ID del evento que se reserva
    
    :exception Excepción de MySQL
    """
    def hacer_reserva(self, id_usuario, id_evento):
        try:
            conexion = self.crear_conexion()
            cursor = conexion.cursor()
            query = "INSERT INTO usuario_hace_reserva (id_usuario, id_evento) VALUES ('"+str(id_usuario)+"', '"+str(id_evento)+"')"
            cursor.execute(query)
            conexion.commit()
            print("DEBUG::Se ha ejecutado la query "+query)
        except mysql.connector.Error as err:
            print(f"Error al intentar ingresar una reserva: {err}")
        finally:
            cursor.close()
            conexion.close()

    """
    Método que guarda la codificación de la cara de usuario cuando se registra
    
    :param username, nombre de usuario en el sistema con el que se identifica el usuario
    :param cara, cara codificada del usuario
    
    :exception Excepción de MySQL
    """
    def guardar_codificacion_cara_usuario(self, username, cara):
        try:
            conexion = self.crear_conexion()
            cursor = conexion.cursor()
            cara_json = cara.tolist()
            encoding_str = json.dumps(cara_json)
            cursor.execute("SELECT id FROM usuarios WHERE username = '" + username + "'")
            result = cursor.fetchone()
            if result:
                id_usuario = result[0]
                query = "INSERT INTO caras_codificadas (id_usuario, cara) VALUES ('"+str(id_usuario)+"', '"+encoding_str+"')"
                cursor.execute(query)
                conexion.commit()
                print("DEBUG::Se ha ejecutado la query "+query)
        except mysql.connector.Error as err:
            print(f"Error al intentar ingresar una codificacion de una cara: {err}")
        finally:
            cursor.close()
            conexion.close()

    """
    Método que guarda en la base de datos un nuevo usuario cuando se registre
    
    :param username, username del usuario 
    :param name,  nombre real del usuario
    :param surname, apellidos del usuario
    :param dni, DNI del usuario
    :param email, email del usuario
    
    :exception Excepción de MySQL
    """
    def aniadir_usuario(self, username, name, surname, dni, email):
        try:
            conexion = self.crear_conexion()

            cursor = conexion.cursor()

            if surname == None or surname == '':
                query = f"INSERT INTO usuarios (nombre, apellidos, dni, mail, username) VALUES ('{name}', 'NULL', '{dni}', '{email}', '{username}')"
            else:
                query = f"INSERT INTO usuarios (nombre, apellidos, dni, mail, username) VALUES ('{name}', '{surname}', '{dni}', '{email}', '{username}')"

            print("DEBUG::Vamos a ejecutar la query la query " + query)
            cursor.execute(query)
            conexion.commit()

        except mysql.connector.Error as err:
            print(f"Error al intentar ingresar un usuario: {err}")
        finally:
            cursor.close()
            conexion.close()

    """
    Método que obtiene de la base de datos la cara codificada de un usuario dado
    
    :param id_usuario, ID del usuario del que queremos obtener la cara
    
    :returns la tupla con al cara
    
    :exception Excepción de MySQL
    """
    def get_codificacion_cara(self, id_usuario):
        try:
            conexion = self.crear_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT cara FROM caras_codificadas WHERE id_usuario='" + str(id_usuario) + "'")
            data = cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error al intentar trae un evento por su id: {err}")
        finally:
            cursor.close()
            conexion.close()

        return data[0]