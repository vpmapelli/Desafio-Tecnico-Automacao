"""
Desafio Técnico - Automação RPA
Extração de dados da tabela 1209 do SIDRA/IBGE
População com 60 anos ou mais por Unidades da Federação
"""

import argparse
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


TABLE = '1209'
DEFAULT_SLEEP_SECONDS = 1
DEFAULT_TIMEOUT_MS = 1000
DEFAULT_PAGE_TIMEOUT_MS = 10000
MODAL_TIMEOUT_MS = 500
DOWNLOAD_TIMEOUT_MS = 30000  # Timeout para operações de download
AGE_SELECTORS = [
    'text="60 a 69 anos"',
    'text="70 anos ou mais"',
]
class SidraAutomation:
    """Classe para automação de extração de dados do SIDRA/IBGE"""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.base_url = "https://sidra.ibge.gov.br/"
        self.output_dir = Path("dados")
        self.output_file = self.output_dir / "populacao_60mais_1209.csv"
        
    def setup(self):
        """Configura o diretório de saída"""
        self.output_dir.mkdir(exist_ok=True)
        print(f"✓ Diretório '{self.output_dir}' criado/verificado")
        
    def navigate_to_table_1209(self, page):
        """
        Navega pelo site até encontrar a tabela 1209
        Simula o comportamento de um usuário explorando a interface
        """
        print("\n[1/5] Acessando página inicial do SIDRA...")
        page.goto(self.base_url, wait_until="networkidle")
        print("✓ Página inicial carregada")
        
        # Aguardar carregamento completo da página
        page.wait_for_load_state("domcontentloaded")
        time.sleep(DEFAULT_SLEEP_SECONDS)
        
        print("\n[2/5] Buscando pela tabela 1209...")
        try:
            self._search_table(page, TABLE)
            
        except Exception as e:
            print(f"⚠ Erro na busca padrão: {e}")
            #TODO: metodo alternativo
            exit(1)
            
    
    def _search_table(self, page, table):
        try:
            print("Pesquisando tabela...")
        
            search_icon_locator = page.wait_for_selector('a[title="Pesquisa Tabela"]', timeout=DEFAULT_TIMEOUT_MS)
            search_icon_locator.click()

            print("Digitando string no campo de pesquisa...")
            
            search_input_locator = page.wait_for_selector('#sidra-pesquisa-lg input[placeholder="pesquisar"]', timeout=DEFAULT_TIMEOUT_MS)
            search_input_locator.fill(table)

            print("Submetendo pesquisa...")
            
            search_button_locator = page.wait_for_selector('#sidra-pesquisa-lg button:has-text("OK")', timeout=DEFAULT_TIMEOUT_MS)
            search_button_locator.click()

            time.sleep(DEFAULT_SLEEP_SECONDS)
            print("Pesquisa completa.")            

        except Exception as e:
            print(f"✗ Erro ao pesquisar tabela {TABLE}: {e}")
            raise
    
    def configure_table(self, page):
        """
        Configura os filtros da tabela:
        - Grupo de idade: 60 anos ou mais
        - Recorte territorial: Unidades da Federação
        """
        print("\n[3/5] Configurando filtros da tabela...")
        
        try:
            # Aguardar carregamento da interface da tabela
            page.wait_for_load_state("domcontentloaded")
            time.sleep(DEFAULT_SLEEP_SECONDS)
            
            # Procurar por elementos de filtro/configuração
            # Normalmente o SIDRA tem botões ou links para configurar variáveis
            
            # Estratégia: Procurar por "Grupo de idade" e configurar
            print("→ Configurando 'Grupo de idade: 60 anos ou mais'...")
            
            for selector in AGE_SELECTORS:
                try:
                    option = page.wait_for_selector(selector, timeout=DEFAULT_TIMEOUT_MS)
                    if option.is_visible():
                        option.click()
                        print(f"✓ Grupo de idade {selector} selecionado")
                        time.sleep(1)
                except Exception as e:
                    print(f"⚠ Não foi possível selecionar {selector}: {e}")
                    continue
            
            # Configurar Unidades da Federação
            print("→ Configurando 'Unidades da Federação'...")
            
            all_list_items = page.locator('#arvore-niveis > li').all()

            for item_locator in all_list_items:
                target_label = "Unidade da Federação"

                toggle_button_locator = item_locator.locator('.nome-arvore .sidra-toggle').first
                
                # Item que queremos selecionar "Unidade da Federação"
                is_target_item = item_locator.text_content().strip().startswith(target_label)
                
                # Check the current state using the parent div's class
                is_currently_checked = 'checked' in item_locator.locator('.sidra-check').first.get_attribute('class')

                if is_target_item and not is_currently_checked:
                    print(f"  ->  Selecionando: '{target_label}'.")
                    toggle_button_locator.click()

                if not is_target_item and is_currently_checked:
                    print("  ->  Retirando da seleção item não desejado.")
                    toggle_button_locator.click()
            
            print("✓ Tabela configurada com sucesso")
            
        except Exception as e:
            print(f"⚠ Aviso durante configuração: {e}")
            print("Continuando com configurações padrão...")
    
    def download_csv(self, page):
        """Realiza o download do arquivo CSV"""
        print("\n[4/5] Iniciando download do arquivo CSV...")
        
        # Clicka no botão de download
        apply_buttons = [
            'button:has-text("Download")',
        ]
        
        for selector in apply_buttons:
            try:
                apply_btn = page.wait_for_selector(selector, timeout=DEFAULT_TIMEOUT_MS)
                if apply_btn.is_visible():
                    apply_btn.click()
                    print("✓ Botão Download clicado")
                    page.wait_for_load_state("networkidle")
                    time.sleep(2)
                    break
            except Exception as e:
                print(f"⚠ Tentativa de clicar em '{selector}' falhou: {e}")
                continue

        # Configura download

        # Espera modal aparecer
        page.wait_for_selector('#modal-downloads.in', state='visible', timeout=MODAL_TIMEOUT_MS)

        select_locator = page.wait_for_selector('#modal-downloads select[name="formato-arquivo"]', timeout=MODAL_TIMEOUT_MS)

        print("Seleciona formato CSV (BR)...")
        select_locator.select_option(value="br.csv")

        download_button = page.wait_for_selector('#opcao-downloads', timeout=DOWNLOAD_TIMEOUT_MS)
        # Configurar listener para download
        with page.expect_download() as download_info:
            download_button.click()
            print("✓ Download iniciado...")
            
        download = download_info.value

        # Salvar arquivo no caminho especificado
        download.save_as(self.output_file)
        print(f"✓ Arquivo salvo em: {self.output_file}")

    def run(self):
        """Executa a automação completa"""
        print("=" * 60)
        print("DESAFIO TÉCNICO - AUTOMAÇÃO RPA SIDRA/IBGE")
        print("Tabela 1209: População com 60 anos ou mais por UF")
        print("=" * 60)
        
        self.setup()
        
        with sync_playwright() as p:
            # Iniciar browser
            print("\nIniciando navegador...")
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # Configurar timeout padrão
            page.set_default_timeout(DEFAULT_PAGE_TIMEOUT_MS)
            
            try:
                # Executar fluxo de automação
                self.navigate_to_table_1209(page)
                self.configure_table(page)
                self.download_csv(page)
                
                print("\n" + "=" * 60)
                print("[5/5] AUTOMAÇÃO CONCLUÍDA COM SUCESSO! ✓")
                print("=" * 60)
                print(f"\nArquivo gerado: {self.output_file}")
                
                # Verificar se o arquivo foi criado
                if self.output_file.exists():
                    file_size = self.output_file.stat().st_size
                    print(f"Tamanho do arquivo: {file_size:,} bytes")
                else:
                    print("⚠ Arquivo não encontrado no caminho especificado")
                
            except Exception as e:
                print(f"\n✗ ERRO: {e}")
                print("\nCapturando screenshot para debug...")
                page.screenshot(path="erro_debug.png")
                print("Screenshot salvo: erro_debug.png")
                raise
            
            finally:
                # Fechar browser
                browser.close()
                print("\nNavegador fechado.")


def main():
    """Função principal"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Executa o navegador em modo headless (sem interface gráfica)'
    )
    args = parser.parse_args()

    try:
        # Criar instância da automação
        automation = SidraAutomation(headless=args.headless)

        # Executar automação
        automation.run()

    except KeyboardInterrupt:
        print("\n\n⚠ Automação interrompida pelo usuário")
    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
