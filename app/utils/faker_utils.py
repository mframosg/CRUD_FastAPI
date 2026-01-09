import random
from faker import Faker
from typing import List, Dict, Any

fake = Faker('es_ES')
DOMINIOS_REALES = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com']

def generar_personas(cantidad: int) -> List[Dict[str, Any]]:
    """Genera personas para inserción masiva."""
    if cantidad <= 0 or cantidad >= 1000:
        raise ValueError("Cantidad debe estar entre 1 y 999")
    
    personas = []
    for _ in range(cantidad):
        firstname = fake.first_name()
        lastname = fake.last_name()
        dominio = random.choice(DOMINIOS_REALES)
        personas.append({
            "firstname": firstname,
            "lastname": lastname,
            "email": f"{firstname.lower()}.{lastname.lower()}@{dominio}",
            "phone": fake.phone_number()[:15],
            "birthdate": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
            "isactive": random.choice([True, False]),
            "notes": fake.sentence(nb_words=6) if random.random() > 0.2 else None
        })
    return personas