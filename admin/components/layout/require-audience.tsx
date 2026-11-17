import { isMemberOf, type Audience } from "@/constants/navigation";
import { Route } from "@/constants/web-routes";
import { getMe } from "@/utils/viewer";
import { redirect } from "next/navigation";

type RequireAudienceProp = Readonly<{
  audience: Audience;
  children: React.ReactNode;
}>;

export default async function RequireAudience({
  audience,
  children,
}: RequireAudienceProp) {
  const { data: user } = await getMe();
  if (!user || !isMemberOf(audience, user)) redirect(Route.home);
  return children;
}
