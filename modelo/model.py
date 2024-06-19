# model.py
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
                print("Conexión exitosa")
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
            conexion.close()
        except mysql.connector.Error as err:
            print(f"Error al intentar trae un evento por su id: {err}")

        return [item for item in data]

    def hacer_reserva(self, id_usuario, id_evento):
        try:
            conexion = self.crear_conexion()
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO `prueba`.`usuario_hace_reserva` (`id_usuario`, `id_reserva`) VALUES ('"+id_usuario+"', '"+id_evento+"')")
            conexion.close()
        except mysql.connector.Error as err:
            print(f"Error al intentar ingresar una reserva: {err}")