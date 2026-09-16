# ============================================================
# LAB 04 - ACO: Feromonio, Evaporacao e Atratividade
# Tema: Otimizacao de Caminhos e Grafos de Rede.
# ============================================================
import numpy as np

# Grafo de Latencia entre Roteadores (Matriz de Custo)
latency_matrix = np.array([
    [0, 5, 2, 9],
    [5, 0, 3, 1],
    [2, 3, 0, 7],
    [9, 1, 7, 0]
])

num_nodes = len(latency_matrix)
pheromone = np.ones((num_nodes, num_nodes))
rho = 0.25  # Taxa de Evaporacao


def update_pheromone(pheromone_matrix, paths, costs, rho):
    # TODO 1: Aplicar a evaporacao em toda a matriz de feromonio: (1 - rho) * feromonio
    pheromone_matrix = (1 - rho) * pheromone_matrix

    # TODO 2: Depositar o novo feromonio para cada caminho percorrido pelas formigas
    for path, cost in zip(paths, costs):
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            # O deposito e inversamente proporcional ao custo: + (1.0 / cost)
            pheromone_matrix[u][v] += 1.0 / cost

    return pheromone_matrix


print("=" * 70)
print("LAB 04 - ATUALIZACAO DE FEROMONIO (EVAPORACAO + DEPOSITO)")
print("=" * 70)
print("Matriz de feromonio ANTES da atualizacao:")
print(pheromone)

# Simulacao mock para teste da funcao desenvolvida
mock_paths = [[0, 2, 1, 3], [0, 1, 3]]
mock_costs = [6.0, 6.0]

updated_pheromone = update_pheromone(pheromone, mock_paths, mock_costs, rho)
print("\n[LAB 04] Matriz de Feromônio Atualizada:\n", updated_pheromone)

# ------------------------------------------------------------------
# Conferencia manual dos valores (para a analise/relatorio)
# ------------------------------------------------------------------
print("\nConferencia manual:")
print(f"  Todas as celulas comecam evaporadas para {1 - rho} (1x1 * (1-{rho})).")
print(f"  Enlace 0->2 (rota 1): {1 - rho} + 1/6 = {(1 - rho) + 1/6:.4f} "
      f"| valor obtido: {updated_pheromone[0][2]:.4f}")
print(f"  Enlace 0->1 (rota 2): {1 - rho} + 1/6 = {(1 - rho) + 1/6:.4f} "
      f"| valor obtido: {updated_pheromone[0][1]:.4f}")
print(f"  Enlace 3->? (nenhuma formiga saiu do no 3): permanece em {1 - rho} "
      f"| valor obtido: {updated_pheromone[3][0]:.4f}")

# ------------------------------------------------------------------
# Relacao matematica entre latencia e atratividade inicial (eta)
# citada na Questao Tecnica 2
# ------------------------------------------------------------------
print("\nAtratividade inicial (eta = 1/latencia) de cada enlace:")
with np.errstate(divide="ignore"):
    eta = np.where(latency_matrix > 0, 1.0 / np.where(latency_matrix == 0, 1, latency_matrix), 0)
print(eta)
