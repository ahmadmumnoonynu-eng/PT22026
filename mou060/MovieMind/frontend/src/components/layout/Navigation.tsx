import { Bookmark, Compass, Film, Home, Settings, Star, UserRound } from "lucide-react";
import { NavLink } from "react-router-dom";

const items = [
  { icon: Home, label: "Home", to: "/" },
  { icon: Compass, label: "Discover", to: "/discover" },
  { icon: Bookmark, label: "My List", to: "/watchlist" },
  { icon: Star, label: "Ratings", to: "/ratings" },
  { icon: UserRound, label: "Profile", to: "/profile" },
  { icon: Settings, label: "Settings", to: "/settings" },
];

export function Navigation() {
  return (
    <>
      <aside className="hidden min-h-screen border-r border-[var(--mm-border)] bg-[var(--mm-bg-elevated)] px-4 py-7 lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col">
        <NavLink className="mb-10 flex items-center gap-3 px-3" to="/">
          <span className="grid size-12 place-items-center rounded-2xl bg-linear-to-br from-[var(--mm-primary)] to-[var(--mm-primary-deep)] shadow-[0_8px_24px_rgba(118,43,250,.36)]"><Film aria-hidden="true" className="size-7" /></span>
          <span>
            <span className="block text-2xl font-bold tracking-tight">Movie<span className="text-[var(--mm-accent)]">Mind</span></span>
            <span className="block text-xs text-[var(--mm-text-muted)]">Discover. Watch. Enjoy.</span>
          </span>
        </NavLink>
        <nav aria-label="Main navigation" className="space-y-1">
          {items.map(({ icon: Icon, label, to }) => (
            <NavLink
              key={to}
              className={({ isActive }) => `flex min-h-12 items-center gap-3 rounded-2xl px-4 text-sm font-semibold transition ${isActive ? "bg-linear-to-r from-[var(--mm-primary-deep)] to-[var(--mm-primary)] text-white shadow-[0_6px_22px_rgba(118,43,250,.25)]" : "text-[var(--mm-text-muted)] hover:bg-white/5 hover:text-[var(--mm-text)]"}`}
              to={to}
            >
              <Icon aria-hidden="true" className="size-5" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto rounded-3xl border border-[var(--mm-border)] bg-linear-to-br from-[#2B1C49] to-[var(--mm-surface)] p-5">
          <p className="text-sm font-bold text-[var(--mm-text)]">Build your taste</p>
          <p className="mt-2 text-xs leading-5 text-[var(--mm-text-muted)]">Rate movies to make your recommendations more personal.</p>
        </div>
      </aside>
      <nav aria-label="Mobile navigation" className="fixed inset-x-0 bottom-0 z-30 flex gap-1 overflow-x-auto border-t border-[var(--mm-border)] bg-[color:rgb(13_17_38_/_0.96)] px-2 py-2 backdrop-blur-xl lg:hidden">
        {items.slice(0, 5).map(({ icon: Icon, label, to }) => (
          <NavLink key={to} className={({ isActive }) => `flex min-w-0 flex-1 flex-col items-center gap-1 rounded-xl px-1 py-1.5 text-[10px] font-semibold ${isActive ? "bg-[var(--mm-primary)] text-white" : "text-[var(--mm-text-muted)]"}`} to={to}>
            <Icon aria-hidden="true" className="size-5" />
            {label}
          </NavLink>
        ))}
      </nav>
    </>
  );
}
