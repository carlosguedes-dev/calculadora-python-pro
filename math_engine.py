"""
Módulo MathEngine - Motor Matemático e Parser Seguro
Calculadora Altamente Profissional em Python

Suporta:
- Modo Padrão (Standard): operações básicas, porcentagem, quadrado, raiz, recíproco, inversão de sinal.
- Modo Científico (Scientific): trigonometria (RAD/DEG), logaritmos, exponenciais, potências, raízes, fatorial, constantes (pi, e), módulo, valor absoluto.
- Modo Programador (Programmer): conversão instantânea entre bases (DEC, HEX, OCT, BIN) e operações bitwise (AND, OR, XOR, NOT, shift left/right).
- Sistema de Memória Completo (MC, MR, M+, M-, MS, lista/pilha de memória).
- Sistema de Histórico de Cálculos (registro de timestamps, expressões, resultados, limpeza e reobtenção).
- Avaliação Segura (AST Parsing com Whitelist).
- Tratamento Gracioso de Erros com mensagens amigáveis em português.
"""

import ast
import operator
import math
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Union, Any


# =====================================================================
# EXCEÇÕES CUSTOMIZADAS
# =====================================================================
class MathEngineError(Exception):
    """Exceção base para erros de cálculo na calculadora."""
    def __init__(self, message: str = "Erro no cálculo"):
        super().__init__(message)
        self.user_message = message

class DivisionByZeroError(MathEngineError):
    def __init__(self):
        super().__init__("Erro: Divisão por zero")

class DomainError(MathEngineError):
    def __init__(self, message: str = "Erro: Domínio inválido"):
        super().__init__(message)

class MalformedExpressionError(MathEngineError):
    def __init__(self, message: str = "Erro: Expressão malformada"):
        super().__init__(message)

class NumericalOverflowError(MathEngineError):
    def __init__(self):
        super().__init__("Erro: Estouro numérico")


# =====================================================================
# ESTRUTURAS DE DADOS (HISTÓRICO E MEMÓRIA)
# =====================================================================
@dataclass
class CalculationHistoryItem:
    timestamp: str
    expression: str
    result: str
    mode: str = "STANDARD"

@dataclass
class MemoryItem:
    value: Union[int, float]
    timestamp: str
    formatted_str: str = ""

    def __post_init__(self):
        if not self.formatted_str:
            self.formatted_str = MathEngine.format_number(self.value)


# =====================================================================
# AVALIADOR AST SEGURO (SAFE EVALUATOR)
# =====================================================================
class SafeEvaluator(ast.NodeVisitor):
    """
    Avaliador de expressões matemáticas utilizando AST com whitelist de nós e funções.
    Evita totalmente o uso de eval() perigoso ou injeção de código.
    """
    def __init__(self, angle_unit: str = "DEG", mode: str = "STANDARD"):
        self.angle_unit = angle_unit.upper()
        self.mode = mode.upper()
        
        # Mapeamento de operadores binários permitidos
        self.bin_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: self._safe_div,
            ast.Mod: self._safe_mod,
            ast.Pow: self._safe_pow,
            ast.BitAnd: operator.and_,
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.LShift: self._safe_lshift,
            ast.RShift: self._safe_rshift,
        }
        
        # Mapeamento de operadores unários permitidos
        self.unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.Invert: operator.invert,
        }
        
        # Whitelist de funções e constantes matemáticas
        self.functions = {
            # Trigonometria
            'sin': self._sin,
            'cos': self._cos,
            'tan': self._tan,
            'asin': self._asin,
            'acos': self._acos,
            'atan': self._atan,
            # Exponenciais e Logarítmicas
            'log': self._log,
            'log10': self._log10,
            'ln': self._ln,
            'exp': self._exp,
            'sqrt': self._sqrt,
            'root': self._root,
            'fact': self._fact,
            'mod': self._safe_mod,
            'abs': abs,
        }
        
        self.constants = {
            'pi': math.pi,
            'π': math.pi,
            'e': math.e,
        }

    # --- Operadores seguros ---
    def _safe_div(self, a, b):
        if b == 0:
            raise DivisionByZeroError()
        return operator.truediv(a, b)

    def _safe_mod(self, a, b):
        if b == 0:
            raise DivisionByZeroError()
        return operator.mod(a, b)

    def _safe_pow(self, a, b):
        try:
            # Checagens para evitar estouro numérico ou raízes de negativos no real
            if a < 0 and isinstance(b, float) and not b.is_integer():
                raise DomainError("Erro: Domínio inválido")
            if abs(b) > 10000:  # Limite para evitar travamento em computação de potências colossais
                raise NumericalOverflowError()
            res = operator.pow(a, b)
            if isinstance(res, complex):
                raise DomainError("Erro: Domínio inválido")
            if math.isinf(res) or math.isnan(res):
                raise NumericalOverflowError()
            return res
        except (OverflowError, ValueError):
            raise NumericalOverflowError()

    def _safe_lshift(self, a, b):
        if b < 0 or b > 10000:
            raise DomainError("Erro: Domínio inválido")
        return operator.lshift(int(a), int(b))

    def _safe_rshift(self, a, b):
        if b < 0 or b > 10000:
            raise DomainError("Erro: Domínio inválido")
        return operator.rshift(int(a), int(b))

    # --- Funções matemáticas seguras ---
    def _sin(self, x):
        val = math.radians(x) if self.angle_unit == "DEG" else x
        res = math.sin(val)
        # Limpar imprecisão de float para ângulos exatos (ex: sin(180 deg) == 0)
        return 0.0 if abs(res) < 1e-15 else res

    def _cos(self, x):
        val = math.radians(x) if self.angle_unit == "DEG" else x
        res = math.cos(val)
        return 0.0 if abs(res) < 1e-15 else res

    def _tan(self, x):
        if self.angle_unit == "DEG":
            # Em graus, tan(90 + k*180) é indefinido
            if abs((x - 90) % 180) < 1e-10 or abs((x - 90) % 180 - 180) < 1e-10:
                raise DomainError("Erro: Domínio inválido")
            val = math.radians(x)
        else:
            # Em radianos, tan(pi/2 + k*pi) é indefinido
            rem = (x - math.pi/2) % math.pi
            if abs(rem) < 1e-10 or abs(rem - math.pi) < 1e-10:
                raise DomainError("Erro: Domínio inválido")
            val = x
        res = math.tan(val)
        return 0.0 if abs(res) < 1e-15 else res

    def _asin(self, x):
        if x < -1.0 or x > 1.0:
            raise DomainError("Erro: Domínio inválido")
        res = math.asin(x)
        return math.degrees(res) if self.angle_unit == "DEG" else res

    def _acos(self, x):
        if x < -1.0 or x > 1.0:
            raise DomainError("Erro: Domínio inválido")
        res = math.acos(x)
        return math.degrees(res) if self.angle_unit == "DEG" else res

    def _atan(self, x):
        res = math.atan(x)
        return math.degrees(res) if self.angle_unit == "DEG" else res

    def _log10(self, x):
        if x <= 0:
            raise DomainError("Erro: Domínio inválido")
        return math.log10(x)

    def _log(self, x, base=10):
        if x <= 0 or base <= 0 or base == 1:
            raise DomainError("Erro: Domínio inválido")
        return math.log(x, base)

    def _ln(self, x):
        if x <= 0:
            raise DomainError("Erro: Domínio inválido")
        return math.log(x)

    def _exp(self, x):
        try:
            return math.exp(x)
        except OverflowError:
            raise NumericalOverflowError()

    def _sqrt(self, x):
        if x < 0:
            raise DomainError("Erro: Domínio inválido")
        return math.sqrt(x)

    def _root(self, x, y):
        if y == 0:
            raise DivisionByZeroError()
        if x < 0 and isinstance(y, (int, float)):
            # Se y for par ou fração com denominador par no reduzido
            if int(y) == y and int(y) % 2 == 0:
                raise DomainError("Erro: Domínio inválido")
            elif not isinstance(y, int) and not y.is_integer():
                raise DomainError("Erro: Domínio inválido")
            # Raiz ímpar de número negativo
            return -math.pow(-x, 1.0 / y)
        try:
            return math.pow(x, 1.0 / y)
        except (OverflowError, ValueError):
            raise NumericalOverflowError()

    def _fact(self, x):
        if x < 0 or (isinstance(x, float) and not x.is_integer()):
            raise DomainError("Erro: Domínio inválido")
        if x > 5000:  # Evita travamento por cálculo fatorial extremo
            raise NumericalOverflowError()
        try:
            return math.factorial(int(x))
        except OverflowError:
            raise NumericalOverflowError()

    # --- Visitação dos Nós do AST ---
    def visit(self, node):
        return super().visit(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node.value, str) and node.value in self.constants:
            return self.constants[node.value]
        raise MalformedExpressionError()

    def visit_Num(self, node):
        # Suporte para Python mais antigo ou nós AST numéricos
        return node.n

    def visit_Name(self, node):
        name = node.id.lower()
        if name in self.constants:
            return self.constants[name]
        raise MalformedExpressionError()

    def visit_BinOp(self, node):
        op_type = type(node.op)
        if op_type not in self.bin_ops:
            raise MalformedExpressionError()
        
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        
        try:
            return self.bin_ops[op_type](left_val, right_val)
        except (DivisionByZeroError, DomainError, NumericalOverflowError, MalformedExpressionError):
            raise
        except ZeroDivisionError:
            raise DivisionByZeroError()
        except OverflowError:
            raise NumericalOverflowError()
        except Exception:
            raise MalformedExpressionError()

    def visit_UnaryOp(self, node):
        op_type = type(node.op)
        if op_type not in self.unary_ops:
            raise MalformedExpressionError()
        
        val = self.visit(node.operand)
        try:
            return self.unary_ops[op_type](val)
        except Exception:
            raise MalformedExpressionError()

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise MalformedExpressionError()
        
        func_name = node.func.id.lower()
        if func_name not in self.functions:
            raise MalformedExpressionError()
        
        args = [self.visit(arg) for arg in node.args]
        try:
            return self.functions[func_name](*args)
        except (DivisionByZeroError, DomainError, NumericalOverflowError, MalformedExpressionError):
            raise
        except ZeroDivisionError:
            raise DivisionByZeroError()
        except OverflowError:
            raise NumericalOverflowError()
        except Exception:
            raise DomainError("Erro: Domínio inválido")

    def generic_visit(self, node):
        raise MalformedExpressionError()


# =====================================================================
# CLASSE PRINCIPAL DO MOTOR MATEMÁTICO (MATH ENGINE)
# =====================================================================
class MathEngine:
    """
    Motor Matemático central da Calculadora Profissional.
    Gerencia modos, avaliação segura de expressões, histórico e memória.
    """
    MODES = ("STANDARD", "SCIENTIFIC", "PROGRAMMER")
    ANGLE_UNITS = ("DEG", "RAD")

    def __init__(self, mode: str = "STANDARD", angle_unit: str = "DEG"):
        self.mode = mode.upper() if mode.upper() in self.MODES else "STANDARD"
        self.angle_unit = angle_unit.upper() if angle_unit.upper() in self.ANGLE_UNITS else "DEG"
        
        self.history: List[CalculationHistoryItem] = []
        self.memory_stack: List[MemoryItem] = []

    def set_mode(self, mode: str) -> None:
        """Altera o modo de operação da calculadora."""
        if mode.upper() in self.MODES:
            self.mode = mode.upper()

    def set_angle_unit(self, unit: str) -> None:
        """Altera a unidade angular (DEG - Graus, RAD - Radianos) para o modo científico."""
        if unit.upper() in self.ANGLE_UNITS:
            self.angle_unit = unit.upper()

    @staticmethod
    def format_number(val: Union[int, float, complex]) -> str:
        """
        Formata um número para exibição limpa e sem erros de imprecisão de float (IEEE 754).
        Ex: 37.0 -> '37', 0.30000000000000004 -> '0.3'
        """
        if isinstance(val, complex):
            return str(val)
        
        if isinstance(val, int) or (isinstance(val, float) and val.is_integer()):
            # Se for int ou float que representa inteiro exato dentro dos limites normais
            if abs(val) < 1e16:
                return str(int(round(val)))
        
        if isinstance(val, float):
            if math.isnan(val):
                return "Erro: Domínio inválido"
            if math.isinf(val):
                return "Erro: Estouro numérico"
            
            # Formatação com 12 casas significativas, removendo zeros desnecessários
            formatted = f"{val:.12g}"
            if "." in formatted and "e" not in formatted.lower():
                formatted = formatted.rstrip("0").rstrip(".")
            return formatted
        
        return str(val)

    def _preprocess_expression(self, expression: str) -> str:
        """
        Prepara e normaliza a string da expressão antes do parse do AST.
        Converte símbolos matemáticos visuais em operadores Python e trata notações especiais.
        """
        expr = expression.strip()
        if not expr:
            return ""

        # 1. Substituição de vírgula decimal pt-BR por ponto (ex: 3,14 -> 3.14)
        # Atenção para não substituir vírgulas de separação de argumentos: apenas entre dígitos
        expr = re.sub(r'(\d),(\d)', r'\1.\2', expr)

        # 2. Símbolos visuais de operadores
        expr = expr.replace('×', '*').replace('÷', '/').replace('–', '-').replace('−', '-')

        # 3. Constantes visuais
        expr = re.sub(r'\bπ\b|π', 'pi', expr)

        # 4. Modo Programador: operadores bitwise por extenso (case-insensitive) e hex/bin com prefixos automáticos se necessário
        if self.mode == "PROGRAMMER":
            # Preserva '^' como XOR bitwise. Substitui palavras-chave:
            expr = re.sub(r'\bAND\b', ' & ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bOR\b', ' | ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bXOR\b', ' ^ ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bNOT\b', ' ~ ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bMOD\b', ' % ', expr, flags=re.IGNORECASE)
            # Em modo programador, permite conversão rápida de tokens HEX (se contiver A-F e não for função)
            # Para avaliação direta no programador, números em hex que começam com 0x ou 0b são normais em Python
        else:
            # Nos modos Padrão e Científico, '^' representa potência (**)
            expr = expr.replace('^', '**')

        # 5. Tratamento de Raiz Quadrada visual (√x ou √(x))
        # Loop para substituir repetidamente ocorrências de √
        while '√' in expr:
            # Captura √(expr_entre_parênteses) ou √numero/token
            new_expr = re.sub(r'√\s*\(([^()]+)\)', r'sqrt(\1)', expr)
            if new_expr == expr:
                # Tenta capturar √ sem parênteses seguidos de número ou identificador
                new_expr = re.sub(r'√\s*([0-9]+(?:\.[0-9]+)?|\b[a-zA-Z_]\w*\b)', r'sqrt(\1)', expr)
            if new_expr == expr:
                # Se não conseguiu simplificar mais, sai do loop
                break
            expr = new_expr
        # Caso sobre algum √( com parênteses aninhados complexos
        expr = expr.replace('√(', 'sqrt(')
        expr = re.sub(r'√\s*([0-9]+(?:\.[0-9]+)?)', r'sqrt(\1)', expr)

        # 6. Tratamento de Fatorial sufixo (ex: 5! ou (2+3)!)
        while '!' in expr:
            # Procura por número ou variável seguido de !
            new_expr = re.sub(r'([0-9]+(?:\.[0-9]+)?|\b[a-zA-Z_]\w*\b)\s*!', r'fact(\1)', expr)
            if new_expr == expr:
                # Procura por parênteses fechando seguido de !: (expr)! -> fact(expr)
                new_expr = re.sub(r'\(([^()]+)\)\s*!', r'fact(\1)', expr)
            if new_expr == expr:
                break
            expr = new_expr

        # 7. Tratamento de Porcentagem (%) nos Modos Padrão e Científico
        if self.mode != "PROGRAMMER" and '%' in expr:
            # Se a expressão for composta como A + B% ou A - B% -> A + (A * B / 100)
            pattern_add_sub = r'(.*?)([+\-])\s*([0-9]+(?:\.[0-9]+)?)\s*%'
            match = re.search(pattern_add_sub, expr)
            if match:
                base_part = match.group(1).strip()
                op = match.group(2)
                pct_val = match.group(3)
                if base_part:
                    expr = re.sub(pattern_add_sub, rf'\1 \2 (\1 * \3 / 100)', expr, count=1)
            
            # Para casos como A * B% ou A / B% ou apenas B% -> substituímos X% por (X / 100)
            expr = re.sub(r'([0-9]+(?:\.[0-9]+)?)\s*%', r'(\1 / 100)', expr)

        # 8. Palavra-chave MOD para operador módulo nos Modos Padrão e Científico
        if self.mode != "PROGRAMMER":
            expr = re.sub(r'\bMOD\b', ' % ', expr, flags=re.IGNORECASE)

        return expr

    def evaluate(self, expression: str, add_to_history: bool = True) -> str:
        """
        Avalia uma expressão matemática de forma segura.
        Retorna a string com o resultado formatado ou uma mensagem de erro amigável em português.
        """
        if not expression or not expression.strip():
            return "0"
            
        try:
            processed_expr = self._preprocess_expression(expression)
            if not processed_expr:
                return "0"

            # Parse seguro para AST
            try:
                tree = ast.parse(processed_expr, mode='eval')
            except SyntaxError:
                raise MalformedExpressionError()

            # Avaliação via Visitor
            evaluator = SafeEvaluator(angle_unit=self.angle_unit, mode=self.mode)
            raw_result = evaluator.visit(tree)

            # Formatação
            formatted_result = self.format_number(raw_result)
            
            if formatted_result.startswith("Erro:"):
                return formatted_result

            # Adição ao Histórico
            if add_to_history and expression.strip() != formatted_result:
                self.add_to_history(expression.strip(), formatted_result)

            return formatted_result

        except MathEngineError as e:
            return e.user_message
        except ZeroDivisionError:
            return "Erro: Divisão por zero"
        except (OverflowError, MemoryError):
            return "Erro: Estouro numérico"
        except Exception:
            return "Erro: Expressão malformada"

    # =================================================================
    # OPERAÇÕES DIRETAS (BOTÕES DE AÇÃO IMEDIATA NA UI)
    # =================================================================
    def calculate_square(self, val_str: str) -> str:
        """Calcula x² diretamente a partir de um valor no display."""
        res = self.evaluate(f"({val_str}) ** 2", add_to_history=False)
        if not res.startswith("Erro:"):
            self.add_to_history(f"({val_str})²", res)
        return res

    def calculate_sqrt(self, val_str: str) -> str:
        """Calcula √x diretamente."""
        res = self.evaluate(f"sqrt({val_str})", add_to_history=False)
        if not res.startswith("Erro:"):
            self.add_to_history(f"√({val_str})", res)
        return res

    def calculate_reciprocal(self, val_str: str) -> str:
        """Calcula 1/x diretamente."""
        res = self.evaluate(f"1 / ({val_str})", add_to_history=False)
        if not res.startswith("Erro:"):
            self.add_to_history(f"1/({val_str})", res)
        return res

    def toggle_sign(self, val_str: str) -> str:
        """Inverte o sinal do número atual (±)."""
        val_str = val_str.strip()
        if not val_str or val_str == "0" or val_str.startswith("Erro:"):
            return val_str
        
        if val_str.startswith("-"):
            return val_str[1:]
        else:
            return f"-{val_str}"

    def calculate_percentage(self, base_str: str, percent_str: str = None, operator: str = None) -> str:
        """
        Calcula porcentagem para aplicação em cálculos (ex: 50 + 10%).
        Se chamado com apenas um valor, retorna o valor dividido por 100.
        """
        if percent_str is None or operator is None:
            return self.evaluate(f"({base_str}) / 100", add_to_history=False)
        
        if operator in ('+', '-'):
            expr = f"({base_str}) {operator} (({base_str}) * ({percent_str}) / 100)"
            hist_expr = f"{base_str} {operator} {percent_str}%"
        elif operator in ('*', '×', '/', '÷'):
            py_op = '*' if operator in ('*', '×') else '/'
            expr = f"({base_str}) {py_op} (({percent_str}) / 100)"
            hist_expr = f"{base_str} {operator} {percent_str}%"
        else:
            return "Erro: Expressão malformada"
            
        res = self.evaluate(expr, add_to_history=False)
        if not res.startswith("Erro:"):
            self.add_to_history(hist_expr, res)
        return res

    def calculate_factorial(self, val_str: str) -> str:
        """Calcula x! diretamente."""
        res = self.evaluate(f"fact({val_str})", add_to_history=False)
        if not res.startswith("Erro:"):
            self.add_to_history(f"{val_str}!", res)
        return res

    # =================================================================
    # MODO PROGRAMADOR - CONVERSÃO DE BASES E OPERAÇÕES BITWISE
    # =================================================================
    def get_base_conversions(self, val_str: str, from_base: str = "DEC") -> Dict[str, str]:
        """
        Converte instantânea e simultaneamente um valor inteiro para DEC, HEX, OCT e BIN.
        Suporta entrada em qualquer uma das 4 bases ou avaliação da expressão antes de converter.
        """
        val_str = val_str.strip()
        if not val_str or val_str.startswith("Erro:"):
            return {"DEC": "0", "HEX": "0", "OCT": "0", "BIN": "0"}

        try:
            # Tenta interpretar o valor dependendo da base de origem
            if from_base.upper() == "HEX":
                clean_str = val_str.replace("0x", "").replace("0X", "")
                val_int = int(clean_str, 16)
            elif from_base.upper() == "OCT":
                clean_str = val_str.replace("0o", "").replace("0O", "")
                val_int = int(clean_str, 8)
            elif from_base.upper() == "BIN":
                clean_str = val_str.replace("0b", "").replace("0B", "")
                val_int = int(clean_str, 2)
            else:
                # Se for DEC ou expressão, avalia via AST no modo atual
                res_str = self.evaluate(val_str, add_to_history=False)
                if res_str.startswith("Erro:"):
                    return {"DEC": res_str, "HEX": res_str, "OCT": res_str, "BIN": res_str}
                # Converte float exato ou string para inteiro
                val_float = float(res_str)
                val_int = int(round(val_float))

            # Converte para as 4 bases simultaneamente
            dec_str = str(val_int)
            
            # Formatação limpa para HEX (sem '0x', em maiúsculas, com sinal para negativos)
            if val_int < 0:
                hex_str = "-" + hex(abs(val_int))[2:].upper()
                oct_str = "-" + oct(abs(val_int))[2:]
                bin_str = "-" + bin(abs(val_int))[2:]
            else:
                hex_str = hex(val_int)[2:].upper()
                oct_str = oct(val_int)[2:]
                bin_str = bin(val_int)[2:]

            return {
                "DEC": dec_str,
                "HEX": hex_str,
                "OCT": oct_str,
                "BIN": bin_str
            }
        except (ValueError, OverflowError, MathEngineError):
            err = "Erro: Domínio inválido"
            return {"DEC": err, "HEX": err, "OCT": err, "BIN": err}

    # =================================================================
    # SISTEMA DE MEMÓRIA (MC, MR, M+, M-, MS, PILHA DE MEMÓRIA)
    # =================================================================
    def memory_store(self, val_str: str) -> Optional[str]:
        """Armazena um número na memória (MS) no topo da pilha."""
        res_str = self.evaluate(val_str, add_to_history=False)
        if res_str.startswith("Erro:"):
            return None
        
        try:
            val = float(res_str)
            if val.is_integer():
                val = int(val)
            
            item = MemoryItem(
                value=val,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                formatted_str=res_str
            )
            self.memory_stack.append(item)
            return res_str
        except ValueError:
            return None

    def memory_recall(self, index: int = -1) -> str:
        """Recupera um valor da memória (MR). Por padrão, reobtém o topo da pilha."""
        if not self.memory_stack:
            return "0"
        try:
            return self.memory_stack[index].formatted_str
        except IndexError:
            return "0"

    def memory_add(self, val_str: str, index: int = -1) -> Optional[str]:
        """Adiciona o valor à memória (M+). Se a memória estiver vazia, armazena."""
        res_str = self.evaluate(val_str, add_to_history=False)
        if res_str.startswith("Erro:"):
            return None
        
        try:
            add_val = float(res_str)
            if not self.memory_stack:
                return self.memory_store(res_str)
            
            target_item = self.memory_stack[index]
            new_val = target_item.value + add_val
            if isinstance(new_val, float) and new_val.is_integer():
                new_val = int(new_val)
                
            formatted = self.format_number(new_val)
            self.memory_stack[index] = MemoryItem(
                value=new_val,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                formatted_str=formatted
            )
            return formatted
        except (ValueError, IndexError):
            return None

    def memory_subtract(self, val_str: str, index: int = -1) -> Optional[str]:
        """Subtrai o valor da memória (M-). Se a memória estiver vazia, armazena com valor negativo."""
        res_str = self.evaluate(val_str, add_to_history=False)
        if res_str.startswith("Erro:"):
            return None
        
        try:
            sub_val = float(res_str)
            if not self.memory_stack:
                return self.memory_store(f"-({res_str})")
            
            target_item = self.memory_stack[index]
            new_val = target_item.value - sub_val
            if isinstance(new_val, float) and new_val.is_integer():
                new_val = int(new_val)
                
            formatted = self.format_number(new_val)
            self.memory_stack[index] = MemoryItem(
                value=new_val,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                formatted_str=formatted
            )
            return formatted
        except (ValueError, IndexError):
            return None

    def memory_clear(self) -> None:
        """Limpa toda a pilha de memória (MC)."""
        self.memory_stack.clear()

    def memory_remove_item(self, index: int) -> bool:
        """Remove um item específico da pilha de memória pelo índice."""
        try:
            self.memory_stack.pop(index)
            return True
        except IndexError:
            return False

    def get_memory_list(self) -> List[Dict[str, str]]:
        """Retorna a lista da pilha de memória formatada para consumo em interface gráfica."""
        return [
            {
                "value": item.formatted_str,
                "timestamp": item.timestamp,
                "index": str(i)
            }
            for i, item in enumerate(self.memory_stack)
        ]

    # =================================================================
    # SISTEMA DE HISTÓRICO DE CÁLCULOS
    # =================================================================
    def add_to_history(self, expression: str, result: str) -> None:
        """Adiciona um cálculo bem-sucedido ao histórico."""
        item = CalculationHistoryItem(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            expression=expression,
            result=result,
            mode=self.mode
        )
        self.history.append(item)

    def clear_history(self) -> None:
        """Limpa o histórico de cálculos."""
        self.history.clear()

    def remove_history_item(self, index: int) -> bool:
        """Remove um item específico do histórico pelo índice."""
        try:
            self.history.pop(index)
            return True
        except IndexError:
            return False

    def recall_history_item(self, index: int) -> Optional[Tuple[str, str]]:
        """Reobtém um item do histórico na forma (expressão, resultado)."""
        try:
            item = self.history[index]
            return (item.expression, item.result)
        except IndexError:
            return None

    def get_history_list(self) -> List[Dict[str, str]]:
        """Retorna o histórico formatado para consumo na interface gráfica."""
        return [
            {
                "timestamp": item.timestamp,
                "expression": item.expression,
                "result": item.result,
                "mode": item.mode,
                "index": str(i)
            }
            for i, item in enumerate(self.history)
        ]


# =====================================================================
# BLOCO DE VALIDAÇÃO E TESTES DE UNIDADE
# =====================================================================
if __name__ == '__main__':
    import unittest

    class TestMathEngine(unittest.TestCase):
        def setUp(self):
            self.engine = MathEngine(mode="STANDARD", angle_unit="DEG")

        def test_standard_mode_basic_ops(self):
            self.assertEqual(self.engine.evaluate("2 + 3 * 4"), "14")
            self.assertEqual(self.engine.evaluate("(10 - 2) / 4"), "2")
            self.assertEqual(self.engine.evaluate("5 × 6"), "30")
            self.assertEqual(self.engine.evaluate("10 ÷ 2"), "5")
            self.assertEqual(self.engine.evaluate("3,5 + 1,5"), "5")

        def test_standard_mode_advanced_buttons(self):
            self.assertEqual(self.engine.calculate_square("12"), "144")
            self.assertEqual(self.engine.calculate_sqrt("144"), "12")
            self.assertEqual(self.engine.calculate_reciprocal("4"), "0.25")
            self.assertEqual(self.engine.toggle_sign("5"), "-5")
            self.assertEqual(self.engine.toggle_sign("-3.14"), "3.14")

        def test_percentage_ops(self):
            # 50 + 10% de 50 = 55
            self.assertEqual(self.engine.evaluate("50 + 10%"), "55")
            # 200 - 25% de 200 = 150
            self.assertEqual(self.engine.evaluate("200 - 25%"), "150")
            # 100 * 5% = 100 * 0.05 = 5
            self.assertEqual(self.engine.evaluate("100 * 5%"), "5")
            self.assertEqual(self.engine.calculate_percentage("200", "15", "+"), "230")

        def test_error_handling(self):
            self.assertEqual(self.engine.evaluate("5 / 0"), "Erro: Divisão por zero")
            self.assertEqual(self.engine.calculate_reciprocal("0"), "Erro: Divisão por zero")
            self.assertEqual(self.engine.calculate_sqrt("-4"), "Erro: Domínio inválido")
            self.assertEqual(self.engine.evaluate("2 + * 5"), "Erro: Expressão malformada")
            self.assertEqual(self.engine.evaluate("100000 ** 100000"), "Erro: Estouro numérico")

        def test_scientific_mode_trig(self):
            self.engine.set_mode("SCIENTIFIC")
            self.engine.set_angle_unit("DEG")
            self.assertEqual(self.engine.evaluate("sin(30)"), "0.5")
            self.assertEqual(self.engine.evaluate("cos(60)"), "0.5")
            self.assertEqual(self.engine.evaluate("tan(45)"), "1")
            self.assertEqual(self.engine.evaluate("asin(0.5)"), "30")
            self.assertEqual(self.engine.evaluate("tan(90)"), "Erro: Domínio inválido")
            
            # Mudando para Radianos
            self.engine.set_angle_unit("RAD")
            self.assertEqual(self.engine.evaluate("sin(pi / 2)"), "1")
            self.assertEqual(self.engine.evaluate("cos(pi)"), "-1")

        def test_scientific_mode_exp_log_fact(self):
            self.engine.set_mode("SCIENTIFIC")
            self.assertEqual(self.engine.evaluate("log10(100)"), "2")
            self.assertEqual(self.engine.evaluate("ln(e)"), "1")
            self.assertEqual(self.engine.evaluate("2 ^ 10"), "1024")
            self.assertEqual(self.engine.evaluate("root(27, 3)"), "3")
            self.assertEqual(self.engine.evaluate("5!"), "120")
            self.assertEqual(self.engine.calculate_factorial("6"), "720")
            self.assertEqual(self.engine.evaluate("(-3)!"), "Erro: Domínio inválido")
            self.assertEqual(self.engine.evaluate("10 mod 3"), "1")

        def test_programmer_mode(self):
            self.engine.set_mode("PROGRAMMER")
            # No modo programador, ^ é XOR bitwise
            self.assertEqual(self.engine.evaluate("5 ^ 3"), "6")
            self.assertEqual(self.engine.evaluate("5 XOR 3"), "6")
            self.assertEqual(self.engine.evaluate("5 AND 3"), "1")
            self.assertEqual(self.engine.evaluate("5 OR 3"), "7")
            self.assertEqual(self.engine.evaluate("~0"), "-1")
            self.assertEqual(self.engine.evaluate("1 << 4"), "16")
            self.assertEqual(self.engine.evaluate("16 >> 2"), "4")
            
            # Conversões simultâneas de bases
            convs = self.engine.get_base_conversions("255", from_base="DEC")
            self.assertEqual(convs["DEC"], "255")
            self.assertEqual(convs["HEX"], "FF")
            self.assertEqual(convs["OCT"], "377")
            self.assertEqual(convs["BIN"], "11111111")
            
            convs_hex = self.engine.get_base_conversions("FF", from_base="HEX")
            self.assertEqual(convs_hex["DEC"], "255")
            self.assertEqual(convs_hex["BIN"], "11111111")

        def test_memory_system(self):
            self.engine.memory_store("100")
            self.assertEqual(self.engine.memory_recall(), "100")
            self.engine.memory_add("50")
            self.assertEqual(self.engine.memory_recall(), "150")
            self.engine.memory_subtract("25")
            self.assertEqual(self.engine.memory_recall(), "125")
            
            mem_list = self.engine.get_memory_list()
            self.assertEqual(len(mem_list), 1)
            self.assertEqual(mem_list[0]["value"], "125")
            
            self.engine.memory_clear()
            self.assertEqual(self.engine.memory_recall(), "0")
            self.assertEqual(len(self.engine.get_memory_list()), 0)

        def test_history_system(self):
            self.engine.clear_history()
            self.engine.evaluate("10 + 20")
            self.engine.evaluate("30 * 2")
            
            hist = self.engine.get_history_list()
            self.assertEqual(len(hist), 2)
            self.assertEqual(hist[0]["expression"], "10 + 20")
            self.assertEqual(hist[0]["result"], "30")
            self.assertEqual(hist[1]["expression"], "30 * 2")
            self.assertEqual(hist[1]["result"], "60")
            
            recalled = self.engine.recall_history_item(1)
            self.assertEqual(recalled, ("30 * 2", "60"))
            
            self.engine.remove_history_item(0)
            self.assertEqual(len(self.engine.get_history_list()), 1)
            self.engine.clear_history()
            self.assertEqual(len(self.engine.get_history_list()), 0)

        def test_security_ast_whitelist(self):
            # Tentar injeção de comandos
            self.assertEqual(self.engine.evaluate("__import__('os').system('dir')"), "Erro: Expressão malformada")
            self.assertEqual(self.engine.evaluate("open('test.txt', 'w')"), "Erro: Expressão malformada")

    print("Executing MathEngine Unit Tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMathEngine)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nSUCCESS: All MathEngine tests passed with 100% functionality across all modes!")
    else:
        print("\nFAILURE: Some tests failed. Please review the output above.")
        exit(1)
