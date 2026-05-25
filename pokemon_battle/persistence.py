import json
import os

from .constants import ARCHIVO_TOP5


def cargar_top5():
    if os.path.exists(ARCHIVO_TOP5):
        try:
            with open(ARCHIVO_TOP5, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def guardar_top5(top5):
    with open(ARCHIVO_TOP5, "w", encoding="utf-8") as f:
        json.dump(top5, f, ensure_ascii=False, indent=2)


def actualizar_top5(nombre, puntos_delta):
    top5 = cargar_top5()
    encontrado = False
    for e in top5:
        if e["nombre"].lower() == nombre.lower():
            e["puntos"] += puntos_delta
            encontrado = True
            break
    if not encontrado:
        top5.append({"nombre": nombre, "puntos": puntos_delta})
    top5 = sorted(top5, key=lambda x: x["puntos"], reverse=True)[:5]
    guardar_top5(top5)
    return top5
