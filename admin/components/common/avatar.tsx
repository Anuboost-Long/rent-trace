import clsx from "clsx";
import Image from "next/image";

type AvatarProp = Readonly<{
  firstName: string;
  lastName: string;
  userId?: number;
  pictureId?: number | null;
  className?: string;
}>;

export default function Avatar({
  firstName,
  lastName,
  userId,
  pictureId,
  className,
}: AvatarProp) {
  const initials = `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  const base = clsx(
    "inline-flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand-subtle text-caption font-semibold text-admin-text",
    className,
  );
  if (userId !== undefined && pictureId) {
    return (
      <span aria-hidden className={base}>
        <Image
          src={`/profile-pictures/${userId}?v=${pictureId}`}
          alt=""
          width={128}
          height={128}
          unoptimized
          className="size-full object-cover"
        />
      </span>
    );
  }
  return (
    <span aria-hidden className={base}>
      {initials}
    </span>
  );
}
