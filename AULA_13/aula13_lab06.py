# ==============================================================================
# EXERCICIO 6: Pipeline Completo - Otimizacao + Restricao + MCDM
# Objetivo: Integrar Variaveis Inteiras, Restricao de Desigualdade e Tomada de
#           Decisao MCDM em um sistema de escala hospitalar.
# ==============================================================================
import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.optimize import minimize
from pymoo.mcdm.pseudo_weights import PseudoWeights


class EscalaHospitalarProblem(ElementwiseProblem):
    def __init__(self):
        # x1: Medicos Plantonistas (2 a 20), x2: Enfermeiros (4 a 40)
        # TODO 1: Configure 2 variaveis inteiras, 2 objetivos e 1 restricao de desigualdade
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=1,
            xl=np.array([2, 4]),
            xu=np.array([20, 40]),
            vtype=int
        )

    def _evaluate(self, x, out, *args, **kwargs):
        medicos, enfermeiros = x[0], x[1]

        # Objetivo 1: Custo do Plantao (R$)
        f1_custo = (medicos * 1200.0) + (enfermeiros * 450.0)

        # Objetivo 2: Tempo Medio de Espera na Triagem (minutos)
        f2_espera = (180.0 / medicos) + (240.0 / enfermeiros)

        # TODO 2: Restricao de SLA Hospitalar: O tempo de espera (f2_espera) NAO PODE passar de 25 minutos.
        # Lembre-se do formato G(x) <= 0:
        g1 = f2_espera - 25.0

        out["F"] = [f1_custo, f2_espera]
        out["G"] = [g1]


# TODO 3: Instancie o NSGA2 com operadores inteiros (pop_size=40) e rode por 50 geracoes
algorithm6 = NSGA2(
    pop_size=40,
    sampling=IntegerRandomSampling(),
    crossover=SBX(prob=0.9, eta=15, vtype=float, repair=RoundingRepair()),
    mutation=PM(prob=0.2, eta=20, vtype=float, repair=RoundingRepair()),
    eliminate_duplicates=True
)
res6 = minimize(EscalaHospitalarProblem(), algorithm6, termination=('n_gen', 50), seed=42)

print("=" * 70)
print("EXERCICIO 6 - PIPELINE COMPLETO: ESCALA HOSPITALAR")
print("=" * 70)

X6 = np.atleast_2d(res6.X)
F6 = np.atleast_2d(res6.F)
G6 = np.atleast_2d(res6.G) if res6.G is not None else np.zeros((len(F6), 1))

# O NSGA-II pode devolver solucoes com G ligeiramente > 0 (violacao residual).
# Para cumprir o criterio "f2_espera <= 25.0" de forma estrita, filtramos
# explicitamente as solucoes viaveis antes de aplicar o MCDM.
viaveis = np.all(G6 <= 1e-9, axis=1)
print(f"Solucoes retornadas pelo NSGA-II: {len(F6)}")
print(f"Solucoes viaveis (espera <= 25.0 min): {viaveis.sum()}")

X_viavel = X6[viaveis]
F_viavel = F6[viaveis]

# TODO 4: Use PseudoWeights com pesos [0.40, 0.60] (40% Custo, 60% Tempo de Espera)
# para selecionar e imprimir a escala recomendada (quantidade de medicos e enfermeiros).
pesos6 = np.array([0.40, 0.60])
indice6 = PseudoWeights(pesos6).do(F_viavel)

melhor_x6 = X_viavel[indice6]
melhor_f6 = F_viavel[indice6]

print(f"\nDecisao Recomendada (Pesos 40% Custo / 60% Tempo de Espera):")
print(f"-> Medicos Plantonistas: {melhor_x6[0]:.0f}")
print(f"-> Enfermeiros:          {melhor_x6[1]:.0f}")
print(f"-> Custo do Plantao:     R$ {melhor_f6[0]:.2f}")
print(f"-> Tempo de Espera:      {melhor_f6[1]:.2f} min (limite: 25.0 min)")
print(f"-> Restricao respeitada? {melhor_f6[1] <= 25.0}")
