import { Bookmark, BookmarkCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { useAuth } from "@/features/auth/AuthProvider";
import { useAddToWatchlist, useRemoveFromWatchlist, useWatchlist } from "@/features/watchlist/hooks";
import { isApiClientError } from "@/lib/api/errors";

export function WatchlistButton({ movieId }: { movieId: string }) {
  const { isAuthenticated } = useAuth();
  const list = useWatchlist(0, 100, isAuthenticated);
  const add = useAddToWatchlist();
  const remove = useRemoveFromWatchlist();
  const [message, setMessage] = useState<string | null>(null);
  const inWatchlist = list.data?.items.some((item) => item.movie.id === movieId) ?? false;
  const pending = add.isPending || remove.isPending;

  useEffect(() => setMessage(null), [inWatchlist]);
  if (!isAuthenticated) return <Link to="/login"><Button variant="secondary"><Bookmark aria-hidden="true" className="size-4" /> Sign in to save</Button></Link>;

  async function toggle() {
    setMessage(null);
    try {
      if (inWatchlist) await remove.mutateAsync(movieId);
      else await add.mutateAsync(movieId);
      setMessage(inWatchlist ? "Removed from your list." : "Added to your list.");
    } catch (error) {
      setMessage(isApiClientError(error) ? error.message : "We could not update your list.");
    }
  }

  return <div className="space-y-2"><Button disabled={pending || list.isLoading} isLoading={pending} onClick={() => void toggle()} variant={inWatchlist ? "secondary" : "primary"}>{inWatchlist ? <BookmarkCheck aria-hidden="true" className="size-4" /> : <Bookmark aria-hidden="true" className="size-4" />}{inWatchlist ? "Saved to My List" : "Add to My List"}</Button>{message && <p className={`text-sm ${message.includes("could not") || message.includes("Too many") ? "text-[var(--mm-danger)]" : "text-[var(--mm-success)]"}`} role="status">{message}</p>}</div>;
}
