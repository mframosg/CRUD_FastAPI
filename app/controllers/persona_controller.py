from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, Path
from sqlalchemy.orm import Session

from ..database import get_db
from ..views.persona import (
    PersonaCreate,
    PersonaUpdate,
    PersonaRead,
    PoblarRequest,
    PersonaActivoRead,
    BulkDesactivarRequest,
)
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
# Endpoint para consultar la cantidad de personas por dominio de correo
@router.get("/estadisticas/dominios")
def estadisticas_dominios(db: Session = Depends(get_db)):
    # Llamar al servicio que agrupa y cuenta los dominios
    return persona_service.estadisticas_dominios_service(db)


# Endpoint para consultar las estadísticas de edad de las personas
@router.get("/estadisticas/edad")
def estadisticas_edad(db: Session = Depends(get_db)):
    # Llamar al servicio que calcula el promedio, la edad mínima y máxima
    return persona_service.estadisticas_edad_service(db)

# Endpoint para consultar las personas que cumplen años en un mes específico
@router.get("/cumpleanios/mes/{numero_mes}")
def cumpleanios_mes(
    numero_mes: int = Path(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    # Llamar al servicio que busca las personas según el mes de nacimiento
    return persona_service.cumpleanios_mes_service(db, numero_mes)


@router.get("/buscar/{termino}", response_model=List[PersonaRead])
def buscar_personas(termino: str, db: Session = Depends(get_db)):
    """E. Busca por first_name, last_name o email (OR). Retorna [] si no hay coincidencias."""
    return persona_service.search_personas(db, termino)


@router.get("/reporte/activos", response_model=List[PersonaActivoRead])
def reporte_activos(db: Session = Depends(get_db)):
    """F. Personas activas con proyección: id, email, phone, is_active."""
    return persona_service.list_activos(db)


@router.patch("/bulk/desactivar")
def bulk_desactivar(body: BulkDesactivarRequest, db: Session = Depends(get_db)):
    """H. Desactiva una lista de IDs (1 a 100). Reporta los no encontrados sin fallar."""
    if not body.ids or len(body.ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La lista de ids debe tener entre 1 y 100 elementos.",
        )
    desactivados, no_encontrados = persona_service.bulk_desactivar(db, body.ids)
    return {
        "message": "Operación completada.",
        "desactivados": desactivados,
        "no_encontrados": no_encontrados,
        "total_desactivados": len(desactivados),
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

