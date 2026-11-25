import { ShieldAlert } from "lucide-react";

type NoAccessProp = Readonly<{ message?: string }>;

// Shown in place of a page the signed-in admin doesn't have permission for.
export default function NoAccess({ message }: NoAccessProp) {
  return (
    <section className="mx-auto max-w-lg rounded-xl border border-default bg-background p-8 text-center">
      <span className="mx-auto flex size-12 items-center justify-center rounded-full bg-warning-background text-warning-accent">
        <ShieldAlert aria-hidden className="size-6" />
      </span>
      <h1 className="mt-4 text-section">
        You don&apos;t have permission to see this
      </h1>
      <p className="mt-2 text-body-sm text-fg-secondary">
        {message ??
          "Ask an Admin who can manage permissions to add it to your account."}
      </p>
    </section>
  );
}
