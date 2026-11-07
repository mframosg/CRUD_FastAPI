from typing import List
from fastapi import APIRouter, Depends, Query, status, Response
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

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

@router.post("/poblar", status_code=status.HTTP_201_CREATED)
def poblar_datos_masivos(request: PoblarRequest, db: Session = Depends(get_db)):
    """Genera e inserta datos masivos usando Faker."""
    cantidad_creada = persona_service.poblar_personas(db, request.cantidad)
    return {
        "message": f"{cantidad_creada} usuarios creados exitosamente",
        "status": 201
    }

@router.delete("/reset", status_code=status.HTTP_200_OK)
def reset_datos(db: Session = Depends(get_db)):
    """Elimina todos los registros de la base de datos."""
    cantidad_borrada = persona_service.reset_personas_service(db)
    return {
        "message": f"Base de datos reiniciada. Se eliminaron {cantidad_borrada} registros.",
        "status": 200
    }

@router.get("/exportar/csv", response_class=Response)
def exportar_datos_csv(db: Session = Depends(get_db)):
    """Descarga la base de datos en formato CSV."""
    csv_data = persona_service.exportar_personas_csv_service(db)
    
    # Retornamos una respuesta cruda modificando las cabeceras HTTP
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=personas.csv"}
    )

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
