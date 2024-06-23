# model.py
import json

import mysql.connector


class UserModel:
    def __init__(self):
        pass

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