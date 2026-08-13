# Resultado do código

RESULTADOS DA FORCA-BRUTA NO TSP
>>> 4 cidades
    Rotas avaliadas : 6
    Melhor custo    : 80
    Melhor rota     : (0, 1, 3, 2, 0)
    Tempo (segundos): 0.000074

>>> 5 cidades
    Rotas avaliadas : 24
    Melhor custo    : 41
    Melhor rota     : (0, 1, 2, 3, 4, 0)
    Tempo (segundos): 0.000048

>>> 6 cidades
    Rotas avaliadas : 120
    Melhor custo    : 91
    Melhor rota     : (0, 1, 3, 4, 5, 2, 0)
    Tempo (segundos): 0.000201


OBSERVE: o numero de rotas cresce como (n-1)!  (fatorial)
4 cidades -> 6 rotas | 5 -> 24 | 6 -> 120 | 10 -> 362880 | 15 -> 87 bilhoes


---

# Respostas das perguntas


# REFLEXÃO FINAL
# Tabela que as duplas/trio devem preencher
# Numero de cidades | Rotas avaliadas | Tempo (s) | Melhor custo
# 4                 | 6               | 0.000074  | 80
# 5                 | 24              | 0.000048  | 41
# 6                 | 120             | 0.000201  | 91


16. **O numero de rotas cresce de forma linear, quadratica ou muito mais rapido? Explique com as quantidades que voce coletou.**
   * **Resp:** Cresce de forma muito mais rápida, de acordo com os dados coletados. Isso porque, o crescimento não é linear (Por exemplo, de 4 para 5 cidades, aumentou 18 rotas (24-6). De 5 para 6 cidades, aumentou 96 rotas (120-24).) e também não é quadrático, pois fazendo as contas de n^2, ele não retorna os valores obtidos.

17. **Com base no padrao observado, estime (mesmo que de forma grosseira) quanto tempo levaria para 10 cidades no mesmo computador.**
   * **Resp:** Observando o padrão, para fazer o teste com 10 cidades, ele faria aproximadamente 362.880 rotas e com um tempo estimado de 0.6078 segundos.

18. **Por que dizemos que o TSP e um problema “dificil”? A resposta nao e “porque e complicado de entender”, e sim por causa do crescimento do tempo.**
   * **Resp:** O TSP é um problema "difícil" devido ao crescimento fatorial do número de rotas com o aumento das cidades, tornando a solução por força bruta inviável para instâncias maiores.
