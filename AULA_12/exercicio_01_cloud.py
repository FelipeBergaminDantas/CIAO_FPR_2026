# ==============================================================================
# EXERCICIO 1: Compra de Servidores Cloud
# Objetivo: Demonstrar a Fronteira de Pareto simples com 2 objetivos opostos
# (Minimizar Custo Financeiro vs. Minimizar Latencia). Codigo pronto do roteiro,
# executado sem alteracoes na logica (so adicionei savefig).
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


class CloudProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=1, n_obj=2, xl=np.array([1.0]), xu=np.array([32.0]))

    def _evaluate(self, x, out, *args, **kwargs):
        vcpus = x[0]
        f1_custo = vcpus * 15.0         # R$ 15 por vCPU
        f2_latencia = 300.0 / vcpus     # Latencia cai com mais vCPUs
        out["F"] = [f1_custo, f2_latencia]


res1 = minimize(CloudProblem(), NSGA2(pop_size=20), termination=('n_gen', 30), seed=1)

print("=" * 60)
print("EXERCICIO 1 - FRONTEIRA DE PARETO: CLOUD")
print("=" * 60)
print(f"Solucoes nao dominadas: {len(res1.F)}")
ordem = np.argsort(res1.F[:, 0])
for pos, i in enumerate(ordem, start=1):
    vcpus = res1.X[i][0]
    custo, latencia = res1.F[i]
    print(f"  Solucao {pos:2d}: vCPUs={vcpus:5.2f} | Custo=R$ {custo:7.2f} | Latencia={latencia:6.2f} ms")

# Visualizacao
plt.figure(figsize=(7, 4))
plt.scatter(res1.F[:, 0], res1.F[:, 1], color='blue', s=50)
plt.title("Exercicio 1 — Fronteira de Pareto: Cloud")
plt.xlabel("Custo (R$) [Minimizar]")
plt.ylabel("Latencia (ms) [Minimizar]")
plt.grid(True)
plt.tight_layout()
plt.savefig("img_exercicio01_cloud.png", dpi=110)
plt.show()
