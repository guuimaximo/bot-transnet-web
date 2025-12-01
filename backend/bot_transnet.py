# backend/bot_transnet.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def fechar_os(
    usuario,
    senha,
    numero_os,
    caminho_do_arquivo,
    headless=True,
    URL="https://transnet.grupocsc.com.br/sgtweb/index.php?c=controleAcesso.CLogin&m=verTelaLogin"
):
    print("Iniciando Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    def handle_alert(context=""):
        try:
            alert = driver.switch_to.alert
            print(f"Alerta detectado ao {context}: '{alert.text}', aceitando...")
            alert.accept()
            time.sleep(0.5)
        except NoAlertPresentException:
            pass

    def safe_click(locator, context=""):
        try:
            print(f"Tentando {context} em {locator}...")
            driver.find_element(*locator).click()
        except UnexpectedAlertPresentException:
            handle_alert(context)
            print(f"Re-tentando {context} em {locator}...")
            driver.find_element(*locator).click()

    try:
        print("Passo 1: Login")
        driver.get(URL)
        wait.until(EC.visibility_of_element_located((By.ID, "edtLogin"))).send_keys(usuario)
        driver.find_element(By.ID, "edtSenha").send_keys(senha)
        safe_click((By.XPATH, "//input[@type='submit' and @value='ENTRAR']"), "clicar em Entrar")
        time.sleep(3)
        handle_alert("login")

        print("Passo 2: Navegando no menu")
        campo = wait.until(EC.visibility_of_element_located((By.ID, "pesquisaMenu")))
        campo.clear(); time.sleep(0.5)
        campo.send_keys("Ordem de Serviço"); time.sleep(0.5)
        campo.send_keys(Keys.ENTER); time.sleep(2)
        for li in driver.find_elements(By.CSS_SELECTOR, "li"):
            if "Manutenção - Ordem de Serviço" in li.text:
                print("Encontrado item de menu, clicando...")
                li.click(); break
        time.sleep(2)
        handle_alert("abrir menu OS")

        print("\n5. Buscando pela OS...")
        campo_codigo_os = wait.until(EC.visibility_of_element_located((By.NAME, 'cdOrdemServico')))
        campo_codigo_os.send_keys(Keys.CONTROL + "a"); campo_codigo_os.send_keys(Keys.DELETE)
        campo_codigo_os.send_keys(numero_os)
        print(f"   - Número da OS '{numero_os}' inserido.")

        ac = ActionChains(driver)
        ac.send_keys(Keys.TAB).perform(); time.sleep(0.5)
        for _ in range(5): ac.send_keys(Keys.UP).perform(); time.sleep(0.2)
        ac.send_keys(Keys.TAB).perform(); time.sleep(0.5)
        for _ in range(3): ac.send_keys(Keys.UP).perform(); time.sleep(0.2)
        ac.send_keys(Keys.TAB).perform(); time.sleep(0.5)
        ac.send_keys("046")
        for _ in range(4): ac.send_keys(Keys.TAB).perform(); time.sleep(0.2)
        ac.send_keys(Keys.DELETE).perform(); time.sleep(0.2)
        ac.send_keys(Keys.TAB).perform(); time.sleep(0.2)
        ac.send_keys(Keys.DELETE).perform(); time.sleep(0.2)
        ac.send_keys(Keys.TAB).perform(); time.sleep(0.2)
        ac.send_keys(Keys.DELETE).perform(); time.sleep(0.2)
        ac.send_keys(Keys.TAB).perform(); time.sleep(0.2)
        print("Limpeza de Campos realizada")
        for _ in range(2): ac.send_keys(Keys.ENTER).perform(); time.sleep(3)
        print("   - Botão 'Pesquisar' clicado.")

        link_da_os = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "1")))
        link_da_os.click()
        print("6. Detalhes da Ordem de Serviço abertos.")

        print("7. Verificando alertas e pop-ups...")
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alerta = driver.switch_to.alert; alerta.accept()
        except Exception:
            pass
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "janelaAuxiliar_close"))).click()
        except Exception:
            pass

        print("8. Anexando arquivos da pasta...")
        wait.until(EC.element_to_be_clickable((By.NAME, "Anexos"))).click()
        time.sleep(3)

        extensoes_permitidas = ['.jpg', '.jpeg', '.png', '.pdf']
        arquivos = [
            os.path.join(caminho_do_arquivo, f)
            for f in os.listdir(caminho_do_arquivo)
            if os.path.isfile(os.path.join(caminho_do_arquivo, f))
            and not f.lower().startswith('thumbs')
            and os.path.splitext(f)[1].lower() in extensoes_permitidas
        ]

        if not arquivos:
            raise Exception("Nenhum arquivo válido para anexo encontrado!")

        for arquivo in arquivos:
            print(f"   - Anexando: {arquivo}")
            input_file = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            input_file.send_keys(arquivo)
            time.sleep(2)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='javascript:submeter();']"))).click()
            time.sleep(2)

        print("8. Usando atalho Alt+Shift+T para voltar...")
        actions.key_down(Keys.ALT).key_down(Keys.SHIFT).send_keys('t').key_up(Keys.SHIFT).key_up(Keys.ALT).perform()
        print("   - Atalho executado.")
        time.sleep(3)

        print("Verificando alertas e pop-ups...")
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alerta = driver.switch_to.alert; alerta.accept()
        except Exception:
            pass
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "janelaAuxiliar_close"))).click()
        except Exception:
            pass
        time.sleep(5)

        print("Verificando se a OS já está fechada...")
        try:
            driver.find_element(By.XPATH, "//a[contains(@href, 'reabrirAtividade')]")
            print("   - OS já está fechada. Finalizando automação sem alterações.")
            return True

        except:
            print("   - OS ainda não está fechada. Prosseguindo com o fechamento.")

            print("9. Clicando em 'Fechar OS'...")
            botao_fechar_os = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'verEncerrarAtividade')]")))
            botao_fechar_os.click()
            print("   - Botão 'Fechar OS' clicado.")
            time.sleep(3)

            print("10. Preenchendo campo de observações...")
            tentativas = 3
            for tentativa in range(tentativas):
                try:
                    ac = ActionChains(driver)
                    for _ in range(10): ac.send_keys(Keys.DELETE).perform(); time.sleep(0.2)
                    for _ in range(10): ac.send_keys(Keys.BACKSPACE).perform(); time.sleep(0.2)
                    ac.send_keys(datetime.now().strftime("%d%m%Y")).perform(); time.sleep(0.2)
                    ac.send_keys(Keys.TAB).perform(); time.sleep(0.2)
                    for _ in range(5): ac.send_keys(Keys.BACKSPACE).perform(); time.sleep(0.2)
                    ac.send_keys(datetime.now().strftime("%H%M")).perform(); time.sleep(0.2)
                    ac.send_keys(Keys.TAB).perform(); time.sleep(0.2)
                    ac.send_keys("******ORDEM DE SERVIÇO EM ANEXO*******")
                    ac.send_keys(Keys.ENTER).perform(); time.sleep(0.2)
                    ac.send_keys(Keys.ENTER).perform(); time.sleep(2)
                    print("   - Observações preenchidas.")
                    break
                except Exception as e:
                    print(f"   [ERRO tentativa {tentativa+1}] Falha ao preencher observações: {e}")
                    driver.save_screenshot(f"erro_observacoes_t{tentativa+1}.png")
                    time.sleep(1)
            else:
                raise Exception("Falha ao preencher observações após múltiplas tentativas.")

            print("11. Preenchendo crachá e confirmando...")
            try:
                for _ in range(2): ac.send_keys(Keys.TAB).perform(); time.sleep(0.2)
                ac.send_keys("046").perform(); time.sleep(0.2)
                for _ in range(3): ac.send_keys(Keys.TAB).perform(); time.sleep(0.2)
                ac.send_keys("30060534").perform(); time.sleep(0.2)
                for _ in range(2): ac.send_keys(Keys.ENTER).perform(); time.sleep(0.2)
                print("   - Crachá preenchido e OK clicado.")
            except Exception as e:
                print(f"   [ERRO] Não foi possível preencher o crachá: {e}")
                driver.save_screenshot("erro_cracha.png")
                raise

            print("PASSO FINAL: Encerrando OS...")
            dropdowns_situacao = driver.find_elements(By.NAME, 'csSituacao[]')
            print(f"   - {len(dropdowns_situacao)} SRs encontradas.")

            if dropdowns_situacao:
                for i, dropdown in enumerate(dropdowns_situacao):
                    select_obj = Select(dropdown)
                    if select_obj.first_selected_option.text == "Em Aberto":
                        select_obj.select_by_visible_text("Atendida")
                        print(f"     - SR #{i+1} alterada para 'Atendida'.")
                    else:
                        print(f"     - SR #{i+1} já está '{select_obj.first_selected_option.text}'.")
            else:
                print("   - Nenhuma SR vinculada. Prosseguindo com encerramento.")

            tentativas = 5
            for tentativa in range(1, tentativas + 1):
                try:
                    print(f"   - Tentativa {tentativa}: clicando em 'Encerrar'...")
                    botao_encerrar = wait.until(EC.element_to_be_clickable((By.NAME, 'encerrar')))
                    botao_encerrar.click()

                    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'OS Fechada !')]")))
                    print("   - OS encerrada com sucesso e confirmação visível na tela.")
                    break

                except Exception as e:
                    print(f"     ⚠ Tentativa {tentativa} falhou: {e}")
                    if tentativa == tentativas:
                        print("     ❌ Não foi possível encerrar a OS após múltiplas tentativas.")
                        driver.save_screenshot("erro_final_encerrar.png")
                        raise
                    time.sleep(2)

            print("\n========================================================")
            print(f"!!! SUCESSO! OS {numero_os} PROCESSADA E FECHADA! !!!")
            print("========================================================")
            return True

    finally:
        driver.quit()
        print("Navegador fechado.")
