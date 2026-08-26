import os
from scapy.all import rdpcap, Ether, Dot1Q, IP, TCP, ICMP, Raw
from collections import defaultdict, OrderedDict

PCAP = os.path.join(os.path.dirname(__file__), "aula02_multiplexacao.pcap")
pkts = rdpcap(PCAP)

def out(*a):
    print(*a)

out("TOTAL DE PACOTES:", len(pkts))
out()

# ------------------------------------------------------------------
# BLOCO 1 - dissecar um quadro representativo (sem VLAN)
# ------------------------------------------------------------------
out("="*70)
out("BLOCO 1 - quadro representativo (pacote indice 0 / Wireshark #1)")
out("="*70)
p0 = pkts[0]
eth = p0[Ether]
ip0 = p0[IP]
proto_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
out("MAC destino   :", eth.dst)
out("MAC origem    :", eth.src)
out("EtherType     :", hex(eth.type))
out("IP origem     :", ip0.src)
out("IP destino    :", ip0.dst)
out("Protocolo(L4) :", proto_map.get(ip0.proto, ip0.proto))
out("Tamanho quadro:", len(p0), "bytes")
out()

# ------------------------------------------------------------------
# BLOCO 2 - conversas TCP sem VLAN (pacotes indices 0-35)
# ------------------------------------------------------------------
out("="*70)
out("BLOCO 2 - conversas TCP (segmento sem VLAN, indices 0-35)")
out("="*70)
convs = OrderedDict()
for i, p in enumerate(pkts[:36]):
    if TCP in p:
        ip = p[IP]
        tcp = p[TCP]
        a = (ip.src, tcp.sport)
        b = (ip.dst, tcp.dport)
        key = tuple(sorted([a, b]))
        convs.setdefault(key, {"pkts": 0, "bytes": 0})
        convs[key]["pkts"] += 1
        convs[key]["bytes"] += len(p)

out(f"Conversas TCP simultaneas encontradas: {len(convs)}")
for key, stats in convs.items():
    (ipA, portA), (ipB, portB) = key
    out(f"  {ipA}:{portA} <-> {ipB}:{portB}  | pacotes={stats['pkts']} bytes={stats['bytes']}")
out()

# ------------------------------------------------------------------
# BLOCO 3 - VLANs (pacotes indices 36-68)
# ------------------------------------------------------------------
out("="*70)
out("BLOCO 3 - trafego com tag 802.1Q")
out("="*70)
vlan_pkts = [p for p in pkts if Dot1Q in p]
out("Total de pacotes com tag VLAN:", len(vlan_pkts))

por_vlan = defaultdict(list)
for p in vlan_pkts:
    vid = p[Dot1Q].vlan
    por_vlan[vid].append(p)

for vid in sorted(por_vlan.keys()):
    lista = por_vlan[vid]
    ips = set()
    tipos = set()
    for p in lista:
        if IP in p:
            ips.add(p[IP].src)
            ips.add(p[IP].dst)
        if ICMP in p:
            tipos.add("ICMP")
        elif TCP in p:
            tipos.add(f"TCP porta {p[TCP].dport if p[TCP].dport < p[TCP].sport else p[TCP].sport}")
    out(f"VLAN {vid}: {len(lista)} pacotes | IPs: {sorted(ips)} | tipos: {tipos}")
out()

out("--- Quadro COM tag (indice 36 / Wireshark #37), primeiros 22 bytes em hex ---")
raw36 = bytes(pkts[36])
out(raw36[:22].hex(" "))
out("EtherType (Ethernet II) do quadro 36:", hex(pkts[36][Ether].type), "-> 0x8100 = 802.1Q")
out("VLAN ID (campo ID da tag):", pkts[36][Dot1Q].vlan)
out("EtherType real (dentro da tag, campo type do Dot1Q):", hex(pkts[36][Dot1Q].type))
out()

out("--- Quadro SEM tag (indice 0 / Wireshark #1), primeiros 22 bytes em hex, para comparar ---")
raw0 = bytes(pkts[0])
out(raw0[:22].hex(" "))
out()

# ------------------------------------------------------------------
# BLOCO 4 - sessao Telnet
# ------------------------------------------------------------------
out("="*70)
out("BLOCO 4 - sessao Telnet (Follow TCP Stream)")
out("="*70)
telnet_pkts = [p for p in pkts if TCP in p and (p[TCP].sport == 23 or p[TCP].dport == 23)]
out("Pacotes na sessao Telnet:", len(telnet_pkts))
if telnet_pkts:
    ip_info = telnet_pkts[0][IP]
    vlan_info = telnet_pkts[0][Dot1Q].vlan if Dot1Q in telnet_pkts[0] else None
    out("Extremos:", ip_info.src, "<->", ip_info.dst, "| VLAN:", vlan_info)

out()
out("--- Stream reconstruido (ordem cronologica, cada bloco rotulado) ---")
full_stream_bytes = b""
for p in telnet_pkts:
    if Raw in p:
        tcp = p[TCP]
        direcao = "CLIENTE->SWITCH" if tcp.sport != 23 else "SWITCH->CLIENTE"
        payload = bytes(p[Raw].load)
        full_stream_bytes += payload
        texto = payload.decode("utf-8", errors="replace")
        out(f"[{direcao}] {texto!r}")

out()
out("--- Stream completo concatenado (decodificado) ---")
out(full_stream_bytes.decode("utf-8", errors="replace"))
