type PageHeaderProp = Readonly<{ title: string; description?: string }>;

export default function PageHeader({ title, description }: PageHeaderProp) {
  return (
    <div className="mb-6">
      <h1 className="text-2xl font-semibold">{title}</h1>
      {description && <p className="mt-1 text-foreground/70">{description}</p>}
    </div>
  );
}
