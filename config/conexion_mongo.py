from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def conectar_mongo():
    try:
        cliente = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
        cliente.admin.command("ping")
        db = cliente["mesa_ayuda_nosql"]
        return db
    except ConnectionFailure as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado en MongoDB: {e}")
        return None

if __name__ == "__main__":
    db_mongo = conectar_mongo()
    if db_mongo is not None:
        print("¡Conexión exitosa a MongoDB (mesa_ayuda_nosql)!")
