
# Hybrid retrieval using FAISS semantic search and keyword matching.
# Multi-answer table questions retrieve all rows from the requested section.

import re
import faiss


class Retriever:

    def __init__(self, embedder):
        self.embedder = embedder
        self.index = None
        self.chunks = []

        self.stop_words = {
            "what", "is", "are", "the", "a", "an",
            "of", "for", "in", "on", "to", "and",
            "does", "do", "how", "which", "who"
        }

    def _normalize_words(self, text):
        words = re.findall(r"[a-zA-Z0-9]+", text.lower())

        normalized = []

        for word in words:
            if word in self.stop_words:
                continue

            if word.endswith("ies") and len(word) > 4:
                word = word[:-3] + "y"
            elif word.endswith("s") and len(word) > 3:
                word = word[:-1]

            normalized.append(word)

        return normalized

    def _keyword_score(self, question, chunk_text):
        query_words = set(self._normalize_words(question))
        chunk_words = set(self._normalize_words(chunk_text))

        if not query_words or not chunk_words:
            return 0.0

        matched_words = query_words.intersection(chunk_words)

        return len(matched_words) / len(query_words)

    def _get_table_section(self, question):
        q = question.lower()

        multi_patterns = [
            r"\bwhat are\b",
            r"\blist\b",
            r"\bcharacteristics\b",
            r"\benumerate\b",
            r"\bfeatures\b",
        ]

        is_multi = any(
            re.search(pattern, q)
            for pattern in multi_patterns
        )

        if not is_multi:
            return None

        if "solar pv" in q or "pv" in q:
            return "solar pv characteristic"

        if "wind turbine" in q or "wind" in q:
            return "wind turbine characteristic"

        return None

    def build(self, chunks):
        if not chunks:
            raise ValueError("There are no chunks to index.")

        texts = [chunk["text"] for chunk in chunks]

        vectors = self.embedder.encode(texts)

        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

        self.chunks = chunks

    def search(self, question, top_k=3):

        if self.index is None:
            raise RuntimeError(
                "Build the index with a document before searching."
            )

        if not question or not question.strip():
            raise ValueError("The question is empty.")

        if not self.chunks:
            return []

        top_k = max(1, min(top_k, len(self.chunks)))

        query_vector = self.embedder.encode([question])

        scores, positions = self.index.search(
            query_vector,
            len(self.chunks)
        )

        results = []

        for score, position in zip(scores[0], positions[0]):

            if position < 0:
                continue

            chunk = dict(self.chunks[position])

            semantic_score = float(score)

            keyword_score = self._keyword_score(
                question,
                chunk["text"]
            )

            table_bonus = (
                0.03
                if chunk.get("type") == "table"
                else 0.0
            )

            hybrid_score = (
                0.55 * semantic_score
                + 0.45 * keyword_score
                + table_bonus
            )

            chunk["semantic_score"] = semantic_score
            chunk["keyword_score"] = keyword_score
            chunk["score"] = hybrid_score
            chunk["_position"] = int(position)

            results.append(chunk)

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        # Special handling for Solar PV and Wind Turbine
        # multi-answer table questions.
        required_section = self._get_table_section(question)

        if required_section:

            table_rows = [
                item
                for item in results
                if (
                    item.get("type") == "table"
                    and required_section in item["text"].lower()
                    and "|" in item["text"]
                )
            ]

            if table_rows:

                # Restore the original document order.
                table_rows.sort(
                    key=lambda item: item["_position"]
                )

                for item in table_rows:
                    item.pop("_position", None)

                return table_rows

        # Normal questions continue to use Top-K retrieval.
        results = results[:top_k]

        for item in results:
            item.pop("_position", None)

        return results
