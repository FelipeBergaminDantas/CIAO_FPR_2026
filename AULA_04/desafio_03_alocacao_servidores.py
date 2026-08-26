# ============================================================
# EXERCICIO 3 (Desafio de Codigo) - Balanceamento de Carga em Servidores
#
# Cenario: 20 tarefas com tempos de processamento fixos (em segundos)
# precisam ser distribuidas entre 4 servidores.
#
# Objetivo: minimizar o MAKESPAN (o tempo do servidor mais carregado),
# ou seja, buscar a distribuicao mais equilibrada possivel.
#
# Representacao do individuo: vetor de 20 posicoes com inteiros em
# [0,3] -- indice = tarefa, valor = servidor escolhido para ela.
# (Diferente do TSP/Mochila, aqui a ORDEM do vetor nao importa para o
# resultado, so importa "quem vai pra onde". Por isso o crossover usado
# e uniforme -- gene a gene, cada filho herda de um dos pais -- em vez
# do OX usado nos problemas de permutacao.)
# ============================================================
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(7)

T = np.array([12, 35, 40, 8, 15, 22, 19, 45, 60, 31,
              14, 28, 50, 18, 25, 33, 42, 10, 5, 29])
NUM_TAREFAS = len(T)
NUM_SERVIDORES = 4

TAM_POPULACAO = 80
GERACOES = 200
TAXA_MUTACAO_GENE = 0.05  # probabilidade de UM gene (uma tarefa) mudar de servidor
TAM_TORNEIO = 3


# ============================================================
# FUNCAO DE FITNESS (MAKESPAN)
# ============================================================
def calcular_cargas(individuo):
    cargas = np.zeros(NUM_SERVIDORES)
    for tarefa, servidor in enumerate(individuo):
        cargas[servidor] += T[tarefa]
    return cargas


def calcular_makespan(individuo):
    return calcular_cargas(individuo).max()


# ============================================================
# OPERADORES GENETICOS
# ============================================================
def criar_individuo():
    return np.random.randint(0, NUM_SERVIDORES, size=NUM_TAREFAS)


def criar_populacao():
    return [criar_individuo() for _ in range(TAM_POPULACAO)]


def selecao_torneio(populacao, fitnesses, k=TAM_TORNEIO):
    participantes = np.random.choice(len(populacao), k, replace=False)
    melhor = participantes[np.argmin([fitnesses[i] for i in participantes])]
    return populacao[melhor].copy()


def crossover_uniforme(pai1, pai2):
    """Cada gene (tarefa) e herdado independentemente de um dos dois pais."""
    mascara = np.random.randint(0, 2, size=NUM_TAREFAS).astype(bool)
    filho1 = np.where(mascara, pai1, pai2)
    filho2 = np.where(mascara, pai2, pai1)
    return filho1, filho2


def mutacao(individuo):
    individuo = individuo.copy()
    for i in range(NUM_TAREFAS):
        if np.random.rand() < TAXA_MUTACAO_GENE:
            individuo[i] = np.random.randint(0, NUM_SERVIDORES)
    return individuo


# ============================================================
# HEURISTICA DE COMPARACAO: LPT (Longest Processing Time first)
# Ordena as tarefas da maior para a menor e, uma a uma, coloca
# cada tarefa no servidor que estiver com a MENOR carga no momento.
# ============================================================
def heuristica_lpt():
    ordem = np.argsort(-T)  # indices das tarefas, da maior para a menor
    cargas = np.zeros(NUM_SERVIDORES)
    individuo = np.zeros(NUM_TAREFAS, dtype=int)
    for tarefa in ordem:
        servidor = np.argmin(cargas)
        individuo[tarefa] = servidor
        cargas[servidor] += T[tarefa]
    return individuo, cargas.max()


# ============================================================
# EXECUCAO DO ALGORITMO GENETICO
# ============================================================
populacao = criar_populacao()
melhor_individuo_global = None
melhor_makespan_global = np.inf
historico_melhor = []
historico_medio = []

for geracao in range(GERACOES):
    fitnesses = [calcular_makespan(ind) for ind in populacao]

    idx_melhor = np.argmin(fitnesses)
    if fitnesses[idx_melhor] < melhor_makespan_global:
        melhor_makespan_global = fitnesses[idx_melhor]
        melhor_individuo_global = populacao[idx_melhor].copy()

    historico_melhor.append(melhor_makespan_global)
    historico_medio.append(np.mean(fitnesses))

    nova_populacao = [melhor_individuo_global.copy()]  # elitismo
    while len(nova_populacao) < TAM_POPULACAO:
        pai1 = selecao_torneio(populacao, fitnesses)
        pai2 = selecao_torneio(populacao, fitnesses)
        filho1, filho2 = crossover_uniforme(pai1, pai2)
        nova_populacao.append(mutacao(filho1))
        if len(nova_populacao) < TAM_POPULACAO:
            nova_populacao.append(mutacao(filho2))

    populacao = nova_populacao


# ============================================================
# RESULTADOS
# ============================================================
lower_bound = max(np.ceil(T.sum() / NUM_SERVIDORES), T.max())
individuo_lpt, makespan_lpt = heuristica_lpt()
cargas_ga = calcular_cargas(melhor_individuo_global)

print("=" * 60)
print("RESULTADOS - BALANCEAMENTO DE CARGA (GA)")
print("=" * 60)
print(f"Soma total dos tempos: {T.sum()} s")
print(f"Limite inferior teorico (lower bound): {lower_bound:.0f} s")
print(f"Makespan da heuristica LPT: {makespan_lpt:.0f} s")
print(f"Makespan encontrado pelo GA: {melhor_makespan_global:.0f} s")
print(f"Gap do GA em relacao ao lower bound: {melhor_makespan_global - lower_bound:.0f} s "
      f"({100*(melhor_makespan_global/lower_bound - 1):.1f}%)")
print()
print("Alocacao final (GA) -- tarefa -> servidor:")
for servidor in range(NUM_SERVIDORES):
    tarefas_do_servidor = [i for i, s in enumerate(melhor_individuo_global) if s == servidor]
    tempos = [int(T[i]) for i in tarefas_do_servidor]
    print(f"  Servidor {servidor}: tarefas {tarefas_do_servidor} | tempos {tempos} "
          f"| carga total = {int(cargas_ga[servidor])} s")

print()
print("Alocacao da heuristica LPT (para comparacao):")
cargas_lpt = calcular_cargas(individuo_lpt)
for servidor in range(NUM_SERVIDORES):
    tarefas_do_servidor = [i for i, s in enumerate(individuo_lpt) if s == servidor]
    print(f"  Servidor {servidor}: tarefas {tarefas_do_servidor} | carga total = {int(cargas_lpt[servidor])} s")

# ------------------------------------------------------------------
# Grafico de convergencia
# ------------------------------------------------------------------
plt.figure(figsize=(10, 5))
plt.plot(historico_melhor, label="Melhor makespan (GA)", linewidth=2)
plt.plot(historico_medio, label="Makespan medio da populacao", alpha=0.6)
plt.axhline(y=lower_bound, color="green", linestyle="--", label=f"Lower bound ({lower_bound:.0f}s)")
plt.axhline(y=makespan_lpt, color="red", linestyle=":", label=f"Heuristica LPT ({makespan_lpt:.0f}s)")
plt.xlabel("Geracao")
plt.ylabel("Makespan (s)")
plt.title("Convergencia do GA - Balanceamento de carga em 4 servidores")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("img_exercicio03_balanceamento.png", dpi=110)
print("\nGrafico salvo em img_exercicio03_balanceamento.png")
plt.show()
