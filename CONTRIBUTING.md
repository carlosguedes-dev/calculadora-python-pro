# 🤝 Guia de Contribuição - Calculadora Altamente Profissional em Python

Agradecemos o seu interesse em contribuir com a **Calculadora Altamente Profissional**! Nosso objetivo é manter este projeto com o mais alto padrão de qualidade estética (UI/UX) e segurança de código.

Este documento estabelece as diretrizes para participar do desenvolvimento, propor melhorias ou corrigir problemas.

---

## 🧭 1. Como Começar

### Ambiente de Desenvolvimento Isolado
Para garantir que as dependências do projeto não entrem em conflito com as globais da sua máquina, siga os passos abaixo para configurar o ambiente de trabalho:

1. **Faça o Fork do projeto** no GitHub e clone o seu repositório localmente:
   ```powershell
   git clone https://github.com/SEU_USUARIO/calculadora-python-pro.git
   cd calculadora-python-pro
   ```

2. **Crie e Ative um Ambiente Virtual (venv):**
   ```powershell
   # No Windows (PowerShell):
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # No Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as Dependências do Projeto:**
   ```powershell
   pip install --upgrade pip
   pip install customtkinter pyperclip
   ```

---

## 🧪 2. Bateria de Testes Automatizados (CI)

Antes de enviar qualquer alteração, é obrigatório executar a nossa bateria de testes de integração automatizados que valida a inicialização headless, temas, modos de operação e precisão dos cálculos sem abrir janelas interativas bloqueantes.

Para executar os testes no seu terminal:
```powershell
# Usando o interpretador do ambiente virtual:
.\venv\Scripts\python.exe main.py --test
```
> ⚠️ **Importante:** O seu Pull Request só será aprovado se a saída final dos testes for `[SUCESSO TOTAL] TODOS OS REQUISITOS DE UI E FUNCIONALIDADE VALIDADOS 100%!`.

---

## 🎨 3. Padrões de Projeto e Arquitetura

Ao contribuir com código, respeite a divisão de responsabilidades dos módulos existentes:

* **[theme_config.py](theme_config.py) (Design System):**
  * Nenhuma cor ou tamanho de fonte deve ser "chumbado" (hardcoded) direto nas views. Se precisar de uma nova cor ou variação de fonte, declare no dicionário de temas e utilize as funções utilitárias como `get_button_style()`.
  * Mantenha a coerência visual entre os 3 temas oficiais (*Obsidian Dark*, *Cyber Neon*, *Sleek Light*).

* **[math_engine.py](math_engine.py) (Motor Matemático & Segurança):**
  * **Regra de Ouro:** É estritamente proibido o uso da função nativa `eval()` em strings recebidas da interface gráfica por razões de segurança.
  * Utilize o analisador de AST (`SafeEvaluator`) ou adicione funções seguras à whitelist da árvore sintática.
  * Tratamento de erros deve ser feito com mensagens claras e amigáveis em português (ex: `"Erro: Divisão por zero"`), sem lançar exceções não tratadas.

* **[gui.py](gui.py) & Componentes:**
  * Utilize sempre componentes do `CustomTkinter` (`CTkButton`, `CTkLabel`, etc.) mantendo o `corner_radius` padronizado.

---

## 🚀 4. Processo para Pull Request (PR)

1. Crie uma branch para sua nova funcionalidade ou correção:
   ```powershell
   git checkout -b feature/nome-da-sua-melhoria
   # ou para correções:
   git checkout -b fix/nome-do-bug
   ```

2. Realize suas modificações e verifique os testes automatizados (`python main.py --test`).

3. Faça o commit seguindo as boas práticas de **Conventional Commits**:
   * `feat: adiciona conversão para base 32 no modo programador`
   * `fix: corrige truncamento de número em visor pequeno`
   * `docs: atualiza instruções de instalação no README`
   * `style: ajusta espaçamento e padding no tema Cyber Neon`

4. Envie a branch para o seu fork:
   ```powershell
   git push origin feature/nome-da-sua-melhoria
   ```

5. Abra um **Pull Request (PR)** no repositório original descrevendo claramente o que foi alterado e incluindo prints ou GIFs caso tenha alterado o visual da interface.

---

## 💬 5. Dúvidas ou Sugestões?
Abra uma **Issue** na aba de problemas do repositório para discutirmos novas ideias e funcionalidades antes de começar a programar. Estamos sempre abertos a inovações que tornem esta calculadora ainda mais incrível!
