import AudienceLayout from "@/components/layout/audience-layout";

export default function Layout({ children }: LayoutProps<"/tenant">) {
  return <AudienceLayout audience="tenant">{children}</AudienceLayout>;
}
