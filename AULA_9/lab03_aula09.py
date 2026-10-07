# ==============================================================================
# AULA 09 — LAB 03: SISTEMA FUZZY DO ZERO
# Problema escolhido: Intensidade ideal de treino a partir do sono da noite
# anterior e da frequência cardíaca (FC) de repouso ao acordar.
#
# Ver a descrição completa do problema (Etapas 1 e 2) em resultados_aula09.md.
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ------------------------------------------------------------------
# ETAPA 2 (parte 1): Universos de discurso (com unidade)
# ------------------------------------------------------------------
sono = ctrl.Antecedent(np.arange(0, 12.01, 0.1), "sono")              # horas de sono
fc_repouso = ctrl.Antecedent(np.arange(40, 100.01, 1), "fc_repouso")   # batimentos por minuto (bpm)
intensidade = ctrl.Consequent(np.arange(0, 100.01, 1), "intensidade")  # % de intensidade recomendada

# ------------------------------------------------------------------
# ETAPA 2 (parte 2): Termos linguísticos e funções de pertinência
# ------------------------------------------------------------------
sono["poucas"] = fuzz.trapmf(sono.universe, [0, 0, 4, 6])
sono["moderadas"] = fuzz.trimf(sono.universe, [4, 6, 8])
sono["muitas"] = fuzz.trapmf(sono.universe, [6, 8, 12, 12])

fc_repouso["baixa"] = fuzz.trapmf(fc_repouso.universe, [40, 40, 55, 65])
fc_repouso["normal"] = fuzz.trimf(fc_repouso.universe, [55, 65, 75])
fc_repouso["alta"] = fuzz.trapmf(fc_repouso.universe, [65, 75, 100, 100])

intensidade["leve"] = fuzz.trimf(intensidade.universe, [0, 0, 40])
intensidade["moderada"] = fuzz.trimf(intensidade.universe, [20, 50, 80])
intensidade["intensa"] = fuzz.trimf(intensidade.universe, [60, 100, 100])

# ------------------------------------------------------------------
# ETAPA 2 (parte 3): Base de regras (mínimo 6, usando E e OU)
# ------------------------------------------------------------------
# Grade completa 3x3 (sono x FC), toda com E -- cada combinação das
# duas entradas decide a categoria de saída:
regras = [
    ctrl.Rule(sono["poucas"] & fc_repouso["alta"], intensidade["leve"]),
    ctrl.Rule(sono["poucas"] & fc_repouso["normal"], intensidade["leve"]),
    ctrl.Rule(sono["poucas"] & fc_repouso["baixa"], intensidade["moderada"]),
    ctrl.Rule(sono["moderadas"] & fc_repouso["alta"], intensidade["leve"]),
    ctrl.Rule(sono["moderadas"] & fc_repouso["normal"], intensidade["moderada"]),
    ctrl.Rule(sono["moderadas"] & fc_repouso["baixa"], intensidade["intensa"]),
    ctrl.Rule(sono["muitas"] & fc_repouso["alta"], intensidade["moderada"]),
    ctrl.Rule(sono["muitas"] & fc_repouso["normal"], intensidade["intensa"]),
    ctrl.Rule(sono["muitas"] & fc_repouso["baixa"], intensidade["intensa"]),
    # Regra extra com OU: qualquer sinal de alerta isolado (dormiu pouco OU
    # a FC está alta) já é suficiente para recomendar cautela, reforçando
    # a conclusão "leve" mesmo fora da combinação exata das regras acima.
    ctrl.Rule(sono["poucas"] | fc_repouso["alta"], intensidade["leve"]),
]

sistema = ctrl.ControlSystem(regras)
simulador = ctrl.ControlSystemSimulation(sistema)

# ------------------------------------------------------------------
# ETAPA 4: Testes (mínimo 4 situações)
# ------------------------------------------------------------------
print("=" * 70)
print("LAB 03 — INTENSIDADE DE TREINO (sono x FC de repouso)")
print("=" * 70)

testes = [
    ("Noite ruim, corpo estressado", 3.5, 82, "leve (esperado: baixa intensidade)"),
    ("Dormiu bem, corpo recuperado", 8.5, 52, "intensa (esperado: alta intensidade)"),
    ("Pouco sono, mas FC baixa (recuperado)", 4.0, 48, "moderada (compensacao parcial)"),
    ("Sono moderado, FC normal (dia comum)", 6.5, 68, "moderada (dia tipico)"),
    ("Dormiu muito, mas FC alta (possivel estresse/doenca)", 9.0, 85, "moderada (sinal de alerta da FC)"),
]

for nome, h_sono, bpm, esperado in testes:
    simulador.input["sono"] = h_sono
    simulador.input["fc_repouso"] = bpm
    simulador.compute()
    saida = simulador.output["intensidade"]
    print(f"[{nome}]")
    print(f"  Entradas: sono = {h_sono}h | FC repouso = {bpm} bpm")
    print(f"  Saida do sistema: intensidade = {saida:.1f}%")
    print(f"  Resposta esperada (raciocinio humano): {esperado}\n")

# ------------------------------------------------------------------
# Gráficos (salvos em arquivo + exibidos na tela)
# ------------------------------------------------------------------
sono.view()
plt.savefig("img_lab03_sono.png", dpi=110)

fc_repouso.view()
plt.savefig("img_lab03_fc.png", dpi=110)

intensidade.view()
plt.savefig("img_lab03_intensidade_sets.png", dpi=110)

# View do ultimo teste computado, para mostrar a area de inferencia
intensidade.view(sim=simulador)
plt.savefig("img_lab03_intensidade_resultado.png", dpi=110)

plt.show()
