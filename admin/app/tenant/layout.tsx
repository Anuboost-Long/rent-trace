import TenantLayout from "@/components/layout/tenant-layout";

export default function Layout({ children }: LayoutProps<"/tenant">) {
  return <TenantLayout>{children}</TenantLayout>;
}
