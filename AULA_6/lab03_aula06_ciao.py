import numpy as np
import random

CUSTOS = np.array([
    [0, 2, 4, np.inf, np.inf, np.inf],
    [2, 0, 1, 5, np.inf, np.inf],
    [4, 1, 0, 2, 3, np.inf],
    [np.inf, 5, 2, 0, 1, 4],
    [np.inf, np.inf, 3, 1, 0, 2],
    [np.inf, np.inf, np.inf, 4, 2, 0]
])

ORIGEM = 0
DESTINO = 5
NUM_FORMIGAS = 20
NUM_ITERACOES = 50
ALPHA = 1.0
BETA = 2.0
TAXA_EVAPORACAO = 0.5
Q = 100

feromonio = np.ones_like(CUSTOS, dtype=float)
feromonio[CUSTOS == np.inf] = 0


def obter_vizinhos(no):
    vizinhos = []
    for proximo in range(len(CUSTOS)):
        if proximo != no and CUSTOS[no][proximo] != np.inf:
            vizinhos.append(proximo)
    return vizinhos


def calcular_atratividade(no_atual, proximo):
    fer = feromonio[no_atual][proximo]
    custo = CUSTOS[no_atual][proximo]
    return (fer ** ALPHA) * ((1 / custo) ** BETA)


def evaporar_feromonio():
    global feromonio
    feromonio *= (1 - TAXA_EVAPORACAO)
    feromonio[CUSTOS == np.inf] = 0


def depositar_feromonio(rota, custo):
    deposito = Q / custo
    for i in range(len(rota) - 1):
        origem = rota[i]
        destino = rota[i + 1]
        feromonio[origem][destino] += deposito


def construir_rota():
    rota = [ORIGEM]
    atual = ORIGEM

    while atual != DESTINO:
        vizinhos = obter_vizinhos(atual)
        candidatos = [no for no in vizinhos if no not in rota]

        if not candidatos:
            return None

        atratividades = [calcular_atratividade(atual, no) for no in candidatos]
        total = sum(atratividades)
        if total == 0:
            proximo = random.choice(candidatos)
        else:
            probs = [a / total for a in atratividades]
            proximo = random.choices(candidatos, weights=probs, k=1)[0]

        rota.append(proximo)
        atual = proximo

    return rota


def calcular_custo(rota):
    total = 0
    for i in range(len(rota) - 1):
        total += CUSTOS[rota[i]][rota[i + 1]]
    return total


def main():
    print("=" * 60)
    print("LABORATÓRIO 03 — COMPLETANDO O ACO")
    print("=" * 60)

    melhor_rota = None
    melhor_custo = float("inf")

    for _ in range(NUM_ITERACOES):
        rotas = []
        for _ in range(NUM_FORMIGAS):
            rota = construir_rota()
            if rota is not None:
                custo = calcular_custo(rota)
                rotas.append((rota, custo))
                if custo < melhor_custo:
                    melhor_custo = custo
                    melhor_rota = rota.copy()

        evaporar_feromonio()
        for rota, custo in rotas:
            depositar_feromonio(rota, custo)

    print("Melhor rota:", melhor_rota)
    print("Melhor custo:", melhor_custo)

    print("\nRespostas:")
    print("1. A fórmula usa 1 / custo porque caminhos de menor custo devem ser mais atraentes; usar o custo direto faria o algoritmo favorecer rotas caras.")
    print("2. Quanto mais feromônio uma rota recebe, maior a sua atratividade, pois a probabilidade de ser escolhida cresce na etapa de decisão.")
    print("3. A formiga não pode visitar novamente um nó porque o problema é de caminho simples em um grafo, e ciclos repetidos aumentam custo e podem bloquear a chegada ao destino.")


if __name__ == "__main__":
    main()
