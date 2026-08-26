# Resultados — Aula 02 (Enquadramento e Multiplexação)

**Telecommunications & Network Security**
Análise feita sobre o arquivo [aula02_multiplexacao.pcap](aula02_multiplexacao.pcap) (69 pacotes, capturado no enlace de trunk entre dois switches).

> **Nota sobre método:** os Blocos 1 e 2 do roteiro pedem para gerar tráfego ao vivo (`ping 8.8.8.8`, abrir sites no navegador) com o Wireshark rodando. Como só temos o arquivo `.pcap` (sem captura ao vivo disponível), usei os primeiros 36 pacotes da própria captura — que já são exatamente isso: 4 conversas TCP simultâneas sem tag de VLAN, saindo de `10.20.0.15` — como equivalente ao que seria gerado ao vivo. O único ajuste é que o Bloco 1 pede um pacote ICMP especificamente (do ping); como este arquivo não tem ICMP fora de VLAN, usei o primeiro pacote da captura (TCP/HTTPS) para a dissecação — a estrutura dos campos Ethernet/IP é idêntica, só muda o protocolo de camada 4.

---

## BLOCO 1 — Anatomia do quadro Ethernet

| Campo | Onde encontrar | Valor observado |
|---|---|---|
| MAC destino | Ethernet II → Destination | `00:1c:42:ff:00:01` |
| MAC origem | Ethernet II → Source | `00:1c:42:aa:00:15` |
| EtherType | Ethernet II → Type | `0x0800` (IPv4) |
| IP origem | IPv4 → Source Address | `10.20.0.15` |
| IP destino | IPv4 → Destination Address | `142.250.190.14` |
| Protocolo (camada 4) | IPv4 → Protocol | TCP |
| Tamanho total do quadro | Frame → Frame Length | 54 bytes |

Pacote usado: **#1** no Wireshark (primeiro pacote do arquivo). É um SYN de `10.20.0.15` para `142.250.190.14:443`.

---

## BLOCO 2 — Multiplexação estatística visível

Analisando os 36 primeiros pacotes (segmento sem tag de VLAN) em **Statistics → Conversations → TCP**:

| Conversa (A ↔ B) | Pacotes | Bytes |
|---|---|---|
| 10.20.0.15:49152 ↔ 142.250.190.14:443 (https) | 9 | 1944 |
| 10.20.0.15:49153 ↔ 104.18.32.47:443 (https) | 9 | 1944 |
| 10.20.0.15:49154 ↔ 10.20.0.5:53 (dns) | 9 | 1944 |
| 10.20.0.15:49155 ↔ 10.20.0.9:80 (http) | 9 | 1944 |

| Pergunta | Resposta |
|---|---|
| Quantas conversas TCP simultâneas apareceram? | 4 |
| Qual porta de destino se repete mais? Por quê? | A porta 443 (HTTPS), repetida em 2 das 4 conversas (`142.250.190.14` e `104.18.32.47`) — reflete o predomínio do tráfego web criptografado, já que a maioria dos serviços modernos usa HTTPS por padrão. |
| Duas conversas diferentes podem usar a mesma porta de destino? Como são distinguidas? | Sim — as duas conversas HTTPS acima usam a mesma porta de destino (443), mas para IPs de destino diferentes, além de portas de origem diferentes (49152 e 49153). A tupla completa **(IP origem, porta origem, IP destino, porta destino)** é o identificador único de cada conversa — é essa combinação, e não só a porta, que funciona como "canal" na camada 4. |

---

## BLOCO 3 — A etiqueta 802.1Q em um enlace de trunk

### 5.1 — Quadro etiquetado

Ao clicar em "802.1Q Virtual LAN" no painel do meio, os 4 bytes destacados no hexadecimal (pacote **#37**) são: `81 00 00 0a`.

- `81 00` → TPID, o valor que aparece no campo *Type* do Ethernet II avisando "existe uma tag 802.1Q a seguir".
- `00 0a` → TCI, que contém o VLAN ID no final: `0x00a` = **10**.
- Logo depois da tag vem o EtherType real: `08 00` (IPv4) — confirmado no campo *Type* dentro do próprio bloco "802.1Q Virtual LAN" do Wireshark.

### 5.2 — Separação por VLAN

| Filtro | Quantos pacotes | Faixa de IP | Tipo de tráfego |
|---|---|---|---|
| `vlan` | 33 | 192.168.10.0/24 e 192.168.20.0/24 | ICMP e TCP (Telnet) |
| `vlan.id == 10` | 10 | 192.168.10.1 e 192.168.10.3 | Somente ICMP (ping) |
| `vlan.id == 20` | 23 | 192.168.20.2, 192.168.20.4 e 192.168.20.9 | ICMP (ping) + TCP porta 23 (Telnet) |

*(A sessão Telnet — Bloco 4 — mostra que a VLAN 10 se chama "FINANCEIRO" e a VLAN 20 se chama "VISITANTES", conforme a saída do `show vlan brief` capturada.)*

### 5.3 — Quadro com e sem etiqueta (comparação em hex)

```
Quadro SEM VLAN (pacote #1):
00 1c 42 ff 00 01 | 00 1c 42 aa 00 15 | 08 00 | 45 00 ...
  MAC dst (6)          MAC src (6)      Type    IP...

Quadro COM VLAN (pacote #37):
00 50 79 66 10 03 | 00 50 79 66 10 01 | 81 00 | 00 0a | 08 00 | 45 00 ...
  MAC dst (6)          MAC src (6)      TPID    TCI     Type    IP...
```

| Pergunta | Resposta |
|---|---|
| Quantos bytes a etiqueta 802.1Q acrescenta ao quadro? | 4 bytes (2 de TPID + 2 de TCI). |
| Qual o valor do campo Type quando existe etiqueta? | `0x8100`. |
| Por que a etiqueta aparece nesta captura, mas não apareceria em uma porta de acesso? | Porque esta captura foi feita no enlace de **trunk** entre switches, que carrega o tráfego de várias VLANs multiplexado no mesmo cabo físico — a tag é o que permite ao switch do outro lado saber a qual VLAN cada quadro pertence. Numa porta de **acesso** (access port), o switch já sabe que aquela porta pertence a uma única VLAN, então ele remove a tag antes de entregar o quadro ao dispositivo final (que, em geral, nem entende 802.1Q). |

---

## BLOCO 4 — A lição de segurança

Sessão Telnet reconstruída (pacotes **#57 a #69**, `192.168.20.2 ↔ 192.168.20.9`, dentro da VLAN 20), equivalente ao Follow TCP Stream:

```
UniFECAF Core Switch - CS-01

login: admin
Password: Unifecaf@2026

Bem-vindo. Ultimo acesso: 24/08/2026 08:14

CS-01# show vlan brief

VLAN  Nome         Portas
10    FINANCEIRO   Gi0/1, Gi0/2
20    VISITANTES   Gi0/3, Gi0/4

CS-01# exit
```

| Pergunta | Resposta |
|---|---|
| Qual usuário e qual senha apareceram em claro? | Usuário `admin`, senha `Unifecaf@2026`. |
| Em qual VLAN essa sessão estava trafegando? | VLAN 20 (a própria captura mostra a tag `vlan.id == 20` nos pacotes desta conversa). |
| Que informação sobre a topologia da rede também vazou? | A saída do `show vlan brief`: os nomes das VLANs (10 = FINANCEIRO, 20 = VISITANTES) e em quais portas físicas do switch (Gi0/1–Gi0/4) cada uma está configurada — informação valiosa para um atacante planejar o próximo passo. |
| A separação por VLAN falhou? Se não falhou, por que o conteúdo foi lido mesmo assim? | Não falhou: a segmentação funcionou perfeitamente (o tráfego da VLAN 20 nunca se misturou com o da VLAN 10). O conteúdo foi lido porque VLAN é um mecanismo de **organização/isolamento de domínio de broadcast**, não de **confidencialidade** — Telnet transmite tudo em texto puro, então qualquer um com acesso ao enlace de trunk (por onde passam todas as VLANs) consegue ler o conteúdo de qualquer uma delas. |
| O que precisaria ser feito para que esse conteúdo NÃO fosse legível? | Usar **SSH** no lugar de Telnet para administração do switch — SSH cifra toda a sessão, então mesmo capturando o tráfego no trunk, o conteúdo apareceria como bytes ilegíveis em vez de texto puro. |

*(Observação à parte: chama atenção que a VLAN que carrega tráfego de administração do switch (login Telnet) seja justamente a nomeada "VISITANTES" — normalmente seria de se esperar essa gestão isolada numa VLAN de management dedicada. É um ponto extra de discussão sobre boas práticas de segmentação, além da questão da criptografia.)*

---

## PONTOS DE CHECAGEM

- [x] Identifiquei os campos MAC destino, MAC origem e EtherType em um quadro real.
- [x] Vi a estrutura hexadecimal mudar entre um quadro sem e com tag 802.1Q.
- [x] Encontrei múltiplas conversas simultâneas (4) no segmento sem VLAN.
- [x] Entendi que IP + porta funcionam como identificador de canal na camada 4.
- [x] Localizei a etiqueta 802.1Q e li o VLAN ID dentro dela (10 e 20).
- [x] Separei o tráfego das duas VLANs usando o filtro `vlan.id`.
- [x] Reconstruí a sessão Telnet em claro (equivalente ao Follow TCP Stream).
- [x] Comprovei que a separação por VLAN não impediu a leitura do conteúdo.

---

## CHECKPOINT

1. **O que é enquadramento, e qual campo do quadro Ethernet diz o que vem dentro dele?**
   Enquadramento é a organização dos bits transmitidos em blocos delimitados (quadros), cada um com cabeçalho, dados e trailer, permitindo ao receptor saber onde um quadro começa/termina e como interpretar cada parte. O campo que diz o que vem a seguir é o **Type** do Ethernet II (EtherType) — por exemplo `0x0800` indica IPv4 e `0x8100` indica que existe uma tag 802.1Q antes do conteúdo real.

2. **Em uma rede de pacotes, o que substitui a frequência (FDM) ou a fatia de tempo (TDM) como identificador de canal?**
   A combinação **endereço + porta**. Na camada 4 (visto no Bloco 2), o par IP+porta de origem e destino identifica cada conversa que compartilha o mesmo meio físico. Num enlace de trunk (Bloco 3), o **VLAN ID** dentro da tag 802.1Q cumpre um papel equivalente na camada 2, identificando a qual "canal lógico" cada quadro pertence.

3. **Por que o campo Type vale 0x8100 nos quadros etiquetados, e onde foi parar o 0x0800?**
   Porque a tag 802.1Q é inserida logo depois dos endereços MAC, empurrando o EtherType original para depois dela. O `0x8100` sinaliza "existe uma tag 802.1Q a seguir"; o EtherType verdadeiro (`0x0800` = IPv4) reaparece nos 2 bytes seguintes à tag, dentro do próprio campo Type do bloco 802.1Q.

4. **A captura mostra as duas VLANs separadas corretamente e, ainda assim, foi possível ler uma senha. Explique por que as duas coisas não são contraditórias.**
   Porque VLAN e criptografia resolvem problemas diferentes. A VLAN cumpriu exatamente o que promete: isolar domínios de broadcast e organizar logicamente o tráfego — os pacotes da VLAN 10 e da VLAN 20 nunca se misturaram. Mas ela não promete, e não entrega, confidencialidade do conteúdo. Quem tem acesso físico/lógico ao enlace de trunk enxerga os quadros de todas as VLANs que passam por ali; se o protocolo transportado (Telnet) não cifra os dados, o conteúdo fica legível independente de estar corretamente segmentado.

5. **Relacione o que você observou no Bloco 4 com a frase "separar em canais é organização, proteger o conteúdo é criptografia".**
   O Bloco 3 mostrou a "organização": o VLAN ID funcionando como identificador de canal, exatamente como a frequência no FDM ou o time slot no TDM, mantendo o tráfego das duas VLANs devidamente separado dentro do mesmo cabo físico. O Bloco 4 mostrou o limite dessa organização: mesmo com a separação funcionando perfeitamente, a sessão Telnet foi lida por inteiro — usuário, senha e até a topologia da rede — porque nenhuma etapa do processo envolveu criptografia. Ou seja, multiplexar/segmentar organiza *quem* usa qual canal, mas só a criptografia protege *o que* trafega dentro dele.

---

## Pendências (só você consegue fazer — precisam da interface gráfica do Wireshark)

O item 9 do roteiro pede 3 prints de tela. Abra `aula02_multiplexacao.pcap` no Wireshark e capture:

1. **Quadro Ethernet dissecado com destaque hexadecimal**: clique no pacote **nº 1**, expanda "Ethernet II" no painel do meio — o Wireshark destaca os 14 primeiros bytes no painel hex. Print dessa tela.
2. **Linha 802.1Q com o VLAN ID**: aplique o filtro `vlan`, clique no pacote **nº 37**, expanda "802.1Q Virtual LAN" — vai aparecer `ID: 10`. Print dessa tela.
3. **Follow TCP Stream da sessão Telnet**: aplique o filtro `tcp.port == 23`, clique com o botão direito em qualquer pacote do resultado (pacotes **nº 57 a 69**) → Follow → TCP Stream. A janela vai mostrar exatamente o texto reconstruído na seção "Bloco 4" acima.

Todo o resto do entregável (tabelas + respostas do checkpoint) já está pronto neste arquivo.
