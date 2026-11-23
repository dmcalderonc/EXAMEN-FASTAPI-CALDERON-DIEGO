# app/esquemas.py 
from pydantic import BaseModel, Field 
 
 
class MedicamentoBase(BaseModel): 
    nombre: str = Field(min_length=3, max_length=60) 
    precio: int = Field(ge=1, le=500) 
    categoria: int = Field(ge=1, le=6) 
    requiere_receta: bool = False 
 
 
class MedicamentoCrear(MedicamentoBase): 
    codigo: str = Field(pattern=r"^[A-Z]{3}\d{3}$") 
 
 
class MedicamentoActualizar(BaseModel): 
    nombre: str | None = Field(default=None, min_length=3, max_length=60) 
    precio: int | None = Field(default=None, ge=1, le=500) 
    categoria: int | None = Field(default=None, ge=1, le=6) 
    requiere_receta: bool | None = None 
 
 
class Medicamento(MedicamentoCrear): 
    """Modelo de salida con los cinco campos completos."""
