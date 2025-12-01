# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
import tempfile
import os

from bot_transnet import fechar_os

app = FastAPI()

@app.post("/fechar-os")
async def api_fechar_os(
    usuario: str = Form(...),
    senha: str = Form(...),
    numero_os: str = Form(...),
    arquivos: List[UploadFile] = File(...)
):
    # Cria pasta temporária para salvar as imagens
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Salvar todos os arquivos enviados
            for f in arquivos:
                conteudo = await f.read()
                caminho = os.path.join(tmpdir, f.filename)
                with open(caminho, "wb") as out:
                    out.write(conteudo)

            # Chama o Selenium
            resultado = fechar_os(
                usuario=usuario,
                senha=senha,
                numero_os=numero_os,
                caminho_do_arquivo=tmpdir,
                headless=True
            )

            return {"status": "ok", "resultado": bool(resultado)}

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"status": "erro", "detalhe": str(e)},
            )
