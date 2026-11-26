import AccessTabs from "./access-tabs";

export default function AccessLayout({
  children,
}: LayoutProps<"/admin/access">) {
  return (
    <>
      <AccessTabs />
      {children}
    </>
  );
}
