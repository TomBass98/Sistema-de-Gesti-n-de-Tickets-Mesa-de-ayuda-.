from mysql.connector import Error
from config.conexion_mysql import conectar_mysql

# Funciones para registrar

def registrar_cliente(nombre, documento, telefono, correo):
    conn = conectar_mysql()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        #En VALUES parametrizamos para evitar inyecciones SQL
        sql = """
            INSERT INTO tbl_clientes (nombre_cli, documento_cli, telefono_cli, correo_cli)
            VALUES (%s, %s, %s, %s)
        """ 
        cursor.execute(sql, (nombre, documento, telefono, correo))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al registrar cliente: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def registrar_tecnico(nombre, especialidad, usuario, password_hash):
    conn = conectar_mysql()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO tbl_tecnicos (nombre_tec, especialidad, usuario, password_hash)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (nombre, especialidad, usuario, password_hash))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al registrar técnico: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def registrar_equipo(tipo, marca, modelo, serial, id_cliente):
    conn = conectar_mysql()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO tbl_equipos (tipo_equipo, marca, modelo, serial_number, id_cliente)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (tipo, marca, modelo, serial, id_cliente))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al registrar equipo: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Funciones con consultas SQL para listar

def listar_clientes():
    conn = conectar_mysql()

    if conn is None:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
                SELECT id_cliente, nombre_cli, documento_cli FROM tbl_clientes ORDER BY nombre_cli
            """
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f"Error al listar los clientes {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def listar_tecnicos():
    conn = conectar_mysql()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT id_tecnico, nombre_tec, especialidad FROM tbl_tecnicos ORDER BY nombre_tec
            """
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f"Error al listar los técnicos {e}")
        return[]
    finally:
        cursor.close()
        conn.close()


def listar_equipos():

    conn = conectar_mysql()

    if conn is None:
        return[]

    try:
        cursor = conn.cursor(dictionary=True)
        sql=""" 
            SELECT e.id_equipo, e.tipo_equipo, e.marca, e.serial_number, c.nombre_cli
            FROM tbl_equipos e 
            INNER JOIN tbl_clientes  c ON e.id_cliente = c.id_cliente
            ORDER BY e.id_equipo DESC
        """
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f"Error al listar los equipos: {e}")
        return[]
    finally:
        cursor.close()
        conn.close()
