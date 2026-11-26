import clsx from "clsx";

type SwitchInputProp = Readonly<
  Omit<React.InputHTMLAttributes<HTMLInputElement>, "type" | "role"> & {
    label: React.ReactNode;
    description?: React.ReactNode;
  }
>;

export default function SwitchInput({
  label,
  description,
  className,
  ...props
}: SwitchInputProp) {
  return (
    <label
      className={clsx(
        "flex items-center justify-between gap-6 py-3",
        props.disabled ? "cursor-not-allowed" : "cursor-pointer",
        className,
      )}
    >
      <span>
        <span className="block text-body">{label}</span>
        {description && (
          <span className="block text-caption font-normal text-fg-secondary">
            {description}
          </span>
        )}
      </span>
      <span className="relative inline-flex shrink-0">
        <input
          {...props}
          type="checkbox"
          role="switch"
          className="peer sr-only"
        />
        <span
          aria-hidden
          className={clsx(
            "h-6 w-10 rounded-full bg-strong transition-colors motion-reduce:transition-none",
            "peer-checked:bg-brand peer-disabled:opacity-50",
            "peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-brand-border",
          )}
        />
        <span
          aria-hidden
          className="absolute top-0.5 left-0.5 size-5 rounded-full bg-background shadow-sm transition-transform peer-checked:translate-x-4 motion-reduce:transition-none"
        />
      </span>
    </label>
  );
}
