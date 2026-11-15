import { ArrowLeft, Film } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/Button";

type AuthPlaceholderPageProps = { mode: "login" | "register" };

export function AuthPlaceholderPage({ mode }: AuthPlaceholderPageProps) {
  const isLogin = mode === "login";
  const title = isLogin ? "Welcome back" : "Create your account";
  const description = isLogin ? "Secure sign-in will be connected to the MovieMind API in the authentication phase." : "Registration will be connected to the MovieMind API in the authentication phase.";

  return (
    <main className="auth-stage grid min-h-screen place-items-center p-5 text-[var(--mm-text)]">
      <section className="w-full max-w-md rounded-[28px] border border-[var(--mm-border)] bg-[color:rgb(18_23_47_/_0.92)] p-7 shadow-[var(--mm-card-shadow)] backdrop-blur-xl sm:p-9">
        <Link className="inline-flex items-center gap-2 text-sm font-semibold text-[var(--mm-text-muted)] hover:text-[var(--mm-text)]" to="/"><ArrowLeft aria-hidden="true" className="size-4" /> Back to Home</Link>
        <div className="mt-10 grid size-12 place-items-center rounded-2xl bg-linear-to-br from-[var(--mm-primary)] to-[var(--mm-primary-deep)]"><Film aria-hidden="true" className="size-7" /></div>
        <h1 className="mt-6 text-3xl font-black tracking-tight">{title}</h1>
        <p className="mt-3 leading-6 text-[var(--mm-text-muted)]">{description}</p>
        <Button className="mt-8 w-full" disabled>{isLogin ? "Sign in coming next" : "Registration coming next"}</Button>
        <p className="mt-6 text-center text-sm text-[var(--mm-text-muted)]">{isLogin ? "New to MovieMind?" : "Already have an account?"} <Link className="font-semibold text-[var(--mm-accent)] hover:text-white" to={isLogin ? "/register" : "/login"}>{isLogin ? "Create an account" : "Log in"}</Link></p>
      </section>
    </main>
  );
}
