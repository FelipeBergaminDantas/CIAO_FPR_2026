# ============================================================
# LAB 05 - MEMETICO: Meta-heuristica + Busca Local
# Tema: Intensificacao do Aprendizado e Convergencia Acelerada.
# ============================================================
import numpy as np

np.random.seed(42)


# Funcao Rastrigin (Funcao com multiplos minimos locais)
def rastrigin(x):
    return 10 * len(x) + sum(x**2 - 10 * np.cos(2 * np.pi * x))


def local_search_hill_climbing(solution, step_size=0.01, max_steps=20):
    """Mecanismo de Intensificacao (Aprendizado Individual / Memetica)"""
    current_sol = np.copy(solution)
    current_fit = rastrigin(current_sol)

    for _ in range(max_steps):
        # TODO: Gerar um vizinho adicionando ruido aleatorio
        neighbor = current_sol + np.random.uniform(-step_size, step_size, size=len(solution))
        neighbor_fit = rastrigin(neighbor)

        # Se o vizinho for melhor (menor fitness), aceita a nova solucao:
        if neighbor_fit < current_fit:
            current_sol, current_fit = neighbor, neighbor_fit

    return current_sol, current_fit


print("=" * 60)
print("LAB 05 - ALGORITMO MEMETICO (HILL CLIMBING SOBRE RASTRIGIN)")
print("=" * 60)

# Teste da Busca Local Isolada
initial_solution = np.array([2.5, -3.1])
refined_solution, final_fit = local_search_hill_climbing(initial_solution)

print(f"[LAB 05] Solucao Inicial: {initial_solution} | Fitness: {rastrigin(initial_solution):.4f}")
print(f"[LAB 05] Solucao Refinada: {refined_solution} | Fitness: {final_fit:.4f}")

# ------------------------------------------------------------------
# Extra: rodando a busca local varias vezes a partir do mesmo ponto,
# e com mais passos, para ilustrar o quanto o hill climbing "puro"
# consegue avancar sozinho (sem fazer parte de uma populacao/GA)
# ------------------------------------------------------------------
print("\nExtra - impacto do numero de passos (max_steps) na mesma solucao inicial:")
for passos in [20, 200, 2000]:
    sol, fit = local_search_hill_climbing(initial_solution, step_size=0.01, max_steps=passos)
    print(f"  max_steps={passos:5d}: solucao = {sol} | fitness = {fit:.4f}")

print("\nOtimo global conhecido da funcao Rastrigin: x = [0, 0], f(x) = 0.0")
