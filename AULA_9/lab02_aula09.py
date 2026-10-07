"""
AULA DE LÓGICA FUZZY - Código 2 (laboratório dos alunos)

Mesmo problema da gorjeta, agora com a biblioteca scikit-fuzzy.
Você vai: (1) rodar, (2) ver os gráficos, (3) fazer os experimentos no final.

Instalação:  pip install numpy matplotlib scikit-fuzzy
Execução:    python lab02_aula09.py

NOTA DE ADAPTAÇÃO: o roteiro original usa input() para ler as notas do
teclado. Como este script precisa rodar de forma automática (sem alguém
digitando), troquei a leitura interativa por uma lista fixa de cenários
de teste -- incluindo o par padrão do roteiro (7, 3) e os três pares que
o próprio roteiro pede para testar no Experimento 5: (0,0), (10,10) e
(5,5). Toda a lógica fuzzy (variáveis, conjuntos, regras, simulação)
continua exatamente a mesma.
"""
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ---------- 1) Variáveis linguísticas (universos de discurso) ----------
servico = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "servico")   # nota 0-10
comida = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "comida")     # nota 0-10
gorjeta = ctrl.Consequent(np.arange(0, 25.01, 0.5), "gorjeta")   # % da conta

# ---------- 2) Conjuntos fuzzy (funções de pertinência) ----------
for var in (servico, comida):
    var["ruim"] = fuzz.trimf(var.universe, [0, 0, 5])
    var["medio"] = fuzz.trimf(var.universe, [0, 5, 10])
    var["bom"] = fuzz.trimf(var.universe, [5, 10, 10])

gorjeta["baixa"] = fuzz.trimf(gorjeta.universe, [0, 0, 13])
gorjeta["media"] = fuzz.trimf(gorjeta.universe, [0, 13, 25])
gorjeta["alta"] = fuzz.trimf(gorjeta.universe, [13, 25, 25])

# ---------- 3) Base de regras  (| = OU, & = E, ~ = NÃO) ----------
regras = [
    ctrl.Rule(servico["ruim"] | comida["ruim"], gorjeta["baixa"]),
    ctrl.Rule(servico["medio"], gorjeta["media"]),
    ctrl.Rule(servico["bom"] | comida["bom"], gorjeta["alta"]),
]

# ---------- 4) Simulação ----------
sistema = ctrl.ControlSystem(regras)
sim = ctrl.ControlSystemSimulation(sistema)

print("=" * 60)
print("LAB 02 — SISTEMA FUZZY DA GORJETA (cenários de teste fixos)")
print("=" * 60)

cenarios = [
    ("Padrão do roteiro", 7, 3),
    ("Pior caso possível", 0, 0),
    ("Melhor caso possível", 10, 10),
    ("Caso neutro/médio", 5, 5),
]

for nome, nota_servico, nota_comida in cenarios:
    sim.input["servico"] = nota_servico
    sim.input["comida"] = nota_comida
    sim.compute()
    print(f"[{nome:<22}] servico={nota_servico:>4} | comida={nota_comida:>4} "
          f"=> gorjeta = {sim.output['gorjeta']:.2f}%")

# ---------- 5) Gráficos (salvos em arquivo + exibidos na tela) ----------
servico.view()
plt.savefig("img_lab02_servico.png", dpi=110)

comida.view()
plt.savefig("img_lab02_comida.png", dpi=110)

# precisa recomputar com o ultimo cenario para a view ficar coerente com o print
sim.input["servico"] = 7
sim.input["comida"] = 3
sim.compute()
gorjeta.view(sim=sim)
plt.savefig("img_lab02_gorjeta.png", dpi=110)

plt.show()


# ============================================================
# EXPERIMENTOS (cada um monta seu próprio sistema fuzzy isolado,
# para não interferir na base de regras acima)
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENTOS")
print("=" * 60)


def novo_servico_comida_padrao():
    s = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "servico")
    c = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "comida")
    for var in (s, c):
        var["ruim"] = fuzz.trimf(var.universe, [0, 0, 5])
        var["medio"] = fuzz.trimf(var.universe, [0, 5, 10])
        var["bom"] = fuzz.trimf(var.universe, [5, 10, 10])
    return s, c


# --- Experimento 1: regra 2 com E (servico['medio'] & comida['medio']) ---
print("\n[Experimento 1] Regra 2 trocada de OU-implicito para E")
s1, c1 = novo_servico_comida_padrao()
g1 = ctrl.Consequent(np.arange(0, 25.01, 0.5), "gorjeta")
g1["baixa"] = fuzz.trimf(g1.universe, [0, 0, 13])
g1["media"] = fuzz.trimf(g1.universe, [0, 13, 25])
g1["alta"] = fuzz.trimf(g1.universe, [13, 25, 25])

regras_exp1 = [
    ctrl.Rule(s1["ruim"] | c1["ruim"], g1["baixa"]),
    ctrl.Rule(s1["medio"] & c1["medio"], g1["media"]),  # <- alterado
    ctrl.Rule(s1["bom"] | c1["bom"], g1["alta"]),
]
sim_exp1 = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras_exp1))
for serv, com in [(7, 3), (7, 9)]:
    sim_exp1.input["servico"] = serv
    sim_exp1.input["comida"] = com
    sim_exp1.compute()

    s1b, c1b = novo_servico_comida_padrao()
    g1b = ctrl.Consequent(np.arange(0, 25.01, 0.5), "gorjeta")
    g1b["baixa"] = fuzz.trimf(g1b.universe, [0, 0, 13])
    g1b["media"] = fuzz.trimf(g1b.universe, [0, 13, 25])
    g1b["alta"] = fuzz.trimf(g1b.universe, [13, 25, 25])
    regras_originais = [
        ctrl.Rule(s1b["ruim"] | c1b["ruim"], g1b["baixa"]),
        ctrl.Rule(s1b["medio"], g1b["media"]),
        ctrl.Rule(s1b["bom"] | c1b["bom"], g1b["alta"]),
    ]
    sim_original_comp = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras_originais))
    sim_original_comp.input["servico"] = serv
    sim_original_comp.input["comida"] = com
    sim_original_comp.compute()

    print(f"  (servico={serv}, comida={com}): regra 2 original = "
          f"{sim_original_comp.output['gorjeta']:.2f}% | regra 2 com E = "
          f"{sim_exp1.output['gorjeta']:.2f}%")


# --- Experimento 2: trapézios em vez de triângulos para servico/comida ---
print("\n[Experimento 2] Triângulos trocados por trapézios em servico/comida")
s2 = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "servico")
c2 = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "comida")
for var in (s2, c2):
    var["ruim"] = fuzz.trapmf(var.universe, [0, 0, 2, 5])
    var["medio"] = fuzz.trapmf(var.universe, [2, 4, 6, 8])
    var["bom"] = fuzz.trapmf(var.universe, [5, 8, 10, 10])

g2 = ctrl.Consequent(np.arange(0, 25.01, 0.5), "gorjeta")
g2["baixa"] = fuzz.trimf(g2.universe, [0, 0, 13])
g2["media"] = fuzz.trimf(g2.universe, [0, 13, 25])
g2["alta"] = fuzz.trimf(g2.universe, [13, 25, 25])

regras_exp2 = [
    ctrl.Rule(s2["ruim"] | c2["ruim"], g2["baixa"]),
    ctrl.Rule(s2["medio"], g2["media"]),
    ctrl.Rule(s2["bom"] | c2["bom"], g2["alta"]),
]
sim_exp2 = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras_exp2))
sim_exp2.input["servico"] = 7
sim_exp2.input["comida"] = 3
sim_exp2.compute()
print(f"  (servico=7, comida=3) com trapézios: {sim_exp2.output['gorjeta']:.2f}% "
      f"(triângulos originais: {sim.output['gorjeta']:.2f}% calculado com servico=7,comida=3 acima)")


# --- Experimento 3: método de defuzzificação (centroid vs mom) ---
print("\n[Experimento 3] Defuzzificação: centroid (padrão) vs mom (mean of maximum)")
s3, c3 = novo_servico_comida_padrao()
g3_centroid = ctrl.Consequent(np.arange(0, 25.01, 0.5), "gorjeta", defuzzify_method="centroid")
g3_mom = ctrl.Consequent(np.arange(0, 25.01, 0.5), "gorjeta", defuzzify_method="mom")
for g in (g3_centroid, g3_mom):
    g["baixa"] = fuzz.trimf(g.universe, [0, 0, 13])
    g["media"] = fuzz.trimf(g.universe, [0, 13, 25])
    g["alta"] = fuzz.trimf(g.universe, [13, 25, 25])

for nome_metodo, s_, c_, g_ in [("centroid", s3, c3, g3_centroid), ("mom", s3, c3, g3_mom)]:
    regras_tmp = [
        ctrl.Rule(s_["ruim"] | c_["ruim"], g_["baixa"]),
        ctrl.Rule(s_["medio"], g_["media"]),
        ctrl.Rule(s_["bom"] | c_["bom"], g_["alta"]),
    ]
    sim_tmp = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras_tmp))
    sim_tmp.input["servico"] = 7
    sim_tmp.input["comida"] = 3
    sim_tmp.compute()
    print(f"  método={nome_metodo:<9}: gorjeta = {sim_tmp.output['gorjeta']:.2f}%")


# --- Experimento 4: adicionar um 4º conjunto "excelente" ao serviço ---
print("\n[Experimento 4] Adicionando o conjunto 'excelente' ao serviço")
s4 = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "servico")
c4 = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "comida")
s4["ruim"] = fuzz.trimf(s4.universe, [0, 0, 5])
s4["medio"] = fuzz.trimf(s4.universe, [0, 5, 8])
s4["bom"] = fuzz.trimf(s4.universe, [5, 8, 10])
s4["excelente"] = fuzz.trimf(s4.universe, [8, 10, 10])  # <- novo conjunto
c4["ruim"] = fuzz.trimf(c4.universe, [0, 0, 5])
c4["medio"] = fuzz.trimf(c4.universe, [0, 5, 10])
c4["bom"] = fuzz.trimf(c4.universe, [5, 10, 10])

g4 = ctrl.Consequent(np.arange(0, 25.01, 0.5), "gorjeta")
g4["baixa"] = fuzz.trimf(g4.universe, [0, 0, 13])
g4["media"] = fuzz.trimf(g4.universe, [0, 13, 25])
g4["alta"] = fuzz.trimf(g4.universe, [13, 25, 25])

regras_exp4 = [
    ctrl.Rule(s4["ruim"] | c4["ruim"], g4["baixa"]),
    ctrl.Rule(s4["medio"], g4["media"]),
    ctrl.Rule(s4["bom"] | c4["bom"], g4["alta"]),
    ctrl.Rule(s4["excelente"], g4["alta"]),  # <- regra nova
]
sim_exp4 = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras_exp4))
for nota_s in [9.5, 8.5, 7.0]:
    sim_exp4.input["servico"] = nota_s
    sim_exp4.input["comida"] = 5
    sim_exp4.compute()
    print(f"  (servico={nota_s}, comida=5) => gorjeta = {sim_exp4.output['gorjeta']:.2f}%")

print("\nFim dos experimentos. Interpretação de cada um em resultados_aula09.md.")
