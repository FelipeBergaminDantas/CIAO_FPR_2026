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
    vizinhos = []
    for proximo in range(len(CUSTOS)):
        if proximo != no and CUSTOS[no][proximo] != np.inf:
            vizinhos.append(proximo)
    return vizinhos


def escolher_proximo(no_atual, visitados):
    vizinhos = obter_vizinhos(no_atual)
    candidatos = [v for v in vizinhos if v not in visitados]
    if not candidatos:
        return None

    atratividades = []
    for proximo in candidatos:
        fer = feromonio[no_atual][proximo]
        custo = CUSTOS[no_atual][proximo]
        atratividade = (fer ** ALPHA) * ((1 / custo) ** BETA)
        atratividades.append(atratividade)

    total = sum(atratividades)
    if total == 0:
        return random.choice(candidatos)

    probabilidades = [a / total for a in atratividades]
    return random.choices(candidatos, weights=probabilidades, k=1)[0]


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
    total = 0
    for i in range(len(rota) - 1):
        total += CUSTOS[rota[i]][rota[i + 1]]
    return total


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
    print("=" * 60)
    print("LABORATÓRIO 01 — ACO")
    print("=" * 60)
    print("Matriz inicial de feromônio:")
    print(feromonio)
    print("\nVizinhos do nó 0:", obter_vizinhos(0))
    print("Vizinhos do nó 2:", obter_vizinhos(2))

    for i in range(5):
        rota = construir_rota()
        print(f"Formiga {i + 1}: {rota}")

    rota_teste = construir_rota()
    if rota_teste is not None:
        print(f"\nRota de teste: {rota_teste}")
        print(f"Custo da rota: {calcular_custo(rota_teste)}")

    melhor_rota = None
    melhor_custo = float("inf")
    historico = []

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

        historico.append(melhor_custo)

    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print("Melhor rota encontrada:", melhor_rota)
    print("Melhor custo:", melhor_custo)

    plt.figure(figsize=(10, 5))
    plt.plot(historico, linewidth=2)
    plt.xlabel("Iteração")
    plt.ylabel("Melhor custo")
    plt.title("Convergência do ACO")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    output_path = os.path.join(BASE_DIR, "lab01_aula06_ciao_resultado.png")
    plt.savefig(output_path, dpi=150)
    print(f"Gráfico salvo em: {output_path}")
    plt.close()


if __name__ == "__main__":
    main()
