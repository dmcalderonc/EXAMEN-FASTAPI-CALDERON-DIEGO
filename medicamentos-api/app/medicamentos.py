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




@router.get("/valorProveedor") 
def cotizacion( 
    
    unidades: Annotated[int, Query(ge=1, le=10)],
    categoria: Annotated[int | None, Query(ge=1, le=10)] = None,
  
) -> dict: 
    resultado = [h for h in MEDICAMENTOS if categoria is None or h["categoria"] == categoria] 
 
    if not resultado: 
        raise HTTPException( 
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No hay medicamentos en la categoria {categoria}", 
        ) 
 
    cantidad = len(resultado) 
    suma_precios= sum(h["precio"] for h in resultado)
    valor_base = suma_precios* unidades


    precio_promedio = round(suma_precios/ cantidad, 2) 

    requiere_receta = sum(1 for h in resultado if h['requiere_receta'])
    porcentaje_con_receta = round((requiere_receta/unidades)*100, 1)

 
    descuento_aplicado = unidades >= 100
    valor_estimado = valor_base *0.88 if  descuento_aplicado else float(valor_base) 

    return { 
        "medicamentos": cantidad, 
        "unidades": unidades, 
        "precio_promedio": precio_promedio, 
        "valor_base": valor_base, 
        "descuento_aplicado": descuento_aplicado, 
        "valor_estimado": round(valor_estimado, 2), 
        "porcentaje_con_receta": porcentaje_con_receta, 
    } 

@router.get("/agotados") 
def agotados( 
    agotados: Annotated[list[str] | None, Query()] = None, 
  
) -> dict: 
    if not MEDICAMENTOS: 
            raise HTTPException( 
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="No hay habitaciones registradas", 
            ) 
     
    codigos_agotados = {c.upper() for c in agotados} if agotados else set() 
    total = 0 
    cant_agotados = 0 
    cant_disponibles = 0 
    ingreso_potencial_libres = 0 
    disponible_mas_economico: str | None = None 
    menor_precio: int | None = None 

    for h in MEDICAMENTOS: 
            total += 1 
            if h["codigo"] in codigos_agotados: 
                cant_agotados += 1 
            else: 
                cant_disponibles += 1 
                precio = h["precio"] 
                ingreso_potencial_libres += precio 
                if menor_precio is None or precio < menor_precio: 
                    menor_precio = precio 
                    disponible_mas_economico = h["codigo"] 
     
    porcentaje_agotado = round((cant_agotados / total) * 100, 1) 

    return { 
        "total": total,
        "agotados": agotados, 
        "disponibles": cant_disponibles, 
        "porcentaje_agotado": porcentaje_agotado, 
        "valor_disponibles": precio, 
        "disponible_mas_economico": disponible_mas_economico, 
    } 



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