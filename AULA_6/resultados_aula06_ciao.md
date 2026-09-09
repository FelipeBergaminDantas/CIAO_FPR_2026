# Resultados — Aula 06 (ACO e Algoritmos Híbridos)

## Lab 01 — ACO básico

Saída executada:

```text
============================================================
LABORATÓRIO 01 — ACO
============================================================
Matriz inicial de feromônio:
[[1. 1. 1. 0. 0. 0.]
 [1. 1. 1. 1. 0. 0.]
 [1. 1. 1. 1. 1. 0.]
 [0. 1. 1. 1. 1. 1.]
 [0. 0. 1. 1. 1. 1.]
 [0. 0. 0. 1. 1. 1.]]

Vizinhos do nó 0: [1, 2]
Vizinhos do nó 2: [0, 1, 3, 4]
Formiga 1: [0, 1, 2, 4, 3, 5]
Formiga 2: [0, 1, 2, 4, 5]
Formiga 3: [0, 1, 2, 4, 3, 5]
Formiga 4: [0, 2, 1, 3, 4, 5]
Formiga 5: [0, 1, 2, 3, 4, 5]

Rota de teste: [0, 1, 3, 4, 5]
Custo da rota: 10.0

============================================================
RESULTADO FINAL
============================================================
Melhor rota encontrada: [0, 1, 2, 3, 4, 5]
Melhor custo: 8.0
```

Conclusão: o ACO encontrou a rota de menor custo para a rede, com custo total de 8.0.

## Lab 02 — Experimentando o ACO

Saída executada:

```text
[Padrao]
  Formigas: 20
  Iterações: 50
  ALPHA: 1.0
  BETA: 2.0
  Taxa de evaporação: 0.5
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0

[ALPHA baixo]
  Formigas: 20
  Iterações: 50
  ALPHA: 0.1
  BETA: 2.0
  Taxa de evaporação: 0.5
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0

[ALPHA alto]
  Formigas: 20
  Iterações: 50
  ALPHA: 5.0
  BETA: 2.0
  Taxa de evaporação: 0.5
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0

[BETA baixo]
  Formigas: 20
  Iterações: 50
  ALPHA: 1.0
  BETA: 0.5
  Taxa de evaporação: 0.5
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0

[BETA alto]
  Formigas: 20
  Iterações: 50
  ALPHA: 1.0
  BETA: 5.0
  Taxa de evaporação: 0.5
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0

[Evaporação baixa]
  Formigas: 20
  Iterações: 50
  ALPHA: 1.0
  BETA: 2.0
  Taxa de evaporação: 0.1
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0

[Evaporação alta]
  Formigas: 20
  Iterações: 50
  ALPHA: 1.0
  BETA: 2.0
  Taxa de evaporação: 0.9
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0

[Poucas formigas]
  Formigas: 5
  Iterações: 50
  ALPHA: 1.0
  BETA: 2.0
  Taxa de evaporação: 0.5
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0

[Muitas formigas]
  Formigas: 50
  Iterações: 50
  ALPHA: 1.0
  BETA: 2.0
  Taxa de evaporação: 0.5
  Melhor rota: [0, 1, 2, 3, 4, 5]
  Melhor custo: 8.0
```

Conclusão: neste grafo pequeno, a melhor rota encontrada permanece estável em todas as configurações testadas, mas a sensibilidade dos parâmetros fica mais evidente em redes maiores. ALPHA alto favorece feromônio, BETA alto favorece custo e evaporação alta pode apagar memória relevante.

## Lab 03 — Completando o ACO

Saída executada:

```text
============================================================
LABORATÓRIO 03 — COMPLETANDO O ACO
============================================================
Melhor rota: [0, 1, 2, 3, 4, 5]
Melhor custo: 8.0
```

Respostas:

1. A fórmula usa 1 / custo porque caminhos de menor custo devem ser mais atraentes; usar o custo direto faria o algoritmo favorecer rotas caras.
2. Quanto mais feromônio uma rota recebe, maior a sua atratividade, pois a probabilidade de ser escolhida cresce na etapa de decisão.
3. A formiga não pode visitar novamente um nó porque o problema é de caminho simples em um grafo, e ciclos repetidos aumentam custo e podem bloquear a chegada ao destino.

## Lab 04 — ACO do zero

Saída executada:

```text
======================================================================
LABORATÓRIO 04 — ACO DO ZERO
======================================================================
Melhor rota encontrada: [0, 1, 2, 3, 4, 5]
Melhor custo: 8.0
```

Questões finais:

1. O feromônio atua como memória coletiva: caminhos bons recebem mais reforço, tornando-se mais prováveis nas próximas iterações.
2. Explorar novos caminhos significa testar possibilidades diferentes; aproveitar significa seguir rotas que já mostraram desempenho promissor, reduzindo a busca aleatória.
3. Eu investigaria primeiro a taxa de evaporação e o número de formigas, porque elas controlam o equilíbrio entre experiência, exploração e eficiência em redes maiores.

## Observação final

Os quatro laboratórios foram implementados e executados com sucesso em [AULA_06](AULA_06), respeitando o material da aula e o padrão das atividades anteriores do curso.
