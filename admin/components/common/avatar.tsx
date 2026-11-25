import clsx from "clsx";

type AvatarProp = Readonly<{
  firstName: string;
  lastName: string;
  className?: string;
}>;

export default function Avatar({ firstName, lastName, className }: AvatarProp) {
  const initials = `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  return (
    <span
      aria-hidden
      className={clsx(
        "inline-flex size-9 shrink-0 items-center justify-center rounded-full bg-brand-subtle text-caption font-semibold text-admin-text",
        className,
      )}
    >
      {initials}
    </span>
  );
}
