"use client";
import { handleGoogleSignIn } from "@/api/services/auth/serve-action";
import AuthCard from "@/components/common/auth-card";
import { homePathFor } from "@/constants/audience";
import { Route } from "@/constants/web-routes";
import { supabase } from "@/utils/supabase-client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const NO_CODE_MESSAGE =
  "Google didn't send you back with a sign-in. Try again.";

export default function GoogleCallback() {
  const router = useRouter();
  const started = useRef(false);
  const [failure, setFailure] = useState<string | null>(null);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    const query = new URLSearchParams(window.location.search);
    window.history.replaceState(null, "", window.location.pathname);

    const finish = async () => {
      const code = query.get("code");
      if (!supabase || !code) {
        return query.get("error_description") ?? NO_CODE_MESSAGE;
      }
      const { data, error } = await supabase.auth.exchangeCodeForSession(code);
      await supabase.auth.signOut({ scope: "local" });
      if (error || !data.session) return NO_CODE_MESSAGE;

      const signedIn = await handleGoogleSignIn(data.session.access_token);
      if (signedIn.error) return signedIn.error.message;
      router.replace(homePathFor(signedIn.data.user));
    };
    finish().then((message) => message && setFailure(message));
  }, [router]);

  if (failure) {
    return (
      <AuthCard heading="Google sign-in failed" message={failure}>
        <Link href={Route.auth.sign_in} className="font-medium underline">
          Back to sign in
        </Link>
      </AuthCard>
    );
  }
  return (
    <AuthCard
      heading="Signing you in"
      message="Finishing sign-in with Google…"
    />
  );
}
