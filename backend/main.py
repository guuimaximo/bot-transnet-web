# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
import tempfile
import os

from fechar_os_definitivo import fechar_os
from processar_pastas import processar_pastas

app = FastAPI()

URL_PADRAO = "https://transnet.grupocsc.com.br/sgtweb/index.php?c=controleAcesso.CLogin&m=verTelaLogin"

@app.post("/fechar-os")
async def api_fechar_os(
    usuario: str = Form(...),
    senha: str = Form(...),
    numero_os: str = Form(...),
    arquivos: List[UploadFile] = File(...)
):
    """
    Endpoint para processar UMA única OS, com arquivos enviados via formulário.
    Essa é a rota ideal para o seu futuro site:
      - usuário digita login/senha
      - informa número da OS
      - sobe imagens
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Salva arquivos da requisição em tmpdir
            for f in arquivos:
                conteudo = await f.read()
                caminho = os.path.join(tmpdir, f.filename)
                with open(caminho, "wb") as out:
                    out.write(conteudo)

            # Chama o Selenium
            sucesso = fechar_os(
                URL=URL_PADRAO,
                usuario=usuario,
                senha=senha,
                numero_os=numero_os,
                caminho_do_arquivo=tmpdir,
                headless=True,
            )

            return {"status": "ok", "resultado": bool(sucesso)}

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"status": "erro", "detalhe": str(e)},
            )


@app.post("/processar-pastas")
async def api_processar_pastas(
    usuario: str = Form(...),
    senha: str = Form(...),
    base_dir: str = Form(...),
):
    """
    Endpoint para disparar o processamento em lote das pastas:
      - base_dir/os_para_processar
      - base_dir/os_processadas
      - base_dir/os_erro

    Obs: isso faz mais sentido para você usar no servidor ou localmente,
    não tanto para usuário final.
    """
    try:
        resultados = processar_pastas(
            base_dir=base_dir,
            url=URL_PADRAO,
            usuario=usuario,
            senha=senha,
            headless=True,
        )
        return {"status": "ok", "resultados": resultados}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "erro", "detalhe": str(e)},
        )
