import type { ButtonHTMLAttributes } from "react";

export default function Button({
    variant = "primary",
    ...props
    }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" }) {
    const base =
        "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-slate-200 disabled:opacity-60";
    const styles =
        variant === "primary"
        ? "bg-slate-900 text-white hover:bg-slate-800"
        : "bg-transparent text-slate-700 hover:bg-slate-100";

    return <button {...props} className={`${base} ${styles} ${props.className ?? ""}`} />;
}