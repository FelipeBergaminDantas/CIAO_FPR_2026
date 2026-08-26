# ============================================================
# RELATORIO TECNICO - Motor de Decisioning SD-WAN Zero-Trust
# ============================================================
# Topologia: 12 nos (0 a 11), malha completa (full-mesh overlay,
# como e tipico numa SD-WAN: qualquer site alcanca qualquer outro
# via tuneis sobre a internet publica). Latencia e perda de pacotes
# sao atributos de ENLACE (matrizes 12x12); reputacao de seguranca
# e atributo de NO (vetor de 12 posicoes), pois representa o quanto
# aquele roteador/site e confiavel -- nao o link entre dois pontos.
# Semente obrigatoria: np.random.seed(2026).
#
# RESULTADO ENCONTRADO (cenario oficial, origem=0, destino=11):
# Com a semente 2026, a rede gerada marca os nos [1, 2, 6, 8, 11]
# como nao confiaveis (reputacao < 50) -- e o NO 11, que e o proprio
# destino OBRIGATORIO da rota, esta entre eles (reputacao = 0.2).
#
# Isso cria um caso-limite importante: como a rota tem que terminar
# no no 11 por especificacao do problema, a penalidade de seguranca
# (+5000) e ACIONADA por QUALQUER rota possivel, nao importa o
# caminho escolhido. Rotear "ao redor" do no 11 nao e uma opcao,
# porque ele e o destino, nao um no de passagem.
#
# Dado que a penalidade e fixa (nao cresce com o numero de nos
# inseguros visitados) e inevitavel neste caso, o motor de
# decisioning corretamente reconhece que a unica alavanca que resta
# e minimizar o componente de desempenho (latencia + perda). A rota
# encontrada foi a rota direta [0, 11] (sem saltos intermediarios),
# que foi validada por forca bruta como o menor custo de desempenho
# possivel entre todas as alternativas com ate 1 no intermediario
# (qualquer desvio so acrescentaria latencia/perda sem remover a
# penalidade, que ja esta "cravada" pelo destino).
#
# Leitura de seguranca correta deste resultado: quando o RISCO esta
# no proprio destino obrigatorio (ex.: um site que ainda nao passou
# por auditoria, mas para o qual o trafego PRECISA ir), a mitigacao
# nao pode vir da escolha de rota -- precisa vir de outra camada de
# controle (inspecao inline, microssegmentacao, MFA na aplicacao
# daquele site, etc.). O roteamento zero-trust so consegue proteger
# contra nos de PASSAGEM inseguros, nunca contra o proprio destino.
#
# DEMONSTRACAO DO MECANISMO DE DESVIO (anexo, mesma rede/semente):
# Para comprovar que a logica de desvio realmente funciona quando o
# destino nao e o proprio no problematico, o script roda um segundo
# cenario ilustrativo dentro da MESMA rede: origem=3, destino=4
# (ambos com reputacao >= 50, portanto validos como extremos fixos).
# Por forca bruta e depois confirmado pelo AG:
#   - a rota mais barata em desempenho puro passa pelo no 6
#     (reputacao 38.5, INSEGURO): custo = 139.70
#   - a segunda mais barata passa pelo no 1 (reputacao 1.9,
#     tambem INSEGURO): custo = 143.00
#   - a melhor rota respeitando seguranca passa pelo no 7
#     (reputacao 92.4, confiavel): custo = 159.92
# O motor com seguranca ativada escolhe a rota via no 7, pagando
# ~14,5% a mais de latencia+perda para eliminar o risco de
# interceptacao -- exatamente o comportamento esperado de um
# roteador zero-trust: sacrificar desempenho marginal em troca de
# nao atravessar nos nao confiaveis, sempre que a rota permitir essa
# escolha.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. CONFIGURACOES DO PROBLEMA
# ============================================================
np.random.seed(2026)

NUM_NOS = 12
ORIGEM_OFICIAL = 0
DESTINO_OFICIAL = 11

TAMANHO_POPULACAO = 80
NUM_GERACOES = 200
TAXA_MUTACAO_SWAP = 0.25
TAXA_MUTACAO_K = 0.15

W1_LATENCIA = 1.0
W2_PERDA = 20.0
LIMIAR_REPUTACAO = 50
PENALIDADE_SEGURANCA = 5000.0


# ============================================================
# 2. GERACAO DA TOPOLOGIA (full-mesh overlay SD-WAN)
# ============================================================
def gerar_matriz_simetrica(minimo, maximo, n):
    m = np.random.uniform(minimo, maximo, (n, n))
    m = (m + m.T) / 2
    np.fill_diagonal(m, 0.0)
    return m


matriz_latencia = gerar_matriz_simetrica(5, 60, NUM_NOS)
matriz_perda = gerar_matriz_simetrica(0, 15, NUM_NOS)
reputacao_nos = np.random.uniform(0, 100, NUM_NOS)

nos_nao_confiaveis = [n for n in range(NUM_NOS) if reputacao_nos[n] < LIMIAR_REPUTACAO]


# ============================================================
# 3. REPRESENTACAO DO INDIVIDUO E DECODIFICACAO DA ROTA
# ============================================================
# Individuo = (perm, k):
#   perm = uma permutacao dos nos intermediarios disponiveis
#   k    = quantos desses nos (na ordem de "perm") entram na rota
# Rota decodificada = [ORIGEM] + perm[:k] + [DESTINO]
#
# Representacao de TAMANHO VARIAVEL: permite ao AG ir desde a rota
# direta (k=0) ate uma rota passando por todos os intermediarios,
# podendo "economizar" saltos e desviar de nos de baixa reputacao
# sem ser obrigado a visita-los -- diferente de uma permutacao fixa
# estilo TSP, que forcaria a passagem por todos os nos.

def intermediarios_disponiveis(origem, destino):
    return [n for n in range(NUM_NOS) if n not in (origem, destino)]


def decodificar_rota(individuo, origem, destino):
    perm, k = individuo
    return [origem] + [int(n) for n in perm[:k]] + [destino]


def criar_individuo(intermediarios):
    perm = np.random.permutation(intermediarios)
    k = np.random.randint(0, len(intermediarios) + 1)
    return (perm, k)


def criar_populacao(intermediarios):
    return [criar_individuo(intermediarios) for _ in range(TAMANHO_POPULACAO)]


# ============================================================
# 4. FUNCAO DE FITNESS
# ============================================================
def calcular_fitness(individuo, origem, destino, usar_seguranca=True):
    rota = decodificar_rota(individuo, origem, destino)

    latencia_total = 0.0
    perda_total = 0.0
    for i in range(len(rota) - 1):
        o, d = rota[i], rota[i + 1]
        latencia_total += matriz_latencia[o, d]
        perda_total += matriz_perda[o, d]

    penalidade = 0.0
    if usar_seguranca and any(reputacao_nos[n] < LIMIAR_REPUTACAO for n in rota):
        penalidade = PENALIDADE_SEGURANCA

    fitness = W1_LATENCIA * latencia_total + W2_PERDA * perda_total + penalidade
    return fitness, latencia_total, perda_total, penalidade


# ============================================================
# 5. OPERADORES GENETICOS
# ============================================================
def crossover_ox(pai1, pai2):
    """OX classico, aplicado apenas sobre o vetor de permutacao."""
    tamanho = len(pai1)
    filho = np.full(tamanho, -1, dtype=int)

    ponto1, ponto2 = sorted(np.random.choice(tamanho, 2, replace=False))
    filho[ponto1:ponto2] = pai1[ponto1:ponto2]

    posicao = ponto2
    for elemento in pai2:
        if elemento not in filho:
            if posicao >= tamanho:
                posicao = 0
            filho[posicao] = elemento
            posicao += 1

    return filho


def crossover(pai1, pai2):
    perm1, k1 = pai1
    perm2, k2 = pai2
    filho_perm = crossover_ox(perm1, perm2)
    filho_k = k1 if np.random.rand() < 0.5 else k2
    return (filho_perm, filho_k)


def mutacao(individuo):
    perm, k = individuo
    perm = perm.copy()

    if np.random.rand() < TAXA_MUTACAO_SWAP:
        idx1, idx2 = np.random.choice(len(perm), 2, replace=False)
        perm[idx1], perm[idx2] = perm[idx2], perm[idx1]

    if np.random.rand() < TAXA_MUTACAO_K:
        k = int(np.clip(k + np.random.choice([-1, 1]), 0, len(perm)))

    return (perm, k)


def selecao_torneio(populacao, fitnesses, tamanho_torneio=3):
    participantes = np.random.choice(len(populacao), tamanho_torneio, replace=False)
    melhor = participantes[np.argmin([fitnesses[i] for i in participantes])]
    return populacao[melhor]


def copiar_individuo(individuo):
    perm, k = individuo
    return (perm.copy(), k)


# ============================================================
# 6. EXECUCAO DO ALGORITMO GENETICO
# ============================================================
def executar_ga(origem, destino, usar_seguranca=True, seed_local=None):
    if seed_local is not None:
        np.random.seed(seed_local)

    intermediarios = intermediarios_disponiveis(origem, destino)
    populacao = criar_populacao(intermediarios)
    melhor_individuo_global = None
    melhor_fitness_global = np.inf
    historico_melhor = []
    historico_medio = []

    for geracao in range(NUM_GERACOES):
        avaliacoes = [calcular_fitness(ind, origem, destino, usar_seguranca) for ind in populacao]
        fitnesses = [a[0] for a in avaliacoes]

        idx_melhor = np.argmin(fitnesses)
        if fitnesses[idx_melhor] < melhor_fitness_global:
            melhor_fitness_global = fitnesses[idx_melhor]
            melhor_individuo_global = copiar_individuo(populacao[idx_melhor])

        historico_melhor.append(melhor_fitness_global)
        historico_medio.append(np.mean(fitnesses))

        nova_populacao = [copiar_individuo(melhor_individuo_global)]
        while len(nova_populacao) < TAMANHO_POPULACAO:
            pai1 = selecao_torneio(populacao, fitnesses)
            pai2 = selecao_torneio(populacao, fitnesses)
            filho = mutacao(crossover(pai1, pai2))
            nova_populacao.append(filho)

        populacao = nova_populacao

    return melhor_individuo_global, melhor_fitness_global, historico_melhor, historico_medio


def imprimir_detalhe_rota(rota, titulo):
    print(titulo)
    for i in range(len(rota) - 1):
        o, d = rota[i], rota[i + 1]
        flag = "  <-- NO NAO CONFIAVEL" if reputacao_nos[d] < LIMIAR_REPUTACAO else ""
        print(f"  {o:2d} -> {d:2d} | latencia={matriz_latencia[o,d]:6.2f} ms | "
              f"perda={matriz_perda[o,d]:5.2f}% | reputacao({d})={reputacao_nos[d]:5.1f}{flag}")


# ============================================================
# 7. CENARIO OFICIAL: origem=0, destino=11
# ============================================================
melhor_individuo, melhor_fitness, historico_melhor, historico_medio = executar_ga(
    ORIGEM_OFICIAL, DESTINO_OFICIAL, usar_seguranca=True, seed_local=2026
)
rota_final = decodificar_rota(melhor_individuo, ORIGEM_OFICIAL, DESTINO_OFICIAL)
fit, lat, perda, pen = calcular_fitness(melhor_individuo, ORIGEM_OFICIAL, DESTINO_OFICIAL, True)

print("=" * 70)
print("MOTOR DE DECISIONING SD-WAN ZERO-TRUST - CENARIO OFICIAL (0 -> 11)")
print("=" * 70)
print(f"Nos nao confiaveis na topologia (reputacao < {LIMIAR_REPUTACAO}): {nos_nao_confiaveis}")
print(f"Reputacao de cada no nao confiavel: "
      f"{[(n, round(float(reputacao_nos[n]), 1)) for n in nos_nao_confiaveis]}")
print()
print(f"Rota selecionada: {rota_final}")
print(f"  Latencia total : {lat:.2f} ms")
print(f"  Perda total    : {perda:.2f} %")
print(f"  Penalidade     : {pen:.2f}  "
      f"({'inevitavel: destino 11 e nao confiavel' if pen > 0 else 'nenhuma'})")
print(f"  Fitness final  : {fit:.2f}")
print()
imprimir_detalhe_rota(rota_final, "Detalhamento enlace a enlace:")

# ------------------------------------------------------------------
# Grafico de convergencia do cenario oficial
# ------------------------------------------------------------------
plt.figure(figsize=(10, 5))
plt.plot(historico_melhor, label="Melhor fitness (0 -> 11)", linewidth=2)
plt.plot(historico_medio, label="Fitness medio da populacao", alpha=0.6)
plt.xlabel("Geracao")
plt.ylabel("Fitness (menor = melhor)")
plt.title("Convergencia - cenario oficial (origem=0, destino=11)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("img_desafio_ac1_convergencia.png", dpi=110)
print("\nGrafico de convergencia salvo em img_desafio_ac1_convergencia.png")
plt.show()


# ============================================================
# 8. ANEXO: demonstracao do mecanismo de desvio (origem=3, destino=4)
# ============================================================
# Cenario ilustrativo dentro da MESMA rede/semente, escolhido porque
# origem e destino aqui SAO confiaveis (reputacao >= 50), permitindo
# observar o AG de fato desviar de um no de passagem inseguro -- o
# que o cenario oficial (0->11) nao pode demonstrar, ja que o proprio
# destino 11 e inseguro e torna a penalidade inevitavel em qualquer
# rota.
ORIGEM_DEMO, DESTINO_DEMO = 3, 4

melhor_demo, fitness_demo, _, _ = executar_ga(
    ORIGEM_DEMO, DESTINO_DEMO, usar_seguranca=True, seed_local=2026
)
melhor_demo_sem_seg, _, _, _ = executar_ga(
    ORIGEM_DEMO, DESTINO_DEMO, usar_seguranca=False, seed_local=2026
)

rota_demo = decodificar_rota(melhor_demo, ORIGEM_DEMO, DESTINO_DEMO)
rota_demo_sem_seg = decodificar_rota(melhor_demo_sem_seg, ORIGEM_DEMO, DESTINO_DEMO)

fit_d, lat_d, perda_d, pen_d = calcular_fitness(melhor_demo, ORIGEM_DEMO, DESTINO_DEMO, True)
_, lat_ds, perda_ds, _ = calcular_fitness(melhor_demo_sem_seg, ORIGEM_DEMO, DESTINO_DEMO, False)
_, _, _, pen_ds_avaliada = calcular_fitness(melhor_demo_sem_seg, ORIGEM_DEMO, DESTINO_DEMO, True)

print()
print("=" * 70)
print(f"ANEXO - DEMONSTRACAO DO DESVIO DE SEGURANCA ({ORIGEM_DEMO} -> {DESTINO_DEMO})")
print("=" * 70)
print(f"Rota SEM considerar seguranca (melhor desempenho puro): {rota_demo_sem_seg}")
print(f"  Latencia+perda ponderadas: {lat_ds + W2_PERDA*perda_ds:.2f} "
      f"| acionaria a penalidade? {'SIM' if pen_ds_avaliada > 0 else 'nao'}")
print(f"Rota COM seguranca (motor zero-trust): {rota_demo}")
print(f"  Latencia+perda ponderadas: {lat_d + W2_PERDA*perda_d:.2f} | penalidade: {pen_d:.2f}")
custo_perf_seguro = lat_d + W2_PERDA * perda_d
custo_perf_inseguro = lat_ds + W2_PERDA * perda_ds
print(f"  Custo extra pago para eliminar o risco: "
      f"{custo_perf_seguro - custo_perf_inseguro:.2f} "
      f"({100*(custo_perf_seguro/custo_perf_inseguro - 1):.1f}% mais lento/instavel)")
print()
imprimir_detalhe_rota(rota_demo, "Detalhamento da rota segura escolhida:")
