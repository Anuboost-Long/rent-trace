import type { Metadata } from "next";

import GoogleCallback from "./google-callback";

export const metadata: Metadata = {
  title: "Signing in · RentTrace",
  referrer: "no-referrer",
  robots: { index: false },
};

export default function GoogleCallbackPage() {
  return <GoogleCallback />;
}
