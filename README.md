# Desafio Técnico - Automação RPA SIDRA/IBGE

Automação desenvolvida para extrair dados da **Tabela 1209** do SIDRA/IBGE (População por grupos de idade), filtrando especificamente a população com **60 anos ou mais** por **Unidades da Federação (UF)**.

## 📋 Sobre o Projeto

Este projeto implementa uma solução que:

- Navega automaticamente pelo site SIDRA/IBGE (https://sidra.ibge.gov.br/)
- Localiza a Tabela 1209 através da interface (sem acesso direto à URL)
- Configura os filtros necessários
- Realiza o download dos dados em formato CSV
- Salva o arquivo no caminho `dados/populacao_60mais_1209.csv`

## 🚀 Passo a Passo de Execução

### Pré-requisitos

- Python 3.10 ou superior (testado em 3.12)
- pip (gerenciador de pacotes Python)
- Opcional:
  - mise

### 1. Clonar o Repositório

```bash
git clone https://github.com/vpmapelli/Desafio-Tecnico-Automacao.git
cd Desafio-Tecnico-Automacao
```

### 2. Instalar Dependências

#### 2.1 Ambiente virtual (opcional)
Recomendável criar um ambiente python isolado para instalar as dependências

```bash
python -m venv .venv
```

Se utilizar [mise](https://mise.jdx.dev/) para desenvolvimento, execute:

```bash
mise install
``` 

Isso garantirá a mesma versão de python (3.12.11) para desenvolvimento.

#### 2.2 Dependências
```bash
# Instalar a biblioteca Playwright
pip install -r requirements.txt

# Instalar os browsers do Playwright
playwright install chromium
```

### 3. Executar a Automação

```bash
python desafio_ibge_1209.py
```

Para execução headless:

```bash
python desafio_ibge_1209.py --headless
```

## 📦 Dependências Necessárias

- **Playwright** (1.48.0): Framework de automação web da Microsoft
  - Suporta Chromium, Firefox e WebKit
  - Possui excelente tratamento de esperas e estabilidade

### Por que Playwright?

- Além de ser uma biblioteca robusta com diversas features interessantes, a escolha pelo Playwright se deu principalmente por parecer ter uma API mais amigável do que o selenium em uma análise exploratório das documentações.


## 🎯 Estratégia Adotada

### 1. Arquitetura Orientada a Objetos

O código foi estruturado usando uma classe `SidraAutomation` que encapsula toda a lógica de automação, facilitando manutenção e extensibilidade.

### 2. Aceleração do desenvolvimento

Dado o prazo e escopo do desafio, foi utilizado um código base como ponto de partida gerado a partir do modelo Claude Sonnet 4.5.


### 3. Seletores Resilientes

Uso de múltiplos seletores CSS para cada elemento, através de análise do html da página, com intuito de manter o código funcional:

```python
search_selectors = [
    'input[type="search"]',
    'input[name="pesquisa"]',
    'input[placeholder*="Pesquis"]',
    '#pesquisa',
    '.pesquisa'
]
```

### 4. Configuração de Filtros

A automação configura dinamicamente:

- **Grupo de idade**: Seleciona os grupos que correspondem a idade de 60 anos ou mais
- **Recorte territorial**: Define "Unidades da Federação"

### 5. Download e Persistência

- Utiliza a API de downloads do Playwright
- Cria automaticamente o diretório `dados/` se não existir
- Salva o arquivo com nome padronizado: `populacao_60mais_1209.csv`

### 6. Tratamento de Erros

Implementa camadas de tratamento como:

- Timeout configurável para elementos
- Screenshot em caso de erro para debug
- Mensagens informativas durante toda a execução

## 🔧 Principais Desafios Encontrados

### 1. Interface Dinâmica do SIDRA

**Desafio**: O site SIDRA possui interface com carregamento dinâmico e elementos que aparecem/desaparecem, como o modal para download da tabela:

**Solução**: 
- Implementação de esperas explícitas (`wait_for_selector`)
- Uso de `wait_for_load_state("networkidle")` para garantir carregamento completo

### 2. Variabilidade nos Seletores

**Desafio**: Elementos da página podem ter IDs, classes ou atributos diferentes.

**Solução**: 
- Verificação de ids e classes genéricos para elementos de interesse
- Uso de seletores baseados em texto quando possível

### 3. Configuração de Filtros

**Desafio**: Interface de configuração da tabela pode variar, sendo o principal problema encontrado a configuração do filtro de 'Unidade de Federação'. Isso porque as opções em si podem ou não ser árvores, dificultando a lógica.

**Solução**: 
- Tentativa de diferentes métodos de seleção
- Lógica para evitar pegar múltiplos elementos (.first) para uma classe de interesse (e.g., ```.sidra-check```)
- Verificação para validar se somente filtro de interesse está selecionado

### 4. Download de Arquivos

**Desafio**: Garantir que o arquivo seja baixado corretamente e salvo no local especificado.

**Solução**: 
- Uso da API nativa de downloads do Playwright
- Verificação de existência e tamanho do arquivo
- Criação automática de diretórios necessários

### 6. Robustez e Manutenibilidade

**Desafio**: Criar código que seja resiliente a mudanças no site.

**Solução**: 
- Código modular e bem documentado
- Separação clara de responsabilidades
- Logs informativos em cada etapa
- Captura de screenshots para debug

## 📁 Estrutura de Arquivos

```
.
├── desafio_ibge_1209.py          # Script principal de automação
├── requirements.txt               # Dependências do projeto
├── README.md                      # Esta documentação
└── dados/                         # Diretório criado automaticamente
    └── populacao_60mais_1209.csv  # Arquivo CSV gerado
```

## 📊 Saída Esperada

O arquivo CSV gerado contém dados estruturados com:
- População com 60 anos ou mais
- Segmentado por Unidade da Federação
- Ano mais recente disponível

## 🔄 Possíveis Melhorias Futuras

- [ ] Implementar logs estruturados (usando logging)
- [ ] Adicionar testes automatizados
- [ ] Criar configuração via arquivo YAML/JSON com as variáveis globais (timeouts, diretório de saída, nome do arquivo)
- [ ] Implementar retry automático em caso de falhas
- [ ] Adicionar suporte para múltiplas tabelas
- [ ] Criar uma interface CLI mais robusta com argumentos como ```--output FILE```, ```--output-dir DIR```
- [ ] Implementar validação dos dados baixados
- [ ] Aprimorar lógica de seleção de filtros

---

**Data de desenvolvimento**: Novembro 2025  
**Tecnologia**: Python 3 + Playwright
