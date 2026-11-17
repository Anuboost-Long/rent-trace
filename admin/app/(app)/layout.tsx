import AudienceLayout from "@/components/layout/audience-layout";

export default function Layout({ children }: LayoutProps<"/">) {
  return <AudienceLayout>{children}</AudienceLayout>;
}
