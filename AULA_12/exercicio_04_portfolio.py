# ==============================================================================
# EXERCICIO 4: Selecao de Portfolio de Investimentos
# Objetivo: Implementar restricao de investimento e objetivos de Risco vs.
# Retorno.
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


class PortfolioProblem(ElementwiseProblem):
    def __init__(self):
        # x1: % Renda Fixa (0 a 100), x2: % Acoes (0 a 100)
        super().__init__(n_var=2, n_obj=2, xl=np.array([0.0, 0.0]), xu=np.array([100.0, 100.0]))

    def _evaluate(self, x, out, *args, **kwargs):
        rf, acoes = x[0], x[1]

        # TODO 1: O Retorno Esperado e (rf * 0.08 + acoes * 0.18).
        # Como o pymoo MINIMIZA por padrao, inverta o sinal do retorno para maximiza-lo!
        f1_retorno_negativo = -(rf * 0.08 + acoes * 0.18)

        # TODO 2: O Risco e dado por (rf * 0.02 + acoes * 0.25). Queremos MINIMIZAR o risco.
        f2_risco = rf * 0.02 + acoes * 0.25

        out["F"] = [f1_retorno_negativo, f2_risco]


# TODO 3: Execute o NSGA-II e plote o Risco (eixo X) versus Retorno Real (eixo Y - lembre de reverter o sinal!)
res4 = minimize(PortfolioProblem(), NSGA2(pop_size=30), termination=('n_gen', 40), seed=42, verbose=False)

print("=" * 60)
print("EXERCICIO 4 - PORTFOLIO DE INVESTIMENTOS (RISCO x RETORNO)")
print("=" * 60)
print(f"Solucoes nao dominadas: {len(res4.F)}")

retorno_real = -res4.F[:, 0]
risco = res4.F[:, 1]
ordem4 = np.argsort(risco)
for pos, i in enumerate(ordem4, start=1):
    rf, acoes = res4.X[i]
    print(f"  Solucao {pos:2d}: RendaFixa={rf:5.1f}% | Acoes={acoes:5.1f}% "
          f"| Retorno={retorno_real[i]:6.2f}% | Risco={risco[i]:6.2f}")

plt.figure(figsize=(7, 5))
plt.scatter(risco, retorno_real, color='teal', s=50)
plt.title("Exercicio 4 — Fronteira de Pareto: Risco x Retorno")
plt.xlabel("Risco [Minimizar]")
plt.ylabel("Retorno Esperado (%) [Maximizar]")
plt.grid(True)
plt.tight_layout()
plt.savefig("img_exercicio04_portfolio.png", dpi=110)
plt.show()
