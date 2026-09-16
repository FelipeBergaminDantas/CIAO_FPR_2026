# ============================================================
# LAB 02 - ALGORITMO GENETICO: Selecao, Crossover e Mutacao
# Tema: Otimizacao Combinatoria (Selecao de Ativos / Problema da Mochila)
# ============================================================
import numpy as np

np.random.seed(42)

# Problema da Mochila (Blindagem de Ativos)
weights = np.array([12, 2, 1, 4, 1])   # Custo/Consumo de Memoria dos ativos
values = np.array([4, 2, 1, 10, 2])    # Cobertura de Risco/Valor do ativo
max_weight = 15

pop_size = 10
num_genes = len(weights)
generations = 10
mutation_rate = 0.1

# Inicializacao da Populacao (Matriz Binaria 10x5)
population = np.random.randint(0, 2, size=(pop_size, num_genes))


def calculate_fitness(ind):
    total_weight = np.sum(ind * weights)
    total_value = np.sum(ind * values)
    # TODO 1: Implementar a restricao de peso. Se total_weight > max_weight,
    # retorne fitness = 0 (penalizacao). Caso contrario, retorne total_value.
    if total_weight > max_weight:
        return 0
    return total_value


def tournament_selection(pop, fitnesses):
    # TODO 2: Selecionar 2 individuos aleatorios da populacao e retornar
    # o individuo que possui o maior fitness (Selecao por Torneio).
    idx1, idx2 = np.random.choice(len(pop), 2, replace=False)
    if fitnesses[idx1] >= fitnesses[idx2]:
        return pop[idx1].copy()
    return pop[idx2].copy()


def crossover(parent1, parent2):
    point = np.random.randint(1, num_genes)
    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])
    return child1, child2


def mutate(ind):
    for i in range(num_genes):
        if np.random.rand() < mutation_rate:
            ind[i] = 1 - ind[i]  # Inverte o bit (0 -> 1 ou 1 -> 0)
    return ind


def melhor_individuo(pop, fitnesses):
    idx = np.argmax(fitnesses)
    return pop[idx], fitnesses[idx]


print("=" * 60)
print("LAB 02 - ALGORITMO GENETICO (PROBLEMA DA MOCHILA)")
print("=" * 60)
print(f"Pesos : {weights}")
print(f"Valores: {values}")
print(f"Capacidade maxima: {max_weight}\n")

fitnesses_iniciais = np.array([calculate_fitness(ind) for ind in population])
melhor_ind_inicial, melhor_fit_inicial = melhor_individuo(population, fitnesses_iniciais)
print(f"Geracao 0 (populacao inicial aleatoria): melhor fitness = {melhor_fit_inicial}")

historico_melhor = [melhor_fit_inicial]

# Loop Evolutivo
for g in range(generations):
    fitnesses = np.array([calculate_fitness(ind) for ind in population])
    new_population = []

    for _ in range(pop_size // 2):
        p1 = tournament_selection(population, fitnesses)
        p2 = tournament_selection(population, fitnesses)
        c1, c2 = crossover(p1, p2)
        new_population.extend([mutate(c1), mutate(c2)])

    population = np.array(new_population)

    fitnesses = np.array([calculate_fitness(ind) for ind in population])
    melhor_ind, melhor_fit = melhor_individuo(population, fitnesses)
    historico_melhor.append(melhor_fit)
    print(f"Geracao {g+1:2d}: melhor individuo = {melhor_ind} | fitness (valor) = {melhor_fit}")

fitnesses_finais = np.array([calculate_fitness(ind) for ind in population])
melhor_final, fit_final = melhor_individuo(population, fitnesses_finais)
peso_final = np.sum(melhor_final * weights)

print("\n" + "=" * 60)
print("RESULTADO FINAL")
print("=" * 60)
print(f"Melhor individuo encontrado: {melhor_final}")
print(f"Valor total (fitness): {fit_final}")
print(f"Peso total: {peso_final} (capacidade: {max_weight})")

# Comparacao com o otimo (forca bruta, viavel pois sao so 5 itens / 32 combinacoes)
melhor_bruteforce = 0
melhor_comb = None
for mask in range(2 ** num_genes):
    comb = np.array([(mask >> i) & 1 for i in range(num_genes)])
    peso = np.sum(comb * weights)
    valor = np.sum(comb * values)
    if peso <= max_weight and valor > melhor_bruteforce:
        melhor_bruteforce = valor
        melhor_comb = comb

print(f"\nOtimo por forca bruta (32 combinacoes possiveis): {melhor_comb} | valor = {melhor_bruteforce}")
if fit_final == melhor_bruteforce:
    print("=> O GA encontrou o OTIMO GLOBAL.")
else:
    print(f"=> Gap do GA em relacao ao otimo: {melhor_bruteforce - fit_final}")
