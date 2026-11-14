

from app.db.base import Base
from app.db.models.movie import Genre, Movie, MovieGenre
from app.db.models.rating import Rating
from app.db.models.user import User, UserRole
from app.db.models.watchlist import WatchlistItem

__all__ = [
    "Base",
    "Genre",
    "Movie",
    "MovieGenre",
    "Rating",
    "User",
    "UserRole",
    "WatchlistItem",
]
