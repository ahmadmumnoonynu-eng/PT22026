import { type ButtonHTMLAttributes, type PropsWithChildren } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "icon";

type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant;
    isLoading?: boolean;
  }
>;

const variants: Record<ButtonVariant, string> = {
  primary: "bg-linear-to-r from-[#6D24F5] to-[#963BFF] text-white shadow-[0_8px_24px_rgba(118,43,250,.32)] hover:brightness-110",
  secondary: "border border-[var(--mm-border)] bg-[var(--mm-surface-strong)] text-[var(--mm-text)] hover:bg-[var(--mm-surface)]",
  ghost: "text-[var(--mm-text-muted)] hover:bg-white/5 hover:text-[var(--mm-text)]",
  icon: "size-11 rounded-full border border-[var(--mm-border)] bg-[var(--mm-surface-strong)] p-0 text-[var(--mm-text)] hover:bg-white/10",
};

export function Button({ children, className = "", disabled, isLoading, type = "button", variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-2xl px-5 text-sm font-semibold transition duration-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--mm-accent)] disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`}
      disabled={disabled || isLoading}
      type={type}
      {...props}
    >
      {isLoading && <span aria-hidden="true" className="size-4 animate-spin rounded-full border-2 border-current border-r-transparent" />}
      {children}
    </button>
  );
}
