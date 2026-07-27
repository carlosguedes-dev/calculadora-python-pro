"""
Módulo GUI - Interface Visual Moderna com CustomTkinter
Calculadora Altamente Profissional em Python

Este módulo implementa a interface gráfica da aplicação, integrando:
- Motor Matemático (`math_engine.py`) para cálculos de alta precisão e segurança.
- Design System e Temas (`theme_config.py`) para estética premium (Obsidian Dark, Cyber Neon, Sleek Light).
- Três modos de operação: Padrão, Científica e Programador (com displays simultâneos HEX/DEC/OCT/BIN clicáveis).
- Painel lateral retrátil com abas de Histórico interativo (clicar reobtem o valor) e Memória completa.
- Suporte integral a atalhos de teclado, incluindo Numpad, Backspace, Escape, Enter e Ctrl+C/Ctrl+V via pyperclip.
"""

import os
import sys
import customtkinter as ctk
import tkinter as tk
import pyperclip
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from theme_config import (
    get_theme, list_themes, get_button_style, get_display_style,
    get_frame_style, get_font_tuple, LAYOUT_CONFIG, FONTS, DEFAULT_THEME, Theme
)
from math_engine import MathEngine


class CalculatorGUI(ctk.CTk):
    """
    Janela Principal da Calculadora Profissional.
    Gerencia layout, temas, eventos de mouse e teclado, integração com motor matemático
    e painéis dinâmicos.
    """

    def __init__(self, start_mode: str = "Padrão", start_theme: str = DEFAULT_THEME):
        super().__init__()

        # =====================================================================
        # 1. INICIALIZAÇÃO DE ESTADO E MOTOR MATEMÁTICO
        # =====================================================================
        self.current_theme_name: str = start_theme
        self.theme: Theme = get_theme(self.current_theme_name)
        
        # Mapeamento entre nomes na UI (Português) e modos no MathEngine
        self.mode_map = {
            "Padrão": "STANDARD",
            "Científica": "SCIENTIFIC",
            "Programador": "PROGRAMMER"
        }
        self.rev_mode_map = {v: k for k, v in self.mode_map.items()}
        
        self.current_mode_label: str = start_mode if start_mode in self.mode_map else "Padrão"
        self.math_engine = MathEngine(
            mode=self.mode_map[self.current_mode_label],
            angle_unit="DEG"
        )
        
        # Variáveis de Estado da Interface e Cálculo
        self.current_input: str = "0"
        self.expression_in_progress: str = ""
        self.reset_input_on_next_digit: bool = False
        self.programmer_base: str = "DEC"  # "DEC", "HEX", "OCT", "BIN"
        self.side_panel_open: bool = False
        self.copy_timer_id: Optional[str] = None
        
        # Armazenamento de referências para botões do teclado (para habilitar/desabilitar dinamicamente)
        self.keypad_buttons: Dict[str, ctk.CTkButton] = {}
        
        # =====================================================================
        # 2. CONFIGURAÇÃO DA JANELA PRINCIPAL
        # =====================================================================
        self.title("Calculadora Pro - Modern CustomTkinter")
        self._setup_window_geometry()
        
        # Configuração do Grid Principal da Janela
        self.grid_columnconfigure(0, weight=1)  # Coluna da Calculadora
        self.grid_columnconfigure(1, weight=0)  # Coluna do Painel Lateral (inicia retrátil)
        self.grid_rowconfigure(0, weight=1)
        
        # =====================================================================
        # 3. CONSTRUÇÃO DA INTERFACE (CONTAINERS PRINCIPAIS)
        # =====================================================================
        self._build_main_container()
        self._build_side_panel()
        
        # Aplicação Inicial do Tema e Construtor do Teclado
        self.apply_theme(self.current_theme_name)
        
        # Suporte Completo a Teclado (Bindings)
        self._setup_keyboard_bindings()

    def _setup_window_geometry(self) -> None:
        """Configura as dimensões da janela e limites mínimos/máximos."""
        self.width_closed = 460
        self.width_open = 780
        self.height_default = 720
        
        self.geometry(f"{self.width_closed}x{self.height_default}")
        self.minsize(400, 600)
        self.resizable(True, True)

    # =====================================================================
    # 4. CONSTRUÇÃO DOS COMPONENTES VISUAIS (HEADER, DISPLAY, KEYPAD)
    # =====================================================================
    def _build_main_container(self) -> None:
        """Constrói o container esquerdo onde ficam o cabeçalho, visor e teclado."""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=LAYOUT_CONFIG.window_padx, pady=LAYOUT_CONFIG.window_pady)
        
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)  # Header
        self.main_frame.grid_rowconfigure(1, weight=0)  # Display Principal
        self.main_frame.grid_rowconfigure(2, weight=0)  # Displays Programador (Dinâmico)
        self.main_frame.grid_rowconfigure(3, weight=0)  # Barra de Memória / Status
        self.main_frame.grid_rowconfigure(4, weight=1)  # Teclado Numérico/Científico
        
        # 4.1. Header Bar (Seletor de Modo, Tema e Botão Painel)
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=40)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)
        self.header_frame.grid_columnconfigure(2, weight=0)
        
        # Seletor de Modo (Segmented Button)
        self.mode_selector = ctk.CTkSegmentedButton(
            self.header_frame,
            values=["Padrão", "Científica", "Programador"],
            command=self.on_mode_change,
            font=get_font_tuple("tab", theme_name=self.current_theme_name),
            corner_radius=LAYOUT_CONFIG.tab_corner_radius
        )
        self.mode_selector.set(self.current_mode_label)
        self.mode_selector.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Seletor de Tema (OptionMenu)
        self.theme_selector = ctk.CTkOptionMenu(
            self.header_frame,
            values=list_themes(),
            command=self.on_theme_change,
            font=get_font_tuple("status", theme_name=self.current_theme_name),
            width=135,
            corner_radius=LAYOUT_CONFIG.tab_corner_radius
        )
        self.theme_selector.set(self.current_theme_name)
        self.theme_selector.grid(row=0, column=1, sticky="e", padx=(0, 8))
        
        # Botão Painel Lateral
        self.btn_panel = ctk.CTkButton(
            self.header_frame,
            text="🕒 Histórico",
            width=105,
            command=self.toggle_side_panel,
            font=get_font_tuple("status", theme_name=self.current_theme_name),
            corner_radius=LAYOUT_CONFIG.tab_corner_radius
        )
        self.btn_panel.grid(row=0, column=2, sticky="e")
        
        # 4.2. Visor de Cálculo Principal (Dual-Line Display)
        self.display_frame = ctk.CTkFrame(self.main_frame)
        self.display_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(1, weight=0)
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(1, weight=2)
        
        # Linha Superior (Equação Anterior / Em Andamento)
        self.lbl_history = ctk.CTkLabel(
            self.display_frame,
            text="",
            anchor="e",
            justify="right"
        )
        self.lbl_history.grid(row=0, column=0, columnspan=2, sticky="ew", padx=LAYOUT_CONFIG.display_padx, pady=(10, 0))
        
        # Linha Inferior (Entrada / Resultado)
        self.lbl_result = ctk.CTkLabel(
            self.display_frame,
            text="0",
            anchor="e",
            justify="right"
        )
        self.lbl_result.grid(row=1, column=0, sticky="ew", padx=(LAYOUT_CONFIG.display_padx, 5), pady=(0, 10))
        
        # Botão Copiar no Display
        self.btn_copy = ctk.CTkButton(
            self.display_frame,
            text="📋 Copiar",
            width=80,
            height=32,
            command=self.on_copy_click,
            corner_radius=8
        )
        self.btn_copy.grid(row=1, column=1, sticky="e", padx=(0, 12), pady=(0, 10))
        
        # 4.3. Displays de Base para Modo Programador (HEX, DEC, OCT, BIN)
        self.prog_display_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        # Não damos grid ainda, só será mapeado no Modo Programador
        self.prog_display_frame.grid_columnconfigure(0, weight=0)
        self.prog_display_frame.grid_columnconfigure(1, weight=1)
        
        self.prog_labels: Dict[str, ctk.CTkLabel] = {}
        self.prog_rows: Dict[str, ctk.CTkFrame] = {}
        
        for idx, base in enumerate(["HEX", "DEC", "OCT", "BIN"]):
            row_frame = ctk.CTkFrame(self.prog_display_frame, height=32, corner_radius=8, cursor="hand2")
            row_frame.grid(row=idx, column=0, columnspan=2, sticky="ew", pady=2)
            row_frame.grid_columnconfigure(1, weight=1)
            
            lbl_base = ctk.CTkLabel(row_frame, text=base, width=45, anchor="w", font=get_font_tuple("status"))
            lbl_base.grid(row=0, column=0, padx=(10, 5), pady=4)
            
            lbl_val = ctk.CTkLabel(row_frame, text="0", anchor="e", font=get_font_tuple("btn_sci"))
            lbl_val.grid(row=0, column=1, padx=(5, 10), pady=4, sticky="ew")
            
            self.prog_labels[base] = lbl_val
            self.prog_rows[base] = row_frame
            
            # Binding para clique (selecionar base)
            row_frame.bind("<Button-1>", lambda e, b=base: self.on_programmer_base_select(b))
            lbl_base.bind("<Button-1>", lambda e, b=base: self.on_programmer_base_select(b))
            lbl_val.bind("<Button-1>", lambda e, b=base: self.on_programmer_base_select(b))
            
        # 4.4. Barra de Memória e Status (MC, MR, M+, M-, MS, DEG/RAD)
        self.memory_bar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=38)
        self.memory_bar_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        for i in range(6):
            self.memory_bar_frame.grid_columnconfigure(i, weight=1)
            
        mem_ops = [("MC", self.on_mc), ("MR", self.on_mr), ("M+", self.on_m_plus), ("M-", self.on_m_minus), ("MS", self.on_ms)]
        self.mem_buttons: List[ctk.CTkButton] = []
        for idx, (txt, cmd) in enumerate(mem_ops):
            btn = ctk.CTkButton(self.memory_bar_frame, text=txt, command=cmd, height=32)
            btn.grid(row=0, column=idx, sticky="ew", padx=2)
            self.mem_buttons.append(btn)
            
        # Botão DEG/RAD (Apenas Modo Científico)
        self.btn_angle_unit = ctk.CTkButton(
            self.memory_bar_frame,
            text="DEG",
            command=self.toggle_angle_unit,
            height=32
        )
        self.btn_angle_unit.grid(row=0, column=5, sticky="ew", padx=2)
        
        # 4.5. Teclado Principal (Container dinâmico)
        self.keypad_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.keypad_frame.grid(row=4, column=0, sticky="nsew")

    def _build_side_panel(self) -> None:
        """Constrói o painel lateral com abas para Histórico e Memória."""
        self.side_panel_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0, width=310)
        # O painel inicia não mapeado (aberto com toggle_side_panel)
        self.side_panel_frame.grid_columnconfigure(0, weight=1)
        self.side_panel_frame.grid_rowconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self.side_panel_frame, corner_radius=LAYOUT_CONFIG.card_corner_radius)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.tabview.add("Histórico")
        self.tabview.add("Memória")
        
        # --- Aba Histórico ---
        self.tabview.tab("Histórico").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Histórico").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Histórico").grid_rowconfigure(1, weight=0)
        
        self.history_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Histórico"), fg_color="transparent")
        self.history_scroll.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.history_scroll.grid_columnconfigure(0, weight=1)
        
        self.btn_clear_history = ctk.CTkButton(
            self.tabview.tab("Histórico"),
            text="🗑️ Limpar Histórico",
            command=self.on_clear_history
        )
        self.btn_clear_history.grid(row=1, column=0, sticky="ew", pady=5)
        
        # --- Aba Memória ---
        self.tabview.tab("Memória").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Memória").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Memória").grid_rowconfigure(1, weight=0)
        
        self.memory_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Memória"), fg_color="transparent")
        self.memory_scroll.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.memory_scroll.grid_columnconfigure(0, weight=1)
        
        self.btn_clear_memory_panel = ctk.CTkButton(
            self.tabview.tab("Memória"),
            text="🗑️ Limpar Memória (MC)",
            command=self.on_mc
        )
        self.btn_clear_memory_panel.grid(row=1, column=0, sticky="ew", pady=5)

    # =====================================================================
    # 5. GERENCIAMENTO DE TEMAS E ESTILOS
    # =====================================================================
    def apply_theme(self, theme_name: str) -> None:
        """Aplica dinamicamente o tema visual selecionado em todos os widgets da aplicação."""
        self.current_theme_name = theme_name
        self.theme = get_theme(theme_name)
        colors = self.theme.colors
        layout = self.theme.layout
        
        # 5.1. Fundo da Janela e Main Frame
        self.configure(fg_color=colors.bg_primary)
        self.main_frame.configure(fg_color=colors.bg_primary)
        self.side_panel_frame.configure(fg_color=colors.bg_secondary)
        
        # 5.2. Estilo do Visor Principal
        disp_style = get_display_style(theme_name)
        self.display_frame.configure(
            fg_color=disp_style["fg_color"],
            border_color=disp_style["border_color"],
            border_width=disp_style["border_width"],
            corner_radius=disp_style["corner_radius"]
        )
        self.lbl_history.configure(text_color=colors.text_secondary, font=disp_style["font_history"])
        self.lbl_result.configure(text_color=colors.text_primary, font=disp_style["font_main"])
        
        # Estilo do Botão Copiar
        btn_copy_style = get_button_style(theme_name, "sci", custom_width=80, custom_height=32)
        self.btn_copy.configure(**btn_copy_style)
        
        # 5.3. Estilo dos Controles de Header e Memória
        tab_style = get_button_style(theme_name, "sci")
        self.mode_selector.configure(
            fg_color=colors.bg_tertiary,
            selected_color=colors.accent_primary,
            selected_hover_color=colors.btn_op_hover,
            unselected_color=colors.bg_secondary,
            unselected_hover_color=colors.btn_num_hover,
            text_color=colors.text_primary,
            font=get_font_tuple("tab", theme_name=theme_name)
        )
        
        self.theme_selector.configure(
            fg_color=colors.bg_secondary,
            button_color=colors.bg_tertiary,
            button_hover_color=colors.btn_num_hover,
            text_color=colors.text_primary,
            dropdown_fg_color=colors.bg_secondary,
            dropdown_hover_color=colors.accent_primary,
            dropdown_text_color=colors.text_primary,
            font=get_font_tuple("status", theme_name=theme_name)
        )
        
        btn_panel_style = get_button_style(theme_name, "sci", custom_width=105, custom_height=32)
        self.btn_panel.configure(**btn_panel_style)
        
        # Botões da Barra de Memória e DEG/RAD
        mem_btn_style = get_button_style(theme_name, "memory", custom_height=32)
        for btn in self.mem_buttons:
            btn.configure(**mem_btn_style)
        self.btn_angle_unit.configure(**mem_btn_style)
        
        # 5.4. Estilo do Tabview (Painel Lateral)
        self.tabview.configure(
            fg_color=colors.bg_tertiary,
            segmented_button_fg_color=colors.bg_secondary,
            segmented_button_selected_color=colors.accent_primary,
            segmented_button_selected_hover_color=colors.btn_op_hover,
            segmented_button_unselected_color=colors.bg_secondary,
            segmented_button_unselected_hover_color=colors.btn_num_hover,
            text_color=colors.text_primary
        )
        self.btn_clear_history.configure(**get_button_style(theme_name, "clear", custom_height=36))
        self.btn_clear_memory_panel.configure(**get_button_style(theme_name, "clear", custom_height=36))
        
        # 5.5. Atualiza Displays do Programador (Se aplicável)
        self._update_programmer_displays_style()
        
        # 5.6. Reconstrói o Teclado com as Novas Cores
        self.build_keypad()
        
        # 5.7. Atualiza Listas de Histórico e Memória
        self.refresh_side_panel()

    def _update_programmer_displays_style(self) -> None:
        """Atualiza cores e destaques das linhas do display do programador."""
        colors = self.theme.colors
        for base, row_frame in self.prog_rows.items():
            is_selected = (base == self.programmer_base)
            fg = colors.bg_tertiary if is_selected else colors.bg_display
            border = colors.accent_primary if is_selected else colors.border_color
            bw = 2 if is_selected else 1
            row_frame.configure(fg_color=fg, border_color=border, border_width=bw)
            
            lbl_val = self.prog_labels[base]
            tc = colors.accent_primary if is_selected else colors.text_secondary
            lbl_val.configure(text_color=tc)

    # =====================================================================
    # 6. CONSTRUTOR DE TECLADO RESPONSIVO (KEYPAD BUILDER)
    # =====================================================================
    def build_keypad(self) -> None:
        """Limpa e reconstrói a grade de botões do teclado conforme o modo e tema atuais."""
        for widget in self.keypad_frame.winfo_children():
            widget.destroy()
        self.keypad_buttons.clear()
        
        layout_def = self._get_keypad_layout(self.current_mode_label)
        rows = len(layout_def)
        cols = max(len(r) for r in layout_def) if rows > 0 else 4
        
        # Configuração responsiva de peso para linhas e colunas
        for c in range(cols):
            self.keypad_frame.grid_columnconfigure(c, weight=1)
        for r in range(rows):
            self.keypad_frame.grid_rowconfigure(r, weight=1)
            
        # Instanciação dos botões
        for r_idx, row in enumerate(layout_def):
            for c_idx, btn_def in enumerate(row):
                if not btn_def:
                    continue
                    
                text = btn_def.get("text", "")
                btype = btn_def.get("type", "num")
                colspan = btn_def.get("colspan", 1)
                
                style = get_button_style(self.current_theme_name, button_type=btype)
                # Removemos width e height fixos para deixar o grid (sticky="nsew") gerenciar o tamanho
                style.pop("width", None)
                style.pop("height", None)
                
                btn = ctk.CTkButton(
                    self.keypad_frame,
                    text=text,
                    command=lambda t=text: self.on_keypad_click(t),
                    **style
                )
                btn.grid(
                    row=r_idx, 
                    column=c_idx, 
                    columnspan=colspan, 
                    sticky="nsew", 
                    padx=LAYOUT_CONFIG.grid_padx, 
                    pady=LAYOUT_CONFIG.grid_pady
                )
                self.keypad_buttons[text] = btn
                
        # Atualiza visibilidade dos displays programador e botões habilitados/desabilitados
        if self.current_mode_label == "Programador":
            self.prog_display_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
            self.btn_angle_unit.grid_remove()
            self._update_programmer_button_states()
        else:
            self.prog_display_frame.grid_remove()
            if self.current_mode_label == "Científica":
                self.btn_angle_unit.grid()
            else:
                self.btn_angle_unit.grid_remove()

    def _get_keypad_layout(self, mode: str) -> List[List[Dict[str, Any]]]:
        """Retorna a matriz de definição dos botões para o modo especificado."""
        if mode == "Padrão":
            return [
                [{"text": "%", "type": "sci"}, {"text": "CE", "type": "clear"}, {"text": "C", "type": "clear"}, {"text": "⌫", "type": "clear"}],
                [{"text": "1/x", "type": "sci"}, {"text": "x²", "type": "sci"}, {"text": "√x", "type": "sci"}, {"text": "÷", "type": "op"}],
                [{"text": "7", "type": "num"}, {"text": "8", "type": "num"}, {"text": "9", "type": "num"}, {"text": "×", "type": "op"}],
                [{"text": "4", "type": "num"}, {"text": "5", "type": "num"}, {"text": "6", "type": "num"}, {"text": "–", "type": "op"}],
                [{"text": "1", "type": "num"}, {"text": "2", "type": "num"}, {"text": "3", "type": "num"}, {"text": "+", "type": "op"}],
                [{"text": "±", "type": "num"}, {"text": "0", "type": "num"}, {"text": ".", "type": "num"}, {"text": "=", "type": "eq"}]
            ]
        elif mode == "Científica":
            return [
                [{"text": "sin", "type": "sci"}, {"text": "cos", "type": "sci"}, {"text": "tan", "type": "sci"}, {"text": "CE", "type": "clear"}, {"text": "C", "type": "clear"}],
                [{"text": "x!", "type": "sci"}, {"text": "ln", "type": "sci"}, {"text": "log", "type": "sci"}, {"text": "(", "type": "sci"}, {"text": ")", "type": "sci"}],
                [{"text": "√x", "type": "sci"}, {"text": "x²", "type": "sci"}, {"text": "x^y", "type": "sci"}, {"text": "π", "type": "sci"}, {"text": "⌫", "type": "clear"}],
                [{"text": "1/x", "type": "sci"}, {"text": "7", "type": "num"}, {"text": "8", "type": "num"}, {"text": "9", "type": "num"}, {"text": "÷", "type": "op"}],
                [{"text": "e", "type": "sci"}, {"text": "4", "type": "num"}, {"text": "5", "type": "num"}, {"text": "6", "type": "num"}, {"text": "×", "type": "op"}],
                [{"text": "±", "type": "num"}, {"text": "1", "type": "num"}, {"text": "2", "type": "num"}, {"text": "3", "type": "num"}, {"text": "–", "type": "op"}],
                [{"text": "%", "type": "sci"}, {"text": "0", "type": "num"}, {"text": ".", "type": "num"}, {"text": "=", "type": "eq"}, {"text": "+", "type": "op"}]
            ]
        elif mode == "Programador":
            return [
                [{"text": "AND", "type": "sci"}, {"text": "OR", "type": "sci"}, {"text": "XOR", "type": "sci"}, {"text": "NOT", "type": "sci"}, {"text": "(", "type": "sci"}, {"text": ")", "type": "sci"}],
                [{"text": "<<", "type": "sci"}, {"text": ">>", "type": "sci"}, {"text": "MOD", "type": "sci"}, {"text": "CE", "type": "clear"}, {"text": "AC", "type": "clear"}, {"text": "⌫", "type": "clear"}],
                [{"text": "A", "type": "num"}, {"text": "B", "type": "num"}, {"text": "7", "type": "num"}, {"text": "8", "type": "num"}, {"text": "9", "type": "num"}, {"text": "÷", "type": "op"}],
                [{"text": "C", "type": "num"}, {"text": "D", "type": "num"}, {"text": "4", "type": "num"}, {"text": "5", "type": "num"}, {"text": "6", "type": "num"}, {"text": "×", "type": "op"}],
                [{"text": "E", "type": "num"}, {"text": "F", "type": "num"}, {"text": "1", "type": "num"}, {"text": "2", "type": "num"}, {"text": "3", "type": "num"}, {"text": "–", "type": "op"}],
                [{"text": "±", "type": "num"}, {"text": "0", "type": "num"}, {"text": ".", "type": "num"}, {"text": "=", "type": "eq", "colspan": 2}, {"text": "+", "type": "op"}]
            ]
        return []

    def _update_programmer_button_states(self) -> None:
        """Habilita ou desabilita botões numéricos (0-9, A-F) dependendo da base ativa."""
        if self.current_mode_label != "Programador":
            return
            
        base = self.programmer_base
        allowed = {
            "BIN": set("01"),
            "OCT": set("01234567"),
            "DEC": set("0123456789"),
            "HEX": set("0123456789ABCDEF")
        }[base]
        
        all_digits = set("0123456789ABCDEF")
        colors = self.theme.colors
        
        for text, btn in self.keypad_buttons.items():
            if text in all_digits and len(text) == 1:
                if text in allowed:
                    btn.configure(state="normal", fg_color=colors.btn_num_bg, text_color=colors.btn_num_text)
                else:
                    btn.configure(state="disabled", fg_color=colors.bg_tertiary, text_color=colors.text_muted)

    # =====================================================================
    # 7. MANIPULADORES DE EVENTOS DE BOTÕES E AÇÕES DO USUÁRIO
    # =====================================================================
    def on_mode_change(self, new_mode: str) -> None:
        """Manipulador de troca de modo (Padrão, Científica, Programador)."""
        if new_mode == self.current_mode_label:
            return
        self.current_mode_label = new_mode
        self.math_engine.set_mode(self.mode_map[new_mode])
        
        # Limpa o estado da operação ao trocar de modo para evitar incompatibilidade
        self.current_input = "0"
        self.expression_in_progress = ""
        self.reset_input_on_next_digit = False
        
        self.build_keypad()
        self._update_display_labels()
        self.update_programmer_displays()
        self.refresh_side_panel()

    def on_theme_change(self, new_theme: str) -> None:
        """Manipulador de troca de tema visual."""
        self.apply_theme(new_theme)

    def toggle_angle_unit(self) -> None:
        """Alterna entre Graus (DEG) e Radianos (RAD)."""
        new_unit = "RAD" if self.math_engine.angle_unit == "DEG" else "DEG"
        self.math_engine.set_angle_unit(new_unit)
        self.btn_angle_unit.configure(text=new_unit)
        self._update_display_labels()

    def on_programmer_base_select(self, base: str) -> None:
        """Altera a base de numeração ativa no Modo Programador."""
        if self.current_mode_label != "Programador" or base == self.programmer_base:
            return
            
        # Converte o input atual para a nova base selecionada
        conversions = self.math_engine.get_base_conversions(self.current_input, from_base=self.programmer_base)
        self.programmer_base = base
        self.current_input = conversions.get(base, "0")
        self.reset_input_on_next_digit = True
        
        self._update_programmer_displays_style()
        self._update_programmer_button_states()
        self._update_display_labels()

    def toggle_side_panel(self) -> None:
        """Abre ou fecha o painel lateral com animação/slide de largura."""
        if self.side_panel_open:
            # Fechar painel
            self.side_panel_frame.grid_forget()
            self.geometry(f"{self.width_closed}x{self.winfo_height()}")
            self.btn_panel.configure(text="🕒 Histórico")
            self.side_panel_open = False
        else:
            # Abrir painel
            self.geometry(f"{self.width_open}x{self.winfo_height()}")
            self.side_panel_frame.grid(row=0, column=1, sticky="nsew", pady=LAYOUT_CONFIG.window_pady, padx=(0, LAYOUT_CONFIG.window_padx))
            self.btn_panel.configure(text="✕ Fechar")
            self.side_panel_open = True
            self.refresh_side_panel()

    def on_copy_click(self) -> None:
        """Copia o valor do visor para a área de transferência com feedback visual."""
        try:
            pyperclip.copy(self.current_input)
            self.btn_copy.configure(
                text="✓ Copiado!",
                fg_color=self.theme.colors.accent_primary,
                text_color="#FFFFFF"
            )
            if self.copy_timer_id:
                self.after_cancel(self.copy_timer_id)
            self.copy_timer_id = self.after(1500, self._reset_copy_btn)
        except Exception as e:
            self.lbl_history.configure(text="Erro ao copiar para o clipboard")

    def _reset_copy_btn(self) -> None:
        """Restaura o estado normal do botão copiar após o feedback."""
        btn_copy_style = get_button_style(self.current_theme_name, "sci", custom_width=80, custom_height=32)
        self.btn_copy.configure(text="📋 Copiar", **btn_copy_style)
        self.copy_timer_id = None

    # =====================================================================
    # 8. LÓGICA DE CLIQUE NO TECLADO E CÁLCULO
    # =====================================================================
    def on_keypad_click(self, token: str) -> None:
        """Centraliza o processamento de todos os botões clicados no teclado."""
        # 8.1. Botões de Limpeza (Clear / Backspace)
        if token in ("C", "AC", "CE", "⌫"):
            self._handle_clear_action(token)
        # 8.2. Igual / Resultado
        elif token == "=":
            self._handle_equals_action()
        # 8.3. Operadores Binários
        elif token in ("+", "–", "×", "÷", "x^y", "MOD", "AND", "OR", "XOR", "<<", ">>"):
            self._handle_operator_action(token)
        # 8.4. Funções Científicas e Unárias Instantâneas
        elif token in ("1/x", "x²", "√x", "±", "%", "x!", "sin", "cos", "tan", "ln", "log", "e", "π", "NOT"):
            self._handle_unary_function(token)
        # 8.5. Parênteses
        elif token in ("(", ")"):
            self._handle_parenthesis(token)
        # 8.6. Dígitos Numéricos e Ponto Decimal
        else:
            self._handle_digit_input(token)
            
        self._update_display_labels()
        self.update_programmer_displays()

    def _handle_clear_action(self, token: str) -> None:
        if token == "CE":
            self.current_input = "0"
        elif token in ("C", "AC"):
            self.current_input = "0"
            self.expression_in_progress = ""
            self.reset_input_on_next_digit = False
        elif token == "⌫":
            if self.reset_input_on_next_digit or len(self.current_input) <= 1 or self.current_input == "0" or self.current_input.startswith("Erro:"):
                self.current_input = "0"
            else:
                self.current_input = self.current_input[:-1]
                if self.current_input == "-" or self.current_input == "":
                    self.current_input = "0"

    def _handle_equals_action(self) -> None:
        if not self.expression_in_progress and not self.reset_input_on_next_digit:
            # Nada para calcular
            return
            
        full_expr = f"{self.expression_in_progress} {self.current_input}".strip()
        
        # No modo programador, avaliamos considerando a base atual
        if self.current_mode_label == "Programador" and self.programmer_base != "DEC":
            # Converte a expressão inteira ou avalia valor convertido
            res_str = self._evaluate_programmer_expression(full_expr)
        else:
            res_str = self.math_engine.evaluate(full_expr, add_to_history=True)
            
        self.lbl_history.configure(text=f"{full_expr} =")
        self.current_input = res_str
        self.expression_in_progress = ""
        self.reset_input_on_next_digit = True
        self.refresh_side_panel()

    def _evaluate_programmer_expression(self, expr_str: str) -> str:
        """Auxiliar para avaliar expressões com tokens Hex/Oct/Bin no Modo Programador."""
        # Se for um cálculo direto entre bases, convertemos tudo temporariamente para DEC
        try:
            # Tenta avaliar no MathEngine (que já tem suporte a sintaxe bitwise)
            res = self.math_engine.evaluate(expr_str, add_to_history=True)
            if not res.startswith("Erro:") and self.programmer_base != "DEC":
                convs = self.math_engine.get_base_conversions(res, from_base="DEC")
                return convs.get(self.programmer_base, res)
            return res
        except Exception:
            return "Erro: Expressão malformada"

    def _handle_operator_action(self, token: str) -> None:
        op_map = {"–": "-", "×": "*", "÷": "/", "x^y": "^"}
        py_op = op_map.get(token, token)
        
        if self.reset_input_on_next_digit and self.expression_in_progress:
            # Substitui o último operador se o usuário mudou de ideia
            parts = self.expression_in_progress.rstrip().split()
            if parts and parts[-1] in ("+", "-", "*", "/", "^", "%", "AND", "OR", "XOR", "<<", ">>", "MOD"):
                parts[-1] = py_op
                self.expression_in_progress = " ".join(parts) + " "
                self.lbl_history.configure(text=self.expression_in_progress)
                return
                
        if self.expression_in_progress and not self.reset_input_on_next_digit:
            # Avalia cálculo intermediário em cadeia (ex: 12 + 5 -> 17 + )
            full_expr = f"{self.expression_in_progress} {self.current_input}".strip()
            inter_res = self.math_engine.evaluate(full_expr, add_to_history=False)
            if not inter_res.startswith("Erro:"):
                self.current_input = inter_res
                
        self.expression_in_progress = f"{self.current_input} {py_op} "
        self.reset_input_on_next_digit = True

    def _handle_unary_function(self, token: str) -> None:
        if token == "±":
            self.current_input = self.math_engine.toggle_sign(self.current_input)
        elif token == "1/x":
            self.current_input = self.math_engine.calculate_reciprocal(self.current_input)
            self.reset_input_on_next_digit = True
        elif token == "x²":
            self.current_input = self.math_engine.calculate_square(self.current_input)
            self.reset_input_on_next_digit = True
        elif token == "√x":
            self.current_input = self.math_engine.calculate_sqrt(self.current_input)
            self.reset_input_on_next_digit = True
        elif token == "x!":
            self.current_input = self.math_engine.calculate_factorial(self.current_input)
            self.reset_input_on_next_digit = True
        elif token == "%":
            # Aplica porcentagem em relação à expressão em andamento
            if self.expression_in_progress:
                parts = self.expression_in_progress.rstrip().split()
                if len(parts) >= 2:
                    base_val = parts[-2]
                    op_val = parts[-1]
                    self.current_input = self.math_engine.calculate_percentage(base_val, self.current_input, op_val)
                else:
                    self.current_input = self.math_engine.calculate_percentage(self.current_input)
            else:
                self.current_input = self.math_engine.calculate_percentage(self.current_input)
            self.reset_input_on_next_digit = True
        elif token in ("sin", "cos", "tan", "ln", "log"):
            res = self.math_engine.evaluate(f"{token}({self.current_input})", add_to_history=True)
            self.lbl_history.configure(text=f"{token}({self.current_input}) =")
            self.current_input = res
            self.reset_input_on_next_digit = True
        elif token in ("π", "e"):
            res = self.math_engine.evaluate(token, add_to_history=False)
            self.current_input = res
            self.reset_input_on_next_digit = True
        elif token == "NOT":
            res = self.math_engine.evaluate(f"~({self.current_input})", add_to_history=True)
            self.lbl_history.configure(text=f"NOT({self.current_input}) =")
            self.current_input = res
            self.reset_input_on_next_digit = True
            
        self.refresh_side_panel()

    def _handle_parenthesis(self, token: str) -> None:
        if token == "(":
            if self.reset_input_on_next_digit or self.current_input == "0":
                self.expression_in_progress += "( "
            else:
                self.expression_in_progress += f"{self.current_input} * ( "
            self.current_input = "0"
            self.reset_input_on_next_digit = False
        elif token == ")":
            if self.expression_in_progress:
                self.expression_in_progress += f"{self.current_input} ) "
                self.reset_input_on_next_digit = True

    def _handle_digit_input(self, token: str) -> None:
        if self.current_mode_label == "Programador":
            # Valida se o dígito é aceito na base atual
            allowed = {
                "BIN": set("01"),
                "OCT": set("01234567"),
                "DEC": set("0123456789."),
                "HEX": set("0123456789ABCDEF.")
            }[self.programmer_base]
            if token not in allowed:
                return

        if token == ".":
            if self.reset_input_on_next_digit:
                self.current_input = "0."
                self.reset_input_on_next_digit = False
            elif "." not in self.current_input:
                self.current_input += "."
            return

        if self.reset_input_on_next_digit or self.current_input == "0" or self.current_input.startswith("Erro:"):
            self.current_input = token
            self.reset_input_on_next_digit = False
        else:
            # Limita tamanho de dígitos para evitar overflow visual
            if len(self.current_input.replace(".", "").replace("-", "")) < 24:
                self.current_input += token

    # =====================================================================
    # 9. ATUALIZAÇÃO VISUAL DE DISPLAYS E BASE PROGRAMADOR
    # =====================================================================
    def _update_display_labels(self) -> None:
        """Atualiza os rótulos de texto do visor e ajusta o tamanho da fonte se necessário."""
        self.lbl_history.configure(text=self.expression_in_progress)
        
        # Ajuste dinâmico do tamanho da fonte principal (Auto-Shrink para números longos)
        val_str = self.current_input
        base_font = get_font_tuple("display_main", theme_name=self.current_theme_name)
        
        if len(val_str) > 16:
            adj_size = max(24, int(base_font[1] * (16 / len(val_str))))
            new_font = (base_font[0], adj_size, base_font[2])
            self.lbl_result.configure(font=new_font, text=val_str)
        elif len(val_str) > 11:
            adj_size = max(32, int(base_font[1] * (11 / len(val_str))))
            new_font = (base_font[0], adj_size, base_font[2])
            self.lbl_result.configure(font=new_font, text=val_str)
        else:
            self.lbl_result.configure(font=base_font, text=val_str)

    def update_programmer_displays(self) -> None:
        """Atualiza em tempo real as conversões nas 4 bases do Modo Programador."""
        if self.current_mode_label != "Programador":
            return
            
        conversions = self.math_engine.get_base_conversions(
            self.current_input, 
            from_base=self.programmer_base
        )
        for base, val_str in conversions.items():
            if base in self.prog_labels:
                self.prog_labels[base].configure(text=val_str)

    # =====================================================================
    # 10. MANIPULAÇÃO DA MEMÓRIA (MC, MR, M+, M-, MS)
    # =====================================================================
    def on_mc(self) -> None:
        self.math_engine.memory_clear()
        self.refresh_side_panel()

    def on_mr(self) -> None:
        val = self.math_engine.memory_recall()
        self.current_input = val
        self.reset_input_on_next_digit = True
        self._update_display_labels()
        self.update_programmer_displays()

    def on_m_plus(self) -> None:
        self.math_engine.memory_add(self.current_input)
        self.refresh_side_panel()

    def on_m_minus(self) -> None:
        self.math_engine.memory_subtract(self.current_input)
        self.refresh_side_panel()

    def on_ms(self) -> None:
        self.math_engine.memory_store(self.current_input)
        self.refresh_side_panel()

    # =====================================================================
    # 11. ATUALIZAÇÃO DO PAINEL LATERAL (HISTÓRICO E MEMÓRIA)
    # =====================================================================
    def refresh_side_panel(self) -> None:
        """Recarrega os cards das listas de Histórico e Memória."""
        if not self.side_panel_open:
            return
            
        colors = self.theme.colors
        
        # 11.1. Refresh Histórico
        for w in self.history_scroll.winfo_children():
            w.destroy()
            
        hist_list = self.math_engine.get_history_list()
        if not hist_list:
            lbl_empty = ctk.CTkLabel(self.history_scroll, text="Nenhum histórico recente.", text_color=colors.text_muted)
            lbl_empty.pack(pady=20)
        else:
            for item in reversed(hist_list):
                card = ctk.CTkFrame(
                    self.history_scroll, 
                    fg_color=colors.bg_display, 
                    border_color=colors.border_color, 
                    border_width=1, 
                    corner_radius=10,
                    cursor="hand2"
                )
                card.pack(fill="x", pady=4, padx=4)
                
                lbl_expr = ctk.CTkLabel(card, text=item["expression"], font=get_font_tuple("status"), text_color=colors.text_secondary, anchor="e")
                lbl_expr.pack(fill="x", padx=10, pady=(6, 0))
                
                lbl_res = ctk.CTkLabel(card, text=f"= {item['result']}", font=get_font_tuple("btn_sci"), text_color=colors.accent_primary, anchor="e")
                lbl_res.pack(fill="x", padx=10, pady=(0, 6))
                
                # Binding de clique no card para recarregar no visor
                res_val = item["result"]
                card.bind("<Button-1>", lambda e, r=res_val: self.on_history_card_click(r))
                lbl_expr.bind("<Button-1>", lambda e, r=res_val: self.on_history_card_click(r))
                lbl_res.bind("<Button-1>", lambda e, r=res_val: self.on_history_card_click(r))
                
        # 11.2. Refresh Memória
        for w in self.memory_scroll.winfo_children():
            w.destroy()
            
        mem_list = self.math_engine.get_memory_list()
        if not mem_list:
            lbl_empty = ctk.CTkLabel(self.memory_scroll, text="A memória está vazia.", text_color=colors.text_muted)
            lbl_empty.pack(pady=20)
        else:
            for item in reversed(mem_list):
                idx = int(item["index"])
                card = ctk.CTkFrame(
                    self.memory_scroll, 
                    fg_color=colors.bg_display, 
                    border_color=colors.border_color, 
                    border_width=1, 
                    corner_radius=10
                )
                card.pack(fill="x", pady=4, padx=4)
                
                lbl_val = ctk.CTkLabel(card, text=item["value"], font=get_font_tuple("btn_num", custom_size=18), text_color=colors.text_primary, anchor="e")
                lbl_val.pack(fill="x", padx=10, pady=(8, 4))
                
                btn_row = ctk.CTkFrame(card, fg_color="transparent")
                btn_row.pack(fill="x", padx=8, pady=(0, 6))
                
                btn_style = get_button_style(self.current_theme_name, "memory", custom_height=26)
                btn_style.pop("width", None)
                
                btn_mr = ctk.CTkButton(btn_row, text="MR", width=45, command=lambda i=idx: self._on_mem_card_mr(i), **btn_style)
                btn_mr.pack(side="left", padx=2, expand=True, fill="x")
                
                btn_mp = ctk.CTkButton(btn_row, text="M+", width=45, command=lambda i=idx: self._on_mem_card_add(i), **btn_style)
                btn_mp.pack(side="left", padx=2, expand=True, fill="x")
                
                btn_mm = ctk.CTkButton(btn_row, text="M-", width=45, command=lambda i=idx: self._on_mem_card_sub(i), **btn_style)
                btn_mm.pack(side="left", padx=2, expand=True, fill="x")
                
                btn_del = ctk.CTkButton(btn_row, text="✕", width=30, command=lambda i=idx: self._on_mem_card_del(i), fg_color=colors.btn_clear_bg, hover_color=colors.btn_clear_hover, text_color=colors.btn_clear_text, height=26, corner_radius=6)
                btn_del.pack(side="right", padx=2)

    def on_history_card_click(self, result_val: str) -> None:
        """Quando o usuário clica em um item do histórico, recarrega o valor no visor."""
        self.current_input = result_val
        self.reset_input_on_next_digit = True
        self._update_display_labels()
        self.update_programmer_displays()

    def on_clear_history(self) -> None:
        self.math_engine.clear_history()
        self.refresh_side_panel()

    def _on_mem_card_mr(self, index: int) -> None:
        val = self.math_engine.memory_recall(index)
        self.current_input = val
        self.reset_input_on_next_digit = True
        self._update_display_labels()
        self.update_programmer_displays()

    def _on_mem_card_add(self, index: int) -> None:
        self.math_engine.memory_add(self.current_input, index)
        self.refresh_side_panel()

    def _on_mem_card_sub(self, index: int) -> None:
        self.math_engine.memory_subtract(self.current_input, index)
        self.refresh_side_panel()

    def _on_mem_card_del(self, index: int) -> None:
        self.math_engine.memory_remove_item(index)
        self.refresh_side_panel()

    # =====================================================================
    # 12. SUPORTE COMPLETO A ATALHOS DE TECLADO (BINDINGS)
    # =====================================================================
    def _setup_keyboard_bindings(self) -> None:
        """Configura os atalhos de teclado na janela root."""
        self.bind("<Key>", self.on_key_press)
        self.bind("<Return>", lambda e: self.on_keypad_click("="))
        self.bind("<KP_Enter>", lambda e: self.on_keypad_click("="))
        self.bind("<BackSpace>", lambda e: self.on_keypad_click("⌫"))
        self.bind("<Escape>", lambda e: self.on_keypad_click("C"))
        self.bind("<Delete>", lambda e: self.on_keypad_click("CE"))

    def on_key_press(self, event: tk.Event) -> None:
        """Processa eventos globais de digitação na janela."""
        char = event.char
        keysym = event.keysym
        
        # Ignora modificadores puros
        if keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"):
            return

        # Atalhos Ctrl+C / Ctrl+V
        is_ctrl = (event.state & 0x0004) or (event.state & 0x0080)
        if is_ctrl:
            if keysym.lower() == 'c':
                self.on_copy_click()
                return
            elif keysym.lower() == 'v':
                self._handle_paste_shortcut()
                return

        # Mapeamento de teclas numéricas e operadores
        if char in "0123456789.":
            self.on_keypad_click(char)
        elif char in "+-*/^()%":
            op_map = {"*": "×", "/": "÷", "-": "–", "^": "x^y"}
            self.on_keypad_click(op_map.get(char, char))
        elif keysym in ("equal", "KP_Equal"):
            self.on_keypad_click("=")
        elif self.current_mode_label == "Programador" and char.upper() in "ABCDEF":
            self.on_keypad_click(char.upper())

    def _handle_paste_shortcut(self) -> None:
        """Processa a colagem de dados do clipboard."""
        try:
            text = pyperclip.paste().strip()
            if not text:
                return
            # Valida e processa o texto colado
            res = self.math_engine.evaluate(text, add_to_history=True)
            if not res.startswith("Erro:"):
                self.current_input = res
                self.reset_input_on_next_digit = True
                self._update_display_labels()
                self.update_programmer_displays()
                self.refresh_side_panel()
        except Exception:
            pass


if __name__ == "__main__":
    # Teste local de inicialização do GUI (modo standalone)
    ctk.set_appearance_mode("dark")
    app = CalculatorGUI()
    app.mainloop()
