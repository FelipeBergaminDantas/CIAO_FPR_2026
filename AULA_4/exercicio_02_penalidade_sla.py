# ============================================================
# EXERCICIO 2 - Insercao de Penalidades por Descumprimento de SLA
# Objetivo: calcular uma penalidade estatica de +1000 ms para
# qualquer enlace da rota cuja latencia exceda o limite
# operacional de 50 ms.
# ============================================================
import numpy as np

np.random.seed(15)
matriz_latencia = np.random.uniform(5, 80, (6, 6))


def calcular_custo_com_sla(rota, matriz, limite_sla=50.0):
    custo_total = 0.0
    penalidade = 0.0

    for i in range(len(rota) - 1):
        latencia_enlace = matriz[rota[i], rota[i + 1]]
        custo_total += latencia_enlace

        # Incrementa a penalidade caso a latencia do enlace ultrapasse o SLA
        if latencia_enlace > limite_sla:
            penalidade += 1000.0

    return custo_total, penalidade


rota_teste = np.array([0, 1, 2, 3, 4, 5])
custo_total, penalidade = calcular_custo_com_sla(rota_teste, matriz_latencia)
custo_final = custo_total + penalidade

print(f"[Exercicio 2] Custo Total (Com Penalizacoes de SLA): {custo_final:.2f} ms")

# ------------------------------------------------------------------
# Detalhamento enlace a enlace, para evidenciar onde a penalidade
# foi aplicada
# ------------------------------------------------------------------
print("\n[Exercicio 2] Detalhamento por enlace:")
n_violacoes = 0
for i in range(len(rota_teste) - 1):
    origem, destino = rota_teste[i], rota_teste[i + 1]
    latencia = matriz_latencia[origem, destino]
    violou = latencia > 50.0
    n_violacoes += violou
    status = "VIOLOU SLA (+1000 ms)" if violou else "dentro do SLA"
    print(f"  Enlace {origem} -> {destino}: {latencia:6.2f} ms | {status}")

print(f"\n[Exercicio 2] Latencia acumulada (sem penalidade): {custo_total:.2f} ms")
print(f"[Exercicio 2] Enlaces que violaram o SLA (>50 ms): {n_violacoes} de {len(rota_teste)-1}")
print(f"[Exercicio 2] Penalidade total aplicada: {penalidade:.2f} ms")
print(f"[Exercicio 2] Custo final (com penalidade): {custo_final:.2f} ms")
