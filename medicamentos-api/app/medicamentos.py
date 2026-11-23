from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import MEDICAMENTOS
from app.esquemas import Medicamento, MedicamentoActualizar, MedicamentoCrear

router = APIRouter(prefix="/medicamentos", tags=["medicamentos"])


def obtener_medicamento(codigo: str) -> dict:
    """Devuelve el diccionario de la medicamento o lanza 404."""
    for medicamento in MEDICAMENTOS:
        if medicamento["codigo"] == codigo.upper():
            return medicamento
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la medicamento '{codigo}'",
    )


MedicamentoEncontrado = Annotated[dict, Depends(obtener_medicamento)]




@router.get("", response_model=list[Medicamento])
def listar_medicamentos(
    categoria: Annotated[int | None, Query(ge=1, le=10)] = None,
    solo_requiere_receta : bool = False,
) -> list[dict]:
    resultado = MEDICAMENTOS
    if categoria is not None:
        resultado = [m for m in resultado if m["categoria"] == categoria]
    if solo_requiere_receta :
        resultado = [m for m in resultado if m["obligatoria"]]
    return resultado


@router.post("", response_model=Medicamento, status_code=status.HTTP_201_CREATED)
def crear_medicamento(nueva: MedicamentoCrear) -> dict:
    if any(m["codigo"] == nueva.codigo for m in MEDICAMENTOS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El medicamento '{nueva.codigo}' ya existe",
        )
    MEDICAMENTOS.append(nueva.model_dump())
    return MEDICAMENTOS[-1]


@router.get("/{codigo}", response_model=Medicamento)
def ver_medicamento(medicamento: MedicamentoEncontrado) -> dict:
    return medicamento


@router.put("/{codigo}", response_model=Medicamento)
def actualizar_medicamento(cambios: MedicamentoActualizar, medicamento: MedicamentoEncontrado) -> dict:
    medicamento.update(cambios.model_dump(exclude_unset=True))
    return medicamento


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medicamento(medicamento: MedicamentoEncontrado) -> None:
    MEDICAMENTOS.remove(medicamento)