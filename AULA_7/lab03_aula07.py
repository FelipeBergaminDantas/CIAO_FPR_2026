# ============================================================
# LAB 03 - PSO: Inercia, Componente Cognitiva e Social
# Tema: Otimizacao Continua de Parametros e Limiares.
#
# NOTA DE CORRECAO: o codigo original do roteiro fazia
# "gbest_X = X[i]" dentro do loop. Em NumPy, indexar uma linha de
# uma matriz (X[i]) devolve uma VIEW (referencia), nao uma copia --
# entao, se essa MESMA particula i se movesse de novo numa iteracao
# futura, gbest_X mudava sozinho junto com X[i], sem passar pelo
# teste de "current_fitness < fitness_function(gbest_X)". Confirmei
# isso na pratica: no log da versao sem correcao, o fitness do gbest
# chegava a PIORAR de uma iteracao para outra (ex.: 0.017 -> 0.529),
# o que e impossivel num PSO correto (gbest so deveria atualizar para
# algo melhor). A correcao e usar "gbest_X = X[i].copy()".
# ============================================================
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)


# Funcao de Custo Esferica (Queremos encontrar o minimo em x=0, y=0)
def fitness_function(position):
    return np.sum(position**2)


num_particles = 10
dimensions = 2
max_iter = 15

# Inicializacao de Posicoes e Velocidades
X = np.random.uniform(-5, 5, (num_particles, dimensions))
V = np.random.uniform(-1, 1, (num_particles, dimensions))

pbest_X = np.copy(X)
pbest_fitness = np.array([fitness_function(p) for p in pbest_X])

gbest_index = np.argmin(pbest_fitness)
gbest_X = np.copy(pbest_X[gbest_index])

w = 0.5   # Inercia
c1 = 1.5  # Componente Cognitiva (Individual)
c2 = 1.5  # Componente Social (Coletiva)

historico_gbest = [fitness_function(gbest_X)]

print("=" * 60)
print("LAB 03 - PSO NA FUNCAO ESFERICA")
print("=" * 60)
print(f"gbest inicial: {gbest_X} | fitness = {historico_gbest[0]:.6f}\n")

for t in range(max_iter):
    for i in range(num_particles):
        r1, r2 = np.random.rand(), np.random.rand()

        # TODO: Implementar a equacao de atualizacao da velocidade da particula i
        # V[i] = (w * V[i]) + (c1 * r1 * (pbest_X[i] - X[i])) + (c2 * r2 * (gbest_X - X[i]))
        V[i] = (w * V[i]) + (c1 * r1 * (pbest_X[i] - X[i])) + (c2 * r2 * (gbest_X - X[i]))

        # Atualizacao da posicao
        X[i] = X[i] + V[i]

        # Avaliacao de Fitness
        current_fitness = fitness_function(X[i])
        if current_fitness < pbest_fitness[i]:
            pbest_fitness[i] = current_fitness
            pbest_X[i] = X[i]

            if current_fitness < fitness_function(gbest_X):
                gbest_X = X[i].copy()  # .copy() evita o bug de aliasing (ver nota no topo)

    historico_gbest.append(fitness_function(gbest_X))
    print(f"Iteracao {t+1:2d}: gbest = {gbest_X} | fitness = {fitness_function(gbest_X):.6f}")

print(f"\n[LAB 03] Melhor posicao encontrada pelo Enxame (gbest): {gbest_X}")
print(f"[LAB 03] Fitness final: {fitness_function(gbest_X):.6f}")

plt.plot(historico_gbest, marker="o")
plt.xlabel("Iteracao")
plt.ylabel("Fitness do gbest")
plt.title("Convergencia do PSO (funcao esferica)")
plt.grid()
plt.savefig("img_lab03_convergencia.png", dpi=110)
plt.show()
