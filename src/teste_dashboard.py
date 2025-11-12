import os
import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, expect # pyright: ignore[reportMissingImports]

# Caminhos base
BASE_DIR = os.path.dirname(__file__)
REPORT_DIR = os.path.join(BASE_DIR, '..', 'reports')
VIDEO_DIR = os.path.join(REPORT_DIR, 'videos')
SCREENSHOT_DIR = os.path.join(REPORT_DIR, 'screenshots')
LOG_FILE = os.path.join(REPORT_DIR, 'test_iframe_log.txt')

# Cria diretórios se não existirem
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def log(msg):
    """Escreve mensagens no console e no arquivo de log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {msg}"
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def test_dashboard_iframe():
    with sync_playwright() as p:
        log("🚀 Iniciando teste com iframe no Dashboard Escolar...")

        # Inicia o navegador com gravação de vídeo
        browser = p.chromium.launch(channel="chrome", headless=False, slow_mo=150)
        context = browser.new_context(
            record_video_dir=VIDEO_DIR,
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        dashboard_url = "https://a3gustavo.streamlit.app/"
        log(f"🌐 Acessando: {dashboard_url}")
        page.goto(dashboard_url, wait_until="networkidle")

        # Aguarda o iframe aparecer e obtém o frame real
        log("⌛ Aguardando iframe do Streamlit carregar...")
        iframe_locator = page.locator('iframe[title="streamlitApp"]')
        iframe_locator.wait_for(state="visible", timeout=60000)
        iframe_element = iframe_locator.element_handle()
        frame = iframe_element.content_frame()

        # Aguarda texto inicial
        log("📘 Aguardando campo 'Selecione a Turma'...")
        expect(frame.get_by_text("Selecione a Turma")).to_be_visible(timeout=30000)

        # Seleciona Turma = 2025B
        log("📘 Selecionando turma '2025B'...")
        combo_turma = frame.get_by_role("combobox", name="Selecione a Turma")
        combo_turma.click()
        page.keyboard.type("2025B")
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        # Seleciona Disciplina = Português
        log("📗 Selecionando disciplina 'Português'...")
        combo_disc = frame.get_by_role("combobox", name="Selecione a Disciplina")
        combo_disc.click()
        page.keyboard.type("Português")
        page.keyboard.press("Enter")

        # Aguarda renderização dos gráficos
        log("📊 Aguardando renderização dos gráficos...")
        expect(frame.get_by_text("Notas da disciplina")).to_be_visible(timeout=20000)
        expect(frame.get_by_text("Percentual de Presença")).to_be_visible(timeout=20000)
        log("✅ Gráficos renderizados com sucesso.")

        # Screenshot inicial
        screenshot_path = os.path.join(SCREENSHOT_DIR, "iframe_inicio.png")
        page.screenshot(path=screenshot_path, full_page=True)
        log(f"📸 Screenshot inicial salva em: {screenshot_path}")

        # --- INÍCIO DA ALTERAÇÃO (5 roladas por print) ---

        log("🎥 Iniciando rolagem automática com 5 roladas por print...")
        log("🖱️ Movendo o mouse para o centro do iframe...")

        iframe_box = iframe_locator.bounding_box()
        if iframe_box:
            page.mouse.move(
                iframe_box['x'] + iframe_box['width'] / 2,
                iframe_box['y'] + iframe_box['height'] / 2
            )
            log("✅ Mouse posicionado.")
        else:
            log("⚠️ Não foi possível localizar o centro do iframe, o scroll pode falhar.")

        # Configurações
        scroll_steps = 1       # número de ciclos (cada ciclo faz N roladas e um print)
        rolls_per_step = 5      # 👈 5 roladas por print
        scroll_amount = 400     # pixels por rolagem
        sleep_time = 1.5        # tempo de espera após cada ciclo (antes do print)
        scroll_index = 1

        log(f"ℹ️ Executando {scroll_steps} ciclos com {rolls_per_step} roladas por print...")

        try:
            for i in range(scroll_steps):
                log(f"📜 Ciclo {i+1}/{scroll_steps} - Executando {rolls_per_step} roladas...")

                for r in range(rolls_per_step):
                    log(f"➡️ Rolagem {r+1}/{rolls_per_step} ({scroll_amount}px)")
                    page.mouse.wheel(0, scroll_amount)
                    time.sleep(0.4)  # intervalo curto entre roladas para fluidez no vídeo

                log(f"⌛ Aguardando {sleep_time}s antes do print...")
                time.sleep(sleep_time)

                scroll_path = os.path.join(SCREENSHOT_DIR, f"iframe_scroll_{scroll_index}.png")
                log(f"⌛ Aguardando {sleep_time}s antes do print...")
                time.sleep(sleep_time)

                scroll_path = os.path.join(SCREENSHOT_DIR, f"iframe_scroll_{scroll_index}.png")
                iframe_locator.screenshot(path=scroll_path)  # <<< corrigido aqui
                log(f"📸 Print {scroll_index} salvo: {scroll_path}")
                scroll_index += 1

        except Exception as e:
            log(f"❌ Erro ao tentar rolar com mouse.wheel: {e}")
            error_path = os.path.join(SCREENSHOT_DIR, "iframe_scroll_ERRO.png")
            page.screenshot(path=error_path, full_page=True)
            log(f"📸 Screenshot de erro salvo em: {error_path}")
            log("Continuando o teste...")

        log("📜 Rolagem concluída.")

        # --- FIM DA ALTERAÇÃO ---

        # Verificação das Estatísticas Rápidas
        log("🔍 Verificando 'Estatísticas Rápidas'...")
        expect(frame.get_by_text("Estatísticas Rápidas")).to_be_visible(timeout=20000)
        expect(frame.get_by_text("Nota média da disciplina")).to_be_visible()
        expect(frame.get_by_text("Presença média da disciplina")).to_be_visible()
        expect(frame.get_by_text("Número de alunos na turma")).to_be_visible()
        log("✅ Estatísticas Rápidas verificadas com sucesso.")

        # Screenshot final
        final_screenshot = os.path.join(SCREENSHOT_DIR, "iframe_dashboard_final.png")
        page.screenshot(path=final_screenshot, full_page=True)
        log(f"📸 Screenshot final salva em: {final_screenshot}")

        # Fecha o contexto e encerra o vídeo
        context.close()
        browser.close()
        log("🏁 Teste concluído com sucesso! Vídeo salvo em:")
        for file in os.listdir(VIDEO_DIR):
            if file.endswith(".webm"):
                log(f"🎬 {os.path.join(VIDEO_DIR, file)}")

if __name__ == "__main__":
    test_dashboard_iframe()
