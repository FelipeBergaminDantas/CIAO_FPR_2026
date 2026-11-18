# ==============================================================================
# EXERCICIO 3: Operadores Geneticos (Exploracao vs. Explotacao)
# Objetivo: Comparar visualmente duas configuracoes do NSGA-II: alta mutacao/baixa
#           pressao (exploracao ampla) vs. baixa mutacao/alta pressao (convergencia).
# Codigo pronto do roteiro, executado sem alteracoes na logica.
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.optimize import minimize


class BenchmarkTradeoffProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=2, n_obj=2, xl=np.array([0.1, 0.1]), xu=np.array([10.0, 10.0]))

    def _evaluate(self, x, out, *args, **kwargs):
        f1 = x[0]**2 + x[1]
        f2 = (10.0 / x[0]) + (5.0 / x[1])
        out["F"] = [f1, f2]


problem = BenchmarkTradeoffProblem()

# Configuracao A: Exploracao agressiva (eta baixo = filhos distantes dos pais)
alg_exploracao = NSGA2(
    pop_size=30,
    crossover=SBX(prob=0.9, eta=5),
    mutation=PM(prob=0.5, eta=5)
)

# Configuracao B: Explotacao refinada (eta alto = filhos muito proximos dos pais)
alg_explotacao = NSGA2(
    pop_size=30,
    crossover=SBX(prob=0.9, eta=30),
    mutation=PM(prob=0.05, eta=30)
)

res_a = minimize(problem, alg_exploracao, ('n_gen', 20), seed=42)
res_b = minimize(problem, alg_explotacao, ('n_gen', 20), seed=42)

print("=" * 60)
print("EXERCICIO 3 - EXPLORACAO vs. EXPLOTACAO")
print("=" * 60)
print(f"Config A (exploracao, eta=5):  {len(res_a.F)} solucoes nao dominadas")
print(f"Config B (explotacao, eta=30): {len(res_b.F)} solucoes nao dominadas")
print(f"Amplitude Obj.1 - Config A: {res_a.F[:, 0].max() - res_a.F[:, 0].min():.2f}")
print(f"Amplitude Obj.1 - Config B: {res_b.F[:, 0].max() - res_b.F[:, 0].min():.2f}")

plt.figure(figsize=(8, 5))
plt.scatter(res_a.F[:, 0], res_a.F[:, 1], color='orange', label='Config A: Alta Exploracao (eta=5)', alpha=0.8, s=60)
plt.scatter(res_b.F[:, 0], res_b.F[:, 1], color='navy', marker='x', label='Config B: Alta Explotacao (eta=30)', s=60)
plt.title("Exercicio 3 - Efeito dos Parametros SBX/PM em 20 Geracoes")
plt.xlabel("Objetivo 1 [Minimizar]")
plt.ylabel("Objetivo 2 [Minimizar]")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("img_exercicio03_exploracao_explotacao.png", dpi=110)
plt.show()
