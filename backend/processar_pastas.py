# backend/processar_pastas.py

import os
import shutil
from fechar_os_definitivo import fechar_os  # importa a função que você já tem

def processar_pastas(
    base_dir: str,
    url: str,
    usuario: str,
    senha: str,
    headless: bool = True
):
    """
    Processa todas as subpastas dentro de 'os_para_processar' a partir de base_dir.
    Cada pasta deve ter o formato: 'prefixo - (numero_os)'.

    As pastas são movidas para:
      - 'os_processadas' se sucesso
      - 'os_erro' em caso de erro
    """

    pasta_origem = os.path.join(base_dir, 'os_para_processar')
    pasta_processadas = os.path.join(base_dir, 'os_processadas')
    pasta_erro = os.path.join(base_dir, 'os_erro')

    # Garante que as pastas existam
    os.makedirs(pasta_origem, exist_ok=True)
    os.makedirs(pasta_processadas, exist_ok=True)
    os.makedirs(pasta_erro, exist_ok=True)

    # Lista subpastas de origem
    pastas_para_processar = [
        nome for nome in os.listdir(pasta_origem)
        if os.path.isdir(os.path.join(pasta_origem, nome))
    ]

    print(f"\nIniciando processamento de {len(pastas_para_processar)} pastas...\n")

    resultados = []

    for pasta in pastas_para_processar:
        caminho_pasta = os.path.join(pasta_origem, pasta)

        try:
            print("=" * 60)
            print(f"📂 Processando pasta: {pasta}")

            # Extrai o número da OS (ex: "prefixo - (1057421)")
            numero_os = pasta.split("-")[-1].strip(" ()")

            # Verifica se há arquivos dentro da pasta
            arquivos = os.listdir(caminho_pasta)
            if not arquivos:
                raise Exception("Nenhum arquivo encontrado na pasta!")

            print(f"📎 {len(arquivos)} arquivo(s) serão anexados.")

            # Chama a automação principal passando a PASTA
            sucesso = fechar_os(
                URL=url,
                usuario=usuario,
                senha=senha,
                numero_os=numero_os,
                caminho_do_arquivo=caminho_pasta,
                headless=headless
            )

            # Define destino
            destino_base = pasta_processadas if sucesso else pasta_erro
            destino_final = os.path.join(destino_base, pasta)

            shutil.move(caminho_pasta, destino_final)
            print(f"📦 Pasta movida para: {destino_base}")

            resultados.append({
                "pasta": pasta,
                "numero_os": numero_os,
                "status": "processada" if sucesso else "erro",
                "destino": destino_base,
            })

        except Exception as e:
            print(f"❌ Erro ao processar pasta '{pasta}': {e}")
            try:
                destino_final = os.path.join(pasta_erro, pasta)
                shutil.move(caminho_pasta, destino_final)
            except Exception as err:
                print(f"⚠️ Falha ao mover pasta com erro: {err}")

            resultados.append({
                "pasta": pasta,
                "numero_os": None,
                "status": "erro",
                "erro": str(e),
                "destino": pasta_erro,
            })

    print("\n✅ Processamento concluído.")
    return resultados


if __name__ == "__main__":
    # Modo "script local" (executar direto em Python)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    URL = "https://transnet.grupocsc.com.br/sgtweb/index.php?c=controleAcesso.CLogin&m=verTelaLogin"
    USUARIO = "COLOCAR SEU USUARIO"
    SENHA = "COLOCAR SUA SENHA"

    processar_pastas(
        base_dir=BASE_DIR,
        url=URL,
        usuario=USUARIO,
        senha=SENHA,
        headless=True,
    )
