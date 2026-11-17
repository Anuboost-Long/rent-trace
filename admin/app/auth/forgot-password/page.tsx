import AuthCard from "@/components/common/auth-card";
import type { Metadata } from "next";

import ForgotPasswordForm from "./forgot-password-form";

export const metadata: Metadata = { title: "Forgot password · RentTrace" };

export default function ForgotPasswordPage() {
  return (
    <AuthCard
      heading="Forgot your password?"
      message="Enter your email and we'll send you a link to choose a new one."
    >
      <ForgotPasswordForm />
    </AuthCard>
  );
}
