# Sistema de Gestión y Soporte Técnico TI

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-6.0%2B-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter%20%2F%20ttk-1E293B?style=for-the-badge)

Aplicación de escritorio desarrollada en **Python** para la gestión integral de órdenes de servicio técnico, inventario de equipos y seguimiento de bitácoras de diagnóstico. Implementa una **arquitectura en capas** respaldada por un modelo de almacenamiento híbrido que combina la integridad referencial de **MySQL** con la flexibilidad documental de **MongoDB**.

---

## Arquitectura del Sistema y Flujo de Datos

El sistema separa las responsabilidades en cuatro capas independientes y sincroniza ambos motores de bases de datos mediante el identificador autoincremental generado al crear cada orden (`id_ticket_sql`).

```mermaid
flowchart TD
    MAIN["Punto de Entrada (main.py)"]
    UI["Interfaz Gráfica (ui/ventana_principal.py)<br/>Tkinter + ttk (Navegación por vistas)"]
    SQLM["Modelo Relacional (models/gestion_sql.py)"]
    ORQ["Capa Coordinadora (models/gestion_poliglota.py)"]
    CFG["Configuración (config/conexion_*.py)"]

    MYSQL[("MySQL<br/>Clientes, Técnicos, Equipos y Tickets<br/>(SP + Vistas + Triggers)")]
    MONGO[("MongoDB<br/>Colección: bitacoras_diagnostico<br/>(Checklist, Repuestos e Historial)")]

    MAIN --> UI
    UI -->|Registros maestros| SQLM
    UI -->|Órdenes y bitácoras| ORQ
    SQLM --> CFG
    ORQ --> CFG
    CFG --> MYSQL
    CFG --> MONGO
    MYSQL -.->|Retorna id_ticket| ORQ
    ORQ -.->|Vincula id_ticket_sql| MONGO
```

---

## Modelo de Base de Datos Relacional (MySQL)

Almacena los datos maestros y transaccionales garantizando integridad referencial mediante llaves primarias (`PK`) y foráneas (`FK`):

```mermaid
erDiagram
    TBL_CLIENTES ||--o{ TBL_EQUIPOS : "posee"
    TBL_EQUIPOS ||--o{ TBL_TICKETS_SERVICIO : "ingresa_en"
    TBL_TECNICOS ||--o{ TBL_TICKETS_SERVICIO : "atiende"

    TBL_CLIENTES {
        int id_cliente PK
        varchar nombre_cli
        varchar documento_cli
        varchar telefono_cli
        varchar correo_cli
    }

    TBL_TECNICOS {
        int id_tecnico PK
        varchar nombre_tec
        varchar especialidad
        varchar usuario_tec
        varchar clave_tec
    }

    TBL_EQUIPOS {
        int id_equipo PK
        varchar tipo_equipo
        varchar marca
        varchar modelo
        varchar serial_number
        int id_cliente FK
    }

    TBL_TICKETS_SERVICIO {
        int id_ticket PK
        text falla_reportada
        decimal costo_estimado
        varchar estado
        datetime fecha_creacion
        datetime fecha_cierre
        int id_equipo FK
        int id_tecnico FK
    }
```

---

## Modelo Documental e Integración Híbrida (MongoDB)

Para evitar rigidez estructural en los diagnósticos técnicos, cada orden registrada en MySQL se vincula con un documento flexible en la colección `bitacoras_diagnostico` mediante el campo `id_ticket_sql`:

```mermaid
flowchart LR
    subgraph SQL ["MySQL: tbl_tickets_servicio"]
        T["id_ticket: 12<br/>falla_reportada: 'No enciende'<br/>costo_estimado: 150000<br/>estado: 'Abierto'"]
    end

    subgraph MONGO ["MongoDB: bitacoras_diagnostico"]
        B["id_ticket_sql: 12<br/>diagnostico_tecnico: 'Revisión de fuente'<br/>checklist_hardware: { enciende, pantalla_ok, bateria_ok }<br/>repuestos_utilizados: [ 'Cargador 65W' ]<br/>historial_acciones: [ { fecha, nota } ]"]
    end

    T <==>|"Sincronización por ID"| B
```

### Estructura del Documento JSON en MongoDB
```json
{
  "id_ticket_sql": 12,
  "diagnostico_tecnico": "Revisión de fuente de poder",
  "checklist_hardware": {
    "enciende": false,
    "pantalla_ok": true,
    "bateria_ok": true
  },
  "repuestos_utilizados": [
    "Adaptador AC 65W"
  ],
  "historial_acciones": [
    {
      "fecha": "2026-11-25 14:30",
      "nota": "Ticket abierto y registrado en sistema."
    }
  ]
}
```

---

## Distribución de Datos y Automatización

### Responsabilidad por Motor
| Motor | Entidad / Colección | Tipo de Datos | Función en el Sistema |
| :--- | :--- | :--- | :--- |
| **MySQL** | `tbl_clientes` | Estructurados | Registro de propietarios, documentos de identidad y contacto. |
| **MySQL** | `tbl_tecnicos` | Estructurados | Personal de soporte, especialidad y credenciales de acceso. |
| **MySQL** | `tbl_equipos` | Estructurados | Inventario de hardware asociado a cada cliente. |
| **MySQL** | `tbl_tickets_servicio` | Transaccionales | Cabecera de la orden, falla, costo, estado y fechas de control. |
| **MongoDB** | `bitacoras_diagnostico` | Semiestructurados | Diagnóstico inicial, checklist variable, repuestos e historial técnico. |

### Objetos Programados en MySQL
| Objeto | Nombre | Tipo de Ejecución | Función Principal |
| :--- | :--- | :--- | :--- |
| **Procedimiento Almacenado** | `sp_crear_ticket` | Explícita (`cursor.callproc`) | Inserta la orden de servicio y devuelve el ID generado mediante un parámetro `OUT`. |
| **Vista SQL** | `vw_reporte_tickets` | Bajo demanda (`SELECT`) | Consolida mediante `INNER JOIN` los datos de la orden, equipo, cliente y técnico asignado. |
| **Trigger de Validación** | `trg_validar_costo` | Automática (`BEFORE INSERT`) | Bloquea el registro de órdenes con costos negativos lanzando una excepción hacia Python. |
| **Trigger de Cierre** | `trg_fecha_cierre` | Automática (`BEFORE UPDATE`) | Detecta cuando el estado cambia a `'Cerrado'` y asigna automáticamente la fecha actual (`NOW()`). |

---

## Estructura del Proyecto

```text
mesa_ayuda_proyecto/
├── config/
│   ├── conexion_mysql.py       # Parámetros y gestión de conexión TCP hacia MySQL
│   └── conexion_mongo.py       # Conexión al servidor local de MongoDB (PyMongo)
├── models/
│   ├── gestion_sql.py          # Operaciones CRUD parametrizadas para clientes, técnicos y equipos
│   └── gestion_poliglota.py    # Orquestación de operaciones entre MySQL y MongoDB ($push / find_one)
├── ui/
│   └── ventana_principal.py    # Interfaz gráfica POO con gestor de vistas (ttk.Notebook) y ficha técnica
├── .gitignore                  # Exclusión de entornos virtuales (.venv) y archivos temporales
├── main.py                     # Punto de arranque único de la aplicación
└── README.md                   # Documentación del repositorio
```

---

## Instalación y Ejecución

### 1. Requisitos Previos
* **Python 3.10** o superior.
* Servidor **MySQL** activo con el esquema, vista, procedimiento y triggers cargados.
* Servidor **MongoDB** activo en `localhost:27017`.

### 2. Clonar el Repositorio e Instalar Dependencias
```bash
git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
cd TU_REPOSITORIO

# Crear y activar entorno virtual (opcional)
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar conectores de bases de datos
pip install mysql-connector-python pymongo
```

### 3. Configurar Credenciales y Ejecutar
Ajusta las credenciales locales en `config/conexion_mysql.py` y `config/conexion_mongo.py`, y ejecuta el punto de entrada:
```bash
python3 main.py
```

---

## Autores

* **Tomas Alvarez Cano**
