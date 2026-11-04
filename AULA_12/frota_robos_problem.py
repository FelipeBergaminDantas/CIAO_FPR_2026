# ==============================================================================
# EXERCICIO 7: Dimensionamento de Frota de Robos de Logistica
# Objetivo: Projetar e implementar do zero uma classe de Otimizacao
# Multiobjetivo usando pymoo para resolver um problema real de automacao
# industrial (dimensionamento de AMRs em um galpao de triagem).
#
# Variaveis de decisao:
#   x1 - numero de robos na frota, continuo em [5, 50]
#   x2 - velocidade media de operacao (m/s), continua em [1.0, 4.0]
#
# Objetivos a minimizar:
#   f1 (custo, R$ mil)      = x1*25.0 + x2^2*8.0
#   f2 (tempo de ciclo, min) = 120.0/x1 + 40.0/x2
#
# Restricao (consumo energetico/bateria):
#   C(x1,x2) = x1 * x2^1.5  <= 120.0   =>   g1 = x1*x2^1.5 - 120.0 <= 0
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


class FrotaRobosProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=1,
            xl=np.array([5.0, 1.0]),
            xu=np.array([50.0, 4.0]),
        )

    def _evaluate(self, x, out, *args, **kwargs):
        n_robos, velocidade = x[0], x[1]

        f1_custo = (n_robos * 25.0) + (velocidade ** 2) * 8.0
        f2_tempo_ciclo = (120.0 / n_robos) + (40.0 / velocidade)

        consumo_energetico = n_robos * (velocidade ** 1.5)
        g1 = consumo_energetico - 120.0

        out["F"] = [f1_custo, f2_tempo_ciclo]
        out["G"] = [g1]


def escolher_solucao_intermediaria(F):
    """
    Normaliza os dois objetivos para [0,1] e escolhe o 'ponto de joelho'
    (knee point): a solucao mais proxima do canto ideal (0,0), que
    representa o melhor compromisso simultaneo entre os dois objetivos.
    """
    f_min = F.min(axis=0)
    f_max = F.max(axis=0)
    F_norm = (F - f_min) / (f_max - f_min)
    distancias = np.sqrt((F_norm ** 2).sum(axis=1))
    return int(np.argmin(distancias))


def main():
    problema = FrotaRobosProblem()
    algoritmo = NSGA2(pop_size=40)

    resultado = minimize(
        problema,
        algoritmo,
        ("n_gen", 60),
        seed=42,
        verbose=False,
    )

    if resultado.X is None or resultado.F is None:
        raise RuntimeError("Nenhuma solucao viavel foi encontrada.")

    X = np.atleast_2d(resultado.X)
    F = np.atleast_2d(resultado.F)

    print("=" * 70)
    print("EXERCICIO 7 — DIMENSIONAMENTO DE FROTA DE ROBOS (AMRs)")
    print("=" * 70)
    print(f"Solucoes nao dominadas encontradas: {len(F)}")

    idx_menor_custo = int(np.argmin(F[:, 0]))
    idx_menor_tempo = int(np.argmin(F[:, 1]))
    idx_intermediaria = escolher_solucao_intermediaria(F)

    def imprimir_solucao(titulo, idx):
        n_robos, vel = X[idx]
        custo, tempo = F[idx]
        consumo = n_robos * (vel ** 1.5)
        print(f"\n{titulo}")
        print(f"  Robos: {n_robos:.2f} | Velocidade: {vel:.2f} m/s")
        print(f"  Custo: R$ {custo:.2f} mil | Tempo de ciclo: {tempo:.2f} min")
        print(f"  Consumo energetico: {consumo:.2f} (limite: 120.0)")

    imprimir_solucao("[1] MENOR CUSTO", idx_menor_custo)
    imprimir_solucao("[2] MENOR TEMPO DE CICLO", idx_menor_tempo)
    imprimir_solucao("[3] SOLUCAO INTERMEDIARIA (knee point)", idx_intermediaria)

    # ---------------------------------------------------------------
    # Grafico da Fronteira de Pareto, destacando as 3 solucoes escolhidas
    # ---------------------------------------------------------------
    plt.figure(figsize=(8, 6))
    plt.scatter(F[:, 0], F[:, 1], s=40, color="steelblue", label="Solucoes nao dominadas")
    plt.scatter(*F[idx_menor_custo], s=150, color="green", marker="*", label="Menor custo", zorder=5)
    plt.scatter(*F[idx_menor_tempo], s=150, color="red", marker="*", label="Menor tempo de ciclo", zorder=5)
    plt.scatter(*F[idx_intermediaria], s=150, color="orange", marker="*", label="Solucao intermediaria", zorder=5)
    plt.xlabel("Custo (R$ mil) [Minimizar]")
    plt.ylabel("Tempo de Ciclo (min) [Minimizar]")
    plt.title("Exercicio 7 — Fronteira de Pareto: Frota de Robos de Logistica")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("img_exercicio07_frota_robos.png", dpi=110)
    plt.show()


if __name__ == "__main__":
    main()
