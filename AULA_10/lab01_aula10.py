# ==============================================================================
# AULA 10 — MOTOR DE INFERÊNCIA MAMDANI E SUPERFÍCIE 3D (SPRINT 2 DA AC-3)
# DESAFIO INVESTIGATIVO: POR QUE O CENTROIDE NÃO DÁ 0% NEM 100%?
#
# Sistema: triagem de urgência de um incidente de segurança, a partir do
# Impacto (%) e da Explorabilidade (score 0-10, estilo CVSS) -> Urgência (%).
# Construído do zero (o roteiro desta aula não trouxe um código pronto,
# só a especificação da matriz de regras e o desafio investigativo).
# ==============================================================================
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (necessário para projection="3d")


# ==============================================================================
# 1) FUZZIFICAÇÃO — variáveis e funções de pertinência
# ==============================================================================
def construir_sistema(urgencia_critica_mf=None, metodo_defuzz="centroid"):
    """Monta o sistema fuzzy completo. Permite trocar a forma da função
    'critica' e o método de defuzzificação, para comparar as abordagens
    do desafio investigativo sem duplicar todo o resto do sistema."""

    impacto = ctrl.Antecedent(np.arange(0, 101, 1), "impacto")
    explorabilidade = ctrl.Antecedent(np.arange(0, 10.01, 0.1), "explorabilidade")
    urgencia = ctrl.Consequent(np.arange(0, 101, 1), "urgencia", defuzzify_method=metodo_defuzz)

    # Conjuntos de entrada (ranges conforme a matriz de regras do roteiro)
    impacto["baixo"] = fuzz.trapmf(impacto.universe, [0, 0, 20, 40])
    impacto["medio"] = fuzz.trimf(impacto.universe, [20, 50, 80])
    impacto["alto"] = fuzz.trapmf(impacto.universe, [60, 80, 100, 100])

    explorabilidade["baixa"] = fuzz.trapmf(explorabilidade.universe, [0, 0, 2, 4])
    explorabilidade["moderada"] = fuzz.trimf(explorabilidade.universe, [2, 5, 8])
    explorabilidade["alta"] = fuzz.trapmf(explorabilidade.universe, [6, 8, 10, 10])

    # Conjuntos de saída (4 categorias, conforme a matriz de regras)
    urgencia["baixa"] = fuzz.trimf(urgencia.universe, [0, 0, 35])
    urgencia["media"] = fuzz.trimf(urgencia.universe, [20, 40, 60])
    urgencia["alta"] = fuzz.trimf(urgencia.universe, [45, 65, 85])
    if urgencia_critica_mf is None:
        urgencia["critica"] = fuzz.trimf(urgencia.universe, [70, 100, 100])  # baseline
    else:
        urgencia["critica"] = urgencia_critica_mf(urgencia.universe)

    # ==============================================================================
    # 2) INFERÊNCIA FUZZY — Matriz de Regras 3x3 (9 regras, só com E)
    # ==============================================================================
    regras = [
        ctrl.Rule(impacto["baixo"] & explorabilidade["baixa"], urgencia["baixa"]),
        ctrl.Rule(impacto["baixo"] & explorabilidade["moderada"], urgencia["baixa"]),
        ctrl.Rule(impacto["baixo"] & explorabilidade["alta"], urgencia["media"]),
        ctrl.Rule(impacto["medio"] & explorabilidade["baixa"], urgencia["media"]),
        ctrl.Rule(impacto["medio"] & explorabilidade["moderada"], urgencia["alta"]),
        ctrl.Rule(impacto["medio"] & explorabilidade["alta"], urgencia["alta"]),
        ctrl.Rule(impacto["alto"] & explorabilidade["baixa"], urgencia["critica"]),
        ctrl.Rule(impacto["alto"] & explorabilidade["moderada"], urgencia["critica"]),
        ctrl.Rule(impacto["alto"] & explorabilidade["alta"], urgencia["critica"]),
    ]

    return ctrl.ControlSystem(regras), (impacto, explorabilidade, urgencia)


def simular(sistema, imp, exp):
    """3) DEFUZZIFICAÇÃO embutida no .compute() do scikit-fuzzy."""
    sim = ctrl.ControlSystemSimulation(sistema)
    sim.input["impacto"] = imp
    sim.input["explorabilidade"] = exp
    sim.compute()
    return sim.output["urgencia"]


# ==============================================================================
# DESAFIO DOS EXTREMOS
# ==============================================================================
print("=" * 78)
print("DESAFIO DOS EXTREMOS — sistema baseline (triangulos + centroid)")
print("=" * 78)

sistema_base, _ = construir_sistema()
saida_0_0 = simular(sistema_base, 0, 0)
saida_100_10 = simular(sistema_base, 100, 10)

print(f"Impacto=0%,   Explorabilidade=0   -> Urgencia = {saida_0_0:.2f}%  (esperado ingenuamente: 0%)")
print(f"Impacto=100%, Explorabilidade=10  -> Urgencia = {saida_100_10:.2f}%  (esperado ingenuamente: 100%)")

print("""
Por que isso acontece (prova geometrica):
Em (0,0), SO a regra 'baixo & baixa -> baixa' dispara (forca 1.0); nenhuma
outra regra contribui. A regiao agregada e exatamente o proprio conjunto
'urgencia baixa' = trimf[0, 0, 35], um triangulo com vertices (0,0) (0,1) (35,0).
O centroide de QUALQUER triangulo e a MEDIA dos seus 3 vertices (geometria
basica), entao:
    centroide_x = (0 + 0 + 35) / 3 = 11.67
...que bate exatamente com o valor calculado acima. O mesmo vale no topo:
so a regra 'alto & alta -> critica' dispara, regiao = trimf[70, 100, 100],
vertices (70,0) (100,1) (100,0):
    centroide_x = (70 + 100 + 100) / 3 = 90.0
O centroide NUNCA cai exatamente no apice do triangulo porque ele pondera
TODA a area da figura (inclusive a base larga, distante do apice) -- nao so
o ponto de pertinencia maxima.
""")


# ==============================================================================
# ABORDAGEM A — Trapézio na borda superior da Urgência Crítica
# ==============================================================================
print("=" * 78)
print("ABORDAGEM A — trocar o triangulo da Urgencia Critica por um trapezio")
print("=" * 78)

testes_trapezio = {
    "triangulo original [70,100,100]": lambda u: fuzz.trimf(u, [70, 100, 100]),
    "trapezio largo [70,90,100,100]  (mesmo pe esquerdo, so achata o topo)":
        lambda u: fuzz.trapmf(u, [70, 90, 100, 100]),
    "trapezio estreito [85,95,100,100] (base deslocada para a direita)":
        lambda u: fuzz.trapmf(u, [85, 95, 100, 100]),
    "trapezio bem estreito [95,99,100,100]":
        lambda u: fuzz.trapmf(u, [95, 99, 100, 100]),
}

for nome, mf in testes_trapezio.items():
    sis, _ = construir_sistema(urgencia_critica_mf=mf)
    resultado = simular(sis, 100, 10)
    print(f"  {nome}\n    -> Urgencia(100,10) = {resultado:.2f}%")

print("""
Resultado CONTRAINTUITIVO: o trapezio "largo" [70,90,100,100] (que so
achata o topo do MESMO triangulo original) da 89.17% -- PIOR que o
triangulo puro (90.00%)! Isso acontece porque achatar o topo sem mexer
no pe esquerdo ACRESCENTA area na regiao 70-90 (onde antes a pertinencia
do triangulo era baixa), e essa area extra, distante do extremo 100,
PUXA o centroide para baixo. Um trapezio so melhora o extremo se a base
inteira for deslocada/estreitada para perto do 100 (ex.: [85,95,100,100]
da 94.58%, e [95,99,100,100] da 98.28%) -- ou seja, "trocar triangulo por
trapezio" sozinho nao basta; o desenho da forma importa tanto quanto o tipo.
""")


# ==============================================================================
# ABORDAGEM B — Método de defuzzificação MOM (Mean of Maximum)
# ==============================================================================
print("=" * 78)
print("ABORDAGEM B — metodo de defuzzificacao MOM em vez de centroid")
print("=" * 78)

sistema_mom, _ = construir_sistema(metodo_defuzz="mom")
saida_mom_0_0 = simular(sistema_mom, 0, 0)
saida_mom_100_10 = simular(sistema_mom, 100, 10)
print(f"MOM: Impacto=0,   Explorabilidade=0  -> Urgencia = {saida_mom_0_0:.2f}%")
print(f"MOM: Impacto=100, Explorabilidade=10 -> Urgencia = {saida_mom_100_10:.2f}%")
print("""
Com MOM, os dois extremos batem EXATAMENTE em 0% e 100%. Motivo: o pico
de pertinencia maxima (1.0) dos triangulos 'baixa' e 'critica' ocorre num
UNICO PONTO exatamente na borda (x=0 e x=100, respectivamente) -- MOM
calcula a media dos pontos de maximo, que aqui e so esse unico ponto.
""")


# ==============================================================================
# COMPARACAO DE SUAVIDADE (o "preco" de cada abordagem)
# ==============================================================================
print("=" * 78)
print("COMPARACAO DE SUAVIDADE — varrendo Impacto de 0 a 100 (Explorabilidade=5)")
print("=" * 78)

sistema_trap_bom, _ = construir_sistema(
    urgencia_critica_mf=lambda u: fuzz.trapmf(u, [85, 95, 100, 100])
)

valores_impacto = list(range(0, 101, 5))
curva_base = [simular(sistema_base, i, 5) for i in valores_impacto]
curva_trap = [simular(sistema_trap_bom, i, 5) for i in valores_impacto]
curva_mom = [simular(sistema_mom, i, 5) for i in valores_impacto]

print(f"{'Impacto':>8} | {'Baseline':>9} | {'Trapezio OK':>11} | {'MOM':>7}")
for i, b, t, m in zip(valores_impacto, curva_base, curva_trap, curva_mom):
    print(f"{i:8d} | {b:9.2f} | {t:11.2f} | {m:7.2f}")

maior_salto_mom = max(abs(curva_mom[k + 1] - curva_mom[k]) for k in range(len(curva_mom) - 1))
maior_salto_base = max(abs(curva_base[k + 1] - curva_base[k]) for k in range(len(curva_base) - 1))
print(f"\nMaior salto entre pontos vizinhos -> baseline/trapezio: {maior_salto_base:.2f} pontos "
      f"| MOM: {maior_salto_mom:.2f} pontos")

plt.figure(figsize=(9, 5))
plt.plot(valores_impacto, curva_base, "o-", label="Baseline (triangulo + centroid)")
plt.plot(valores_impacto, curva_trap, "s-", label="Trapezio bem desenhado + centroid")
plt.plot(valores_impacto, curva_mom, "^-", label="Triangulo + MOM")
plt.xlabel("Impacto (%)")
plt.ylabel("Urgencia (%)")
plt.title("Suavidade: Urgencia vs. Impacto (Explorabilidade = 5)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("comparacao_suavidade.png", dpi=110)


# ==============================================================================
# SUPERFÍCIE DE DECISÃO 3D (sistema baseline)
# ==============================================================================
print("\nGerando superficie de decisao 3D (pode levar alguns segundos)...")

eixo_impacto = np.linspace(0, 100, 40)
eixo_explorabilidade = np.linspace(0, 10, 40)
Z = np.zeros((len(eixo_explorabilidade), len(eixo_impacto)))

for i, imp in enumerate(eixo_impacto):
    for j, exp in enumerate(eixo_explorabilidade):
        Z[j, i] = simular(sistema_base, imp, exp)

X, Y = np.meshgrid(eixo_impacto, eixo_explorabilidade)

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")
superficie = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none", antialiased=True)
ax.set_xlabel("Impacto (%)")
ax.set_ylabel("Explorabilidade (0-10)")
ax.set_zlabel("Urgencia (%)")
ax.set_title("Superficie de Decisao — Motor de Inferencia Mamdani (Urgencia)")
fig.colorbar(superficie, shrink=0.6, label="Urgencia (%)")
plt.tight_layout()
plt.savefig("superficie_decisao.png", dpi=120)
print("Imagem salva: superficie_decisao.png")

plt.show()
