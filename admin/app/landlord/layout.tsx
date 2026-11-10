import AudienceLayout from "@/components/layout/audience-layout";

export default function Layout({ children }: LayoutProps<"/landlord">) {
  return <AudienceLayout audience="landlord">{children}</AudienceLayout>;
}
