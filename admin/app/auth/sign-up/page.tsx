import GoogleSignIn from "@/components/common/google-sign-in";
import type { Metadata } from "next";

import SignUpFlow from "./sign-up-flow";

export const metadata: Metadata = { title: "Create account · RentTrace" };

export default function SignUpPage() {
  return <SignUpFlow google={<GoogleSignIn label="Sign up with Google" />} />;
}
