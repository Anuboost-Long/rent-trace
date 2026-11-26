type AuthCardProp = Readonly<{
  heading: string;
  message?: string;
  // A small label beside the logo, such as "Admin" on screens only admins reach.
  tag?: string;
  // A grey hint box under the card's content.
  note?: React.ReactNode;
  children?: React.ReactNode;
}>;

export default function AuthCard({
  heading,
  message,
  tag,
  note,
  children,
}: AuthCardProp) {
  return (
    <main className="flex flex-1 items-center justify-center bg-admin-subtle px-4 py-12">
      <section className="w-full max-w-sm rounded-xl border border-default bg-background p-6 shadow-medium">
        <div className="flex items-center gap-2">
          <span
            aria-hidden
            className="flex size-7 items-center justify-center rounded-md bg-brand text-body-sm font-semibold text-on-brand"
          >
            R
          </span>
          <p className="text-body-sm font-semibold">RentTrace</p>
          {tag && (
            <span className="rounded bg-brand px-1.5 py-0.5 text-caption uppercase text-on-brand">
              {tag}
            </span>
          )}
        </div>
        <h1 className="mt-5 text-section">{heading}</h1>
        {message && (
          <p className="mt-2 text-body-sm text-fg-secondary" role="status">
            {message}
          </p>
        )}
        {children && <div className="mt-5">{children}</div>}
        {note && (
          <div className="mt-5 rounded-lg border border-default p-3 text-caption font-normal text-fg-secondary">
            {note}
          </div>
        )}
      </section>
    </main>
  );
}
