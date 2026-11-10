import AudienceLayout from "@/components/layout/audience-layout";

export default function Layout({ children }: LayoutProps<"/admin">) {
  return <AudienceLayout audience="admin">{children}</AudienceLayout>;
}
