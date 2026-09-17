"""Academic metadata retrieval. No general web search or full-text claims."""
import re
from html import unescape
from urllib.parse import quote

import requests


def plain_text(value):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", str(value or "")))).strip()


class AcademicSearchService:
    def __init__(self, session=None):
        self.session = session or requests.Session()

    def search(self, query, max_results=10):
        query = str(query or "").strip()[:500]
        limit = max(1, min(int(max_results), 20))
        results, warnings, providers = [], [], []
        if not query:
            return {"query": query, "results": [], "warnings": [], "providers": []}
        callbacks = [("Crossref", self._crossref)]
        for name, callback in callbacks:
            try:
                results.extend(callback(query, limit))
                providers.append(name)
            except (requests.RequestException, ValueError, KeyError, TypeError):
                # Do not expose request headers or credentials in errors.
                warnings.append(f"{name}: no se pudo completar la consulta académica.")
        unique = {}
        for item in results:
            key = (item.get("doi") or item["url"]).lower()
            if key not in unique or (not unique[key]["snippet"] and item["snippet"]):
                unique[key] = item
        return {"query": query, "results": list(unique.values()),
                "warnings": warnings, "providers": providers}

    def _crossref(self, query, limit):
        response = self.session.get(
            "https://api.crossref.org/works",
            params={"query.bibliographic": query, "rows": limit,
                    "filter": "type:journal-article,type:proceedings-article"},
            headers={"User-Agent": "ThesisSRS-AcademicRAG/1.0"}, timeout=30)
        response.raise_for_status()
        results = []
        for item in response.json().get("message", {}).get("items", []):
            if item.get("type") not in {"journal-article", "proceedings-article"}:
                continue
            title = plain_text((item.get("title") or [""])[0])
            doi = str(item.get("DOI") or "").strip()
            if not title or not doi:
                continue
            dates = (item.get("published") or {}).get("date-parts") or [[]]
            results.append({
                "title": title, "doi": doi,
                "url": "https://doi.org/" + quote(doi, safe="/"),
                "snippet": plain_text(item.get("abstract")),
                "authors": [" ".join(filter(None, [a.get("given"), a.get("family")]))
                            or a.get("name", "") for a in item.get("author", [])],
                "year": str(dates[0][0]) if dates[0] else "",
                "venue": plain_text((item.get("container-title") or [""])[0]),
                "provider": "Crossref", "document_type": item["type"],
                "evidence_type": "abstract" if item.get("abstract") else "metadata_only",
            })
        return results


