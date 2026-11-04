# ==============================================================================
# EXERCICIO 2: Triagem de Incidentes SOC
# Objetivo: Completar a classe do problema e a definicao dos objetivos para
# o SOC Autonomo (Security Operations Center).
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


class SOCAllocationProblem(ElementwiseProblem):
    def __init__(self):
        # TODO 1: Defina 2 variaveis (x1: 1 a 50 analistas, x2: 1 a 10 regimento de seguranca)
        # TODO 2: Defina 2 objetivos a serem minimizados
        super().__init__(
            n_var=2,
            n_obj=2,
            xl=np.array([1.0, 1.0]),
            xu=np.array([50.0, 10.0])
        )

    def _evaluate(self, x, out, *args, **kwargs):
        analistas, regimento = x[0], x[1]

        # TODO 3: Implemente a formula do Custo (R$ 100 por analista + R$ 50 por regimento)
        f1_custo = (analistas * 100.0) + (regimento * 50.0)

        # TODO 4: Implemente o Tempo de Resposta em minutos (200 / analistas + 50 / regimento)
        f2_tempo = (200.0 / analistas) + (50.0 / regimento)

        out["F"] = [f1_custo, f2_tempo]


# TODO 5: Instancie o algoritmo NSGA2 com pop_size=30 e execute a minimizacao com 40 geracoes
algorithm2 = NSGA2(pop_size=30)
res2 = minimize(SOCAllocationProblem(), algorithm2, ('n_gen', 40), seed=42, verbose=False)

print("=" * 60)
print("EXERCICIO 2 - TRIAGEM DE INCIDENTES SOC")
print("=" * 60)
print(f"Solucoes nao dominadas: {len(res2.F)}")
ordem2 = np.argsort(res2.F[:, 0])
for pos, i in enumerate(ordem2, start=1):
    analistas, regimento = res2.X[i]
    custo, tempo = res2.F[i]
    print(f"  Solucao {pos:2d}: Analistas={analistas:5.2f} | Regimento={regimento:5.2f} "
          f"| Custo=R$ {custo:8.2f} | Tempo={tempo:6.2f} min")

plt.figure(figsize=(7, 4))
plt.scatter(res2.F[:, 0], res2.F[:, 1], color='darkred', s=50)
plt.title("Exercicio 2 — Fronteira de Pareto: Triagem SOC")
plt.xlabel("Custo (R$) [Minimizar]")
plt.ylabel("Tempo de Resposta (min) [Minimizar]")
plt.grid(True)
plt.tight_layout()
plt.savefig("img_exercicio02_soc.png", dpi=110)
plt.show()
