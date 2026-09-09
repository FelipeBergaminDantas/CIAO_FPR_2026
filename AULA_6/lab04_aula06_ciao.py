import os
import numpy as np
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    return [v for v in range(len(CUSTOS)) if v != no and CUSTOS[no][v] != np.inf]


def calcular_atratividade(no_atual, proximo):
    fer = feromonio[no_atual][proximo]
    custo = CUSTOS[no_atual][proximo]
    return (fer ** ALPHA) * ((1 / custo) ** BETA)


def escolher_proximo(no_atual, rota):
    vizinhos = obter_vizinhos(no_atual)
    candidatos = [v for v in vizinhos if v not in rota]
    if not candidatos:
        return None

    atratividades = [calcular_atratividade(no_atual, v) for v in candidatos]
    total = sum(atratividades)
    if total == 0:
        return random.choice(candidatos)

    probs = [a / total for a in atratividades]
    return random.choices(candidatos, weights=probs, k=1)[0]


def construir_rota():
    rota = [ORIGEM]
    atual = ORIGEM
    while atual != DESTINO:
        proximo = escolher_proximo(atual, rota)
        if proximo is None:
            return None
        rota.append(proximo)
        atual = proximo
    return rota


def calcular_custo(rota):
    return sum(CUSTOS[rota[i]][rota[i + 1]] for i in range(len(rota) - 1))


def depositar_feromonio(rota, custo):
    deposito = Q / custo
    for i in range(len(rota) - 1):
        origem = rota[i]
        destino = rota[i + 1]
        feromonio[origem][destino] += deposito


def evaporar_feromonio():
    global feromonio
    feromonio *= (1 - TAXA_EVAPORACAO)
    feromonio[CUSTOS == np.inf] = 0


def main():
    print("=" * 70)
    print("LABORATÓRIO 04 — ACO DO ZERO")
    print("=" * 70)

    melhor_rota = None
    melhor_custo = float("inf")
    historico = []

    for _ in range(NUM_ITERACOES):
        rotas = []
        for _ in range(NUM_FORMIGAS):
            rota = construir_rota()
            if rota is None:
                continue
            custo = calcular_custo(rota)
            rotas.append((rota, custo))
            if custo < melhor_custo:
                melhor_custo = custo
                melhor_rota = rota.copy()

        evaporar_feromonio()
        for rota, custo in rotas:
            depositar_feromonio(rota, custo)

        historico.append(melhor_custo)

    print("Melhor rota encontrada:", melhor_rota)
    print("Melhor custo:", melhor_custo)

    plt.figure(figsize=(10, 5))
    plt.plot(historico, linewidth=2, color='tab:blue')
    plt.xlabel("Iteração")
    plt.ylabel("Melhor custo")
    plt.title("Evolução do melhor custo ao longo das iterações")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    output_path = os.path.join(BASE_DIR, "lab04_aula06_ciao_resultado.png")
    plt.savefig(output_path, dpi=150)
    print(f"Gráfico salvo em: {output_path}")
    plt.close()

    print("\nQuestões finais:")
    print("1. O feromônio atua como memória coletiva: caminhos bons recebem mais reforço, tornando-se mais prováveis nas próximas iterações.")
    print("2. Explorar novos caminhos significa testar possibilidades diferentes; aproveitar significa seguir rotas que já mostraram desempenho promissor, reduzindo a busca aleatória.")
    print("3. Eu investigaria primeiro a taxa de evaporação e o número de formigas, porque elas controlam o equilíbrio entre experiência, exploração e eficiência em redes maiores.")


if __name__ == "__main__":
    main()
