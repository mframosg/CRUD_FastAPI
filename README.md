# FastAPI Persona CRUD (MySQL por defecto)

Proyecto de demostración con FastAPI + SQLAlchemy y estructura MVC para un CRUD de `Persona`. Usa MySQL por defecto y permite apuntar a otra base SQL mediante la variable de entorno `DATABASE_URL` (configurable en `.env`).

## Requisitos

- Python 3.10+ (recomendado 3.11)

## Instalación y ejecución

1. Crear entorno virtual e instalar dependencias:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales de MySQL
   # Por defecto: DATABASE_URL=mysql+pymysql://user:password@localhost:3306/fastapi_demo
   ```

3. Ejecutar el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Documentación interactiva:
   - Swagger UI: <http://localhost:8000/docs>
   - ReDoc: <http://localhost:8000/redoc>

## Conexión a otras bases de datos

Edita `DATABASE_URL` en `.env`.
- MySQL: `mysql+pymysql://user:password@localhost:3306/mydb`

> Nota: Instala el driver correspondiente (psycopg2, PyMySQL, pyodbc, etc.).

## Ejemplo de `.env` (MySQL local)

```env
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/nombre_basedatos
```

## Endpoints principales

- `GET /health` → estado del servicio
- `POST /personas` → crear persona
- `GET /personas` → listar personas (`skip`, `limit`)
- `GET /personas/{id}` → obtener persona por ID
- `PUT /personas/{id}` → actualizar (parcial) persona
- `DELETE /personas/{id}` → eliminar persona

### Esquemas (JSON)

- Crear:
  ```json
  {
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan.perez@example.com",
    "phone": "+57 3000000000",
    "birth_date": "1990-05-20",
    "is_active": true,
    "notes": "Cliente frecuente"
  }
  ```

- Actualizar (parcial):
  ```json
  {
    "email": "juan.perez2@example.com",
    "notes": "Actualizado"
  }
  ```

## Colección de Postman

Importa `FastAPI-CRUD-Demo.postman_collection.json` en Postman. Variables:

- `base_url` (por defecto `http://localhost:8000`)
- `persona_id` (por defecto `1`)

## Notas

- Las tablas se crean automáticamente al iniciar (solo con fines de demo).
- Asegúrate de crear la base de datos en MySQL y de que el usuario tenga permisos (por ejemplo, `CREATE DATABASE fastapi_demo;`).

## Estructura MVC

- `app/models/` → modelos SQLAlchemy (por ejemplo, `persona.py`).
- `app/views/` → esquemas Pydantic (por ejemplo, `persona.py`).
- `app/controllers/` → routers/controladores FastAPI (por ejemplo, `persona_controller.py`).

## Pruebas rápidas (curl)

```bash
# Health
curl -s http://127.0.0.1:8000/health

# Crear persona
curl -s -X POST http://127.0.0.1:8000/personas \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name":"Juan",
    "last_name":"Perez",
    "email":"juan.perez@example.com",
    "phone":"+57 3000000000",
    "birth_date":"1990-05-20",
    "is_active":true,
    "notes":"Cliente frecuente"
  }'

#Listar
curl -s http://127.0.0.1:8000/personas

# Obtener por ID
curl -s http://127.0.0.1:8000/personas/1

# Actualizar parcial
curl -s -X PUT http://127.0.0.1:8000/personas/1 \
  -H 'Content-Type: application/json' \
  -d '{"email":"juan.perez2@example.com","notes":"Actualizado"}'

# Eliminar
curl -s -X DELETE http://127.0.0.1:8000/personas/1 -i

```

## Detener el servidor

- Si lo iniciaste en la misma terminal: usa `CTRL+C`.
- Si corre en background, puedes cerrar esa terminal o matar el proceso de uvicorn (`pkill -f uvicorn`).

## Nuevos Endpoints (Jimmy)

Como parte de los requerimientos de este taller, se desarrollaron e integraron tres nuevos endpoints en la arquitectura de la API:

*   **Poblar Base de Datos (`POST /personas/poblar`):** Genera e inserta datos masivos en la base de datos. Para esto, utiliza un esquema de validación llamado `PoblarRequest` que define la cantidad de registros a crear. La lógica interna emplea la librería `Faker` para generar nombres, apellidos, fechas de nacimiento, números de teléfono y asegurar que los correos electrónicos generados sean únicos.
*   **Reiniciar Base de Datos (`DELETE /personas/reset`):** Elimina todos los registros actuales de la tabla `personas` en la base de datos. El borrado se hace de manera eficiente directamente en la base de datos sin cargar los objetos en memoria y retorna la cantidad de registros que fueron eliminados.
*   **Exportar a CSV (`GET /personas/exportar/csv`):** Consulta todos los registros de la base de datos y permite descargarlos en formato CSV. El endpoint modifica las cabeceras HTTP para retornar un `Response` de tipo `text/csv` como archivo adjunto (`attachment; filename=personas.csv`).

### Otras Actualizaciones
*   **Dependencias:** Se añadió la librería `Faker==40.44.0` al archivo `requirements.txt` para soportar la generación de datos falsos de usuarios.
*   **Colección de Postman:** Se actualizó el archivo `FastAPI-CRUD-Demo.postman_collection.json` agregando y renombrando las solicitudes necesarias ("Poblar Base de Datos", "Reset Base de Datos" y "Exportar a CSV") para probar estos nuevos endpoints directamente desde la herramienta.

## Aportes: endpoints analíticos (Salomé)

Se desarrollaron tres endpoints en FastAPI para realizar consultas estadísticas y obtener información específica de las personas registradas en la base de datos.

### 1. Estadísticas por dominios de correo

* **Método y Ruta:** `GET /personas/estadisticas/dominios`
* **Descripción:** Agrupa los registros según el dominio del correo electrónico y devuelve la cantidad de personas que utilizan cada dominio.

### 2. Estadísticas de edad

* **Método y Ruta:** `GET /personas/estadisticas/edad`
* **Descripción:** Calcula y devuelve la edad promedio de las personas registradas, redondeada a un decimal, junto con la edad mínima y máxima.

### 3. Personas que cumplen años en un mes específico

* **Método y Ruta:** `GET /personas/cumpleanios/mes/{numero_mes}`
* **Descripción:** Permite consultar las personas que cumplen años en un mes determinado. El endpoint valida que el número del mes esté entre 1 y 12 y filtra los registros según la fecha de nacimiento.

## Aportes: búsquedas, proyección y bulk (Integrante 3 — Daniela)

Se desarrollaron tres endpoints para búsquedas, reportes con proyección y manipulación masiva de datos.

### 1. Buscador general

* **Método y Ruta:** `GET /personas/buscar/{termino}`
* **Descripción:** Busca coincidencias parciales (sin distinguir mayúsculas) en `first_name`, `last_name` o `email` usando el operador OR. Devuelve una lista vacía `[]` si no hay resultados.

### 2. Reporte de activos

* **Método y Ruta:** `GET /personas/reporte/activos`
* **Descripción:** Devuelve solo las personas con `is_active = true`, mostrando únicamente `id`, `email`, `phone` e `is_active` (proyección con el schema `PersonaActivoRead`).

### 3. Desactivación masiva

* **Método y Ruta:** `PATCH /personas/bulk/desactivar`
* **Descripción:** Recibe `{"ids": [...]}` con entre 1 y 100 IDs (si no, responde 400). Desactiva en una sola operación los IDs que existen y reporta `desactivados`, `no_encontrados` y `total_desactivados` sin fallar cuando algún ID no existe.
