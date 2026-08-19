# Resultado do código

Rodando 20 instancias...

| Instância | Ótimo | Gulosa | Gap |
| :---: | :---: | :---: | :---: |
| 1 | 199 | 199 | 0,0% |
| 2 | 170 | 170 | 0,0% |
| 3 | 155 | 155 | 0,0% |
| 4 | 147 | 147 | 0,0% |
| 5 | 261 | 261 | 0,0% |
| 6 | 214 | 214 | 0,0% |
| 7 | 191 | 187 | 2,1% |
| 8 | 183 | 183 | 0,0% |
| 9 | 215 | 206 | 4,2% |
| 10 | 174 | 174 | 0,0% |
| 11 | 262 | 262 | 0,0% |
| 12 | 206 | 206 | 0,0% |
| 13 | 231 | 231 | 0,0% |
| 14 | 309 | 309 | 0,0% |
| 15 | 294 | 294 | 0,0% |
| 16 | 247 | 247 | 0,0% |
| 17 | 136 | 134 | 1,5% |
| 18 | 212 | 212 | 0,0% |
| 19 | 243 | 243 | 0,0% |
| 20 | 193 | 193 | 0,0% |

### Resumo
* **Gap médio:** 0,39%
* **Gap mínimo:** 0,00%
* **Gap máximo:** 4,19%
* **Desvio padrão:** 1,03%

---

# Respostas das perguntas

19. **Código completo (com a função `calcular_gap` implementada e o loop funcionando).**
   * **Resp:** Implementado em [lab03_aula02_CIAO.py](lab03_aula02_CIAO.py). A função ficou:
     ```python
     def calcular_gap(valor_heuristica, valor_otimo):
         if valor_otimo == 0:
             return 0
         return ((valor_otimo - valor_heuristica) / valor_otimo) * 100
     ```
     E no loop do experimento foi adicionado `gap = calcular_gap(heur, otimo)` seguido de `gaps.append(gap)`.

20. **Valor do gap médio obtido.**
   * **Resp:** 0,39% (rodando 20 instâncias com 12 itens e capacidade 30, seed fixa em 42).

21. **A heurística gulosa é boa o suficiente para este problema? Em quais situações você usaria ela e em quais preferiria gastar mais tempo para achar o ótimo?**
   * **Resp:** Para este problema a heurística gulosa se mostrou bem próxima do ótimo (gap médio de apenas 0,39%, e em 15 das 20 instâncias ela acertou exatamente o valor ótimo). Isso mostra que, para instâncias desse porte, ela já é "boa o suficiente" na maioria dos casos. Usaria a heurística gulosa em situações onde a velocidade de resposta importa mais do que a garantia de otimalidade (por exemplo, decisões em tempo real, instâncias muito grandes onde a força bruta é inviável, ou quando um resultado "quase ótimo" já atende à necessidade). Já preferiria gastar mais tempo buscando o ótimo em cenários críticos, com poucos itens (onde a força bruta ainda é rápida) ou quando cada unidade de valor perdido tem um custo alto (por exemplo, decisões financeiras de grande impacto), já que ali mesmo um gap pequeno pode representar uma perda relevante.
