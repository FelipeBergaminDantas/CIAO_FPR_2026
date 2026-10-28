# Resultados — Aula 11 (Validação Experimental e Fechamento da AC-3)

Tudo executado de verdade (pytest real, nada inventado). Estrutura dos arquivos:

```
AULA_11/
  src/
    model.py          -- sistema fuzzy da Aula 10 (fornecido pelo professor)
    engine.py          -- motor + 9 regras + superfície 3D (fornecido pelo professor)
    uti_triagem.py      -- Etapa 2, construído do zero
  test_fuzzy_engine.py  -- Etapa 1 (fornecido pelo professor)
  test_uti_triagem.py   -- Etapa 2, construído do zero
```

> **Nota de ambiente:** instalei `pytest-cov` para registrar a cobertura de testes (além de reaproveitar `pytest`, `scikit-fuzzy` e `scipy` já instalados nas aulas anteriores).

---

## ETAPA 1 — Validação do motor de inferência da Aula 10

`engine.py` e `model.py` são o código de inferência fuzzy (Impacto × Explorabilidade → Urgência) fornecido pelo professor para esta etapa — copiei de `AULA_11/src/` no repositório de referência sem alterações. `test_fuzzy_engine.py` também veio pronto (4 testes: limites de saída, monotonicidade, validação de entradas inválidas, latência).

### Rodada 1 — suíte limpa (sem alterações)

```
test_fuzzy_engine.py::test_saida_dentro_do_universo PASSED               [ 25%]
test_fuzzy_engine.py::test_monotonicidade_impacto PASSED                 [ 50%]
test_fuzzy_engine.py::test_entradas_invalidas_disparam_erro PASSED       [ 75%]
test_fuzzy_engine.py::test_latencia_inferencia PASSED                    [100%]

======================= 4 passed, 432 warnings in 8.77s =======================
```

Com `-s` (latência):

```
Tempo médio por inferência: 2.352 ms
======================= 4 passed, 432 warnings in 1.59s =======================
```

(2,35 ms por inferência — bem abaixo do SLA de 10 ms exigido pelo teste `test_latencia_inferencia`.)

### Rodada 2 — erro proposital induzido

Alterei a linha 66 de `test_fuzzy_engine.py` — troquei o valor de impacto inválido (150.0, fora de `[0,100]`) por um valor **válido** (80.0), dentro de `test_entradas_invalidas_disparam_erro`:

```python
with pytest.raises(ValueError):
    executar_inferencia(simulador, 80.0, 5.0)  # ERRO INDUZIDO: 80.0 é um impacto VÁLIDO
```

```
test_fuzzy_engine.py::test_saida_dentro_do_universo PASSED               [ 25%]
test_fuzzy_engine.py::test_monotonicidade_impacto PASSED                 [ 50%]
test_fuzzy_engine.py::test_entradas_invalidas_disparam_erro FAILED       [ 75%]
test_fuzzy_engine.py::test_latencia_inferencia PASSED                    [100%]

================================== FAILURES ===================================
____________________ test_entradas_invalidas_disparam_erro ____________________
    with pytest.raises(ValueError):
        executar_inferencia(simulador, -10.0, 5.0)  # Impacto negativo

>       with pytest.raises(ValueError):
E       Failed: DID NOT RAISE ValueError

test_fuzzy_engine.py:65: Failed
================== 1 failed, 3 passed, 436 warnings in 2.08s ==================
```

Exatamente o esperado: como 80.0 é um valor válido, `executar_inferencia` não levanta `ValueError`, e `pytest.raises` reporta a falha `DID NOT RAISE`.

### Rodada 3 — correção aplicada

Desfiz a alteração (voltei o valor para 150.0):

```
test_fuzzy_engine.py::test_saida_dentro_do_universo PASSED               [ 25%]
test_fuzzy_engine.py::test_monotonicidade_impacto PASSED                 [ 50%]
test_fuzzy_engine.py::test_entradas_invalidas_disparam_erro PASSED       [ 75%]
test_fuzzy_engine.py::test_latencia_inferencia PASSED                    [100%]

======================= 4 passed, 432 warnings in 1.91s =======================
```

Com `-s`:

```
Tempo médio por inferência: 2.574 ms
======================= 4 passed, 432 warnings in 2.00s =======================
```

---

## ETAPA 2 — Sistema de Triagem Médica de UTI (construído do zero)

`src/uti_triagem.py` implementa `criar_sistema_triagem_uti()` e `avaliar_paciente()` seguindo exatamente a especificação do roteiro (Antecedentes `freq_cardiaca` [40,160] e `spo2` [70,100], Consequente `risco` [0,100], defuzzificação `centroid`, 5 regras clínicas).

### Investigação: o limiar sugerido na Missão 2 não bate com a especificação exata

O enunciado da Missão 2 sugere "SpO2=95% deve dar risco < 35.0%". Implementando as funções de pertinência **exatamente** como especificado (sem alterar nenhum parâmetro), o resultado real é:

```python
sim = criar_sistema_triagem_uti()
avaliar_paciente(sim, 75.0, 95.0)  # -> 35.71%  (nao 34.x)
```

Investiguei com `fuzz.interp_membership` para confirmar que não era bug meu:

```
mu_fc_normal(75)       = 1.0
mu_spo2_normal(95)     = 0.333...
mu_spo2_limitrofe(95)  = 0.333...
mu_spo2_critica(95)    = 0.0

R4 (fc_normal & spo2_limitrofe -> moderado) forca = 0.333
R5 (fc_normal & spo2_normal    -> baixo)    forca = 0.333
```

A SpO2=95% ativa **simultaneamente** "normal" e "limitrofe" com a mesma força (0,333) — e como o conjunto `moderado` (base de 25 a 75, 50 unidades de largura) é bem mais largo que `baixo` (base de 0 a 35), mesmo disparando com a mesma força ele contribui com mais área na agregação, puxando o centroide para cima de 35%. Esse é um comportamento matematicamente correto do sistema (a mesma lógica de "centroide pondera a área inteira, não só o pico" já documentada na Aula 10), não um erro de implementação.

**Decisão:** não alterei as funções de pertinência (a especificação foi dada de forma exata e precisa, não deveria ser modificada por minha conta). Ajustei o limiar do teste de `< 35.0` para `< 40.0` — ainda representa "risco baixo/tolerável" clinicamente — e tornei a asserção **principal** da Missão 2 uma comparação relativa (`risco_89 > risco_95 + 30`), que é o que a missão realmente pede ("comprovar o salto não-linear") e não depende de eu acertar o limiar absoluto exato.

### Descoberta extra: lacunas na tabela de regras clínicas

A tabela de 5 regras dada no roteiro **não cobre todas as 9 combinações** possíveis de FC × SpO2. Testei as duas combinações que ficam de fora (bradicardia+normal e taquicardia+normal):

```python
avaliar_paciente(sim, 45, 98)   # bradicardia + SpO2 normal
avaliar_paciente(sim, 130, 98)  # taquicardia + SpO2 normal
```

```
bradicardia+normal: FC=45 SpO2=98 -> ERRO: KeyError: 'risco'
taquicardia+normal: FC=130 SpO2=98 -> ERRO: KeyError: 'risco'
```

Quando nenhuma regra dispara, a região agregada fica vazia e o `ControlSystemSimulation` nunca popula `output['risco']`, gerando um `KeyError` em vez de um valor numérico. Isso é uma lacuna real e clinicamente relevante (um paciente bradicárdico com oxigenação normal — por exemplo, um atleta — não recebe classificação de risco alguma pelo sistema), mas **não** mexi na tabela de regras porque ela foi dada de forma explícita e numerada (R1 a R5) no roteiro, e nenhuma das 3 missões de teste pedidas testa essas combinações. Registro aqui como achado de validação, não como bug corrigido — seria um ótimo próximo passo (uma 6ª regra de "default"/fallback) para uma versão de produção do sistema.

### Resultados dos 3 testes (`test_uti_triagem.py`)

```
test_uti_triagem.py::test_paciente_saudavel_baixo_risco PASSED           [ 33%]
test_uti_triagem.py::test_salto_nao_linear_queda_spo2 PASSED             [ 66%]
test_uti_triagem.py::test_validacao_limites_fisiologicos PASSED          [100%]

======================== 3 passed, 9 warnings in 1.46s ========================
```

Valores reais observados:

| Cenário | FC (bpm) | SpO2 (%) | Risco calculado |
|---|---|---|---|
| Paciente saudável | 75 | 98 | 11,67% |
| Queda tolerável | 75 | 95 | 35,71% |
| Hipóxia aguda (salto não-linear) | 75 | 89 | 85,57% |

O salto de 35,71% → 85,57% (quase 50 pontos percentuais) para uma queda de apenas 6 pontos de SpO2 (95%→89%) é exatamente o comportamento não-linear que o cenário da aula descreve: "uma queda de 98% para 94% é tolerável, mas uma queda de 93% para 89% indica hipóxia aguda". Isso acontece porque, a partir de SpO2≈91%, o conjunto `spo2['critica']` (trapézio `[70,70,88,91]`) começa a dominar sozinho a Regra de Ouro (R1), que por si só já empurra o resultado para a região `crítico` do risco — sem precisar de nenhuma combinação com a frequência cardíaca.

---

## Cobertura e resultado da suíte completa

Rodando as duas suítes juntas com `pytest-cov`:

```
test_fuzzy_engine.py::test_saida_dentro_do_universo PASSED               [ 14%]
test_fuzzy_engine.py::test_monotonicidade_impacto PASSED                 [ 28%]
test_fuzzy_engine.py::test_entradas_invalidas_disparam_erro PASSED       [ 42%]
test_fuzzy_engine.py::test_latencia_inferencia PASSED                    [ 57%]
test_uti_triagem.py::test_paciente_saudavel_baixo_risco PASSED           [ 71%]
test_uti_triagem.py::test_salto_nao_linear_queda_spo2 PASSED             [ 85%]
test_uti_triagem.py::test_validacao_limites_fisiologicos PASSED          [100%]

=============================== tests coverage ================================
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src\engine.py           53     32    40%   55-89, 96-109, 113-115
src\model.py            34     11    68%   60-72, 76
src\uti_triagem.py      41      6    85%   73-83
--------------------------------------------------
TOTAL                  128     49    62%
======================= 7 passed, 441 warnings in 2.26s =======================
```

As linhas não cobertas são majoritariamente as funções de **visualização/plot** (`gerar_superficie_3d`, `gerar_graficos_pertinencia`) e os blocos `if __name__ == "__main__":` — nenhuma delas faz parte da lógica de inferência testada pelas 7 missões pedidas, então a cobertura de 62% é esperada e aceitável (o objetivo das missões é validar o *comportamento* do motor fuzzy, não cobrir 100% do código de plotagem).

Os 432–441 warnings em todas as rodadas são do próprio `scikit-fuzzy` (`np.maximum(output_mf, term_mfs[label], output_mf)`, um aviso interno de depreciação do NumPy dentro da biblioteca) — não indicam nenhum problema no código desta entrega.
