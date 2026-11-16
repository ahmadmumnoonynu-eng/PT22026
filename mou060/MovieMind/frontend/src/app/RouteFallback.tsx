import { StatusPanel } from "@/components/ui/StatusPanel";

export function RouteFallback() {
  return <div className="mx-auto max-w-3xl pt-10"><StatusPanel>Loading this part of MovieMind…</StatusPanel></div>;
}
