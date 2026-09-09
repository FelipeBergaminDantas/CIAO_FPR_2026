import numpy as np
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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


def executar_aco(num_formigas=20, num_iteracoes=50, alpha=1.0, beta=2.0, taxa_evap=0.5, q=100, seed=None):
    if seed is not None:
        random.seed(seed)

    feromonio = np.ones_like(CUSTOS, dtype=float)
    feromonio[CUSTOS == np.inf] = 0

    def obter_vizinhos(no):
        return [p for p in range(len(CUSTOS)) if p != no and CUSTOS[no][p] != np.inf]

    def escolher_proximo(no_atual, visitados):
        vizinhos = obter_vizinhos(no_atual)
        candidatos = [v for v in vizinhos if v not in visitados]
        if not candidatos:
            return None

        atratividades = []
        for proximo in candidatos:
            fer = feromonio[no_atual][proximo]
            custo = CUSTOS[no_atual][proximo]
            atratividade = (fer ** alpha) * ((1 / custo) ** beta)
            atratividades.append(atratividade)

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
        deposito = q / custo
        for i in range(len(rota) - 1):
            origem = rota[i]
            destino = rota[i + 1]
            feromonio[origem][destino] += deposito

    def evaporar_feromonio():
        nonlocal feromonio
        feromonio *= (1 - taxa_evap)
        feromonio[CUSTOS == np.inf] = 0

    melhor_rota = None
    melhor_custo = float("inf")
    historico = []

    for _ in range(num_iteracoes):
        rotas = []
        for _ in range(num_formigas):
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

    return {
        "melhor_rota": melhor_rota,
        "melhor_custo": melhor_custo,
        "historico": historico,
        "num_formigas": num_formigas,
        "num_iteracoes": num_iteracoes,
        "alpha": alpha,
        "beta": beta,
        "taxa_evap": taxa_evap,
    }


def main():
    print("=" * 70)
    print("LABORATÓRIO 02 — EXPERIMENTANDO O ACO")
    print("=" * 70)

    configuracoes = [
        {"nome": "Padrao", "num_formigas": 20, "num_iteracoes": 50, "alpha": 1.0, "beta": 2.0, "taxa_evap": 0.5},
        {"nome": "ALPHA baixo", "num_formigas": 20, "num_iteracoes": 50, "alpha": 0.1, "beta": 2.0, "taxa_evap": 0.5},
        {"nome": "ALPHA alto", "num_formigas": 20, "num_iteracoes": 50, "alpha": 5.0, "beta": 2.0, "taxa_evap": 0.5},
        {"nome": "BETA baixo", "num_formigas": 20, "num_iteracoes": 50, "alpha": 1.0, "beta": 0.5, "taxa_evap": 0.5},
        {"nome": "BETA alto", "num_formigas": 20, "num_iteracoes": 50, "alpha": 1.0, "beta": 5.0, "taxa_evap": 0.5},
        {"nome": "Evaporação baixa", "num_formigas": 20, "num_iteracoes": 50, "alpha": 1.0, "beta": 2.0, "taxa_evap": 0.1},
        {"nome": "Evaporação alta", "num_formigas": 20, "num_iteracoes": 50, "alpha": 1.0, "beta": 2.0, "taxa_evap": 0.9},
        {"nome": "Poucas formigas", "num_formigas": 5, "num_iteracoes": 50, "alpha": 1.0, "beta": 2.0, "taxa_evap": 0.5},
        {"nome": "Muitas formigas", "num_formigas": 50, "num_iteracoes": 50, "alpha": 1.0, "beta": 2.0, "taxa_evap": 0.5},
    ]

    for cfg in configuracoes:
        res = executar_aco(
            num_formigas=cfg["num_formigas"],
            num_iteracoes=cfg["num_iteracoes"],
            alpha=cfg["alpha"],
            beta=cfg["beta"],
            taxa_evap=cfg["taxa_evap"],
            seed=42,
        )
        print(f"\n[{cfg['nome']}]")
        print(f"  Formigas: {res['num_formigas']}")
        print(f"  Iterações: {res['num_iteracoes']}")
        print(f"  ALPHA: {res['alpha']}")
        print(f"  BETA: {res['beta']}")
        print(f"  Taxa de evaporação: {res['taxa_evap']}")
        print(f"  Melhor rota: {res['melhor_rota']}")
        print(f"  Melhor custo: {res['melhor_custo']}")

    print("\nConclusões:")
    print("- ALPHA alto aumenta o peso do feromônio acumulado.")
    print("- BETA alto favorece caminhos de menor custo.")
    print("- Evaporação alta pode apagar memória útil cedo demais.")
    print("- Mais formigas tendem a aumentar a exploração e a qualidade da solução.")


if __name__ == "__main__":
    main()
