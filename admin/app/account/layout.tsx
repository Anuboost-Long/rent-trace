import AudienceLayout from "@/components/layout/audience-layout";

export default function Layout({ children }: LayoutProps<"/account">) {
  return <AudienceLayout>{children}</AudienceLayout>;
}
