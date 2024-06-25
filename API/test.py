from fastapi import FastAPI

app = FastAPI()

def imprimir(titulo: str, descripcion: str):
    mensaje = f"El titulo del video es {titulo} y su descripcion es {descripcion}"
    print(mensaje)
    return mensaje

@app.get("/video/")
def obtener_video(titulo: str, descripcion: str):
    mensaje = imprimir(titulo, descripcion)
    return {"mensaje": mensaje}
