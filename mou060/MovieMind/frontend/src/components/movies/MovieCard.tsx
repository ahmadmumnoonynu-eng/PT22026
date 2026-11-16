import { Star } from "lucide-react";
import { Link } from "react-router-dom";

import { MoviePoster } from "@/components/movies/MoviePoster";
import type { Movie } from "@/types/api";

type MovieCardProps = { movie: Movie; priority?: boolean };

export function MovieCard({ movie, priority = false }: MovieCardProps) {
  const genres = movie.genres.slice(0, 2).join(" · ");

  return (
    <article className="group overflow-hidden rounded-2xl border border-[var(--mm-border)] bg-[var(--mm-surface)] shadow-[var(--mm-card-shadow)] transition duration-200 motion-safe:hover:-translate-y-1 motion-safe:hover:border-[rgba(193,123,255,.4)]">
      <Link aria-label={`View details for ${movie.title}`} className="block focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--mm-accent)]" to={`/movies/${movie.id}`}>
        <MoviePoster className="aspect-[2/3]" movie={movie} priority={priority} />
        <div className="space-y-2 p-3.5">
          <h3 className="line-clamp-2 min-h-10 text-sm font-bold leading-5 text-[var(--mm-text)]">{movie.title}</h3>
          <div className="flex items-center justify-between gap-2 text-xs text-[var(--mm-text-muted)]">
            <span>{movie.release_year ?? "Year unavailable"}</span>
            {movie.average_rating !== null && (
              <span className="inline-flex items-center gap-1 font-semibold text-[var(--mm-gold)]"><Star aria-hidden="true" className="size-3.5 fill-current" /> {movie.average_rating.toFixed(1)}</span>
            )}
          </div>
          {genres && <p className="truncate text-xs text-[var(--mm-text-subtle)]">{genres}</p>}
        </div>
      </Link>
    </article>
  );
}
