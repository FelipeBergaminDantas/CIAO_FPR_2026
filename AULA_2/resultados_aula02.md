##Resultado do código
Após a execução do código, nós obtivemos a seguinte resposta:

Total de solucoes avaliadas: 32
Tempo de execucao: 0.000149 segundos
Melhor valor encontrado: 9
Combinacao otima (0=nao leva, 1=leva): (1, 1, 0, 1, 1)

Itens escolhidos:
 - Livro (peso: 2 , valor: 3 )
 - Fone (peso: 1 , valor: 2 )
 - Carregador (peso: 1 , valor: 3 )
 - Chocolate (peso: 1 , valor: 1 )

##Respostas das perguntas:
1. Por que o total de solucoes avaliadas e exatamente 32?
   Resp: Porque temos 5 itens, que tem duas opções de respostas diferentes (0, 1). Sendo assim, considerando que n=5, a conta de 2**n seria igual a 32.

2. O que aconteceria se eu colocasse 15 itens?
   Resp: Ele passaria a ter 32.768 soluções possiveis, e de acordo com o peso e valor benefício de cada item, ele selecionaria as melhores opções dentro da capacidade total da mochila.

3.Voces conseguem imaginar um problema da vida real que seja parecido com este?
   Resp: Uma situação dentro de uma empresa, onde você tem x produtos para serem analisados, e ver quais deles tem o melhor custo benefício para a empresa.
