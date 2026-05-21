import math
from collections import defaultdict

class ModeloNgramas:
    def __init__(self, k: float = 1.0):
        self.k = k
        self.bigramas = defaultdict(lambda: defaultdict(int))
        self.trigramas = defaultdict(lambda: defaultdict(int))
        self.unigramas = defaultdict(int)
        self.vocab = set()

    def entrenar(self, corpus: list[str], k: float | None = None):
        if k is not None:
            self.k = k
        self.bigramas = defaultdict(lambda: defaultdict(int))
        self.trigramas = defaultdict(lambda: defaultdict(int))
        self.unigramas = defaultdict(int)
        self.vocab = set()

        for texto in corpus:
            palabras = ["<s>"] + texto.lower().split() + ["</s>"]
            for i, p in enumerate(palabras):
                self.unigramas[p] += 1
                self.vocab.add(p)
                if i > 0:
                    self.bigramas[palabras[i - 1]][p] += 1
                if i > 1:
                    ctx = (palabras[i - 2], palabras[i - 1])
                    self.trigramas[ctx][p] += 1

    def prob_bigrama(self, palabra: str, anterior: str) -> float:
        V = len(self.vocab)
        num = self.bigramas[anterior][palabra] + self.k
        den = self.unigramas[anterior] + self.k * V
        return num / den

    def prob_trigrama(self, palabra: str, ant1: str, ant2: str) -> float:
        V = len(self.vocab)
        ctx = (ant1, ant2)
        num = self.trigramas[ctx][palabra] + self.k
        den = sum(self.trigramas[ctx].values()) + self.k * V
        return num / den

    def perplejidad(self, texto: str) -> float:
        palabras = ["<s>"] + texto.lower().split() + ["</s>"]
        N = len(palabras)
        if N < 2:
            return 0.0
        log_prob = 0.0
        for i in range(1, N):
            p = self.prob_bigrama(palabras[i], palabras[i - 1])
            log_prob += math.log(p)
        return math.exp(-log_prob / N)

    def tabla_bigramas(self, top_n: int = 10) -> list[dict]:
        filas = []
        for ctx, siguientes in self.bigramas.items():
            for palabra, conteo in siguientes.items():
                prob = self.prob_bigrama(palabra, ctx)
                filas.append({"contexto": ctx, "siguiente": palabra, "prob": round(prob, 6), "conteo": conteo})
        filas.sort(key=lambda x: x["prob"], reverse=True)
        return filas[:top_n]

    def tabla_trigramas(self, top_n: int = 10) -> list[dict]:
        filas = []
        for ctx, siguientes in self.trigramas.items():
            for palabra, conteo in siguientes.items():
                prob = self.prob_trigrama(palabra, ctx[0], ctx[1])
                filas.append({"contexto": f"{ctx[0]} {ctx[1]}", "siguiente": palabra, "prob": round(prob, 6), "conteo": conteo})
        filas.sort(key=lambda x: x["prob"], reverse=True)
        return filas[:top_n]
