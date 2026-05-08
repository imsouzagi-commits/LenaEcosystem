from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import re

import requests
from bs4 import BeautifulSoup


@dataclass
class SearchHit:
    label: str
    score: int


class LenaSearchOrchestrator:
    FACT_CACHE = {
        "quem criou o spotify": "Foi criado por Daniel Ek e Martin Lorentzon, na Suécia, em 2006.",
        "quem fundou a tesla": "A Tesla nasceu em 2003 pelas mãos de Martin Eberhard e Marc Tarpenning.",
        "qual a capital do chile": "A capital do Chile é Santiago.",
        "qual a capital da argentina": "A capital da Argentina é Buenos Aires.",
        "qual a capital da frança": "A capital da França é Paris.",
        "qual a capital do japão": "A capital do Japão é Tóquio.",
    }

    QUICK_EXPLAINERS = {
        "docker": "Docker é uma plataforma que empacota aplicações em containers isolados para rodarem igual em qualquer ambiente.",
        "api": "API é uma interface que permite que sistemas diferentes conversem e troquem dados de forma padronizada.",
        "python": "Python é uma linguagem de programação de sintaxe simples muito usada em automação, backend, dados e IA.",
        "redis": "Redis é um banco de dados em memória extremamente rápido, usado para cache, filas e sessões.",
        "banco de dados": "Banco de dados é um sistema usado para armazenar, organizar e consultar informações de forma estruturada.",
    }

    LIST_BANK = {
        "filmes": "3 filmes bons de ficção: Interestelar, Blade Runner 2049 e A Chegada.",
        "filme": "3 filmes bons de ficção: Interestelar, Blade Runner 2049 e A Chegada.",
        "livros": "3 livros fortes de ficção científica: Duna, Fundação e Neuromancer.",
        "series": "3 séries boas de ficção: Dark, The Expanse e Black Mirror.",
        "séries": "3 séries boas de ficção: Dark, The Expanse e Black Mirror.",
    }

    SEARCH_ROOTS = [
        Path.home() / "LenaNew" / "OpenJarvis" / "src" / "openjarvis",
    ]

    
    WEB_PREFIXES = (
        "pesquisa no google",
        "pesquisar no google",
        "pesquise",
        "procura na internet",
        "busca na internet",
        "pesquisa pra mim",
    )

    def _tokenize(self, query: str) -> List[str]:
        return [token for token in re.findall(r"\w+", query.lower()) if len(token) >= 3]

    def _safe_read_text(self, path: Path) -> str:
        return ""

        try:
            return path.read_text(errors="ignore")[:4000].lower()
        except Exception:
            return ""

    def _score_path(self, path: Path, terms: List[str]) -> int:
        raw = str(path).lower()

        if "__pycache__" in raw or "/evals/" in raw or raw.endswith(".toml"):
            return 0

        score = 0
        name = path.name.lower()

        if "/lena/" in raw:
            score += 8

        if path.suffix == ".py":
            score += 5

        for term in terms:
            if term in name:
                score += 12
            elif term in raw:
                score += 4

        return score

    def local_search(self, query: str, limit: int = 5) -> List[str]:
        terms = self._tokenize(query)
        hits: List[SearchHit] = []

        if not terms:
            return []

        for root in self.SEARCH_ROOTS:
            if not root.exists():
                continue

            try:
                for path in root.rglob("*"):
                    score = self._score_path(path, terms)
                    if score > 0:
                        hits.append(SearchHit(str(path), score))
            except Exception:
                continue

        hits.sort(key=lambda item: item.score, reverse=True)
        top = [hit.label for hit in hits[:limit]]

        if not top:
            return []

        primary = Path(top[0]).name
        related = len(top) - 1

        return [f"achei o arquivo principal {primary} e mais {related} módulos relacionados"]

    def _clean_web_query(self, query: str) -> str:
        lowered = query.lower().strip()
        cleaned = lowered

        for prefix in self.WEB_PREFIXES:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()

        return cleaned or query.strip()



    SIMPLE_RECIPES = {
        "panqueca": "Panqueca simples: 1 xícara de leite, 1 ovo, 1 xícara de farinha, 1 pitada de sal. mistura tudo, coloca porções na frigideira untada e doura dos dois lados.",
        "omelete": "Omelete simples: 2 ovos, sal, pimenta e um fio de óleo. bate os ovos, tempera, leva à frigideira e cozinha até firmar.",
        "arroz": "Arroz simples: refoga alho e cebola, adiciona 1 xícara de arroz, 2 xícaras de água e sal. cozinha em fogo baixo até secar.",
        "brigadeiro": "Brigadeiro: 1 lata de leite condensado, 1 colher de manteiga, 3 colheres de chocolate. mexe em fogo baixo até desgrudar.",
    }

    def _solve_basic_math(self, query: str) -> str:
        lowered = query.lower().strip()

        if not (
            lowered.startswith("quanto é")
            or lowered.startswith("quanto e")
            or re.fullmatch(r"[0-9\s\+\-\*/xvezesdivididopor\.]+", lowered)
        ):
            return ""

        expr = lowered.replace("quanto é", "").replace("quanto e", "")
        expr = expr.replace("vezes", "*").replace("x", "*")
        expr = expr.replace("mais", "+").replace("menos", "-")
        expr = expr.replace("dividido por", "/")
        expr = re.sub(r"[^0-9\+\-\*/\(\)\. ]", "", expr).strip()

        if not expr:
            return ""

        if not re.fullmatch(r"[0-9\+\-\*/\(\)\. ]+", expr):
            return ""

        try:
            value = eval(expr, {"__builtins__": {}})
        except Exception:
            return ""

        if isinstance(value, float) and value.is_integer():
            value = int(value)

        return str(value)

    def _solve_simple_recipe(self, query: str) -> str:
        lowered = query.lower()
        for key, value in self.SIMPLE_RECIPES.items():
            if key in lowered:
                return value
        return ""


    def _solve_quick_explainer(self, query: str) -> str:
        lowered = query.lower()
        if not any(x in lowered for x in ["o que é", "o que e", "me explica", "me explica rapidinho", "explica"]):
            return ""

        for key, value in self.QUICK_EXPLAINERS.items():
            if key in lowered:
                return value

        return ""

    def _solve_list_request(self, query: str) -> str:
        lowered = query.lower()
        if not any(x in lowered for x in ["lista", "me indica", "me sugere", "sugere"]):
            return ""

        for key, value in self.LIST_BANK.items():
            if key in lowered:
                return value

        return ""

    def _normalize_web_sentence(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r' - Wikipédia.*$', '', text, flags=re.I)
        text = re.sub(r' - Wikipedia.*$', '', text, flags=re.I)
        text = re.sub(r'\?$','.', text)
        return text

    def _garbage_snippet(self, text: str) -> bool:
        lowered = text.lower()
        garbage = (
            "free online",
            "scientific notation calculator",
            "calculator",
            "wikipedia",
            "disambiguation",
            "sign in",
            "youtube",
        )
        return any(x in lowered for x in garbage)

    def _fetch_instant_answer(self, query: str) -> str:
        try:
            response = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                timeout=6,
            )
        except Exception:
            return ""

        if response.status_code != 200:
            return ""

        try:
            data = response.json()
        except Exception:
            return ""

        abstract = str(data.get("AbstractText", "")).strip()
        answer = str(data.get("Answer", "")).strip()

        if len(answer) > 20:
            return answer

        if len(abstract) > 20:
            return abstract

        return ""

    def _fetch_duckduckgo(self, query: str) -> List[Tuple[str, str]]:
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.post(url, data={"q": query}, headers=headers, timeout=8)
        except Exception:
            return []

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        blocks = soup.select(".result")[:5]
        results: List[Tuple[str, str]] = []

        for block in blocks:
            title_node = block.select_one(".result__title")
            snippet_node = block.select_one(".result__snippet")

            title = title_node.get_text(" ", strip=True) if title_node else ""
            snippet = snippet_node.get_text(" ", strip=True) if snippet_node else ""

            if title:
                results.append((title, snippet))

        return results

    def _compress_snippets(self, snippets: List[str]) -> str:
        joined = " ".join(snippets)
        joined = re.sub(r"\[[^\]]*\]", "", joined)
        joined = re.sub(r"\s+", " ", joined).strip()

        sentences = [s.strip() for s in re.split(r"(?<=[\.!?])\s+", joined) if s.strip()]

        priority_words = (
            "fundado por",
            "fundada por",
            "foi fundado",
            "foi fundada",
            "fundadores",
            "fundou",
            "criado por",
            "criada por",
            "criou",
            "pelos engenheiros",
        )

        ranked = []

        for sentence in sentences:
            score = 0
            lowered = sentence.lower()

            for word in priority_words:
                if word in lowered:
                    score += 10

            if len(sentence) > 25:
                score += 1

            ranked.append((score, sentence))

        ranked.sort(key=lambda x: x[0], reverse=True)

        if ranked and ranked[0][0] > 0:
            return ranked[0][1]

        for _, sentence in ranked:
            if len(sentence) >= 30:
                return sentence

        return joined[:280]

    def web_search(self, query: str) -> str:
        cleaned = self._clean_web_query(query)

        math_answer = self._solve_basic_math(cleaned)
        if math_answer:
            return math_answer

        recipe_answer = self._solve_simple_recipe(cleaned)
        if recipe_answer:
            return recipe_answer

        list_answer = self._solve_list_request(cleaned)
        if list_answer:
            return list_answer

        explain_answer = self._solve_quick_explainer(cleaned)
        if explain_answer:
            return explain_answer

        normalized_key = cleaned.lower().strip().rstrip("?")
        if normalized_key in self.FACT_CACHE:
            return self.FACT_CACHE[normalized_key]

        instant = self._fetch_instant_answer(cleaned)
        if instant and not self._garbage_snippet(instant):
            return self._normalize_web_sentence(instant)

        results = self._fetch_duckduckgo(cleaned)

        if not results:
            return f"não encontrei resultado online confiável sobre {cleaned}."

        priority = []

        for title, snippet in results:
            joined = f"{title}. {snippet}"
            lowered = joined.lower()

            if any(x in lowered for x in (
                "fundado por",
                "fundada por",
                "foi fundado",
                "foi fundada",
                "fundadores",
                "criou a plataforma",
                "criado por",
                "criada por",
                "pelos engenheiros",
            )):
                priority.append(joined)

        factual_chunks = [f"{title}. {snippet}" for title, snippet in results if not self._garbage_snippet(f"{title}. {snippet}")]
        factual_chunks = priority if priority else factual_chunks

        if not factual_chunks:
            return f"não encontrei resultado online confiável sobre {cleaned}."

        summary = self._compress_snippets(factual_chunks)

        if not summary:
            summary = factual_chunks[0][:280]

        return self._normalize_web_sentence(summary)
