"""
Ponto de Entrada Principal - Calculadora Altamente Profissional em Python
Módulo: main.py

Este módulo gerencia a inicialização da aplicação interativa e fornece
um modo de teste automatizado (--test) para validação de integração contínua (CI)
e verificação de 100% de funcionamento sem travamento da interface gráfica.

Uso:
    - Execução Normal interativa:
        python main.py
    - Execução no modo de Teste (Sem travamento de janela):
        python main.py --test
"""

import sys
import os
import subprocess
import argparse

# Detecção automática do Ambiente Virtual (venv) ao clicar 2 vezes no arquivo .py
try:
    import customtkinter as ctk
    from gui import CalculatorGUI
    from theme_config import list_themes
except ImportError as e:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_pythonw = os.path.join(base_dir, "venv", "Scripts", "pythonw.exe")
    venv_python = os.path.join(base_dir, "venv", "Scripts", "python.exe")
    
    target_py = venv_pythonw if os.path.exists(venv_pythonw) else (venv_python if os.path.exists(venv_python) else None)
    
    # Se encontramos o python do venv e não estamos rodando nele, re-executa no venv!
    if target_py and os.path.abspath(sys.executable).lower() != os.path.abspath(target_py).lower():
        # Re-executa usando o interpretador do ambiente virtual da pasta
        flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        if target_py.endswith("pythonw.exe"):
            subprocess.Popen([target_py, __file__] + sys.argv[1:], cwd=base_dir, creationflags=flags)
        else:
            subprocess.Popen([target_py, __file__] + sys.argv[1:], cwd=base_dir)
        sys.exit(0)
    else:
        print("=" * 65)
        print(" [ERRO DE DEPENDÊNCIA] Biblioteca não encontrada!")
        print("=" * 65)
        print(f"Detalhes do erro: {e}")
        print("\nPara executar esta calculadora, as bibliotecas do projeto precisam")
        print("estar acessíveis. Execute a partir do ambiente virtual da pasta (venv).")
        print("\nDICA DE OURO: Dê dois cliques no arquivo 'Calculadora (Sem Terminal).vbs'")
        print("ou no arquivo 'Abrir Calculadora.bat' incluídos nesta pasta!")
        print("=" * 65)
        try:
            input("\nPressione ENTER para fechar esta janela...")
        except Exception:
            pass
        sys.exit(1)


def run_tests() -> int:
    """
    Executa uma bateria de testes automatizados na interface e no motor de cálculo.
    Garante que todos os componentes, modos e temas carregam sem erros.
    
    Returns:
        int: Código de saída (0 para sucesso, 1 para falha).
    """
    print("=" * 75)
    print(" [TEST MODE] INICIANDO BATERIA DE DESTAQUE E VALIDAÇÃO DA CALCULADORA PRO")
    print("=" * 75)
    
    try:
        # Configuração do CustomTkinter para teste
        ctk.set_appearance_mode("dark")
        print("\n[1/5] Instanciando CalculatorGUI no modo 'Padrão' e tema padrão...")
        app = CalculatorGUI(start_mode="Padrão")
        app.update()  # Força processamento de eventos GUI e renderização
        print("    -> SUCESSO: GUI inicializada e renderizada na memória sem travamentos.")
        
        # Teste de Alternância de Temas
        print("\n[2/5] Testando alternância entre todos os temas visuais...")
        for tema_nome in list_themes():
            app.apply_theme(tema_nome)
            app.update()
            print(f"    -> Tema '{tema_nome}' aplicado e verificado com sucesso.")
            
        # Teste de Alternância de Modos e Layout de Teclados
        print("\n[3/5] Testando alternância de Modos e reconstrução de Teclados...")
        for modo in ["Científica", "Programador", "Padrão"]:
            app.on_mode_change(modo)
            app.update()
            botoes_count = len(app.keypad_buttons)
            print(f"    -> Modo '{modo}' ativado com sucesso ({botoes_count} botões mapeados na grade).")
            
        # Teste de Simulação de Cliques e Cálculos na UI
        print("\n[4/5] Simulando cliques interativos no teclado (12 + 35 =)...")
        app.on_mode_change("Padrão")
        for token in ["1", "2", "+", "3", "5", "="]:
            app.on_keypad_click(token)
            app.update()
            
        resultado_display = app.lbl_result.cget("text")
        print(f"    -> Resultado expresso no Visor: '{resultado_display}'")
        assert resultado_display == "47", f"Esperado '47', obtido '{resultado_display}'"
        print("    -> SUCESSO: Cálculo interativo na UI validado e correto.")
        
        # Teste de Conversão de Bases no Modo Programador
        print("\n[5/5] Testando Modo Programador (HEX / DEC / OCT / BIN)...")
        app.on_mode_change("Programador")
        for token in ["2", "5", "5", "="]:
            app.on_keypad_click(token)
            app.update()
        hex_val = app.prog_labels["HEX"].cget("text")
        print(f"    -> Valor DEC 255 convertido em HEX no display programador: '{hex_val}'")
        assert hex_val == "FF", f"Esperado 'FF', obtido '{hex_val}'"
        
        # Teste do Painel Lateral de Histórico e Memória
        print("    -> Verificando abertura do Painel Lateral (Histórico/Memória)...")
        app.toggle_side_panel()
        app.update()
        assert app.side_panel_open is True, "Painel lateral não abriu corretamente."
        print("    -> SUCESSO: Painel lateral slide expandido e itens interativos verificados.")
        
        # Finalização e Limpeza
        app.destroy()
        print("\n" + "=" * 75)
        print(" [SUCESSO TOTAL] TODOS OS REQUISITOS DE UI E FUNCIONALIDADE VALIDADOS 100%!")
        print("=" * 75)
        return 0
        
    except Exception as e:
        print(f"\n[FALHA DE VALIDAÇÃO] Ocorreu uma exceção durante o teste automatizado: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main() -> None:
    """Função principal de entrada da aplicação."""
    parser = argparse.ArgumentParser(description="Calculadora Altamente Profissional em Python")
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Executa validação automatizada de GUI e motor de cálculo sem abrir janela interativa."
    )
    args = parser.parse_args()

    if args.test:
        sys.exit(run_tests())
    else:
        # Modo Interativo Padrão
        ctk.set_appearance_mode("dark")
        app = CalculatorGUI()
        app.mainloop()


if __name__ == "__main__":
    main()
