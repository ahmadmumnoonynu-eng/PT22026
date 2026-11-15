import { ArrowRight, Compass, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";

export function HomePage() {
  return (
    <div className="space-y-8 lg:space-y-10">
      <section className="hero-orbit relative isolate overflow-hidden rounded-[28px] border border-[var(--mm-border)] px-6 py-12 shadow-[var(--mm-card-shadow)] sm:px-10 sm:py-16 lg:px-14 lg:py-20">
        <div className="relative z-10 max-w-2xl">
          <p className="mb-4 flex items-center gap-2 text-sm font-bold text-[var(--mm-accent)]"><Sparkles aria-hidden="true" className="size-4" /> MovieMind</p>
          <h1 className="max-w-xl text-4xl font-black leading-[1.03] tracking-tight text-[var(--mm-text)] sm:text-5xl lg:text-6xl">Your Personal Movie <span className="text-gradient">Companion</span></h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-[var(--mm-text-muted)] sm:text-lg">Discover films you will love and shape recommendations around your own taste.</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/discover"><Button><Compass aria-hidden="true" className="size-4" /> Start exploring</Button></Link>
            <Link className="inline-flex min-h-11 items-center gap-2 rounded-2xl border border-[var(--mm-border)] bg-black/15 px-5 text-sm font-semibold text-[var(--mm-text)] transition hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--mm-accent)]" to="/register">Create your account <ArrowRight aria-hidden="true" className="size-4" /></Link>
          </div>
        </div>
        <div aria-hidden="true" className="hero-reel absolute inset-y-0 right-0 w-1/2 opacity-70" />
      </section>
      <section aria-labelledby="catalogue-status" className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_20rem]">
        <div>
          <div className="mb-4 flex items-center justify-between gap-4">
            <div><p className="text-sm font-semibold text-[var(--mm-gold)]">Your movie space</p><h2 id="catalogue-status" className="mt-1 text-2xl font-bold">Ready for discovery</h2></div>
            <Link className="hidden text-sm font-semibold text-[var(--mm-accent)] hover:text-white sm:block" to="/discover">Open Discover <span aria-hidden="true">→</span></Link>
          </div>
          <EmptyState title="The catalogue is next" description="The application shell is ready. The next phase will connect the real MovieMind catalogue, search, and movie details." action={<Link to="/discover"><Button variant="secondary">See the discovery plan</Button></Link>} />
        </div>
        <aside className="rounded-3xl border border-[var(--mm-border)] bg-linear-to-br from-[#2B1C49] to-[var(--mm-surface)] p-6 shadow-[var(--mm-card-shadow)]">
          <Sparkles aria-hidden="true" className="size-7 text-[var(--mm-accent)]" />
          <h2 className="mt-6 text-xl font-bold">Recommendations that grow with you</h2>
          <p className="mt-3 text-sm leading-6 text-[var(--mm-text-muted)]">Your personalized recommendations will use ratings returned by MovieMind—not made-up suggestions.</p>
          <Link className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-[var(--mm-accent)] hover:text-white" to="/ratings">How ratings work <ArrowRight aria-hidden="true" className="size-4" /></Link>
        </aside>
      </section>
    </div>
  );
}
