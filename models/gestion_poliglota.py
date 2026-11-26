from datetime import datetime
from mysql.connector import Error
from config.conexion_mysql import conectar_mysql
from config.conexion_mongo import conectar_mongo

def crear_ticket_completo(falla, costo, id_equipo, id_tecnico, diagnostico_inicial, checklist):
    conn_sql = conectar_mysql()
    db_mongo = conectar_mongo()

    if conn_sql is None or db_mongo is None:
        print("No se pudo establecer conexión con ambos motores de base de datos.")
        return None

    try:
        # 1. Llamar al Procedimiento Almacenado en MySQL
        cursor = conn_sql.cursor()
        # El último parámetro (0) es el OUT p_nuevo_id
        args = [falla, costo, id_equipo, id_tecnico, 0]
        resultado_proc = cursor.callproc("sp_crear_ticket", args)
        conn_sql.commit()

        # Capturamos el ID generado por MySQL
        nuevo_id_ticket = resultado_proc[4]

        # 2. Guardar la bitácora técnica en MongoDB usando el mismo ID
        coleccion_bitacoras = db_mongo["bitacoras_diagnostico"]
        documento_mongo = {
            "id_ticket_sql": nuevo_id_ticket,
            "diagnostico_tecnico": diagnostico_inicial,
            "checklist_hardware": checklist,
            "repuestos_utilizados": [],
            "historial_acciones": [
                {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "nota": "Ticket abierto y registrado en sistema."
                }
            ]
        }
        coleccion_bitacoras.insert_one(documento_mongo)

        print(f"Ticket #{nuevo_id_ticket} creado en MySQL y bitácora vinculada en MongoDB.")
        return nuevo_id_ticket

    except Error as e:
        # Si el trigger de costo negativo salta, lo capturamos aquí
        print(f"Error de regla de negocio / MySQL: {e}")
        return None
    except Exception as e:
        print(f"Error en persistencia políglota: {e}")
        return None
    finally:
        cursor.close()
        conn_sql.close()

def consultar_expediente_ticket(id_ticket):
    conn_sql = conectar_mysql()
    db_mongo = conectar_mongo()

    if conn_sql is None or db_mongo is None:
        return None

    try:
        # 1. Consultar la VISTA con INNER JOINs en MySQL
        cursor = conn_sql.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vw_reporte_tickets WHERE id_ticket = %s", (id_ticket,))
        datos_sql = cursor.fetchone()

        # 2. Consultar la bitácora en MongoDB
        coleccion_bitacoras = db_mongo["bitacoras_diagnostico"]
        datos_mongo = coleccion_bitacoras.find_one({"id_ticket_sql": id_ticket}, {"_id": 0})


        return {
            "ticket_sql": datos_sql,
            "bitacora_mongo": datos_mongo
        }
    finally:
        cursor.close()
        conn_sql.close()



def cerrar_ticket(id_ticket, nota_cierre):
    conn_sql = conectar_mysql()
    db_mongo = conectar_mongo()
    
    if conn_sql is None or db_mongo is None:
        return None

    try:
        cursor = conn_sql.cursor()
        sql = "UPDATE tbl_tickets_servicio SET estado = 'Cerrado' WHERE id_ticket = %s"
        cursor.execute(sql, (id_ticket,))
        conn_sql.commit()

        coleccion_bitacoras = db_mongo["bitacoras_diagnostico"]
        coleccion_bitacoras.update_one(
            {"id_ticket_sql": id_ticket},
            {"$push":{"historial_acciones": {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "nota": nota_cierre
            }}}
        )

        return True

    except Error as e:
        print(f"Error al cerrar el ticket en MySQL: {e}")
        return False
    except Exception as e:
        print(f"Error al actualizar bitacora: {e}")
        return False
    
    finally:
        cursor.close()
        conn_sql.close()

# Funcion listar todos los tickets:

def listar_todos_tickets():
    conn_sql = conectar_mysql()
    if conn_sql is None:
        return []
    try:
        cursor = conn_sql.cursor(dictionary=True)
        sql = "SELECT * FROM vw_reporte_tickets ORDER BY id_ticket DESC"
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f"Error al listar los tickets: {e}")
        return []
    finally:
        cursor.close()
        conn_sql.close()


# Función única para agregar avances dentro ed las bitacoras en mongo 

def agregar_avance_bitacora(id_ticket, nueva_nota, repuesto=""):
    db_mongo = conectar_mongo()
    if db_mongo is None:
        return False

    try:
        coleccion_bitacoras = db_mongo["bitacoras_diagnostico"]
        operacion_push = {
            "historial_acciones": {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "nota": nueva_nota
            }
        }

        if repuesto.strip():
            operacion_push["repuestos_utilizados"] = repuesto.strip()

        coleccion_bitacoras.update_one(
            {"id_ticket_sql": id_ticket},
            {"$push": operacion_push}
        )
        return True

    except Exception as e:
        print(f"Error al agregar avance en MongoDB: {e}")
        return False


    