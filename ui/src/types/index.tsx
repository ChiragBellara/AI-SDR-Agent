export type BadgeKind = "good" | "warn" | "bad" | "neutral";

export type Step = {
    name: string;
    status: "Done" | "Running" | "Queued" | "Error";
    badge: BadgeKind;
    chips: string[];
};

export type Source = {
    url: string;
    snippet: string;
};