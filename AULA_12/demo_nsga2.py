# ==========================================================
# DEMO DA AULA (nao faz parte dos 7 exercicios do lab, mas e o
# exemplo usado na teoria para introduzir o NSGA-II -- incluido
# aqui para fundamentar as respostas das perguntas de interpretacao
# no resultados_aula12_CIAO.md).
#
# Otimizacao do custo e da latencia entre cinco servidores
# ==========================================================

# 1. Importacao das bibliotecas
import numpy as np
import matplotlib.pyplot as plt

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.optimize import minimize


# ==========================================================
# 2. DEFINICAO DO PROBLEMA DE OTIMIZACAO
# ==========================================================

class DistribuicaoCargaProblem(ElementwiseProblem):

    def __init__(self):

        super().__init__(
            n_var=4,             # Quatro variaveis de decisao
            n_obj=2,              # Dois objetivos
            n_ieq_constr=1,       # Uma restricao
            xl=np.zeros(4),       # Limite minimo: 0
            xu=np.ones(4)         # Limite maximo: 1
        )

        # Custo estimado de cada servidor
        self.custos = np.array([
            1.2, 2.5, 0.8, 3.0, 1.5
        ])

        # Latencia estimada de cada servidor
        self.latencias = np.array([
            45, 12, 80, 8, 30
        ])

    # ======================================================
    # 3. AVALIACAO DE CADA SOLUCAO
    # ======================================================

    def _evaluate(self, x, out, *args, **kwargs):

        # Os quatro primeiros servidores recebem as porcentagens definidas pelas variaveis x.
        # O quinto servidor recebe o restante da carga.
        carga_servidor_5 = max(0.0, 1.0 - np.sum(x))

        # Monta o vetor com a distribuicao dos cinco servidores.
        cargas = np.append(x, carga_servidor_5)

        # OBJETIVO 1: minimizar o custo operacional.
        custo_total = np.sum(cargas * self.custos)

        # OBJETIVO 2: minimizar a latencia media.
        latencia_media = np.sum(cargas * self.latencias)

        # RESTRICAO: a soma das quatro primeiras cargas nao pode ultrapassar 100% (1.0).
        restricao = np.sum(x) - 1.0

        # Entrega os dois objetivos ao NSGA-II.
        out["F"] = [custo_total, latencia_media]

        # Entrega a restricao ao algoritmo. No pymoo, uma restricao e satisfeita quando G <= 0.
        out["G"] = [restricao]


# 4. CRIACAO DO PROBLEMA
problem = DistribuicaoCargaProblem()

# 5. CONFIGURACAO DO ALGORITMO NSGA-II

algorithm = NSGA2(
    pop_size=200,
    sampling=FloatRandomSampling(),
    crossover=SBX(
        prob=0.9,
        eta=15
    ),
    mutation=PM(
        prob=0.1,
        eta=20
    ),
    eliminate_duplicates=True
)

# 6. EXECUCAO DA OTIMIZACAO

resultado = minimize(

    problem,
    algorithm,
    ("n_gen", 150),
    seed=42,
    verbose=False
)

# 7. APRESENTACAO DOS RESULTADOS

if resultado.X is None or resultado.F is None:
    raise RuntimeError("Nenhuma solucao viavel foi encontrada.")

# Garante que os resultados estejam organizados como matrizes.
X = np.atleast_2d(resultado.X)
F = np.atleast_2d(resultado.F)

print("      RESULTADOS DA OTIMIZACAO NSGA-II")
print(f"Solucoes nao dominadas: {len(F)}")

# Ordena as solucoes pelo custo crescente.
ordem = np.argsort(F[:, 0])

# Apresenta ate dez solucoes encontradas.
for posicao, indice in enumerate(ordem[:10], start=1):

    # Recupera os quatro valores de decisao.
    x = X[indice]

    # Calcula a carga destinada ao quinto servidor.
    carga_5 = max(0.0, 1.0 - np.sum(x))

    # Reconstroi a distribuicao completa.
    cargas = np.append(x, carga_5)

    # Converte as proporcoes para porcentagens.
    percentuais = cargas * 100

    custo, latencia = F[indice]

    print(f"\nSolucao {posicao}")
    print(f"Distribuicao: {np.round(percentuais, 1)}")
    print(f"Custo: US$ {custo:.2f}/h")
    print(f"Latencia: {latencia:.2f} ms")

# 8. VISUALIZACAO DA FRONTEIRA DE PARETO

plt.figure(figsize=(9, 6))
plt.scatter(
    F[:, 0],
    F[:, 1],
    s=35,
    label="Solucoes nao dominadas"
)

plt.xlabel("Custo estimado (US$/h)")
plt.ylabel("Latencia media (ms)")
plt.title("NSGA-II - Aproximacao da Fronteira de Pareto")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("img_demo_5_servidores.png", dpi=110)
plt.show()
