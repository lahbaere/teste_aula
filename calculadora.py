import ast
import operator
import re
import tkinter as tk
from tkinter import messagebox


# CORES DA CALCULADORA
cor_fundo = "#202124"
cor_visor = "#303134"
cor_numeros = "#3c4043"
cor_operacoes = "#f29900"
cor_especiais = "#5f6368"
cor_texto = "#ffffff"


# CRIAR A JANELA
janela = tk.Tk()
janela.title("Minha Calculadora")
janela.geometry("350x500")
janela.resizable(False, False)
janela.configure(bg=cor_fundo)

# Guardar o que aparece no visor
texto_visor = tk.StringVar()


# FUNÇÕES DA CALCULADORA

def adicionar_ao_visor(valor):
    """Adiciona um número ou operador ao visor."""
    texto_atual = texto_visor.get()
    texto_visor.set(texto_atual + valor)


def limpar_visor():
    """Apaga toda a expressão."""
    texto_visor.set("")


def apagar_ultimo():
    """Apaga somente o último caractere."""
    texto_atual = texto_visor.get()
    texto_visor.set(texto_atual[:-1])


def alternar_sinal():
    """Troca o sinal do último número."""
    expressao = texto_visor.get()

    # Encontrar o último número da expressão
    resultado = re.search(r"\d+(?:\.\d*)?$", expressao)

    if resultado:
        inicio = resultado.start()
        fim = resultado.end()
        numero = expressao[inicio:fim]

        # Verificar se o número já possui sinal negativo
        if inicio > 0 and expressao[inicio - 1] == "-":
            antes_do_sinal = expressao[:inicio - 1]

            # O sinal é negativo quando está no começo
            # ou depois de outro operador
            if (
                antes_do_sinal == ""
                or antes_do_sinal[-1] in "+-*/("
            ):
                expressao = (
                    antes_do_sinal + numero
                    + expressao[fim:]
                )
            else:
                expressao = (
                    expressao[:inicio] + "-" + numero
                    + expressao[fim:]
                )
        else:
            expressao = (
                expressao[:inicio] + "-" + numero
                + expressao[fim:]
            )

        texto_visor.set(expressao)


def inserir_decimal():
    """Insere um ponto decimal no número atual."""
    expressao = texto_visor.get()

    # Separar a expressão pelo último operador
    partes = re.split(r"[+\-×÷]", expressao)
    numero_atual = partes[-1]

    # Só permite um ponto por número
    if "." not in numero_atual:
        if numero_atual == "":
            expressao += "0."
        else:
            expressao += "."

        texto_visor.set(expressao)


def resolver_conta(no):
    """Calcula somente operações matemáticas permitidas."""

    # Números
    if isinstance(no, ast.Constant):
        if type(no.value) in (int, float):
            return no.value
        raise ValueError("Valor inválido")

    # Operações matemáticas permitidas
    operacoes = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    # Contas como 2 + 3 ou 8 / 4
    if isinstance(no, ast.BinOp):
        tipo_operacao = type(no.op)

        if tipo_operacao not in operacoes:
            raise ValueError("Operação não permitida")

        esquerda = resolver_conta(no.left)
        direita = resolver_conta(no.right)

        return operacoes[tipo_operacao](esquerda, direita)

    # Permitir números positivos e negativos
    if isinstance(no, ast.UnaryOp):
        numero = resolver_conta(no.operand)

        if isinstance(no.op, ast.UAdd):
            return numero

        if isinstance(no.op, ast.USub):
            return -numero

    raise ValueError("Expressão inválida")


def calcular():
    """Realiza o cálculo e mostra o resultado."""
    expressao = texto_visor.get()

    if not expressao:
        return

    try:
        # Trocar os símbolos visuais pelos símbolos do Python
        expressao = expressao.replace("×", "*")
        expressao = expressao.replace("÷", "/")

        # Transformar porcentagens simples em divisões por 100
        expressao = re.sub(
            r"(\d+(?:\.\d+)?)%",
            r"(\1/100)",
            expressao
        )

        # Interpretar a expressão sem executar comandos arbitrários
        arvore = ast.parse(expressao, mode="eval")
        resultado = resolver_conta(arvore.body)

        # Evitar mostrar .0 em resultados inteiros
        if isinstance(resultado, float) and resultado.is_integer():
            resultado = int(resultado)

        texto_visor.set(str(resultado))

    except ZeroDivisionError:
        messagebox.showerror(
            "Erro",
            "Não é possível dividir por zero."
        )

    except (ValueError, SyntaxError, TypeError):
        messagebox.showerror(
            "Erro",
            "Digite uma conta válida."
        )


# CRIAR O VISOR
visor = tk.Entry(
    janela,
    textvariable=texto_visor,
    font=("Arial", 24),
    bg=cor_visor,
    fg=cor_texto,
    justify="right",
    state="readonly",
    readonlybackground=cor_visor,
    insertbackground=cor_texto,
    borderwidth=0
)
visor.grid(
    row=0,
    column=0,
    columnspan=4,
    padx=10,
    pady=20,
    ipady=20,
    sticky="nsew"
)


# ORGANIZAR OS BOTÕES
botoes = [
    ("C", limpar_visor, cor_especiais),
    ("⌫", apagar_ultimo, cor_especiais),
    ("%", lambda: adicionar_ao_visor("%"), cor_especiais),
    ("÷", lambda: adicionar_ao_visor("÷"), cor_operacoes),

    ("7", lambda: adicionar_ao_visor("7"), cor_numeros),
    ("8", lambda: adicionar_ao_visor("8"), cor_numeros),
    ("9", lambda: adicionar_ao_visor("9"), cor_numeros),
    ("×", lambda: adicionar_ao_visor("×"), cor_operacoes),

    ("4", lambda: adicionar_ao_visor("4"), cor_numeros),
    ("5", lambda: adicionar_ao_visor("5"), cor_numeros),
    ("6", lambda: adicionar_ao_visor("6"), cor_numeros),
    ("-", lambda: adicionar_ao_visor("-"), cor_operacoes),

    ("1", lambda: adicionar_ao_visor("1"), cor_numeros),
    ("2", lambda: adicionar_ao_visor("2"), cor_numeros),
    ("3", lambda: adicionar_ao_visor("3"), cor_numeros),
    ("+", lambda: adicionar_ao_visor("+"), cor_operacoes),

    ("+/-", alternar_sinal, cor_especiais),
    ("0", lambda: adicionar_ao_visor("0"), cor_numeros),
    (".", inserir_decimal, cor_numeros),
    ("=", calcular, cor_operacoes),
]


# Posicionar os botões na janela
for indice, botao in enumerate(botoes):
    texto, funcao, cor = botao

    linha = (indice // 4) + 1
    coluna = indice % 4

    tk.Button(
        janela,
        text=texto,
        command=funcao,
        font=("Arial", 16, "bold"),
        bg=cor,
        fg=cor_texto,
        activebackground=cor,
        activeforeground=cor_texto,
        borderwidth=0
    ).grid(
        row=linha,
        column=coluna,
        padx=4,
        pady=4,
        sticky="nsew",
        ipadx=5,
        ipady=12
    )


# Ajustar o tamanho das linhas e colunas
for coluna in range(4):
    janela.columnconfigure(coluna, weight=1)

for linha in range(1, 6):
    janela.rowconfigure(linha, weight=1)


# INICIAR A CALCULADORA
janela.mainloop()
