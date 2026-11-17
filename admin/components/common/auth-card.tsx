type AuthCardProp = Readonly<{
  heading: string;
  message?: string;
  children?: React.ReactNode;
}>;

export default function AuthCard({ heading, message, children }: AuthCardProp) {
  return (
    <main className="mx-auto w-full max-w-md px-4 py-12">
      <p className="mb-4 text-xl font-bold">RentTrace</p>
      <section className="rounded-xl border border-foreground/15 p-8">
        <h1 className="text-2xl font-semibold">{heading}</h1>
        {message && (
          <p className="mt-3 text-foreground/70" role="status">
            {message}
          </p>
        )}
        {children && <div className="mt-6">{children}</div>}
      </section>
    </main>
  );
}
