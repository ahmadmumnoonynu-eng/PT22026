type MovieGridSkeletonProps = { count?: number };

export function MovieGridSkeleton({ count = 10 }: MovieGridSkeletonProps) {
  return (
    <div aria-label="Loading movies" className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 md:grid-cols-4 xl:grid-cols-5" role="status">
      {Array.from({ length: count }, (_, index) => (
        <div className="overflow-hidden rounded-2xl border border-[var(--mm-border)] bg-[var(--mm-surface)]" key={index}>
          <div className="aspect-[2/3] animate-pulse bg-[var(--mm-surface-strong)]" />
          <div className="space-y-2 p-3.5"><div className="h-4 w-4/5 animate-pulse rounded bg-[var(--mm-surface-strong)]" /><div className="h-3 w-2/5 animate-pulse rounded bg-[var(--mm-surface-strong)]" /></div>
        </div>
      ))}
    </div>
  );
}
