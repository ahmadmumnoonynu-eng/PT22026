import { Search } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";

import { Navigation } from "@/components/layout/Navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/features/auth/AuthProvider";

export function AppShell() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const { isAuthenticated, signOut, user } = useAuth();

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    const search = params.toString();
    navigate({ pathname: "/search", search: search ? `?${search}` : "" });
  }

  return (
    <div className="min-h-screen bg-[var(--mm-bg)] text-[var(--mm-text)] lg:grid lg:grid-cols-[15.5rem_minmax(0,1fr)]">
      <Navigation />
      <div className="min-w-0">
        <header className="sticky top-0 z-20 flex min-h-20 items-center justify-between gap-4 border-b border-[var(--mm-border)] bg-[color:rgb(8_11_27_/_0.88)] px-4 backdrop-blur-xl sm:px-6 lg:px-10">
          <form className="relative hidden w-full max-w-xl md:block" onSubmit={submitSearch} role="search">
            <label className="sr-only" htmlFor="global-movie-search">Search for movies or genres</label>
            <Search aria-hidden="true" className="pointer-events-none absolute left-4 top-1/2 size-5 -translate-y-1/2 text-[var(--mm-text-subtle)]" />
            <Input id="global-movie-search" onChange={(event) => setQuery(event.target.value)} placeholder="Search for movies, genres..." value={query} className="rounded-full pl-12 pr-28" />
            <button className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full px-3 py-2 text-sm font-semibold text-[var(--mm-accent)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--mm-accent)]" type="submit">Search</button>
          </form>
          <Link className="font-bold tracking-tight text-[var(--mm-text)] md:hidden" to="/">Movie<span className="text-[var(--mm-accent)]">Mind</span></Link>
          <nav aria-label="Account" className="ml-auto flex items-center gap-2">
            {isAuthenticated && user ? <><Link aria-label="Open profile" className="hidden items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-[var(--mm-text-muted)] transition hover:bg-white/5 hover:text-[var(--mm-text)] sm:flex" to="/profile"><span className="grid size-7 place-items-center rounded-full bg-[var(--mm-primary-deep)] text-xs text-white">{(user.display_name ?? user.username ?? user.email).slice(0, 1).toUpperCase()}</span>{user.display_name ?? user.username ?? "Account"}</Link><Button className="min-h-10 rounded-xl px-4" onClick={signOut} variant="secondary">Sign out</Button></> : <><Link className="hidden rounded-xl px-3 py-2 text-sm font-semibold text-[var(--mm-text-muted)] transition hover:bg-white/5 hover:text-[var(--mm-text)] sm:block" to="/login">Log in</Link><Link to="/register"><Button className="min-h-10 rounded-xl px-4">Create account</Button></Link></>}
          </nav>
        </header>
        <main className="mx-auto w-full max-w-[1440px] px-4 py-6 pb-24 sm:px-6 sm:py-8 lg:px-10 lg:pb-10"><Outlet /></main>
      </div>
    </div>
  );
}
