import logging
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def iniciar_driver(headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=pt-BR")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        logging.info("🌐 Navegador iniciado com sucesso.")
        return driver
    except WebDriverException as exc:
        logging.error(f"❌ Não foi possível iniciar o navegador: {exc}")
        raise


def esperar_elemento(driver, condicao, timeout=10, tentativas=3, delay=3.1):
    for tentativa in range(1, tentativas + 1):
        try:
            elemento = WebDriverWait(driver, timeout).until(condicao)
            logging.info(f"✅ Elemento encontrado na tentativa {tentativa}/{tentativas}.")
            return elemento
        except (TimeoutException, WebDriverException) as exc:
            logging.warning(
                f"⚠️ Falha ao aguardar elemento na tentativa {tentativa}/{tentativas}: {exc}"
            )
            if tentativa < tentativas:
                time.sleep(delay)
    raise TimeoutException(f"Elemento não encontrado após {tentativas} tentativas.")


def find_elemento(driver, by, valor, timeout=10, tentativas=3, delay=3.1):
    condicao = EC.presence_of_element_located((by, valor))
    return esperar_elemento(driver, condicao, timeout, tentativas, delay)


def fechar_driver(driver):
    if driver:
        try:
            driver.quit()
            logging.info("🧹 Navegador encerrado.")
        except WebDriverException as exc:
            logging.warning(f"⚠️ Não foi possível encerrar o navegador corretamente: {exc}")
