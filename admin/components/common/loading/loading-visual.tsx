import clsx from "clsx";

import Spinner from "./spinner";

type LoadingVisualProp = Readonly<{
  message?: string;
  immersive?: boolean;
  className?: string;
}>;

export default function LoadingVisual({
  message = "Loading…",
  immersive,
  className,
}: LoadingVisualProp) {
  return (
    <div
      role="status"
      className={clsx(
        "flex flex-col items-center justify-center gap-3",
        immersive ? "min-h-screen" : "py-12",
        className,
      )}
    >
      <Spinner />
      <p className="text-sm text-foreground/70">{message}</p>
    </div>
  );
}
