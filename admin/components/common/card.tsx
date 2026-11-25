import clsx from "clsx";

type CardProp = Readonly<{
  title?: string;
  description?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
  children?: React.ReactNode;
}>;

export default function Card({
  title,
  description,
  action,
  className,
  children,
}: CardProp) {
  return (
    <section
      className={clsx(
        "rounded-xl border border-default bg-background p-5",
        className,
      )}
    >
      {(title || action) && (
        <div className="flex items-start justify-between gap-4">
          {title && <h2 className="text-section">{title}</h2>}
          {action}
        </div>
      )}
      {description && (
        <p className="mt-1 text-body-sm text-fg-secondary">{description}</p>
      )}
      {children && <div className={clsx(title && "mt-4")}>{children}</div>}
    </section>
  );
}
