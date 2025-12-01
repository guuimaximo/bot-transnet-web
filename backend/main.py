# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
import os
import tempfile

from bot_transnet import fechar_os  # sua função Selenium real

app = FastAPI()


@app.get("/")
def healthcheck():
    return {"status": "ok", "mensagem": "API no ar no Railway"}


@app.post("/fechar-os")
async def api_fechar_os(
    usuario: str = Form(...),
    senha: str = Form(...),
    numero_os: str = Form(...),
    arquivos: List[UploadFile] = File(...)
):
    """
    Endpoint que recebe:
      - usuario / senha do Transnet
      - número da OS
      - arquivos (imagens/PDFs)
    Salva tudo numa pasta temporária e chama o Selenium.
    """
    URL = "https://transnet.grupocsc.com.br/sgtweb/index.php?c=controleAcesso.CLogin&m=verTelaLogin"

    # cria pasta temporária
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # salva arquivos enviados
            nomes_arquivos = []
            for f in arquivos:
                conteudo = await f.read()
                caminho = os.path.join(tmpdir, f.filename)
                with open(caminho, "wb") as out:
                    out.write(conteudo)
                nomes_arquivos.append(f.filename)

            # chama sua automação Selenium
            sucesso = fechar_os(
                URL=URL,
                usuario=usuario,
                senha=senha,
                numero_os=numero_os,
                caminho_do_arquivo=tmpdir,
                headless=True,
            )

            return {
                "status": "ok",
                "resultado": bool(sucesso),
                "numero_os": numero_os,
                "arquivos_processados": nomes_arquivos,
            }

        except Exception as e:
            # aqui qualquer erro do Selenium/Chrome/etc vai voltar em JSON
            return JSONResponse(
                status_code=500,
                content={
                    "status": "erro",
                    "detalhe": str(e),
                },
            )
