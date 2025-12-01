# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form
from typing import List

app = FastAPI()

@app.get("/")
def healthcheck():
    return {"status": "ok", "mensagem": "API no ar no Railway"}

@app.post("/fechar-os")
async def fechar_os_teste(
    usuario: str = Form(...),
    senha: str = Form(...),
    numero_os: str = Form(...),
    arquivos: List[UploadFile] = File(...)
):
    # Por enquanto, não chama Selenium. Só responde OK.
    nomes_arquivos = [f.filename for f in arquivos]
    return {
        "status": "ok",
        "resultado": True,
        "usuario": usuario,
        "numero_os": numero_os,
        "arquivos_recebidos": nomes_arquivos,
    }
