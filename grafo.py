import heapq
from collections import deque


class Grafo:
    def __init__(self, num_vertices, direcionado=False, ponderado=False, base=0):
        self.num_vertices = num_vertices
        self.direcionado = direcionado
        self.ponderado = ponderado
        self.base = base
        self.vertices = list(range(base, base + num_vertices))

    def adicionar_aresta(self, origem, destino, peso=1):
        self._inserir(origem, destino, peso)
        if not self.direcionado:
            self._inserir(destino, origem, peso)

    def _inserir(self, origem, destino, peso):
        raise NotImplementedError

    def vizinhos(self, v):
        raise NotImplementedError

    @classmethod
    def ler_arquivo(cls, caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [l.split() for l in f if l.strip()]
        if not linhas or len(linhas[0]) < 4:
            raise ValueError("Cabecalho invalido, esperado 'V A D P'")

        num_vertices, num_arestas, direcionado, ponderado = (int(x) for x in linhas[0][:4])
        corpo = linhas[1:]
        if len(corpo) < num_arestas:
            raise ValueError(f"Esperadas {num_arestas} arestas, encontradas {len(corpo)}")
        corpo = corpo[:num_arestas]

        ids = [int(p[i]) for p in corpo for i in (0, 1)]
        base = 1 if ids and min(ids) >= 1 and max(ids) >= num_vertices else 0

        g = cls(num_vertices, direcionado == 1, ponderado == 1, base)
        for partes in corpo:
            if ponderado and len(partes) < 3:
                raise ValueError(f"Aresta sem peso: {' '.join(partes)}")
            peso = float(partes[2]) if ponderado else 1
            if isinstance(peso, float) and peso.is_integer():
                peso = int(peso)
            g.adicionar_aresta(int(partes[0]), int(partes[1]), peso)
        return g

    def __str__(self):
        tipo = "direcionado" if self.direcionado else "nao direcionado"
        tipo += ", ponderado" if self.ponderado else ", nao ponderado"
        linhas = [f"{type(self).__name__} ({tipo}) com {self.num_vertices} vertices"]
        for v in self.vertices:
            if self.ponderado:
                viz = ", ".join(f"{d}(p={p})" for d, p in self.vizinhos(v))
            else:
                viz = ", ".join(str(d) for d, _ in self.vizinhos(v))
            linhas.append(f"  {v} -> [{viz}]")
        return "\n".join(linhas)


class GrafoLista(Grafo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adj = {v: [] for v in self.vertices}

    def _inserir(self, origem, destino, peso):
        self.adj[origem].append((destino, peso))

    def vizinhos(self, v):
        return sorted(self.adj[v])


class GrafoMatriz(Grafo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        n = self.num_vertices
        self.mat = [[None] * n for _ in range(n)]

    def _inserir(self, origem, destino, peso):
        self.mat[origem - self.base][destino - self.base] = peso

    def vizinhos(self, v):
        linha = self.mat[v - self.base]
        return [(j + self.base, p) for j, p in enumerate(linha) if p is not None]


def busca_em_largura(grafo, inicio):
    visitado = {inicio}
    ordem = []
    fila = deque([inicio])
    while fila:
        atual = fila.popleft()
        ordem.append(atual)
        for vizinho, _ in grafo.vizinhos(atual):
            if vizinho not in visitado:
                visitado.add(vizinho)
                fila.append(vizinho)
    return ordem


def busca_em_profundidade(grafo, inicio):
    visitado = set()
    ordem = []
    pilha = [inicio]
    while pilha:
        atual = pilha.pop()
        if atual in visitado:
            continue
        visitado.add(atual)
        ordem.append(atual)
        for vizinho, _ in reversed(grafo.vizinhos(atual)):
            if vizinho not in visitado:
                pilha.append(vizinho)
    return ordem


def dijkstra(grafo, inicio):
    distancia = {v: float("inf") for v in grafo.vertices}
    pai = {v: None for v in grafo.vertices}
    distancia[inicio] = 0
    fila = [(0, inicio)]
    while fila:
        d, atual = heapq.heappop(fila)
        if d > distancia[atual]:
            continue
        for vizinho, peso in grafo.vizinhos(atual):
            nova = d + peso
            if nova < distancia[vizinho]:
                distancia[vizinho] = nova
                pai[vizinho] = atual
                heapq.heappush(fila, (nova, vizinho))

    caminho = {}
    for v in grafo.vertices:
        if distancia[v] == float("inf"):
            caminho[v] = None
            continue
        cam = [v]
        while cam[-1] != inicio:
            cam.append(pai[cam[-1]])
        caminho[v] = cam[::-1]
    return distancia, caminho


def executar(grafo, origem):
    print(grafo)
    print(f"BFS a partir de {origem}: {busca_em_largura(grafo, origem)}")
    print(f"DFS a partir de {origem}: {busca_em_profundidade(grafo, origem)}")
    distancia, caminho = dijkstra(grafo, origem)
    print(f"Dijkstra a partir de {origem}:")
    for v in grafo.vertices:
        print(f"  {v}: distancia={distancia[v]}  caminho={caminho[v]}")
    print()


if __name__ == "__main__":
    import sys

    arquivo = sys.argv[1] if len(sys.argv) > 1 else "grafo.txt"
    for classe in (GrafoLista, GrafoMatriz):
        g = classe.ler_arquivo(arquivo)
        origem = int(sys.argv[2]) if len(sys.argv) > 2 else g.vertices[0]
        executar(g, origem)
