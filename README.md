# Sistema de Gestión de Tickets — Mesa de Ayuda

Aplicación de escritorio en Python (Tkinter) para gestionar las órdenes de servicio de un centro de soporte técnico TI. Usa **persistencia políglota**:

- **MySQL**: datos estructurados (clientes, técnicos, equipos y tickets), con triggers, un procedimiento almacenado y una vista.
- **MongoDB**: bitácoras de diagnóstico de cada ticket (checklist, repuestos e historial de acciones).

## Funcionalidades

- Registro de clientes, técnicos y equipos (cada equipo pertenece a un cliente).
- Creación de órdenes de servicio con checklist del estado físico al ingreso.
- Historial de órdenes y ficha técnica de cada una (datos de MySQL + bitácora de MongoDB).
- Registro de avances y repuestos en la bitácora.
- Cierre de órdenes con la solución aplicada; la fecha de cierre se guarda automáticamente.

## Estructura

```
main.py                         Punto de entrada (abre la ventana principal)
config/
  conexion_mysql.py             Conexión a MySQL (base mesa_ayuda)
  conexion_mongo.py             Conexión a MongoDB (base mesa_ayuda_nosql)
database/
  schema.sql                    Creación de la base y tablas
  objetos_avanzados.sql         Triggers, procedimiento sp_crear_ticket y vista vw_reporte_tickets
  bitacoras_diagnostico.json    Ejemplo de documento de bitácora en MongoDB
models/
  gesiton_sql.py                CRUD de clientes, técnicos y equipos (MySQL)
  gestion_poliglota.py          Tickets: MySQL + bitácoras en MongoDB
ui/
  ventana_principal.py          Interfaz gráfica en Tkinter
```

## Requisitos

- Python 3 con Tkinter
- MySQL (configurado en `localhost:3307`, usuario `root`, sin contraseña)
- MongoDB (configurado en `localhost:27017`)
- Paquetes de Python:

```bash
pip install mysql-connector-python pymongo
```

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/TomBass98/Sistema-de-Gesti-n-de-Tickets-Mesa-de-ayuda-.git
   cd Sistema-de-Gesti-n-de-Tickets-Mesa-de-ayuda-
   ```

2. Crea la base de datos MySQL:

   ```bash
   mysql -u root -P 3307 < database/schema.sql
   ```

3. Agrega la columna `fecha_cierre`, que usan el trigger y la vista pero no está en `schema.sql`:

   ```sql
   USE mesa_ayuda;
   ALTER TABLE tbl_tickets_servicio ADD COLUMN fecha_cierre DATETIME NULL;
   ```

4. Crea los triggers, el procedimiento y la vista:

   ```bash
   mysql -u root -P 3307 < database/objetos_avanzados.sql
   ```

5. Inicia MongoDB. La base `mesa_ayuda_nosql` y la colección `bitacoras_diagnostico` se crean solas al registrar el primer ticket.

6. Si tu MySQL o MongoDB usa otro puerto, usuario o contraseña, edita `config/conexion_mysql.py` y `config/conexion_mongo.py`.

## Uso

```bash
python main.py
```

Para probar solo las conexiones:

```bash
python -m config.conexion_mysql
python -m config.conexion_mongo
```

## Modelo de datos

**MySQL (`mesa_ayuda`)**

| Tabla | Descripción |
|---|---|
| `tbl_clientes` | Clientes (documento único) |
| `tbl_tecnicos` | Técnicos (usuario único) |
| `tbl_equipos` | Equipos, asociados a un cliente |
| `tbl_tickets_servicio` | Órdenes de servicio, asociadas a un equipo y un técnico |

Objetos avanzados:

- `trg_fecha_cierre_ticket`: guarda `fecha_cierre` cuando el estado pasa a `Cerrado`.
- `trg_validar_costo_ticket`: impide registrar tickets con costo negativo.
- `sp_crear_ticket`: crea un ticket y devuelve su id.
- `vw_reporte_tickets`: resumen de tickets con cliente, equipo y técnico.

**MongoDB (`mesa_ayuda_nosql`)**

La colección `bitacoras_diagnostico` guarda un documento por ticket, vinculado con `id_ticket_sql`. Ver el ejemplo en `database/bitacoras_diagnostico.json`.
