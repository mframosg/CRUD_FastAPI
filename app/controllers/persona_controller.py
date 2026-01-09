from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.utils import faker_utils
from sqlalchemy import text
from ..database import get_db
from ..views.persona import PersonaCreate, PersonaUpdate, PersonaRead, PoblarRequest
from ..services import persona_service

router = APIRouter(prefix="/personas", tags=["personas"])


@router.post("", response_model=PersonaRead, status_code=status.HTTP_201_CREATED)
def create_persona(persona_in: PersonaCreate, db: Session = Depends(get_db)):
    """Create a new Persona delegating to service layer."""
    # Let domain errors bubble up to global handlers
    return persona_service.create_persona(db, persona_in)


@router.get("", response_model=List[PersonaRead])
def list_personas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List Personas with pagination via service layer."""
    return persona_service.list_personas(db, skip=skip, limit=limit)

# --- RUTAS FIJAS NUEVAS DE LOS ENDPIONTS REQUERIDOS (ANTES de /{persona_id}) ---

@router.get("/contar-dominios", status_code=200)
async def contar_dominios_endpoint(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT SUBSTRING_INDEX(email, '@', -1) AS dominio, COUNT(*) AS cantidad
            FROM personas
            GROUP BY dominio
        """)
    )
    dominios_count = {row[0]: row[1] for row in result}
    return dominios_count

@router.post("/poblar", status_code=201)
async def poblar_personas_endpoint(request: PoblarRequest, db: Session = Depends(get_db)):
    personas_data = faker_utils.generar_personas(request.cantidad)
    db.execute(text("DELETE FROM personas"))
    db.execute(text("ALTER TABLE personas AUTO_INCREMENT = 1"))
    db.execute(
        text("""
            INSERT INTO personas
            (first_name, last_name, email, phone, birth_date, is_active, notes)
            VALUES (:firstname, :lastname, :email, :phone, :birthdate, :isactive, :notes)
        """),
        personas_data
    )
    db.commit()
    return {"message": f"{request.cantidad} usuarios creados exitosamente", "status": 201}

@router.delete("/reset")
async def reset_personas_endpoint(db: Session = Depends(get_db)):
    result = db.execute(text("DELETE FROM personas"))
    deleted_count = result.rowcount
    db.execute(text("ALTER TABLE personas AUTO_INCREMENT = 1"))
    db.commit()
    return {
        "message": "Base de datos limpiada. Se eliminaron todos los registros.",
        "deletedcount": deleted_count,
    }

@router.get("/estadisticas-edad", status_code=200)
async def estadisticas_edad_endpoint(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT
                AVG(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS edad_promedio,
                MIN(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS edad_minima,
                MAX(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS edad_maxima
            FROM personas
        """)
    )
    row = result.fetchone()
    return {
        "edad_promedio": float(row[0]) if row[0] is not None else None,
        "edad_minima": int(row[1]) if row[1] is not None else None,
        "edad_maxima": int(row[2]) if row[2] is not None else None,
    }



@router.get("/{persona_id}", response_model=PersonaRead)
def get_persona(persona_id: int, db: Session = Depends(get_db)):
    """Retrieve a Persona by ID via service layer."""
    return persona_service.get_persona(db, persona_id)


@router.put("/{persona_id}", response_model=PersonaRead)
def update_persona(persona_id: int, persona_in: PersonaUpdate, db: Session = Depends(get_db)):
    """Update an existing Persona (partial) via service layer."""
    return persona_service.update_persona(db, persona_id, persona_in)

@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    """Delete a Persona by ID via service layer."""
    persona_service.delete_persona(db, persona_id)
    return None


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    """Delete a Persona by ID via service layer."""
    persona_service.delete_persona(db, persona_id)
    return None

# 2) RUTA DINÁMICA: por ID (debe ir DESPUÉS)
@router.get("/{persona_id}", response_model=PersonaRead)
def get_persona(persona_id: int, db: Session = Depends(get_db)):
    return persona_service.get_persona(db, persona_id)