# model.py
import mysql.connector


class UserModel:
    def __init__(self):
        self.username = 'user'
        self.password = 'pass'

    def validate_user(self, username, password):
        return username == self.username and password == self.password

    def crear_conexion(self):
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="prueba"
            )
            if conexion.is_connected():
                print("Conexión exitosa")
                return conexion
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def traer_eventos(self):
        conexion = self.crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM eventos")
        data = cursor.fetchall()
        conexion.close()

        return [item for item in data]

    def traer_evento_por_id(self, id):
        conexion = self.crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM eventos WHERE id='"+ str(id) +"'")
        data = cursor.fetchone()
        conexion.close()

        return [item for item in data]
