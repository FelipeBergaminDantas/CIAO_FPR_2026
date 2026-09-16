# ============================================================
# EXERCICIO 1 - Analise do Elitismo na Estabilidade Algoritmica
# Objetivo: alterar a flag de controle do elitismo (USAR_ELITISMO)
# e observar o impacto da preservacao do melhor individuo na
# curva de convergencia (estabilidade x instabilidade).
#
# Para isolar o efeito real do elitismo (e nao apenas a sorte do
# sorteio aleatorio), este script roda AMBAS as configuracoes
# (True e False) sobre a MESMA matriz de distancias e a MESMA
# populacao inicial (mesma semente antes de cada corrida), e
# registra o "melhor custo da geracao atual" (nao o melhor global
# acumulado) para deixar visivel quando a curva piora de uma
# geracao para a outra.
# ============================================================
import numpy as np
import matplotlib.pyplot as plt

SEED = 42
NUM_NOS = 8
TAM_POP = 40
GERACOES = 80
TAXA_MUTACAO = 0.3


def calcular_custo(rota, matriz):
    dist = 0
    for i in range(len(rota) - 1):
        dist += matriz[rota[i], rota[i + 1]]
    return dist + matriz[rota[-1], rota[0]]


def rodar_experimento(usar_elitismo, matriz_teste, populacao_inicial):
    populacao = [ind.copy() for ind in populacao_inicial]
    historico_melhor_geracao = []

    for g in range(GERACOES):
        custos = [calcular_custo(ind, matriz_teste) for ind in populacao]
        melhor_idx = np.argmin(custos)
        historico_melhor_geracao.append(custos[melhor_idx])

        novos = []
        if usar_elitismo:
            novos.append(populacao[melhor_idx].copy())

        while len(novos) < TAM_POP:
            i1, i2 = np.random.choice(TAM_POP, 2, replace=False)
            pai = populacao[i1] if custos[i1] < custos[i2] else populacao[i2]

            filho = pai.copy()
            if np.random.rand() < TAXA_MUTACAO:
                idx1, idx2 = np.random.choice(NUM_NOS, 2, replace=False)
                filho[idx1], filho[idx2] = filho[idx2], filho[idx1]
            novos.append(filho)

        populacao = novos

    custos_finais = [calcular_custo(ind, matriz_teste) for ind in populacao]
    return historico_melhor_geracao, min(custos_finais)


def contar_regressoes(historico):
    """Conta quantas vezes o melhor custo da geracao piorou em relacao a anterior."""
    regressoes = 0
    for i in range(1, len(historico)):
        if historico[i] > historico[i - 1] + 1e-9:
            regressoes += 1
    return regressoes


# ------------------------------------------------------------------
# Uma unica rodada pode enganar (o sorteio aleatorio pode favorecer
# por sorte a versao sem elitismo). Por isso rodamos N instancias
# independentes (matriz + populacao inicial diferentes a cada vez,
# mas a MESMA instancia para as duas configuracoes dentro do mesmo
# trial) e comparamos as medias.
# ------------------------------------------------------------------
N_TRIALS = 20
finais_com, finais_sem = [], []
regs_com, regs_sem = [], []
hist_com_plot, hist_sem_plot = None, None

for trial in range(N_TRIALS):
    np.random.seed(SEED + trial)
    matriz_teste = np.random.uniform(10, 100, (NUM_NOS, NUM_NOS))
    populacao_inicial = [np.random.permutation(NUM_NOS) for _ in range(TAM_POP)]

    np.random.seed(1000 + SEED + trial)
    hist_com, custo_com = rodar_experimento(True, matriz_teste, populacao_inicial)

    np.random.seed(1000 + SEED + trial)
    hist_sem, custo_sem = rodar_experimento(False, matriz_teste, populacao_inicial)

    finais_com.append(custo_com)
    finais_sem.append(custo_sem)
    regs_com.append(contar_regressoes(hist_com))
    regs_sem.append(contar_regressoes(hist_sem))

    if trial == 0:
        hist_com_plot, hist_sem_plot = hist_com, hist_sem

print(f"[Exercicio 1] N de instancias testadas: {N_TRIALS}")
print(f"[Exercicio 1] Custo final medio (Elitismo=True) : {np.mean(finais_com):.2f} (desvio {np.std(finais_com):.2f})")
print(f"[Exercicio 1] Custo final medio (Elitismo=False): {np.mean(finais_sem):.2f} (desvio {np.std(finais_sem):.2f})")
print(f"[Exercicio 1] Regressoes medias por execucao (Elitismo=True) : {np.mean(regs_com):.2f} de {GERACOES-1}")
print(f"[Exercicio 1] Regressoes medias por execucao (Elitismo=False): {np.mean(regs_sem):.2f} de {GERACOES-1}")
print(f"[Exercicio 1] Trials em que Elitismo=True obteve o menor (ou igual) custo final: "
      f"{sum(1 for c, s in zip(finais_com, finais_sem) if c <= s)}/{N_TRIALS}")

print()
print(f"[Exercicio 1] --- Rodada unica de referencia (trial 0, seed={SEED}) ---")
print(f"[Exercicio 1] Menor Custo Obtido (Elitismo=True) : {finais_com[0]:.2f}")
print(f"[Exercicio 1] Menor Custo Obtido (Elitismo=False): {finais_sem[0]:.2f}")

# ------------------------------------------------------------------
# Grafico comparativo (trial 0, usado como ilustracao do padrao tipico)
# ------------------------------------------------------------------
plt.figure(figsize=(10, 5))
plt.plot(hist_com_plot, label="Com elitismo", linewidth=2)
plt.plot(hist_sem_plot, label="Sem elitismo", linewidth=2, alpha=0.8)
plt.xlabel("Geracao")
plt.ylabel("Melhor custo da geracao")
plt.title("Impacto do elitismo na estabilidade da convergencia (TSP, 8 nos)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("img_exercicio01_elitismo.png", dpi=110)
print("[Exercicio 1] Grafico salvo em img_exercicio01_elitismo.png")
plt.show()
