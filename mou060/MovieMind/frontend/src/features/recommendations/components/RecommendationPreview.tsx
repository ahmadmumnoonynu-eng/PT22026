import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { StatusPanel } from "@/components/ui/StatusPanel";
import { useAuth } from "@/features/auth/AuthProvider";
import { useMyRecommendations } from "@/features/recommendations/hooks";
import { isApiClientError } from "@/lib/api/errors";

export function RecommendationPreview() {
  const { isAuthenticated } = useAuth();
  const recommendations = useMyRecommendations(3, isAuthenticated);
  if (!isAuthenticated) return <GuestPreview />;
  if (recommendations.isLoading) return <aside className="rounded-3xl border border-[var(--mm-border)] bg-[var(--mm-surface)] p-6 shadow-[var(--mm-card-shadow)]"><StatusPanel>Finding your recommendations…</StatusPanel></aside>;
  if (recommendations.error) return <aside className="rounded-3xl border border-[var(--mm-border)] bg-[var(--mm-surface)] p-6 shadow-[var(--mm-card-shadow)]"><StatusPanel tone="error">{isApiClientError(recommendations.error) ? recommendations.error.message : "We could not load your recommendations."}</StatusPanel></aside>;
  const first = recommendations.data?.items[0];
  if (!first) return <aside className="rounded-3xl border border-[var(--mm-border)] bg-[var(--mm-surface)] p-6 shadow-[var(--mm-card-shadow)]"><Sparkles aria-hidden="true" className="size-7 text-[var(--mm-accent)]" /><h2 className="mt-5 text-xl font-bold">Recommendations are waiting</h2><p className="mt-3 text-sm leading-6 text-[var(--mm-text-muted)]">Rate a few movies to help MovieMind find more to show you.</p><Link className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-[var(--mm-accent)] hover:text-white" to="/discover">Explore movies <ArrowRight aria-hidden="true" className="size-4" /></Link></aside>;
  return <aside className="rounded-3xl border border-[var(--mm-border)] bg-linear-to-br from-[#2B1C49] to-[var(--mm-surface)] p-6 shadow-[var(--mm-card-shadow)]"><Sparkles aria-hidden="true" className="size-7 text-[var(--mm-accent)]" /><p className="mt-5 text-sm font-bold text-[var(--mm-accent)]">{recommendations.data?.is_fallback ? "Popular picks while you get started" : "Recommended for you"}</p><h2 className="mt-2 text-xl font-bold">{first.movie.title}</h2><p className="mt-3 text-sm leading-6 text-[var(--mm-text-muted)]">{first.reason}</p><Link className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-[var(--mm-accent)] hover:text-white" to="/recommendations">See all recommendations <ArrowRight aria-hidden="true" className="size-4" /></Link></aside>;
}

function GuestPreview() {
  return <aside className="rounded-3xl border border-[var(--mm-border)] bg-linear-to-br from-[#2B1C49] to-[var(--mm-surface)] p-6 shadow-[var(--mm-card-shadow)]"><Sparkles aria-hidden="true" className="size-7 text-[var(--mm-accent)]" /><h2 className="mt-6 text-xl font-bold">Recommendations that grow with you</h2><p className="mt-3 text-sm leading-6 text-[var(--mm-text-muted)]">Create an account and rate movies to get recommendations based on your taste.</p><Link className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-[var(--mm-accent)] hover:text-white" to="/register">Create an account <ArrowRight aria-hidden="true" className="size-4" /></Link></aside>;
}
