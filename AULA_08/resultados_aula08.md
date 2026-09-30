# Resultados — Aula 08 (Laboratório Prático de Meta-heurísticas)

AC-2 Parte 2. Códigos completos em [lab01_aula08.py](lab01_aula08.py), [lab02_aula08.py](lab02_aula08.py) e [lab03_aula08.py](lab03_aula08.py) (versões `.ipynb` também incluídas). Tudo foi executado de verdade — nenhuma saída abaixo foi inventada. As conferências independentes (ótimo analítico, força bruta, árvore de custo mínimo) estão em [verificacoes_aula08.py](verificacoes_aula08.py).

---

## LAB 01 — PSO para Balanceamento Dinâmico de Carga em Datacenters

Código fornecido pronto, executado sem alterações. Modelo térmico usado pelo código: `T_i = C_i · (1 + 0,5 · w_i)`, fitness = `Σ w_i · T_i` + penalidade externa (`1000 · Σ max(T_i − 75, 0)`). Parâmetros do PSO: inércia 0,7, c1 = c2 = 1,5, `V_MAX` = 0,20, 100 iterações, normalização (`max(x,0)` e divisão pela soma) a cada atualização de posição.

```
População: 10
Melhor W: [0.111111 0.333333 0.       0.555556 0.       0.      ]
Soma dos pesos: 1.0
Fitness: 39.833333
Temperaturas: [44.3333 40.8333 58.     38.3333 50.     65.    ]
------------------------------------------------------------
População: 30
Melhor W: [0.111111 0.333333 0.       0.555556 0.       0.      ]
Soma dos pesos: 1.0
Fitness: 39.833333
Temperaturas: [44.3333 40.8333 58.     38.3333 50.     65.    ]
------------------------------------------------------------
População: 50
Melhor W: [0.111111 0.333333 0.       0.555556 0.       0.      ]
Soma dos pesos: 1.0
Fitness: 39.833333
Temperaturas: [44.3333 40.8333 58.     38.3333 50.     65.    ]
------------------------------------------------------------
```

### Tabela: melhor distribuição W por população e validação da soma

| Partículas | w1 | w2 | w3 | w4 | w5 | w6 | Soma W | Fitness | Temp. Máx. (°C) |
|---|---|---|---|---|---|---|---|---|---|
| 10 | 0,111111 | 0,333333 | 0,0 | 0,555556 | 0,0 | 0,0 | 1,0 | 39,833333 | 65,0 |
| 30 | 0,111111 | 0,333333 | 0,0 | 0,555556 | 0,0 | 0,0 | 1,0 | 39,833333 | 65,0 |
| 50 | 0,111111 | 0,333333 | 0,0 | 0,555556 | 0,0 | 0,0 | 1,0 | 39,833333 | 65,0 |

Validação (saída real do código) para as três populações:

```
  Soma(W) = 1.000000000000 -> True
  Pesos >= 0 -> True
  Todas as temperaturas <= 75.0 °C -> True
```

### Evolução do fitness

![Convergência Lab 01](img_lab01_convergencia.png)

| Partículas | Fitness inicial (G_best) | Fitness na iteração 10 | Iteração em que estabiliza (tol. 1e-6) | Fitness final |
|---|---|---|---|---|
| 10 | 41,7992 | 39,8334 | 20 | 39,833333 |
| 30 | 46,4567 | 39,8334 | 30 | 39,833333 |
| 50 | 43,3780 | 39,8341 | 29 | 39,833333 |

### Análise técnica

**Conferência do ótimo.** Como o modelo é uma quadrática convexa sobre o simplex, é possível resolver analiticamente via KKT: `w_i = max(0, (λ/C_i − 1)/(2α))` com λ ajustado para `Σ w_i = 1`. Resolvi isso numericamente (bisseção em λ) e o ótimo exato é `W = [0.111111, 0.333333, 0, 0.555556, 0, 0]` com fitness **39,833333** — idêntico ao encontrado pelo PSO nas três populações. Ou seja, **o PSO atingiu o ótimo global** com qualquer tamanho de enxame. Confere também a intuição: com λ ≈ 46,67, só recebem tráfego as AZs com coeficiente menor que λ (AZ1 = 42, AZ2 = 35, AZ4 = 30), e nessas `C_i·(1+2α·w_i) = 46,67` é igual para as três (equalização do custo marginal); as AZs 3, 5 e 6 (C = 58, 50, 65) ficam com peso zero.

**Efeito do tamanho da população.** As três populações chegaram ao mesmo resultado final, mas com dinâmicas diferentes: todas caem abaixo de 39,84 por volta da iteração 10, e estabilizam entre as iterações 20 e 30. Neste problema (6 dimensões, função convexa, sem mínimos locais) 10 partículas já bastam; populações maiores custam mais avaliações de fitness por iteração (10 → 50 = 5x mais) sem ganho na qualidade final. Em nenhum caso o enxame maior foi mais rápido — a diferença na velocidade de estabilização entre os tamanhos é pequena e depende da sorte da inicialização (a semente muda por população), então não há base para afirmar que mais partículas aceleram a convergência aqui.

**Penalidade externa.** Ela está implementada e ativa na função de fitness, mas **não chegou a ser acionada no ótimo**: a temperatura máxima final foi 65 °C (AZ6, que ficou com peso 0 e, portanto, só tem o coeficiente base), abaixo do limite de 75 °C. A penalidade só atua em partículas intermediárias que concentrem muito tráfego numa AZ quente (ex.: AZ6 com `w6 > 0,31` ultrapassa 75 °C), empurrando-as de volta para a região viável.

**Operador de normalização.** Garantiu `Σ w_i = 1,0` em todas as iterações (a soma final foi 1,000000000000 nas três execuções), além de manter `w_i ≥ 0`.

---

## LAB 02 — AG Binário com Reparação/Penalidade para Seleção de Microsserviços em Edge

Código fornecido pronto, executado sem alterações. 15 microsserviços, limites de 16 GB de RAM e 8 cores de CPU, população de 40, 100 gerações, torneio de 3, crossover de ponto único (80%), mutação de 5% por bit, com elitismo. Estratégia A: fitness = 0 se violar qualquer limite. Estratégia B: `fitness = valor · max(0, 1 − excesso_RAM/16 − excesso_CPU/8)`.

```
 A — Penalidade Rígida
Fitness: 346
Valor bruto: 346
RAM: 16.0 GB
CPU: 6.5 cores
Serviços: ['S2', 'S4', 'S6', 'S7', 'S8', 'S14', 'S15']

 B — Penalidade Proporcional
Fitness: 356.25
Valor bruto: 380
RAM: 17.0 GB
CPU: 7.5 cores
Serviços: ['S2', 'S4', 'S6', 'S7', 'S8', 'S9', 'S13']
```

### Tabela comparativa (geração final)

| Métrica | Estratégia A | Estratégia B |
|---|---|---|
| Melhor fitness | 346,0000 | 356,2500 |
| Fitness médio final | 207,1750 | 319,7617 |
| Desvio-padrão final | 153,9363 | 45,2974 |
| Diversidade final | 0,1500 | 0,1467 |

| Estratégia | Fitness | Valor | RAM (GB) | CPU (cores) | RAM válida | CPU válida | Qtd. serviços |
|---|---|---|---|---|---|---|---|
| A | 346,00 | 346 | 16,0 | 6,5 | True | True | 7 |
| B | 356,25 | 380 | 17,0 | 7,5 | **False** | True | 7 |

### Média e desvio-padrão do fitness por geração

![Média do fitness](img_lab02_media.png)

![Desvio-padrão do fitness](img_lab02_desvio.png)

Valores em gerações selecionadas (saída real, semente 42):

| Geração | A: média | A: desvio | B: média | B: desvio |
|---|---|---|---|---|
| 1 | 56,40 | 107,61 | 171,60 | 103,23 |
| 10 | 178,32 | 142,84 | 315,21 | 42,45 |
| 25 | 231,12 | 137,11 | 317,04 | 44,08 |
| 50 | 197,57 | 154,74 | 310,21 | 52,33 |
| 100 | 207,18 | 153,94 | 319,76 | 45,30 |

### Diversidade genética

![Diversidade genética](img_lab02_diversidade.png)

| Geração | A: diversidade | B: diversidade |
|---|---|---|
| 1 | 0,907 | 0,907 |
| 10 | 0,300 | 0,290 |
| 25 | 0,203 | 0,140 |
| 50 | 0,187 | 0,163 |
| 100 | 0,150 | 0,147 |
| **Média das 100 gerações** | **0,1925** | **0,1883** |

### Análise técnica

**Média e desvio-padrão.** A Estratégia B tem fitness médio muito maior (≈ 320 vs ≈ 207) e desvio-padrão muito menor (≈ 45 vs ≈ 154). Isso é um efeito direto da função de penalidade, não necessariamente de melhor busca: na A, todo indivíduo inviável vale 0, então a população fica dividida entre "zeros" e soluções boas, inflando o desvio e puxando a média para baixo; na B, o inviável recebe um valor alto "suavizado", o que achata a distribuição. Portanto a média/desvio de B **não é comparável em termos de qualidade** com a de A — medem coisas diferentes.

**Melhor combinação final — atenção.** O "melhor fitness" de B (356,25) é maior que o de A (346), mas a solução de B **é inviável**: usa 17,0 GB de RAM, violando o limite de 16 GB. O valor bruto de 380 só é "alcançado" porque a penalidade proporcional (6,25% de excesso de RAM, descontando 6,25% do valor) é mais branda que o ganho obtido ao violar a restrição — ou seja, a penalidade de B está mal calibrada: compensa violar. A Estratégia A entregou uma configuração **realmente válida** (16,0 GB / 6,5 cores, valor 346). Para checar o quão boa ela é, enumerei as 2^15 = 32.768 combinações por força bruta: o ótimo viável real é **valor 353** (`S2, S4, S6, S7, S8, S9, S12`, 16,0 GB e 6,5 cores), então a A ficou a 7 pontos (≈ 2%) do ótimo nesta execução. Para não tirar conclusão de uma única semente, repeti as duas estratégias com 20 sementes: a A atingiu o ótimo viável (353) em 11 das 20 execuções (média dos melhores = 350,75); já a melhor solução da B foi **inviável em 20 das 20 execuções** (nenhuma encontrou combinação válida).

**Diversidade genética.** Usei o índice `mean(2·min(p, 1−p))` sobre a frequência de 1s em cada gene (0 = população uniforme, 1 = máxima variação). Ambas perdem diversidade rapidamente (de 0,91 para ≈ 0,30 em 10 gerações, devido ao elitismo + torneio de 3), mas a **Estratégia A preservou marginalmente mais diversidade**: média de 0,1925 vs 0,1883 na semente 42, e com 20 sementes a diferença aparece com mais clareza (0,234 para A vs 0,208 para B). A diferença na semente 42 é pequena (e no final das 100 gerações é praticamente empate: 0,150 vs 0,147), então a conclusão é moderada: A mantém diversidade igual ou ligeiramente maior. Uma explicação plausível é que a B converge rápido para o mesmo grupo de soluções "quase viáveis" de alto valor, já que o gradiente suave da penalidade empurra todos os indivíduos na mesma direção.

**Conclusão.** Em termos de solução final **válida**, a Estratégia A foi a que encontrou a melhor combinação de microsserviços (valor 346, dentro dos limites; ótimo global = 353). A Estratégia B só parece melhor pelo número bruto de fitness porque sua melhor solução viola a restrição de RAM. Para a B ser útil, seria necessário aumentar o fator de penalização (ex.: multiplicar por um coeficiente > 1) ou aplicar reparação (remover serviços até caber).

---

## LAB 03 — ACO para Projeto de Topologia de Rede de Baixa Latência

Código fornecido pronto, executado sem alterações. 10 switches, 30 formigas, 100 iterações, α = 1, β = 3, ρ = 0,2, Q = 100. A construção da árvore usa Union-Find para só aceitar arestas que não formam ciclo; a evaporação é aplicada a toda a matriz e o depósito de feromônio é feito apenas pelas melhores 20% das topologias (6 formigas) da iteração. O custo de uma topologia é a soma de `D[i,j] · P[i,j]`, onde `P` pondera a criticidade dos pares (1, 2 ou 3).

```
Melhor custo encontrado: 166.0
Árvore válida: True
Arestas: [(3, 6), (5, 10), (4, 8), (5, 8), (7, 10), (2, 6), (9, 10), (6, 10), (1, 4)]
```

### Matriz de Adjacência final (10x10)

```
     S1  S2  S3  S4  S5  S6  S7  S8  S9  S10
S1    0   0   0   1   0   0   0   0   0    0
S2    0   0   0   0   0   1   0   0   0    0
S3    0   0   0   0   0   1   0   0   0    0
S4    1   0   0   0   0   0   0   1   0    0
S5    0   0   0   0   0   0   0   1   0    1
S6    0   1   1   0   0   0   0   0   0    1
S7    0   0   0   0   0   0   0   0   0    1
S8    0   0   0   1   1   0   0   0   0    0
S9    0   0   0   0   0   0   0   0   0    1
S10   0   0   0   0   1   1   1   0   1    0

Número de arestas: 9
Conectada e sem ciclos: True
```

### Convergência

![Convergência Lab 03](img_lab03_convergencia.png)

O melhor custo da 1ª iteração foi 177; o ACO chegou ao custo final (166) já na **iteração 2** e se manteve até a iteração 100.

### Ganho em relação a topologia aleatória

| Topologia | Custo de latência ponderado |
|---|---|
| ACO | 166,00 |
| Aleatória (média de 100 árvores) | 305,47 |

```
Ganho percentual de redução de latência: 45.66%
```

### Análise técnica

**Validade.** A solução tem exatamente 9 arestas (N − 1 para 10 switches), é conexa e não tem ciclos (`arvore_valida = True`), como se vê também na matriz de adjacência, que é simétrica com soma total = 18 (9 arestas × 2).

**Qualidade da solução.** Como o custo é aditivo por aresta (`D·P`), o problema é equivalente a uma árvore geradora mínima (MST) sobre a matriz ponderada, que tem solução exata em tempo polinomial. Rodei o algoritmo de Kruskal nessa matriz para conferir: o custo mínimo é **166,0**, com o mesmo conjunto de 9 arestas. Portanto, o **ACO encontrou o ótimo global**. Vale registrar que isso é uma checagem de referência e não uma justificativa para usar ACO em produção nesse formato específico — para esse objetivo aditivo, Kruskal/Prim resolvem de forma exata e barata; o ACO passa a ser mais interessante se o objetivo incluir restrições não aditivas (grau máximo por switch, latência fim a fim entre pares críticos, tolerância a falhas etc.).

**Ganho vs. aleatória.** O ACO reduz a latência ponderada em **45,66%** em relação à média de 100 topologias aleatórias (também árvores válidas, geradas por embaralhamento de arestas + Union-Find), um ganho relevante e que confirma que a combinação de feromônio + heurística `1/(D·P)` direciona a construção para arestas de baixa latência.

**Atualização de feromônio.** A evaporação com ρ = 0,2 multiplica todo τ por 0,8 a cada iteração, e somente as melhores topologias da iteração depositam `Q/custo` nas arestas usadas. Isso reforça as arestas de boas soluções e deixa decair as demais, o que explica a convergência rápida — com β = 3 a heurística de latência tem peso forte, por isso o ACO acha o ótimo logo no início, e a parte do feromônio atua principalmente para estabilizar a solução.
