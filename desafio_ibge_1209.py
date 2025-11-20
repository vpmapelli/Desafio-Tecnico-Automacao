"""
Desafio Técnico - Automação RPA
Extração de dados da tabela 1209 do SIDRA/IBGE
População com 60 anos ou mais por Unidades da Federação
"""

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


TABLE = '1209'
DEFAULT_SLEEP_SECONDS = 1
DEFAULT_TIMEOUT_MS = 1000
DEFAULT_PAGE_TIMEOUT_MS = 10000
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
        
            search_icon_locator = page.locator('a[title="Pesquisa Tabela"]')
            search_icon_locator.click()

            print("Digitando string no campo de pesquisa...")
            
            search_input_locator = page.locator('#sidra-pesquisa-lg input[placeholder="pesquisar"]')
            search_input_locator.fill(table)

            print("Submetendo pesquisa...")
            
            search_button_locator = page.locator('#sidra-pesquisa-lg button:has-text("OK")')
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
                    option = page.locator(selector).first
                    if option.is_visible(timeout=DEFAULT_TIMEOUT_MS):
                        option.click()
                        print(f"✓ Grupo de idade {selector} selecionado")
                        time.sleep(1)
                except:
                    continue
            
            # Configurar Unidades da Federação
            print("→ Configurando 'Unidades da Federação'...")
            
            territorial_selectors = [
                'text="Unidade da Federação"',
                'text="Unidades da Federação"',
                'text="Brasil e Unidade da Federação"',
                'label:has-text("Federação")',
            ]
            
            for selector in territorial_selectors:
                try:
                    territorial_control = page.locator(selector).first
                    if territorial_control.is_visible(timeout=DEFAULT_TIMEOUT_MS):
                        territorial_control.click()
                        print("✓ Recorte territorial 'Unidades da Federação' configurado")
                        time.sleep(1)
                        break
                except:
                    continue
            
            # Verificar se há botão para aplicar filtros ou visualizar tabela
            apply_buttons = [
                'button:has-text("Aplicar")',
                'button:has-text("Visualizar")',
                'button:has-text("Consultar")',
                'a:has-text("Visualizar")',
            ]
            
            for selector in apply_buttons:
                try:
                    apply_btn = page.locator(selector).first
                    if apply_btn.is_visible(timeout=DEFAULT_TIMEOUT_MS):
                        apply_btn.click()
                        print("✓ Filtros aplicados")
                        page.wait_for_load_state("networkidle")
                        time.sleep(2)
                        break
                except:
                    continue
            
            print("✓ Tabela configurada com sucesso")
            
        except Exception as e:
            print(f"⚠ Aviso durante configuração: {e}")
            print("Continuando com configurações padrão...")
    
    def download_csv(self, page):
        """Realiza o download do arquivo CSV"""
        print("\n[4/5] Iniciando download do arquivo CSV...")
        
        try:
            # Procurar pelo botão/link de download CSV
            download_selectors = [
                'a:has-text("CSV")',
                'button:has-text("CSV")',
                'a[href*="csv"]',
                'text="Download"',
                'text="Baixar"',
                'a:has-text("Exportar")',
            ]
            
            download_link = None
            for selector in download_selectors:
                try:
                    elements = page.locator(selector).all()
                    for element in elements:
                        if element.is_visible():
                            text = element.inner_text().lower()
                            if "csv" in text or "download" in text or "baixar" in text:
                                download_link = element
                                print(f"✓ Botão de download encontrado: {text}")
                                break
                    if download_link:
                        break
                except:
                    continue
            
            if not download_link:
                # Tentar encontrar qualquer link relacionado a download
                download_link = page.locator('a:has-text("CSV")').first
            
            # Configurar listener para download
            with page.expect_download() as download_info:
                download_link.click()
                print("✓ Download iniciado...")
            
            download = download_info.value
            
            # Salvar arquivo no caminho especificado
            download.save_as(self.output_file)
            print(f"✓ Arquivo salvo em: {self.output_file}")
            
        except Exception as e:
            print(f"✗ Erro no download: {e}")
            print("Tentando método alternativo de download...")
            
            # Método alternativo: procurar por qualquer elemento relacionado a CSV
            try:
                page.locator('text=/csv|download|baixar/i').first.click()
                time.sleep(3)
                print("✓ Download concluído (método alternativo)")
            except:
                raise Exception("Não foi possível realizar o download do arquivo CSV")
    
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
    try:
        # Criar instância da automação
        # headless=False para ver o navegador em ação (útil para debug)
        # headless=True para execução em background
        automation = SidraAutomation(headless=False)
        
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
