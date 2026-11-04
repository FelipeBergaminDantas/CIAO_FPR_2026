# ==============================================================================
# EXERCICIO 3: Logistica de Drones
# Objetivo: Otimizacao com 3 Objetivos (Custo, Tempo de Entrega e Pegada de
# Carbono). Codigo pronto do roteiro, executado sem alteracoes na logica.
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (necessario para projection="3d")


class DroneProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=2, n_obj=3, xl=np.array([10.0, 1.0]), xu=np.array([80.0, 5.0]))

    def _evaluate(self, x, out, *args, **kwargs):
        velocidade, carga = x[0], x[1]
        f1_tempo = 1000.0 / velocidade
        f2_custo = (velocidade ** 2) * 0.1 + (carga * 50)
        f3_co2 = (velocidade * 1.5) / carga
        out["F"] = [f1_tempo, f2_custo, f3_co2]


res3 = minimize(DroneProblem(), NSGA2(pop_size=40), termination=('n_gen', 50), seed=42)

print("=" * 60)
print("EXERCICIO 3 - LOGISTICA DE DRONES (3 OBJETIVOS)")
print("=" * 60)
print(f"Solucoes nao dominadas: {len(res3.F)}")
ordem3 = np.argsort(res3.F[:, 0])
for pos, i in enumerate(ordem3[:10], start=1):
    vel, carga = res3.X[i]
    tempo, custo, co2 = res3.F[i]
    print(f"  Solucao {pos:2d}: Vel={vel:5.1f} m/s | Carga={carga:4.2f} kg "
          f"| Tempo={tempo:6.2f} min | Custo=R$ {custo:7.2f} | CO2={co2:5.2f}")

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(res3.F[:, 0], res3.F[:, 1], res3.F[:, 2], color='green', s=40)
ax.set_xlabel("Tempo")
ax.set_ylabel("Custo")
ax.set_zlabel("CO2")
plt.title("Exercicio 3 — Pareto 3D: Drones")
plt.tight_layout()
plt.savefig("img_exercicio03_drones.png", dpi=110)
plt.show()
