import mysql.connector
from mysql.connector import Error

def conectar_mysql():

    try:
        conexion = mysql.connector.connect(
            host = 'localhost',
            port = 3307,
            user = "root",
            password = "",
            database = "mesa_ayuda"
        )
        return conexion
    except Error as e:
        print(f"Error al conectar MySQL {e}")
        return None

if __name__ == "__main__":
    conn = conectar_mysql()
    if conn is not None:
        print("¡Conexión exitosa a MySQL (mesa_ayuda)!")
        conn.close()

