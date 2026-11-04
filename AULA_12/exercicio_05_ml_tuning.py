# ==============================================================================
# EXERCICIO 5: Trade-off de Modelos de Machine Learning
# Objetivo: Escolha de hiperparametros minimizando o Erro de Predicao e a
# Complexidade (Tempo de Inferencia). Codigo pronto do roteiro, executado sem
# alteracoes na logica.
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


class MLTuningProblem(ElementwiseProblem):
    def __init__(self):
        # x1: Profundidade da Arvore (1 a 30), x2: Numero de Estimadores (10 a 200)
        super().__init__(n_var=2, n_obj=2, xl=np.array([1.0, 10.0]), xu=np.array([30.0, 200.0]))

    def _evaluate(self, x, out, *args, **kwargs):
        depth, n_trees = x[0], x[1]
        f1_erro = 0.5 / (depth * np.log10(n_trees))   # Erro cai com mais arvores/profundidade
        f2_latencia_ms = (depth * 0.2) + (n_trees * 0.5)  # Latencia sobe
        out["F"] = [f1_erro, f2_latencia_ms]


res5 = minimize(MLTuningProblem(), NSGA2(pop_size=30), termination=('n_gen', 40), seed=7)

print("=" * 60)
print("EXERCICIO 5 - TRADE-OFF ERRO x LATENCIA (ML)")
print("=" * 60)
print(f"Solucoes nao dominadas: {len(res5.F)}")
ordem5 = np.argsort(res5.F[:, 0])
for pos, i in enumerate(ordem5, start=1):
    depth, n_trees = res5.X[i]
    erro, latencia = res5.F[i]
    print(f"  Solucao {pos:2d}: Profundidade={depth:5.2f} | Estimadores={n_trees:6.2f} "
          f"| Erro={erro:.4f} | Latencia={latencia:6.2f} ms")

plt.figure(figsize=(7, 4))
plt.scatter(res5.F[:, 0], res5.F[:, 1], color='purple', s=45)
plt.title("Exercicio 5 — Erro vs. Tempo de Inferencia (ML)")
plt.xlabel("Erro do Modelo [Minimizar]")
plt.ylabel("Tempo de Resposta (ms) [Minimizar]")
plt.grid(True)
plt.tight_layout()
plt.savefig("img_exercicio05_ml.png", dpi=110)
plt.show()
