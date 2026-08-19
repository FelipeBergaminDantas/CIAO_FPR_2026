# ============================================================
# ATIVIDADE 4 - Modelagem de um Problema Real
# Problema escolhido: Grade de materias do proximo semestre
# Objetivo: escolher quais materias cursar, respeitando pre-requisitos
# e a carga horaria maxima, maximizando a prioridade/interesse total.
# ============================================================
import random

# ----------------------------------------------------------
# 1. DEFINICAO DO PROBLEMA (dados de entrada)
# ----------------------------------------------------------
# Cada materia candidata tem: nome, carga horaria semanal, prioridade
# (o quanto o aluno quer/precisa cursar essa materia, de 1 a 10)
# e um pre-requisito (None se nao tiver).
materias = [
    {"nome": "Estrutura de Dados II",   "horas": 4, "prioridade": 9,  "pre_requisito": "Estrutura de Dados I"},
    {"nome": "Banco de Dados",          "horas": 4, "prioridade": 8,  "pre_requisito": None},
    {"nome": "Redes de Computadores",   "horas": 4, "prioridade": 6,  "pre_requisito": None},
    {"nome": "Inteligencia Artificial", "horas": 4, "prioridade": 10, "pre_requisito": "Estrutura de Dados I"},
    {"nome": "Calculo III",             "horas": 6, "prioridade": 5,  "pre_requisito": "Calculo II"},
    {"nome": "Eletronica Digital",      "horas": 4, "prioridade": 7,  "pre_requisito": None},
    {"nome": "Engenharia de Software",  "horas": 4, "prioridade": 8,  "pre_requisito": "Programacao II"},
    {"nome": "Sistemas Operacionais",   "horas": 4, "prioridade": 7,  "pre_requisito": "Estrutura de Dados I"},
    {"nome": "Estatistica Aplicada",    "horas": 3, "prioridade": 6,  "pre_requisito": None},
    {"nome": "Compiladores",            "horas": 4, "prioridade": 5,  "pre_requisito": "Estrutura de Dados II"},
]
n = len(materias)

# Materias que o aluno ja concluiu em semestres anteriores
concluidas = {"Estrutura de Dados I", "Calculo II", "Programacao II"}

# Carga horaria maxima que o aluno pode cursar por semana
capacidade_horas = 20

# ----------------------------------------------------------
# 2. REPRESENTACAO DA SOLUCAO
# ----------------------------------------------------------
# Uma solucao candidata e uma tupla/lista binaria de tamanho n,
# onde solucao[i] = 1 significa "vou cursar a materia i" e
# solucao[i] = 0 significa "nao vou cursar".
# Exemplo: (1, 0, 0, 1, 0, 0, 0, 0, 1, 0) = cursar as materias 0, 3 e 8.
def gera_solucao_aleatoria():
    """Gera uma solucao candidata aleatoria (pode ser factivel ou nao)."""
    return tuple(random.choice([0, 1]) for _ in range(n))

# ----------------------------------------------------------
# 3. FUNCAO OBJETIVO
# ----------------------------------------------------------
# Queremos MAXIMIZAR a soma das prioridades das materias escolhidas.
def calcula_objetivo(solucao):
    """Calcula o valor (soma de prioridades) de uma solucao."""
    return sum(materias[i]["prioridade"] for i in range(n) if solucao[i] == 1)

# ----------------------------------------------------------
# 4. RESTRICOES
# ----------------------------------------------------------
# Uma solucao so e valida (factivel) se:
#   a) a carga horaria total das materias escolhidas nao ultrapassar
#      a capacidade_horas do aluno; e
#   b) toda materia escolhida que tiver pre-requisito so pode ser
#      escolhida se o pre-requisito ja estiver em "concluidas".
def verifica_restricoes(solucao):
    """Retorna (True, 'ok') se a solucao for factivel, ou (False, motivo) caso contrario."""
    horas_totais = sum(materias[i]["horas"] for i in range(n) if solucao[i] == 1)
    if horas_totais > capacidade_horas:
        return False, f"carga horaria excedida ({horas_totais}h > {capacidade_horas}h)"

    for i in range(n):
        if solucao[i] == 1:
            pre = materias[i]["pre_requisito"]
            if pre is not None and pre not in concluidas:
                return False, f"pre-requisito nao cumprido: {materias[i]['nome']} exige {pre}"

    return True, "ok"

# ----------------------------------------------------------
# 5. DEMONSTRACAO
# ----------------------------------------------------------
def mostra_solucao(solucao):
    escolhidas = [materias[i]["nome"] for i in range(n) if solucao[i] == 1]
    horas = sum(materias[i]["horas"] for i in range(n) if solucao[i] == 1)
    valor = calcula_objetivo(solucao)
    factivel, motivo = verifica_restricoes(solucao)

    print("Materias escolhidas:", escolhidas if escolhidas else "(nenhuma)")
    print(f"Carga horaria total: {horas}h (limite: {capacidade_horas}h)")
    print(f"Valor da funcao objetivo (soma de prioridades): {valor}")
    print(f"Factivel? {factivel} ({motivo})")


if __name__ == "__main__":
    random.seed(42)

    print("=" * 60)
    print("Espaco de busca: 2^%d = %d solucoes candidatas possiveis" % (n, 2 ** n))
    print("=" * 60)

    print("\n>>> Uma solucao aleatoria:")
    solucao = gera_solucao_aleatoria()
    print("Vetor binario:", solucao)
    mostra_solucao(solucao)

    print("\n>>> Mais algumas solucoes aleatorias (para ilustrar a variedade):")
    for k in range(5):
        s = gera_solucao_aleatoria()
        valor = calcula_objetivo(s)
        factivel, motivo = verifica_restricoes(s)
        status = "FACTIVEL" if factivel else f"INFACTIVEL ({motivo})"
        print(f"  Tentativa {k+1}: valor={valor:2d} | {status}")
