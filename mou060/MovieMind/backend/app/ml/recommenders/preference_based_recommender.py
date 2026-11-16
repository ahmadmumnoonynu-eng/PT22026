from __future__ import annotations

import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.movie import Movie, MovieGenre
from app.ml.recommenders.content_based_recommender import (
    compute_genre_preferences,
    score_by_preferences,
)
from app.services.recommendation_service import RecommendationItem, RecommendationStrategy


class PreferenceBasedRecommender(RecommendationStrategy):
    """Recommend movies using a preference profile built from chosen genres + favorite movies."""

    source = "preference_based"

    def __init__(
        self,
        db: Session,
        *,
        favorite_genres: list[str],
        favorite_movie_ids: list[uuid.UUID] | list[str],
        description: str | None = None,
    ) -> None:
        self._db = db
        self._favorite_genres = [genre.strip() for genre in favorite_genres if genre and genre.strip()]
        self._favorite_movie_ids = {
            uuid.UUID(str(movie_id)) for movie_id in favorite_movie_ids if str(movie_id).strip()
        }
        self._description = description.strip() if description and description.strip() else None

    def _load_favorite_movies(self) -> list[Movie]:
        if not self._favorite_movie_ids:
            return []
        return list(
            self._db.scalars(
                select(Movie)
                .where(Movie.id.in_(sorted(self._favorite_movie_ids)))
                .options(selectinload(Movie.genre_links).selectinload(MovieGenre.genre))
            ).all()
        )

    def _description_terms(self) -> set[str]:
        if not self._description:
            return set()
        words = re.findall(r"[a-zA-Z0-9]+", self._description.lower())
        return {word for word in words if len(word) > 2}

    def recommend(self, *, limit: int) -> list[RecommendationItem]:
        favorite_movies = self._load_favorite_movies()
        profile: dict[str, float] = {}
        for genre in self._favorite_genres:
            profile[genre] = profile.get(genre, 0.0) + 2.5
        for movie in favorite_movies:
            for genre in movie.genres:
                profile[genre] = profile.get(genre, 0.0) + 1.5

        # The repository ships with existing movie metadata, not an external TF-IDF
        # training artifact; we therefore reuse the same content-based ranking logic
        # that is already part of the application and feed it the explicit preference profile.
        notes = [(movie.genres, 5.0) for movie in favorite_movies]
        profile.update(compute_genre_preferences(notes))

        if not profile:
            return []

        description_terms = self._description_terms()
        movies = list(
            self._db.scalars(
                select(Movie)
                .where(Movie.id.not_in(sorted(self._favorite_movie_ids)))
                .options(selectinload(Movie.genre_links).selectinload(MovieGenre.genre))
            ).all()
        )

        ranked: list[RecommendationItem] = []
        for movie in movies:
            score = score_by_preferences(movie.genres, profile)
            if description_terms:
                haystack = " ".join(
                    part for part in [movie.title, movie.overview or "", " ".join(movie.genres)]
                ).lower()
                boost = sum(1 for term in description_terms if term in haystack)
                score += boost * 0.15
            if score <= 0:
                continue
            ranked.append(
                RecommendationItem(
                    movie=movie,
                    score=float(score),
                    source=self.source,
                    reason="Matches the preference profile you saved",
                )
            )

        ranked.sort(key=lambda item: (-item.score, item.movie.title, str(item.movie.id)))
        return ranked[:limit]
