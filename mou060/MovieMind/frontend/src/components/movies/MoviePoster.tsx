import { Film } from "lucide-react";
import { useEffect, useState } from "react";

import type { Movie } from "@/types/api";

type MoviePosterProps = {
  className?: string;
  movie: Pick<Movie, "poster_url" | "title">;
  priority?: boolean;
};

export function MoviePoster({ className = "", movie, priority = false }: MoviePosterProps) {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [movie.poster_url, movie.title]);
  const canShowImage = Boolean(movie.poster_url) && !failed;

  return (
    <div className={`relative overflow-hidden bg-[linear-gradient(145deg,#30215c,#10162f)] ${className}`}>
      {canShowImage ? (
        <img
          alt={`Poster for ${movie.title}`}
          className="size-full object-cover"
          loading={priority ? "eager" : "lazy"}
          onError={() => setFailed(true)}
          src={movie.poster_url ?? undefined}
        />
      ) : (
        <div className="flex size-full flex-col items-center justify-center gap-3 bg-[radial-gradient(circle_at_50%_30%,rgba(193,123,255,.25),transparent_45%),linear-gradient(145deg,#241e4c,#10162f)] px-4 text-center">
          <Film aria-hidden="true" className="size-9 text-[var(--mm-accent)]" />
          <span className="line-clamp-2 text-xs font-semibold text-[var(--mm-text-muted)]">{movie.title}</span>
        </div>
      )}
    </div>
  );
}
