import type { InputHTMLAttributes } from "react";

export default function Input(props: InputHTMLAttributes<HTMLInputElement>) {
    return (
        <input
        {...props}
        className={[
            "w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm",
            "placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200",
            props.className ?? "",
        ].join(" ")}
        />
    );
}