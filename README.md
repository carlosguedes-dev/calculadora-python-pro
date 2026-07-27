# 🧮 Calculadora Altamente Profissional em Python

![Python Version](https://img.shields.io/badge/Python-3.14%2B-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1f6feb.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-100%25%20Validadada-success.svg)

Uma calculadora de **alta estética, arquitetura modular e desempenho profissional** desenvolvida em Python 3.14 utilizando **CustomTkinter**. O projeto foi arquitetado por uma equipe de agentes de IA com foco em UI/UX premium, motor matemático seguro (AST parsing) e ergonomia nativa.

---

## 📥 Como Baixar e Instalar no Seu Computador

Você pode baixar e rodar este projeto livremente de duas formas rápidas:

### 🚀 Opção 1: Clonando via Git (Recomendado para Desenvolvedores)
Abra o seu terminal (PowerShell, CMD, ou Terminal do Linux/macOS) e execute os seguintes passos:

```powershell
# 1. Clone o repositório oficial diretamente do GitHub
git clone https://github.com/carlosguedes-dev/calculadora-python-pro.git

# 2. Entre na pasta do projeto
cd calculadora-python-pro

# 3. Crie e ative um ambiente virtual isolado (venv)
python -m venv venv
.\venv\Scripts\Activate.ps1    # No Windows (PowerShell)
# source venv/bin/activate     # No Linux / macOS

# 4. Instale todas as dependências automaticamente via requirements.txt
pip install -r requirements.txt
```

### 📦 Opção 2: Download Direto (Arquivo ZIP - Sem usar Git)
Se você não tem o Git instalado ou prefere baixar o arquivo compactado:
1. Acesse a página do repositório no GitHub: **[carlosguedes-dev/calculadora-python-pro](https://github.com/carlosguedes-dev/calculadora-python-pro)**.
2. Clique no botão verde **"<> Code"** no topo direito da lista de arquivos.
3. Selecione a opção **"Download ZIP"**.
4. Extraia o arquivo baixado no seu computador (por exemplo, na Área de Trabalho ou Documentos).
5. Abra o terminal dentro da pasta extraída e instale as bibliotecas digitando:
   ```powershell
   python -m venv venv
   .\venv\Scripts\pip.exe install -r requirements.txt
   ```

---

## ✨ Destaques Visuais e Funcionais

- **🎨 Design System Modular (`theme_config.py`)**:
  - **3 Temas Visuais Integrados:** *Obsidian Dark* (escuro grafite com acentos em ciano/magenta), *Cyber Neon* (preto OLED com acentos roxo/verde neon) e *Sleek Light* (claro macio e limpo).
  - **Cantos Arredondados & Responsividade:** Interface geométrica inspirada no macOS e Windows 11, com detecção de fontes modernas no sistema (*Segoe UI Variable Display*, *Inter*, *Roboto*) e auto-ajuste de fonte no visor.

- **🧠 Motor Matemático Avançado (`math_engine.py`)**:
  - **🧮 Modo Padrão:** Operações aritméticas, porcentagem (`%`), quadrado (`x²`), raiz quadrada (`√x`), recíproco (`1/x`) e inversão de sinal (`±`).
  - **🔬 Modo Científico:** Funções trigonométricas (`sin`, `cos`, `tan`, `asin`, `acos`, `atan`) com alternância instantânea entre **Graus (DEG)** e **Radianos (RAD)**, logaritmos (`ln`, `log`), exponenciais (`x^y`, `e^x`), constantes (`π`, `e`) e parênteses aninhados `( )`.
  - **💻 Modo Programador:** **4 Visores em tempo real** convertendo simultaneamente em **HEX, DEC, OCT e BIN**. Clicar em qualquer visor muda a base de digitação e habilita/desabilita automaticamente os botões alfanuméricos permitidos (0-9 e A-F). Suporta operações bitwise (`AND`, `OR`, `XOR`, `NOT`, `<<`, `>>`).
  - **🛡️ Avaliação Segura com AST:** Zero uso de `eval()` inseguro; toda expressão é analisada por árvore sintática segura com tratamento de erros graciosos em português.

- **🕒 Painel Retrátil de Histórico e Memória**:
  - Animação slide para exibição de histórico da sessão e pilha de memória (`MC, MR, M+, M-, MS`).
  - **Recurso especial:** Clique em qualquer conta anterior no histórico para recarregar o valor no visor principal e dar continuidade aos cálculos!

- **⌨️ Ergonomia Completa**:
  - Mapeamento total de teclado (Numpad, Enter, Backspace, Esc, parênteses e letras A-F no modo programador).
  - Integração com clipboard via botão **"📋 Copiar"** no visor e atalhos **Ctrl+C / Ctrl+V**.

---

## 🚀 Como Executar no Dia a Dia

Após ter instalado o projeto em seu computador usando uma das opções acima:

### 🏆 Opção 1: Duplo Clique Silencioso (Windows - Recomendado)
Dê dois cliques no arquivo **`Calculadora (Sem Terminal).vbs`** dentro da pasta. A interface abrirá instantaneamente em sua tela de forma oculta e limpa, **sem exibir ou piscar nenhuma janela preta de terminal**!

### ⚙️ Opção 2: Atalho em Lote
Dê dois cliques em **`Abrir Calculadora.bat`**.

### 💻 Opção 3: Via Terminal (PowerShell / CMD)
Certifique-se de estar no diretório do projeto e utilize o interpretador do ambiente virtual:
```powershell
.\venv\Scripts\python.exe main.py
```
> **Nota de Inteligência:** Se você der dois cliques diretamente no arquivo `main.py`, ele detectará automaticamente o ambiente virtual da pasta e se auto-reiniciará no interpretador correto sem dar erro de dependência!

---

## 🧪 Validação e Testes Automatizados

O projeto conta com um modo headless de teste de integração contínua (CI) que valida temas, modos de operação, conversões de base e cliques sem abrir janelas bloqueantes:
```powershell
.\venv\Scripts\python.exe main.py --test
```

---

## 🤝 Como Contribuir
Consulte nosso guia oficial em **[CONTRIBUTING.md](CONTRIBUTING.md)** para saber como configurar seu ambiente, rodar os testes e enviar Pull Requests.

---

## 📂 Estrutura do Projeto

```text
calculadora-python-pro/
│
├── main.py                          # Ponto de entrada com auto-detecção de venv e modo --test
├── gui.py                           # Interface gráfica principal em CustomTkinter
├── math_engine.py                   # Motor matemático, parser AST seguro, histórico e memória
├── theme_config.py                  # Design System, temas visuais, tipografia e geometria
├── requirements.txt                 # Dependências oficiais (para pip install -r requirements.txt)
├── Calculadora (Sem Terminal).vbs   # Launcher invisível para Windows (sem tela preta)
├── Abrir Calculadora.bat            # Launcher em lote com auto-fechamento de console
├── README.md                        # Documentação oficial e guia de download
├── CONTRIBUTING.md                  # Guia de contribuição e padrões
├── LICENSE                          # Licença MIT
└── .gitignore                       # Regras de ignorar venv e arquivos temporários
```
