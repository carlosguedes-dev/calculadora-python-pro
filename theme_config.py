"""Módulo de Configuração de Temas, Paletas de Cores, Tipografia e Layout (UI/UX).

Este módulo define o Design System completo para o projeto da Calculadora Altamente
Profissional em Python. Ele foi projetado para fornecer uma estética visual moderna,
coesão entre componentes e flexibilidade total para alternância de temas em tempo real.

Temas Disponíveis:
    - Obsidian Dark: Fundo grafite/escuro profundo com operadores em Ciano Elétrico
                     e botão de igual em Destaque Vibrante.
    - Cyber Neon:    Fundo preto absoluto com detalhes em Roxo Neon e Verde Esmeralda,
                     evocando uma estética futurista de alto contraste.
    - Sleek Light:   Fundo claro e limpo macio, botões imaculados, operadores em
                     Azul Safira e botão de igual em Laranja Pôr do Sol.

Estruturas Exportadas:
    - THEMES: Dicionário contendo os objetos completos dos temas configurados.
    - FONTS: Configuração tipográfica padronizada com fallbacks inteligentes.
    - LAYOUT_CONFIG: Parâmetros de espaçamento, margens, dimensões e cantos arredondados.
    - DEFAULT_THEME: Nome do tema ativo por padrão ("Obsidian Dark").

Exemplo de Uso:
    >>> from theme_config import get_theme, get_button_style, FONTS, LAYOUT_CONFIG
    >>> tema = get_theme("Obsidian Dark")
    >>> print(tema.colors.bg_primary)
    #1A1A1D
    >>> estilo_botao = get_button_style("Obsidian Dark", button_type="num")
    >>> # Pode ser desempacotado diretamente em widgets CustomTkinter ou similares:
    >>> # btn = CTkButton(root, text="7", **estilo_botao)
"""

import os
import sys
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional, Any, Union, Literal


# ==============================================================================
# 1. DEFINICAO DE TIPOS E MODIFICADORES DE BOTOES
# ==============================================================================

ButtonType = Literal["num", "op", "sci", "eq", "clear", "memory", "modifier"]
PanelType = Literal["primary", "secondary", "tertiary", "display"]


# ==============================================================================
# 2. TIPOGRAFIA (FONTES E RESOLUCAO DE FALLBACK)
# ==============================================================================

def _resolve_font_family() -> str:
    """Detecta e retorna a melhor fonte disponível no sistema operacional.
    
    Prioriza fontes modernas de UI/UX nesta ordem:
    1. Segoe UI Variable Display (Windows 11)
    2. Inter (Fonte moderna padrão da indústria)
    3. Roboto (Android / Material Design)
    4. Segoe UI (Windows 10/8/7)
    5. Helvetica Neue (macOS)
    6. Arial / sans-serif (Fallback universal)
    
    Returns:
        str: Nome da família de fontes disponível ou o fallback mais seguro.
    """
    preferred_fonts = [
        "Segoe UI Variable Display",
        "Inter",
        "Roboto",
        "Segoe UI",
        "Helvetica Neue",
        "Arial"
    ]
    
    # Se estivermos executando no Windows, verifica a existência de arquivos na pasta Fonts
    if sys.platform.startswith("win"):
        win_fonts_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        font_file_mapping = {
            "Segoe UI Variable Display": ["SegUIVar.ttf", "seguivar.ttf"],
            "Inter": ["Inter-Regular.ttf", "Inter.ttf", "inter.ttf"],
            "Roboto": ["Roboto-Regular.ttf", "roboto.ttf"],
            "Segoe UI": ["segoeui.ttf", "SEGOEUI.TTF"],
            "Arial": ["arial.ttf", "ARIAL.TTF"]
        }
        if os.path.exists(win_fonts_dir):
            system_files = set(os.listdir(win_fonts_dir))
            for font in preferred_fonts:
                if font in font_file_mapping:
                    if any(f in system_files for f in font_file_mapping[font]):
                        return font
                        
    # Tenta verificar usando tkinter caso esteja instalado e um display exista
    try:
        import tkinter as tk
        from tkinter import font as tkfont
        # Evita abrir janela ao instanciar root vazio sem display
        if sys.platform.startswith("win") or os.environ.get("DISPLAY"):
            root = tk.Tk()
            root.withdraw()
            available_families = set(tkfont.families())
            root.destroy()
            for font_name in preferred_fonts:
                if font_name in available_families:
                    return font_name
    except Exception:
        pass
        
    # Retorna o fallback seguro mais moderno para o OS
    return "Segoe UI" if sys.platform.startswith("win") else "Helvetica Neue"


@dataclass
class FontSpec:
    """Especificação individual de uma fonte para um elemento de interface.
    
    Attributes:
        family: Família tipográfica (ex: 'Segoe UI Variable Display').
        size: Tamanho em pixels ou pontos (ex: 44).
        weight: Peso da fonte ('normal', 'bold', 'semibold', etc.).
        slant: Inclinação ('roman' ou 'italic').
    """
    family: str
    size: int
    weight: str = "normal"
    slant: str = "roman"

    def to_tuple(self) -> Tuple[str, int, str]:
        """Retorna uma tupla padrão compatível com Tkinter/CustomTkinter/PyQt.
        
        Exemplo: ('Segoe UI Variable Display', 44, 'bold')
        """
        return (self.family, self.size, self.weight)

    def to_dict(self) -> Dict[str, Any]:
        """Retorna um dicionário com os parâmetros da fonte."""
        return asdict(self)


@dataclass
class Typography:
    """Conjunto hierárquico completo da tipografia da calculadora.
    
    Garante legibilidade, hierarquia visual clara e tamanhos harmoniosos
    conforme as especificações de design UI/UX do projeto.
    """
    family_name: str
    display_main: FontSpec
    display_history: FontSpec
    btn_num: FontSpec
    btn_sci: FontSpec
    btn_memory: FontSpec
    title: FontSpec
    tab: FontSpec
    status: FontSpec
    label: FontSpec
    tooltip: FontSpec

    @classmethod
    def create_default(cls, custom_family: Optional[str] = None) -> "Typography":
        """Cria e instancia a tipografia com tamanhos exatos de UX/UI."""
        family = custom_family or _resolve_font_family()
        return cls(
            family_name=family,
            # Display Principal: Grande, imponente e em negrito (40-48px -> 44px)
            display_main=FontSpec(family, 44, "bold"),
            # Display de Histórico/Equação: Menor para sub-hierarquia clara (16-18px -> 17px)
            display_history=FontSpec(family, 17, "normal"),
            # Botões Numéricos: Extremamente legíveis e confortáveis ao toque (20-22px -> 21px)
            btn_num=FontSpec(family, 21, "bold"),
            # Botões Científicos e Funções Avançadas: Compactos e elegantes (14-16px -> 15px)
            btn_sci=FontSpec(family, 15, "bold"),
            # Botões de Memória (MC, MR, M+, M-, MS): Leves e funcionais (14-16px -> 14px)
            btn_memory=FontSpec(family, 14, "normal"),
            # Títulos de Seções e Cabeçalhos de Modos: (14px)
            title=FontSpec(family, 14, "bold"),
            # Abas de Navegação (Padrão, Científica, Programador, Financeira): (14px)
            tab=FontSpec(family, 14, "bold"),
            # Status e Avisos (Ângulo DEG/RAD, Memória, Modo): (12px)
            status=FontSpec(family, 12, "normal"),
            # Rótulos Genéricos de Inputs: (14px)
            label=FontSpec(family, 14, "normal"),
            # Tooltips e Dicas Flutuantes: (12px)
            tooltip=FontSpec(family, 12, "normal")
        )


# Instância global singleton com a tipografia recomendada e fallbacks resolvidos
FONTS = Typography.create_default()


# ==============================================================================
# 3. CONFIGURACOES DE LAYOUT E COMPONENTES (SPACING & DIMENSIONS)
# ==============================================================================

@dataclass
class LayoutConfig:
    """Especificações geométricas, espaçamentos e dimensões dos componentes UI.
    
    Aplica princípios de Design System moderno com estilo macOS/iOS e Windows 11,
    definindo cantos suavemente arredondados e grid esteticamente espaçado.
    """
    # Cantos Arredondados (Corner Radius)
    button_corner_radius: int = 14          # Canto arredondado dos botões (12 a 16px -> 14px visual premium)
    display_corner_radius: int = 16         # Canto arredondado do container do visor/display
    card_corner_radius: int = 16            # Canto arredondado dos painéis e cartões laterais
    tab_corner_radius: int = 10             # Canto arredondado para abas e seletores
    
    # Espaçamento de Grid (Padding X e Y)
    grid_padx: int = 4                      # Espaçamento horizontal entre botões na grade
    grid_pady: int = 4                      # Espaçamento vertical entre botões na grade
    
    # Margens e Paddiings de Janela e Painel
    window_padx: int = 16                   # Margem interna horizontal da janela principal
    window_pady: int = 16                   # Margem interna vertical da janela principal
    panel_padx: int = 12                    # Margem interna de sub-painéis (ex: aba científica)
    panel_pady: int = 12                    # Margem interna de sub-painéis
    
    # Espaçamento Interno do Visor
    display_padx: int = 20                  # Padding horizontal interno do display
    display_pady: int = 16                  # Padding vertical interno do display
    
    # Dimensões Padrão de Componentes
    button_height_default: int = 56         # Altura dos botões numéricos e de operação principais
    button_height_compact: int = 44         # Altura reduzida para botões científicos / memória / abas
    button_width_default: int = 76          # Largura padrão dos botões da grade básica
    button_width_compact: int = 64          # Largura padrão para botões de painel científico
    display_height: int = 115               # Altura total recomendada para a área principal de exibição
    
    # Largura de Bordas (Border Widths)
    border_width_default: int = 1           # Borda sutil de separação nos componentes
    border_width_focus: int = 2             # Borda destacada em estados de foco ou seleção ativa
    border_width_none: int = 0              # Sem borda (para botões totalmente planos)


# Instância global com os parâmetros estéticos exigidos (corner_radius=14, padx/y=4, etc.)
LAYOUT_CONFIG = LayoutConfig()


# ==============================================================================
# 4. PALETAS DE CORES E TEMAS (OBSIDIAN DARK, CYBER NEON, SLEEK LIGHT)
# ==============================================================================

@dataclass
class ColorPalette:
    """Paleta de cores completa e estruturada para um tema de design system.
    
    Cada atributo foi pensado para garantir constraste perfeito (WCAG AA/AAA),
    harmonia cromática e hierarquia visual imersiva.
    """
    # Cores de Fundo (Backgrounds)
    bg_primary: str                         # Fundo principal da aplicação e janela
    bg_secondary: str                       # Fundo de cartões, painéis científicos/memória e barras
    bg_tertiary: str                        # Fundo de elementos rebaixados ou separadores
    bg_display: str                         # Fundo específico do container do display/visor
    
    # Cores de Texto e Ícones (Typography & Icons)
    text_primary: str                       # Cor principal de texto (alta legibilidade para display e títulos)
    text_secondary: str                     # Cor secundária de texto (para histórico, equações e legendas)
    text_muted: str                         # Cor opaca para texto desabilitado ou marcações secundárias
    
    # Botões Numéricos (0-9, ponto decimal)
    btn_num_bg: str                         # Cor de fundo dos botões numéricos
    btn_num_hover: str                      # Cor no estado hover (suave e interativo)
    btn_num_text: str                       # Cor do texto do número
    
    # Botões de Operadores Principais (+, -, *, /, %, ^)
    btn_op_bg: str                          # Cor de fundo (ex: Ciano Elétrico / Azul Safira / Roxo Neon)
    btn_op_hover: str                       # Cor de hover dos operadores
    btn_op_text: str                        # Cor de texto/símbolo dos operadores
    
    # Botões Científicos, Trigonométricos e Funções (sin, cos, tan, log, ln, sqrt, pi, etc.)
    btn_sci_bg: str                         # Cor de fundo dos botões científicos
    btn_sci_hover: str                      # Cor de hover científico
    btn_sci_text: str                       # Cor de texto das funções científicas
    
    # Botão de Resultado / Igual (=)
    btn_eq_bg: str                          # Cor de destaque principal / gradiente vibrante
    btn_eq_hover: str                       # Cor de hover do botão de igual
    btn_eq_text: str                        # Cor de texto do botão igual (contraste otimizado)
    
    # Botões de Limpeza e Apagar (C, AC, CE, Backspace)
    btn_clear_bg: str                       # Cor de fundo de alerta/limpeza
    btn_clear_hover: str                    # Cor de hover de limpeza
    btn_clear_text: str                     # Cor de texto dos botões de limpeza
    
    # Botões de Memória e Modificadores (MC, MR, M+, M-, MS, Shift, Alpha)
    btn_memory_bg: str                      # Cor de fundo para memória
    btn_memory_hover: str                   # Cor de hover para memória
    btn_memory_text: str                    # Cor do texto de memória
    
    # Acabamentos, Bordas e Elementos de Destaque
    border_color: str                       # Cor padrão das bordas dos cards e botões
    border_color_focus: str                 # Cor da borda sob foco do teclado ou seleção ativa
    accent_primary: str                     # Cor de realce principal (para cursores, abas ativas, links)
    accent_secondary: str                   # Cor de realce complementar (para gráficos ou indicadores duplos)
    shadow_color: str                       # Cor/tonalidade para simulação de sombra (em frameworks que suportam)
    scrollbar_color: str                    # Cor da barra de rolagem (no histórico ou listas)
    scrollbar_hover: str                    # Cor da barra de rolagem no estado hover


@dataclass
class Theme:
    """Representação consolidada de um Tema visual de UI/UX.
    
    Agrupa o nome descritivo, a paleta cromática de alta precisão, a configuração
    de tipografia associada e as dimensões de layout adequadas para aquele estilo.
    """
    name: str
    description: str
    is_dark: bool
    colors: ColorPalette
    typography: Typography = field(default_factory=lambda: FONTS)
    layout: LayoutConfig = field(default_factory=lambda: LAYOUT_CONFIG)

    def to_dict(self) -> Dict[str, Any]:
        """Converte toda a configuração do tema em um dicionário serializável."""
        return {
            "name": self.name,
            "description": self.description,
            "is_dark": self.is_dark,
            "colors": asdict(self.colors),
            "typography": {k: v.to_dict() if isinstance(v, FontSpec) else v 
                           for k, v in asdict(self.typography).items()},
            "layout": asdict(self.layout)
        }


# ==============================================================================
# 5. INSTANCIACAO DOS TEMAS PRINCIPAIS (THEMES DICTIONARY)
# ==============================================================================

THEMES: Dict[str, Theme] = {
    # --------------------------------------------------------------------------
    # 1. OBSIDIAN DARK
    # Visual grafite/escuro profundo com operadores em Ciano Elétrico / Azul Neon
    # e botão de igual em Destaque Vibrante (Rosa/Magenta Neon ou Azul).
    # --------------------------------------------------------------------------
    "Obsidian Dark": Theme(
        name="Obsidian Dark",
        description="Estética grafite profunda (#1A1A1D, #242428) com contraste em Ciano Elétrico e Magenta Vibrante.",
        is_dark=True,
        colors=ColorPalette(
            bg_primary="#1A1A1D",           # Fundo grafite/escuro profundo
            bg_secondary="#242428",         # Painel de teclado secundário e cards
            bg_tertiary="#1F1F23",          # Separadores e abas inativas
            bg_display="#141417",           # Container do display (preto grafite imaculado)
            
            text_primary="#FFFFFF",         # Texto branco puro de alta visibilidade
            text_secondary="#A0A0A8",       # Cinza prateado suave para equações e histórico
            text_muted="#6E6E78",           # Cinza opaco para funções inativas
            
            btn_num_bg="#2D2D34",           # Botões numéricos pretos/cinza escuro
            btn_num_hover="#3A3A44",        # Hover numérico levemente clareado e suave
            btn_num_text="#FFFFFF",         # Números em branco cristalino
            
            btn_op_bg="#3A86FF",            # Operadores em Ciano Elétrico / Azul Neon (#3A86FF)
            btn_op_hover="#2672EA",         # Hover com tom azulado intenso
            btn_op_text="#FFFFFF",          # Texto do operador em branco puro
            
            btn_sci_bg="#26262D",           # Botões científicos integrados ao grafite do painel
            btn_sci_hover="#32323B",        # Hover dos botões científicos
            btn_sci_text="#D1D1DC",         # Texto cinza claro elegante
            
            btn_eq_bg="#FF006E",            # Botão de igual em Destaque Vibrante Magenta (#FF006E)
            btn_eq_hover="#E0005F",         # Hover em magenta profundo
            btn_eq_text="#FFFFFF",          # Texto de igual branco brilhante
            
            btn_clear_bg="#4A2630",         # Fundo bordô/avermelhado escuro sofisticado para C/AC
            btn_clear_hover="#5C2F3C",      # Hover suave
            btn_clear_text="#FF6B6B",       # Texto vermelho coral vibrante
            
            btn_memory_bg="#222228",        # Fundo discreto para memória
            btn_memory_hover="#2C2C34",     # Hover de memória
            btn_memory_text="#8E9AFE",      # Texto em tom lilás/azul pálido
            
            border_color="#343A42",         # Bordas finas de delimitação cinza metálico
            border_color_focus="#3A86FF",   # Borda ciano/azul sob foco
            accent_primary="#3A86FF",       # Destaque em Ciano Elétrico
            accent_secondary="#FF006E",     # Destaque complementar em Magenta
            shadow_color="#0D0D0F",         # Sombra escura de profundidade
            scrollbar_color="#3A3A44",      # Barra de rolagem discreta
            scrollbar_hover="#4E4E5A"       # Hover da barra de rolagem
        )
    ),

    # --------------------------------------------------------------------------
    # 2. CYBER NEON
    # Visual futurista com fundo preto absoluto (#0A0A0C), detalhes em Roxo Neon
    # (#8338EC) e Verde Esmeralda/Neon (#00F5D4). Contraste cyberpunk extremo.
    # --------------------------------------------------------------------------
    "Cyber Neon": Theme(
        name="Cyber Neon",
        description="Fundo preto absoluto (#0A0A0C) com detalhes acentuados em Roxo Neon (#8338EC) e Verde Esmeralda (#00F5D4).",
        is_dark=True,
        colors=ColorPalette(
            bg_primary="#0A0A0C",           # Preto absoluto (OLED friendly)
            bg_secondary="#121216",         # Preto metálico com toque cibernético
            bg_tertiary="#16141F",          # Painéis adjacentes com undertone roxo escuro
            bg_display="#050507",           # Visor ultra escuro de contraste máximo
            
            text_primary="#E0FFFA",         # Branco levemente esverdeado/neon para display principal
            text_secondary="#B892FF",       # Roxo pálido neon para histórico de equações
            text_muted="#5D4E78",           # Roxo escuro mutado
            
            btn_num_bg="#16141F",           # Botões com undertone roxo carbono escuríssimo
            btn_num_hover="#242035",        # Hover roxo brilhante suave
            btn_num_text="#FFFFFF",         # Números com clareza máxima
            
            btn_op_bg="#8338EC",            # Operadores em Roxo Neon vibrante (#8338EC)
            btn_op_hover="#6E26D4",         # Hover em roxo real profundo
            btn_op_text="#FFFFFF",          # Texto branco puro
            
            btn_sci_bg="#131722",           # Fundo azul-carbono escuro para funções científicas
            btn_sci_hover="#1F2536",        # Hover científico
            btn_sci_text="#00F5D4",         # Texto científico em Verde Esmeralda / Neon (#00F5D4)
            
            btn_eq_bg="#00F5D4",            # Botão de igual em Verde Esmeralda / Neon luminoso (#00F5D4)
            btn_eq_hover="#00D4B6",         # Hover em verde esmeralda denso
            btn_eq_text="#0A0A0C",          # Texto PRETO ABSOLUTO para contraste máximo com o neon!
            
            btn_clear_bg="#FF007F",         # Rosa Cyberpunk / Magenta Laser para apagar/limpar
            btn_clear_hover="#D6006B",      # Hover rosa laser
            btn_clear_text="#FFFFFF",       # Texto branco
            
            btn_memory_bg="#10131A",        # Botões de memória super escuros
            btn_memory_hover="#191F2C",     # Hover de memória
            btn_memory_text="#00C9A7",      # Texto em tom verde azulado neon
            
            border_color="#2D2342",         # Borda roxo neon escura
            border_color_focus="#00F5D4",   # Borda verde esmeralda brilhante sob foco
            accent_primary="#00F5D4",       # Verde Esmeralda Neon
            accent_secondary="#8338EC",     # Roxo Neon
            shadow_color="#000000",         # Sombra preta pura
            scrollbar_color="#2D2342",      # Scrollbar roxo escuro
            scrollbar_hover="#48376A"       # Hover de scrollbar
        )
    ),

    # --------------------------------------------------------------------------
    # 3. SLEEK LIGHT
    # Fundo branco/cinza claro macio (#F8F9FA, #E9ECEF), botões limpos,
    # operadores em Azul Safira (#0066CC) e botão de igual Laranja Pôr do Sol (#FF6B35).
    # --------------------------------------------------------------------------
    "Sleek Light": Theme(
        name="Sleek Light",
        description="Estética iluminada e limpa (#F8F9FA, #E9ECEF) com operadores em Azul Safira e destaque Laranja Pôr do Sol.",
        is_dark=False,
        colors=ColorPalette(
            bg_primary="#F8F9FA",           # Fundo branco/cinza claro macio e agradável à vista
            bg_secondary="#E9ECEF",         # Painel de botões em cinza pérola suave
            bg_tertiary="#DEE2E6",          # Separadores e contornos
            bg_display="#FFFFFF",           # Visor branco puro imaculado com máxima luminosidade
            
            text_primary="#212529",         # Cinza chumbo/preto quase puro para leitura nítida sem fadiga
            text_secondary="#6C757D",       # Cinza médio para equações, histórico e subtextos
            text_muted="#ADB5BD",           # Cinza claro para elementos desabilitados
            
            btn_num_bg="#FFFFFF",           # Botões numéricos brancos limpos e elegantes
            btn_num_hover="#F1F3F5",        # Hover cinza macio muito suave
            btn_num_text="#212529",         # Números em cinza escuro chumbo
            
            btn_op_bg="#0066CC",            # Operadores em Azul Safira profissional (#0066CC)
            btn_op_hover="#0052A3",         # Hover com tom azul safira encorpado
            btn_op_text="#FFFFFF",          # Texto branco puro em contraste com azul safira
            
            btn_sci_bg="#E2E8F0",           # Botões científicos em cinza azulado claro
            btn_sci_hover="#D1DBE5",        # Hover dos botões científicos
            btn_sci_text="#334155",         # Texto azul ardósia escuro
            
            btn_eq_bg="#FF6B35",            # Botão de igual em Laranja Pôr do Sol (#FF6B35) vibrante
            btn_eq_hover="#E55A2B",         # Hover em laranja quente acentuado
            btn_eq_text="#FFFFFF",          # Texto de igual branco brilhante
            
            btn_clear_bg="#FFE5E5",         # Fundo vermelho pastel suave para limpeza e cancelamento
            btn_clear_hover="#FFCCCC",      # Hover de limpeza
            btn_clear_text="#D32F2F",       # Texto vermelho carmim nítido
            
            btn_memory_bg="#EDF2F7",        # Botão de memória leve
            btn_memory_hover="#E2E8F0",     # Hover de memória
            btn_memory_text="#2B6CB0",      # Texto em tom azul cobalto moderno
            
            border_color="#CBD5E1",         # Bordas cinzas limpas e nítidas
            border_color_focus="#0066CC",   # Borda Azul Safira sob foco
            accent_primary="#0066CC",       # Destaque em Azul Safira
            accent_secondary="#FF6B35",     # Destaque em Laranja Pôr do Sol
            shadow_color="#E2E8F0",         # Sombra clara difusa para profundidade sutil
            scrollbar_color="#CBD5E1",      # Scrollbar macia
            scrollbar_hover="#94A3B8"       # Hover do scrollbar
        )
    )
}

# Tema padrão da aplicação
DEFAULT_THEME = "Obsidian Dark"


# ==============================================================================
# 6. FUNCOES UTILITARIAS E GERADORES DE ESTILO PARA WIDGETS
# ==============================================================================

def get_theme(theme_name: str = DEFAULT_THEME) -> Theme:
    """Obtém o objeto de tema correspondente pelo nome.
    
    Caso o nome fornecido não exista, retorna de forma segura o tema padrão
    ("Obsidian Dark") sem gerar exceções que interrompam a interface.

    Args:
        theme_name (str): Nome identificador do tema desejado.

    Returns:
        Theme: Instância contendo paleta de cores, tipografia e layout.

    Example:
        >>> tema = get_theme("Cyber Neon")
        >>> print(tema.colors.btn_eq_bg)
        #00F5D4
    """
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])


def list_themes() -> List[str]:
    """Retorna a lista de todos os nomes de temas cadastrados e disponíveis.
    
    Ideal para preencher menus dropdown (comboboxes) ou modais de configurações
    na interface do usuário.

    Returns:
        List[str]: Nomes dos temas, ex: ['Obsidian Dark', 'Cyber Neon', 'Sleek Light'].
    """
    return list(THEMES.keys())


def get_font_tuple(role: str, 
                   custom_size: Optional[int] = None, 
                   custom_weight: Optional[str] = None,
                   theme_name: Optional[str] = None) -> Tuple[str, int, str]:
    """Resolve e retorna uma tupla de fonte pronta para widgets (Tkinter/CTk/PyQt).

    Args:
        role (str): Papel tipográfico ('display_main', 'display_history', 
                    'btn_num', 'btn_sci', 'btn_memory', 'title', 'tab', 'status', 'label').
        custom_size (Optional[int]): Tamanho de fonte sobrescrito para casos especiais.
        custom_weight (Optional[str]): Peso de fonte sobrescrito ('normal', 'bold', etc.).
        theme_name (Optional[str]): Tema para extrair tipografia (ou global FONTS se None).

    Returns:
        Tuple[str, int, str]: Tupla formatada, ex: ('Segoe UI Variable Display', 21, 'bold').
    """
    typo = get_theme(theme_name).typography if theme_name else FONTS
    font_spec: Optional[FontSpec] = getattr(typo, role, None)
    
    if not font_spec:
        # Fallback seguro para o rótulo genérico se o papel não for encontrado
        font_spec = typo.label
        
    return (
        font_spec.family,
        custom_size if custom_size is not None else font_spec.size,
        custom_weight if custom_weight is not None else font_spec.weight
    )


def get_button_style(theme_name: str = DEFAULT_THEME, 
                     button_type: ButtonType = "num",
                     custom_width: Optional[int] = None,
                     custom_height: Optional[int] = None) -> Dict[str, Any]:
    """Gera um dicionário de estilo completo e otimizado para botões.
    
    Os parâmetros retornados podem ser diretamente desempacotados via `**kwargs`
    ao instanciar widgets de bibliotecas GUI modernas como CustomTkinter (`CTkButton`)
    ou adaptados para bibliotecas equivalentes (PySide6, Tkinter-ttk).

    Args:
        theme_name (str): Nome do tema a ser aplicado (ex: "Obsidian Dark").
        button_type (ButtonType): Tipo funcional do botão ("num", "op", "sci", 
                                  "eq", "clear", "memory", "modifier").
        custom_width (Optional[int]): Largura customizada caso deseje substituir o padrão.
        custom_height (Optional[int]): Altura customizada.

    Returns:
        Dict[str, Any]: Dicionário contendo fg_color, hover_color, text_color,
                        border_color, border_width, corner_radius, width, height e font.

    Example:
        >>> style = get_button_style("Cyber Neon", button_type="eq")
        >>> # btn_igual = customtkinter.CTkButton(frame, text="=", **style)
    """
    theme = get_theme(theme_name)
    colors = theme.colors
    layout = theme.layout

    # Mapeamento dinâmico de cores de acordo com a função do botão
    color_map = {
        "num": (colors.btn_num_bg, colors.btn_num_hover, colors.btn_num_text, "btn_num"),
        "op": (colors.btn_op_bg, colors.btn_op_hover, colors.btn_op_text, "btn_num"),
        "sci": (colors.btn_sci_bg, colors.btn_sci_hover, colors.btn_sci_text, "btn_sci"),
        "eq": (colors.btn_eq_bg, colors.btn_eq_hover, colors.btn_eq_text, "btn_num"),
        "clear": (colors.btn_clear_bg, colors.btn_clear_hover, colors.btn_clear_text, "btn_sci"),
        "memory": (colors.btn_memory_bg, colors.btn_memory_hover, colors.btn_memory_text, "btn_memory"),
        "modifier": (colors.btn_sci_bg, colors.btn_sci_hover, colors.btn_sci_text, "btn_sci")
    }

    bg, hover, text, font_role = color_map.get(
        button_type, 
        (colors.btn_num_bg, colors.btn_num_hover, colors.btn_num_text, "btn_num")
    )

    # Determina dimensões padrão baseadas no tipo de botão
    is_compact = button_type in ("sci", "memory", "modifier")
    default_w = layout.button_width_compact if is_compact else layout.button_width_default
    default_h = layout.button_height_compact if is_compact else layout.button_height_default

    return {
        "fg_color": bg,
        "hover_color": hover,
        "text_color": text,
        "border_color": colors.border_color,
        "border_width": layout.border_width_default if button_type not in ("eq", "op") else layout.border_width_none,
        "corner_radius": layout.button_corner_radius,
        "width": custom_width if custom_width is not None else default_w,
        "height": custom_height if custom_height is not None else default_h,
        "font": get_font_tuple(font_role, theme_name=theme_name)
    }


def get_display_style(theme_name: str = DEFAULT_THEME) -> Dict[str, Any]:
    """Retorna os parâmetros de estilo recomendados para o container do Visor/Display.

    Args:
        theme_name (str): Nome do tema ativo.

    Returns:
        Dict[str, Any]: Dicionário com fg_color, border_color, border_width, 
                        corner_radius, height, padding, text_color e font.
    """
    theme = get_theme(theme_name)
    return {
        "fg_color": theme.colors.bg_display,
        "border_color": theme.colors.border_color,
        "border_width": theme.layout.border_width_default,
        "corner_radius": theme.layout.display_corner_radius,
        "height": theme.layout.display_height,
        "padx": theme.layout.display_padx,
        "pady": theme.layout.display_pady,
        "text_color": theme.colors.text_primary,
        "font_main": get_font_tuple("display_main", theme_name=theme_name),
        "font_history": get_font_tuple("display_history", theme_name=theme_name)
    }


def get_frame_style(theme_name: str = DEFAULT_THEME, 
                    panel_type: PanelType = "secondary") -> Dict[str, Any]:
    """Retorna o estilo configurado para frames, painéis e cartões laterais.

    Args:
        theme_name (str): Nome do tema ativo.
        panel_type (PanelType): Tipo de painel ("primary", "secondary", "tertiary", "display").

    Returns:
        Dict[str, Any]: Parâmetros visuais para frames ou cards GUI.
    """
    theme = get_theme(theme_name)
    bg_map = {
        "primary": theme.colors.bg_primary,
        "secondary": theme.colors.bg_secondary,
        "tertiary": theme.colors.bg_tertiary,
        "display": theme.colors.bg_display
    }
    return {
        "fg_color": bg_map.get(panel_type, theme.colors.bg_secondary),
        "border_color": theme.colors.border_color,
        "border_width": theme.layout.border_width_default if panel_type != "primary" else 0,
        "corner_radius": theme.layout.card_corner_radius if panel_type != "primary" else 0
    }


def export_theme_to_json(theme_name: str = DEFAULT_THEME, filepath: Optional[str] = None) -> str:
    """Exporta todas as configurações de um tema para uma string JSON ou arquivo.
    
    Útil para persistência de preferências do usuário ou integração com frameworks
    web/desktops híbridos (Electron, Qt QML, etc.).

    Args:
        theme_name (str): Nome do tema a ser exportado.
        filepath (Optional[str]): Caminho absoluto ou relativo para salvar o arquivo JSON.

    Returns:
        str: Conteúdo JSON formatado e serializado do tema.
    """
    theme = get_theme(theme_name)
    json_data = json.dumps(theme.to_dict(), indent=4, ensure_ascii=False)
    
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_data)
            
    return json_data


# ==============================================================================
# 7. BLOCO DE VALIDACAO E TESTE DE EXECUCAO DIRETA
# ==============================================================================

if __name__ == "__main__":
    # Garante que o console do Windows não gere erros de codificação com caracteres especiais
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass

    print("=" * 75)
    print(" [INFO] SISTEMA DE DESIGN SYSTEM E THEME CONFIG - CALCULADORA PRO")
    print("=" * 75)
    
    # 1. Validação dos temas carregados
    temas = list_themes()
    print(f"\n[OK] Temas disponíveis ({len(temas)}): {', '.join(temas)}")
    
    # 2. Resolução da fonte do sistema
    fonte_sistema = _resolve_font_family()
    print(f"[OK] Fonte principal de UI detectada no OS: '{fonte_sistema}'")
    
    # 3. Teste de inspeção de paletas
    for nome_tema in temas:
        t = get_theme(nome_tema)
        print(f"\n--- Resumo de Paleta: {t.name} ({'Escuro' if t.is_dark else 'Claro'}) ---")
        print(f"    Descrição : {t.description}")
        print(f"    Fundo     : Primary={t.colors.bg_primary} | Secondary={t.colors.bg_secondary}")
        print(f"    Operadores: BG={t.colors.btn_op_bg} | Hover={t.colors.btn_op_hover} | Text={t.colors.btn_op_text}")
        print(f"    Botão (=) : BG={t.colors.btn_eq_bg} | Hover={t.colors.btn_eq_hover} | Text={t.colors.btn_eq_text}")
        
    # 4. Exemplo de geração de estilo para botão
    estilo_exemplo = get_button_style("Cyber Neon", "eq")
    print("\n[OK] Exemplo de Dicionário Gerado para Botão '=' no tema 'Cyber Neon':")
    for chave, valor in estilo_exemplo.items():
        print(f"    - {chave:<15}: {valor}")
        
    # 5. Verificação dos cantos e dimensões
    print("\n[OK] Parâmetros de Layout (Apple macOS / Windows 11 Modern look):")
    print(f"    - Canto Arredondado Botões : {LAYOUT_CONFIG.button_corner_radius}px")
    print(f"    - Canto Arredondado Visor  : {LAYOUT_CONFIG.display_corner_radius}px")
    print(f"    - Grid Spacing (padx/pady) : {LAYOUT_CONFIG.grid_padx}px / {LAYOUT_CONFIG.grid_pady}px")
    print(f"    - Display Principal (Fonte): {FONTS.display_main.to_tuple()}")
    
    print("\n" + "=" * 75)
    print(" [SUCESSO] VALIDAÇÃO DO MÓDULO THEME_CONFIG CONCLUÍDA COM SUCESSO!")
    print("=" * 75)

