from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, literal_column, or_

from ..models.persona import Persona
from ..views.persona import PersonaCreate, PersonaUpdate
from .errors import PersonaNotFoundError, EmailAlreadyExistsError

import random
from faker import Faker

import csv
import io


def create_persona(db: Session, payload: PersonaCreate) -> Persona:
    """Create a Persona ensuring unique email."""
    # Optimistic check; DB unique constraint is the final guard
    if db.query(Persona).filter(Persona.email == payload.email).first():
        raise EmailAlreadyExistsError()
    obj = Persona(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        birth_date=payload.birth_date,
        is_active=payload.is_active,
        notes=payload.notes,
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Catch race conditions on unique email
        raise EmailAlreadyExistsError() from e
    db.refresh(obj)
    return obj


def list_personas(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Persona]:
    """Return paginated list of Personas."""
    return db.query(Persona).offset(skip).limit(limit).all()


def get_persona(db: Session, persona_id: int) -> Persona:
    """Return Persona by ID or raise if not found."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()
    return obj


def update_persona(db: Session, persona_id: int, payload: PersonaUpdate) -> Persona:
    """Update Persona partially, enforcing unique email."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()

    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] != obj.email:
        if db.query(Persona).filter(Persona.email == data["email"], Persona.id != persona_id).first():
            raise EmailAlreadyExistsError()

    for field, value in data.items():
        setattr(obj, field, value)

    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise EmailAlreadyExistsError() from e
    db.refresh(obj)
    return obj


def delete_persona(db: Session, persona_id: int) -> None:
    """Delete Persona by ID or raise if not found."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()
    db.delete(obj)
    db.commit()

def poblar_personas(db: Session, cantidad: int) -> int:
    """Genera e inserta un número específico de Personas usando Faker."""
    fake = Faker('es_CO') 
    nuevas_personas = []
    dominios = ['@gmail.com', '@outlook.com', '@hotmail.com', '@yahoo.com'] 

    for _ in range(cantidad):
        nombre = fake.first_name()
        apellido = fake.last_name()
        
        correo_base = f"{nombre.lower().replace(' ', '')}.{apellido.lower().replace(' ', '')}"
        correo = f"{correo_base}{random.choice(dominios)}"
        
        contador = 1
        while db.query(Persona).filter(Persona.email == correo).first():
            correo = f"{correo_base}{contador}{random.choice(dominios)}"
            contador += 1
            
        nueva_persona = Persona(
            first_name=nombre,
            last_name=apellido,
            email=correo,
            phone=fake.phone_number()[:30], 
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=85),
            is_active=random.choice([True, False]),
            notes=fake.sentence() if random.choice([True, False]) else None
        )
        nuevas_personas.append(nueva_persona)

    db.add_all(nuevas_personas)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Se generaron correos duplicados en el mismo lote. Intenta de nuevo con una cantidad menor.")
    
    return len(nuevas_personas)


def reset_personas_service(db: Session) -> int:
    """Elimina todos los registros de la tabla Persona."""
    # db.query(Persona).delete() borra todo eficientemente sin cargar los objetos en memoria
    filas_borradas = db.query(Persona).delete()
    db.commit()
    return filas_borradas

def exportar_personas_csv_service(db: Session) -> str:
    """Consulta todos los registros y retorna un string en formato CSV."""
    personas = db.query(Persona).all()
    salida = io.StringIO()
    escritor = csv.writer(salida)
    
    # Escribir encabezados
    escritor.writerow(['id', 'first_name', 'last_name', 'email', 'phone', 'birth_date', 'is_active', 'notes'])
    
    # Escribir filas extrayendo los datos de cada objeto SQLAlchemy
    for p in personas:
        escritor.writerow([p.id, p.first_name, p.last_name, p.email, p.phone, p.birth_date, p.is_active, p.notes])
        
    return salida.getvalue()

# Servicio para calcular estadísticas por dominio de correo usando GROUP BY
def estadisticas_dominios_service(db: Session):
    # Extraer el dominio del correo directamente desde SQL
    dominio = func.substring_index(Persona.email, "@", -1)

    # Agrupar los correos por dominio y contar las personas
    resultados = (
        db.query(
            dominio.label("dominio"),
            func.count(Persona.id).label("cantidad")
        )
        .group_by(dominio)
        .all()
    )

    # Convertir los resultados en un diccionario
    return {dominio: cantidad for dominio, cantidad in resultados}

# Servicio para calcular estadísticas de edad
def estadisticas_edad_service(db: Session):

    # Calcular la edad cumplida de cada persona usando SQL
    edad = func.timestampdiff(
        literal_column("YEAR"),
        Persona.birth_date,
        func.curdate()
    )

    # Calcular el promedio, la edad mínima y la edad máxima
    resultados = db.query(
        func.round(func.avg(edad), 1).label("edad_promedio"),
        func.min(edad).label("edad_minima"),
        func.max(edad).label("edad_maxima")
    ).first()

    # Retornar las estadísticas en un diccionario
    return {
        "edad_promedio": float(resultados.edad_promedio) if resultados.edad_promedio is not None else None,
        "edad_minima": resultados.edad_minima,
        "edad_maxima": resultados.edad_maxima
    }
    
# Servicio para consultar las personas que cumplen años en un mes específico
def cumpleanios_mes_service(db: Session, numero_mes: int):

    # Buscar las personas cuya fecha de nacimiento corresponde al mes indicado
    resultados = db.query(Persona).filter(
        func.month(Persona.birth_date) == numero_mes
    ).all()

    # Retornar la lista de personas encontradas
    return resultados


def search_personas(db: Session, termino: str) -> Sequence[Persona]:
    """Busca el término en first_name, last_name o email (OR, coincidencia parcial)."""
    patron = f"%{termino}%"
    return (
        db.query(Persona)
        .filter(
            or_(
                Persona.first_name.ilike(patron),
                Persona.last_name.ilike(patron),
                Persona.email.ilike(patron),
            )
        )
        .all()
    )


def list_activos(db: Session) -> Sequence[Persona]:
    """Retorna las personas con is_active = true."""
    return db.query(Persona).filter(Persona.is_active.is_(True)).all()


def bulk_desactivar(db: Session, ids: list[int]) -> tuple[list[int], list[int]]:
    """Desactiva en una sola operación los IDs existentes y reporta los no encontrados."""
    ids_unicos = list(dict.fromkeys(ids))
    existentes = {i for (i,) in db.query(Persona.id).filter(Persona.id.in_(ids_unicos)).all()}
    if existentes:
        db.query(Persona).filter(Persona.id.in_(existentes)).update(
            {Persona.is_active: False}, synchronize_session=False
        )
        db.commit()
    desactivados = [i for i in ids_unicos if i in existentes]
    no_encontrados = [i for i in ids_unicos if i not in existentes]
    return desactivados, no_encontrados
