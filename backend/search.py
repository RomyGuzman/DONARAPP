import json
import math
import re
from collections import defaultdict

STOPWORDS = {
    "me", "te", "se", "le", "lo", "la", "los", "las", "un", "una", "unos", "unas",
    "el", "al", "del", "de", "que", "y", "en", "a", "con", "por", "para", "es",
    "su", "sus", "mi", "mis", "tu", "tus", "si", "o", "e", "no", "ni",
    "hace", "desde", "hasta", "como", "cuando", "donde", "que",
}

class MotorBusqueda:

    def __init__(self):
        self.docs: list[str] = []
        self.tfidf: list[dict] = []
        self.idf: dict = {}

    def _tokenizar(self, texto: str, filtrar_stop: bool = True) -> list[str]:
        tokens = re.findall(r"[a-záéíóúüñ]+", texto.lower())
        if filtrar_stop:
            tokens = [t for t in tokens if t not in STOPWORDS]
        return tokens

    def construir_indice(self, documentos: list[str]):
        self.docs = documentos
        N = len(documentos)
        tf_raw: list[dict] = []

        for doc in documentos:
            # Filtramos stopwords en la indexación para mejorar precisión
            tokens = self._tokenizar(doc, filtrar_stop=True)
            conteo: dict = defaultdict(int)
            for t in tokens:
                conteo[t] += 1
            total = len(tokens) or 1
            tf_raw.append({t: c / total for t, c in conteo.items()})

        df: dict = defaultdict(int)
        for tf in tf_raw:
            for t in tf:
                df[t] += 1
        self.idf = {t: math.log((N + 1) / (d + 1)) + 1 for t, d in df.items()}

        self.tfidf = [
            {t: v * self.idf.get(t, 1) for t, v in tf.items()}
            for tf in tf_raw
        ]

    # ── Persistencia ──────────────────────────────────────────────────────────
    def guardar_indice(self, ruta: str):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump({"docs": self.docs, "idf": self.idf, "tfidf": self.tfidf}, f, ensure_ascii=False)

    def cargar_indice(self, ruta: str) -> bool:
        try:
            with open(ruta, encoding="utf-8") as f:
                data = json.load(f)
            self.docs = data["docs"]
            self.idf = data["idf"]
            self.tfidf = data["tfidf"]
            return True
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return False

    # ── Búsqueda ──────────────────────────────────────────────────────────────
    def _vec_query(self, query: str) -> dict:
        # Filtramos stopwords de la query también (POS-aware via lista)
        tokens = self._tokenizar(query, filtrar_stop=True)
        conteo: dict = defaultdict(int)
        for t in tokens:
            conteo[t] += 1
        total = len(tokens) or 1
        return {t: (c / total) * self.idf.get(t, 1) for t, c in conteo.items()}

    def _coseno(self, v1: dict, v2: dict) -> float:
        comunes = set(v1) & set(v2)
        dot = sum(v1[t] * v2[t] for t in comunes)
        n1 = math.sqrt(sum(x ** 2 for x in v1.values()))
        n2 = math.sqrt(sum(x ** 2 for x in v2.values()))
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1 * n2)

    def _snippet(self, doc: str, query_tokens: set, max_words: int = 15) -> str:
        palabras = doc.split()
        for i, p in enumerate(palabras):
            if p.lower() in query_tokens:
                start = max(0, i - 3)
                end = min(len(palabras), i + max_words - 3)
                return f"...{' '.join(palabras[start:end])}..."
        return " ".join(palabras[:max_words]) + "..."

    def buscar(self, query: str, top_k: int = 5) -> list[tuple]:
        q_vec = self._vec_query(query)
        q_tokens = set(self._tokenizar(query, filtrar_stop=False))
        resultados = []
        for i, tfidf_doc in enumerate(self.tfidf):
            score = self._coseno(q_vec, tfidf_doc)
            snippet = self._snippet(self.docs[i], q_tokens)
            resultados.append((self.docs[i], round(score, 4), snippet))
        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados[:top_k]

    def frecuencia_terminos(self, top_n: int = 30) -> list[dict]:
        """Términos más frecuentes en el corpus (para nube de palabras)."""
        conteo: dict = defaultdict(int)
        for doc in self.docs:
            for t in self._tokenizar(doc, filtrar_stop=True):
                conteo[t] += 1
        ordenado = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        return [{"term": t, "freq": f} for t, f in ordenado[:top_n]]

    # ── Evaluación P / R / F1 ─────────────────────────────────────────────────
    def evaluar(self, consultas_etiquetadas: list[dict], umbral: float = 0.05) -> dict:
        resultados_por_consulta = []
        for item in consultas_etiquetadas:
            recuperados = self.buscar(item["query"])
            relevantes_set = set(item["relevantes"])
            recuperados_idx = []
            for r in recuperados:
                if r[1] >= umbral:
                    try:
                        recuperados_idx.append(self.docs.index(r[0]))
                    except ValueError:
                        pass
            recuperados_set = set(recuperados_idx)
            tp = len(relevantes_set & recuperados_set)
            precision = tp / len(recuperados_set) if recuperados_set else 0.0
            recall = tp / len(relevantes_set) if relevantes_set else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
            resultados_por_consulta.append({
                "query": item["query"],
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1": round(f1, 3),
            })
        avg_p = sum(r["precision"] for r in resultados_por_consulta) / max(len(resultados_por_consulta), 1)
        avg_r = sum(r["recall"] for r in resultados_por_consulta) / max(len(resultados_por_consulta), 1)
        avg_f1 = sum(r["f1"] for r in resultados_por_consulta) / max(len(resultados_por_consulta), 1)
        return {
            "promedio": {"precision": round(avg_p, 3), "recall": round(avg_r, 3), "f1": round(avg_f1, 3)},
            "por_consulta": resultados_por_consulta,
        }
