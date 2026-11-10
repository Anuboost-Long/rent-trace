import { handleGetMe } from "@/api/services/auth/serve-action";
import LoadingVisual from "@/components/common/loading/loading-visual";
import { audienceFor } from "@/constants/navigation";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import Account from "./account";

export default function Home() {
  return (
    <Suspense fallback={<LoadingVisual immersive />}>
      <RoleHome />
    </Suspense>
  );
}

async function RoleHome() {
  const { data: user } = await handleGetMe();
  const audience = audienceFor(user!);
  if (audience) redirect(`/${audience}`);
  return <Account user={user!} />;
}
