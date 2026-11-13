import RequireAudience from "@/components/layout/require-audience";

export default function Layout({ children }: LayoutProps<"/admin">) {
  return <RequireAudience audience="admin">{children}</RequireAudience>;
}
