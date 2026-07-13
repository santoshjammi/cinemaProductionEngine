import { cn } from '@/lib/utils';

function LoadingSkeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-muted',
        className
      )}
      {...props}
    />
  );
}

export function SkeletonLine({ className }: { className?: string }) {
  return (
    <LoadingSkeleton
      className={cn('h-4 w-full', className)}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-lg border p-4 space-y-3">
      <SkeletonLine className="h-5 w-1/3" />
      <SkeletonLine className="h-4 w-2/3" />
      <SkeletonLine className="h-4 w-full" />
      <SkeletonLine className="h-4 w-3/4" />
    </div>
  );
}

export { LoadingSkeleton };