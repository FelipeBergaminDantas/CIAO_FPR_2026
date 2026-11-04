# ==============================================================================
# EXERCICIO 6: Desafio Integrado com Restricoes
# Objetivo: Aplicar uma restricao de desigualdade (G <= 0) em um problema de
# infraestrutura (recarga de veiculo eletrico).
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


class EVBatteryProblem(ElementwiseProblem):
    def __init__(self):
        # x1: Potencia de Carga (10 a 150 kW), x2: Temperatura do Ar (15 a 45 C)
        # TODO 1: Configurar 2 variaveis, 2 objetivos e 1 RESTRICAO de desigualdade (n_ieq_constr=1)
        super().__init__(n_var=2, n_obj=2, n_ieq_constr=1, xl=np.array([10.0, 15.0]), xu=np.array([150.0, 45.0]))

    def _evaluate(self, x, out, *args, **kwargs):
        potencia, temp = x[0], x[1]

        f1_tempo_recarga = 3000.0 / potencia
        f2_desgaste_bateria = (potencia ** 1.5) * (temp / 20.0)

        # TODO 2: Adicione a restricao de seguranca: O desgaste (f2) NAO PODE ultrapassar 1500 unidades.
        # Dica no pymoo: Restricoes de desigualdade devem ser escritas na forma G(x) <= 0.
        # Logo: g1 = f2_desgaste_bateria - 1500.0
        g1 = f2_desgaste_bateria - 1500.0

        out["F"] = [f1_tempo_recarga, f2_desgaste_bateria]
        # TODO 3: Passe a restricao para a saida: out["G"] = [g1]
        out["G"] = [g1]


# TODO 4: Execute a otimizacao com o NSGA-II e imprima no console apenas as solucoes viaveis!
res6 = minimize(EVBatteryProblem(), NSGA2(pop_size=40), termination=('n_gen', 60), seed=42, verbose=False)

print("=" * 60)
print("EXERCICIO 6 - RECARGA DE BATERIA EV (COM RESTRICAO)")
print("=" * 60)

# O pymoo ja filtra solucoes inviaveis do resultado final quando CV=0 e exigido,
# mas confirmamos explicitamente verificando resultado.G (ou recalculando) antes
# de imprimir -- assim garantimos que SO solucoes viaveis aparecem no console.
X6 = np.atleast_2d(res6.X)
F6 = np.atleast_2d(res6.F)
G6 = np.atleast_2d(res6.G) if res6.G is not None else np.zeros((len(F6), 1))

viaveis = np.all(G6 <= 1e-6, axis=1)
print(f"Solucoes retornadas pelo NSGA-II: {len(F6)}")
print(f"Solucoes viaveis (desgaste <= 1500): {viaveis.sum()}")

ordem6 = np.argsort(F6[viaveis, 0])
X_viavel = X6[viaveis]
F_viavel = F6[viaveis]
G_viavel = G6[viaveis]

for pos, i in enumerate(ordem6, start=1):
    potencia, temp = X_viavel[i]
    tempo, desgaste = F_viavel[i]
    print(f"  Solucao {pos:2d}: Potencia={potencia:6.2f} kW | Temp={temp:5.2f} C "
          f"| Tempo Recarga={tempo:6.2f} min | Desgaste={desgaste:7.2f} "
          f"(G={G_viavel[i][0]:7.2f})")

plt.figure(figsize=(7, 5))
plt.scatter(F_viavel[:, 0], F_viavel[:, 1], color='orange', s=50, label="Viaveis (desgaste <= 1500)")
plt.axhline(1500.0, color='red', linestyle='--', alpha=0.6, label="Limite de seguranca (1500)")
plt.title("Exercicio 6 — Recarga de Bateria EV (com restricao)")
plt.xlabel("Tempo de Recarga (min) [Minimizar]")
plt.ylabel("Desgaste da Bateria [Minimizar]")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("img_exercicio06_ev_battery.png", dpi=110)
plt.show()
