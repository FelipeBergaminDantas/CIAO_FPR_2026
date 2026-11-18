# ==============================================================================
# EXERCICIO 2: Dimensionamento Inteiro de Cluster Kubernetes
# Objetivo: Aplicar operadores inteiros em um cluster Kubernetes onde replicas
#           de microsservicos e worker nodes nao podem ser fracionados.
# ==============================================================================
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.optimize import minimize


class KubernetesClusterProblem(ElementwiseProblem):
    def __init__(self):
        # x1: Replicas da API (2 a 40), x2: Worker Nodes (1 a 12)
        super().__init__(
            n_var=2,
            n_obj=2,
            xl=np.array([2, 1]),
            xu=np.array([40, 12]),
            vtype=int
        )

    def _evaluate(self, x, out, *args, **kwargs):
        replicas, nodes = x[0], x[1]

        # TODO 1: Calcule o Tempo de Resposta (ms): (600 / replicas) + (200 / nodes)
        f1_tempo = (600.0 / replicas) + (200.0 / nodes)

        # TODO 2: Calcule o Custo Mensal (USD): (replicas * 12) + (nodes * 85)
        f2_custo = (replicas * 12.0) + (nodes * 85.0)

        out["F"] = [f1_tempo, f2_custo]


# TODO 3: Configure o NSGA2 com pop_size=25 utilizando IntegerRandomSampling e RoundingRepair
# no crossover SBX e na mutacao PM (consulte o Exercicio 1 como referencia).
algorithm = NSGA2(
    pop_size=25,
    sampling=IntegerRandomSampling(),
    crossover=SBX(prob=0.9, eta=15, vtype=float, repair=RoundingRepair()),
    mutation=PM(prob=0.2, eta=20, vtype=float, repair=RoundingRepair()),
    eliminate_duplicates=True
)

# TODO 4: Execute a minimizacao por 35 geracoes (seed=10) e imprima as solucoes X e F.
res2 = minimize(KubernetesClusterProblem(), algorithm, termination=('n_gen', 35), seed=10)

print("=" * 60)
print("EXERCICIO 2 - CLUSTER KUBERNETES (VARIAVEIS INTEIRAS)")
print("=" * 60)
print(f"Solucoes nao dominadas: {len(res2.F)}")
ordem2 = np.argsort(res2.F[:, 0])
for pos, i in enumerate(ordem2, start=1):
    replicas, nodes = res2.X[i]
    tempo, custo = res2.F[i]
    print(f"  Solucao {pos:2d}: Replicas={replicas:2d} | Nodes={nodes:2d} "
          f"=> Tempo={tempo:6.2f} ms | Custo=US$ {custo:7.2f}/mes")

print(f"\nTodas as solucoes X sao inteiras? {np.all(res2.X == np.round(res2.X))}")
