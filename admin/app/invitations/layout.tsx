import AudienceLayout from "@/components/layout/audience-layout";

export default function Layout({ children }: LayoutProps<"/invitations">) {
  return <AudienceLayout>{children}</AudienceLayout>;
}
