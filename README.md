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

# Listar
curl -s http://127.0.0.1:8000/personas

# Obtener por ID
curl -s http://127.0.0.1:8000/personas/1

# Actualizar parcial
curl -s -X PUT http://127.0.0.1:8000/personas/1 \
  -H 'Content-Type: application/json' \
  -d '{"email":"juan.perez2@example.com","notes":"Actualizado"}'

# Eliminar
curl -s -X DELETE http://127.0.0.1:8000/personas/1 -i

## Detener el servidor

- Si lo iniciaste en la misma terminal: usa `CTRL+C`.
- Si corre en background, puedes cerrar esa terminal o matar el proceso de uvicorn (`pkill -f uvicorn`).



## Cambios y mejoras aplicadas

### 1. Nuevos endpoints documentados

- Se añadió al listado de endpoints principales:
  - `POST /personas/poblar` → poblar la base con datos de ejemplo.

### 2. Aclaraciones sobre instalación/entorno

- Se especificó:
  - Python 3.10+ (recomendado 3.11).
  - Uso de `uvicorn app.main:app --reload` indicando el módulo `app.main`.

### 3. Conexión a bases de datos

- Se añadió una sección más explícita de conexión a otras bases:
  - Ejemplo para MySQL en `.env`.
  - Recordatorio de instalar el driver correspondiente.

### 4. Ejemplos de uso y pruebas

- Se revisaron y limpiaron las URLs de los ejemplos `curl` (sin formato de Markdown de enlaces) para que puedan copiarse y ejecutarse directamente.
- Se dejó explícito el uso de `Content-Type: application/json` en las peticiones que requieren cuerpo JSON.

### 5. Estructura de proyecto / MVC

- Se reforzó la explicación de la estructura MVC:
  - `models` (SQLAlchemy).
  - `views` (Pydantic).
  - `controllers` (routers FastAPI).

### 6. Endpoint de salud

- Se mantiene documentado `GET /health` como verificación rápida del estado de la aplicación.

### 7. Errores frecuentes que se detectaron (contexto de desarrollo)

Aunque no está en el cuerpo principal, se tuvo en cuenta en el diseño del proyecto:

- Errores de importación del módulo `main` al usar `uvicorn main:app`:
  - Se soluciona con la estructura de paquete `app` y `uvicorn app.main:app`.
- Errores `405 Method Not Allowed` para `/personas/poblar`:
  - Se verificó que el endpoint debe ser `@router.post("/personas/poblar")` y se debe llamar con método `POST`.
- Errores `404 Not Found` en `DELETE /personas/{id}`:
  - Se revisó la correcta definición del endpoint `@router.delete("/{id}")` y la existencia del recurso antes de eliminar.