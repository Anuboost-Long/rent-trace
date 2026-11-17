import RequireAudience from "@/components/layout/require-audience";

export default function Layout({ children }: LayoutProps<"/landlord">) {
  return <RequireAudience audience="landlord">{children}</RequireAudience>;
}
