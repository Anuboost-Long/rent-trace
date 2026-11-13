import AccessTabs from "./access-tabs";

export default function AccessLayout({
  children,
}: LayoutProps<"/admin/access">) {
  return (
    <>
      <div className="mb-4">
        <h1 className="text-2xl font-semibold">Access</h1>
        <p className="mt-1 text-foreground/70">
          Who can do what: roles, the permissions they carry, and individual
          grants.
        </p>
      </div>
      <AccessTabs />
      {children}
    </>
  );
}
