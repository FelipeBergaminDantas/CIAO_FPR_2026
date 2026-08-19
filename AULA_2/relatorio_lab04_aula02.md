# Atividade 4 — Modelagem de um Problema Real

**Problema escolhido:** montar a grade de matérias do próximo semestre, respeitando pré-requisitos e a carga horária máxima que o aluno pode cursar.

Código completo em [lab04_aula02_CIAO.py](lab04_aula02_CIAO.py).

---

## 1. Descrição do problema em linguagem natural

No começo de cada semestre, o aluno precisa decidir quais matérias vai cursar entre um conjunto de matérias candidatas (obrigatórias e optativas ainda não cursadas). Cada matéria tem uma carga horária semanal e um "peso" de prioridade/interesse para o aluno (o quanto ele quer ou precisa cursá-la). Além disso, algumas matérias exigem pré-requisitos — só podem ser cursadas se a matéria anterior já tiver sido concluída em um semestre passado.

O aluno tem uma carga horária máxima que consegue cursar por semana (por limite da grade, tempo disponível, ou regra da faculdade). O objetivo é escolher o subconjunto de matérias que maximize a prioridade total, sem estourar essa carga horária e sem escolher matéria cujo pré-requisito ainda não foi cumprido.

É essencialmente o mesmo tipo de decisão da Mochila (Atividades 1 e 3): cada matéria "pesa" horas e "vale" uma prioridade, e a mochila é a carga horária da semana — só que aqui, além do peso, existe também uma restrição de precedência (pré-requisitos).

## 2. Modelagem formal

**O que é uma solução:**
Uma solução candidata é um vetor binário de tamanho *n* (uma posição por matéria candidata), onde `1` significa "vou cursar essa matéria" e `0` significa "não vou cursar". Exemplo, com 10 matérias candidatas:

```
(1, 0, 0, 1, 0, 0, 0, 0, 1, 0)
```

significa cursar as matérias de índice 0, 3 e 8.

**Espaço de busca:**
Com *n* matérias candidatas, cada uma podendo estar dentro ou fora da grade, existem `2^n` soluções possíveis (ignorando se são válidas ou não). Na instância usada no código, `n = 10`, então o espaço de busca tem `2^10 = 1024` soluções candidatas.

**Função objetivo:**
Maximizar a soma das prioridades das matérias escolhidas:

```
objetivo(solução) = Σ prioridade[i]   para toda matéria i com solução[i] = 1
```

**Restrições (o que torna uma solução inválida):**
1. **Carga horária:** a soma das horas semanais das matérias escolhidas não pode ultrapassar a carga horária máxima do aluno.
2. **Pré-requisito:** uma matéria só pode ser escolhida se o seu pré-requisito (quando existir) já estiver na lista de matérias concluídas em semestres anteriores.

## 3. Classificação: fácil ou difícil?

Esse problema é uma variação do Problema da Mochila (0/1 Knapsack) com uma restrição extra de precedência entre itens. Como o Knapsack 0/1 já é conhecido como **NP-difícil**, e essa variante generaliza o Knapsack (toda instância de Knapsack é um caso particular deste problema, sem pré-requisitos), ela continua sendo **difícil**.

Na prática isso se percebe porque:
- O espaço de busca cresce exponencialmente (`2^n`), igual visto nas Atividades 1 e 3 — não existe um atalho óbvio que evite testar combinações.
- Não existe um algoritmo exato conhecido que resolva o problema em tempo polinomial no pior caso; a única forma de garantir a solução ótima é enumerar (ou usar programação dinâmica, que ainda cresce rápido com o número de matérias e a carga horária).
- Para poucas matérias candidatas (10, 15, 20) ainda é viável resolver por força bruta, mas para uma grade real com dezenas de disciplinas eletivas isso já se tornaria inviável — o mesmo padrão de "explosão combinatória" das Atividades 2 e 3.

## 4. Código

O arquivo [lab04_aula02_CIAO.py](lab04_aula02_CIAO.py) implementa:
- `gera_solucao_aleatoria()` — gera uma solução candidata aleatória (pode ser factível ou não).
- `calcula_objetivo(solucao)` — calcula o valor da função objetivo (soma de prioridades) de uma solução.
- `verifica_restricoes(solucao)` — verifica se a solução respeita a carga horária máxima e os pré-requisitos, retornando o motivo caso não respeite.

### Exemplo de execução

```
============================================================
Espaco de busca: 2^10 = 1024 solucoes candidatas possiveis
============================================================

>>> Uma solucao aleatoria:
Vetor binario: (0, 0, 1, 0, 0, 0, 0, 0, 1, 0)
Materias escolhidas: ['Redes de Computadores', 'Estatistica Aplicada']
Carga horaria total: 7h (limite: 20h)
Valor da funcao objetivo (soma de prioridades): 12
Factivel? True (ok)

>>> Mais algumas solucoes aleatorias (para ilustrar a variedade):
  Tentativa 1: valor=19 | INFACTIVEL (pre-requisito nao cumprido: Compiladores exige Estrutura de Dados II)
  Tentativa 2: valor=28 | FACTIVEL
  Tentativa 3: valor=44 | INFACTIVEL (carga horaria excedida (25h > 20h))
  Tentativa 4: valor=25 | FACTIVEL
  Tentativa 5: valor=54 | INFACTIVEL (carga horaria excedida (27h > 20h))
```

As execuções mostram bem as duas formas de infactibilidade: a Tentativa 1 tenta cursar "Compiladores" sem ter concluído seu pré-requisito ("Estrutura de Dados II"), e as Tentativas 3 e 5 estouram a carga horária máxima de 20h ao escolher matérias demais.
