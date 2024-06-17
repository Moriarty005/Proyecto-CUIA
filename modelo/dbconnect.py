import pymysql

class database:

    conexion = None

    def __init__(self):
        pass

    def crearconexion(self):
        try:
            self.conexion = pymysql.connect(
                host='localhost',
                user='root',
                password='edxFrWmyW9COlrIUsZQb',
                db='prueba')
        except Exception as e:
            print("Excepcion al conectar con la base de datos: ", e)

    def cerrarconexion(self):
        self.conexion.close()

    def traerUsuarios(self):

        cosa = None

        try:
            self.cerrarconexion()
            self.cursor = self.conexion.cursor()
            query = "SELECT * FROM usuarios"
            print("Query (comprobarLoginAlumno): ", query)

            self.cursor.execute(query)
            cosa = self.cursor.fetchall()
            self.cerrarconexion()
        except Exception as e:
            self.cerrarconexion()
            print("Excepcion en comprbarLoginAlumno: ", e)

        return cosa
