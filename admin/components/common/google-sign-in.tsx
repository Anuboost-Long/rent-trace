"use client";
import { Route } from "@/constants/web-routes";
import { supabase } from "@/utils/supabase-client";
import { useState } from "react";

import Button from "./button";

type GoogleSignInProp = Readonly<{ label: string }>;

export default function GoogleSignIn({ label }: GoogleSignInProp) {
  const [pending, setPending] = useState(false);
  const [failure, setFailure] = useState("");

  const start = async () => {
    if (!supabase) return;
    setPending(true);
    setFailure("");
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}${Route.auth.google_callback}`,
      },
    });
    if (error) {
      setPending(false);
      setFailure("We couldn't start Google sign-in. Try again.");
    }
  };

  return (
    <div className="mt-6 border-t border-foreground/15 pt-6">
      {supabase ? (
        <>
          <Button
            variant="quiet"
            className="w-full"
            onClick={start}
            pending={pending}
          >
            {pending ? "Opening Google…" : label}
          </Button>
          {failure && (
            <p role="alert" className="mt-2 text-sm text-red-600">
              {failure}
            </p>
          )}
        </>
      ) : (
        <p className="text-sm text-foreground/70">
          Google sign-in isn&apos;t set up on this server yet.
        </p>
      )}
    </div>
  );
}
