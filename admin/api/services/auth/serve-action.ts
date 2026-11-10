"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import {
  clearSessionCookies,
  setSessionCookies,
} from "@/api/services/auth/session-cookies";
import { Route } from "@/constants/web-routes";
import type {
  ChangePasswordBody,
  Me,
  Message,
  MfaBackupCodes,
  MfaEnrolment,
  OnboardingBody,
  ProfileBody,
  SignedIn,
  SignInBody,
  SignUpBody,
  User,
} from "@/types/auth/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export const handleSignUp = async (body: SignUpBody) => {
  try {
    const data = await ApiServiceServer<Message>({
      url: EndPoints.auth.sign_up,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleVerifyEmail = async (token: string) => {
  try {
    const data = await ApiServiceServer<Message>({
      url: EndPoints.auth.verify_email,
      method: "POST",
      data: { token },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleResendVerification = async (email: string) => {
  try {
    const data = await ApiServiceServer<Message>({
      url: EndPoints.auth.resend_verification,
      method: "POST",
      data: { email },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleSignIn = async (body: SignInBody) => {
  try {
    const signedIn = await ApiServiceServer<SignedIn>({
      url: EndPoints.auth.sign_in,
      method: "POST",
      data: body,
    });
    setSessionCookies(await cookies(), signedIn);
    return { data: signedIn.user, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleGoogleSignIn = async (accessToken: string) => {
  try {
    const signedIn = await ApiServiceServer<SignedIn>({
      url: EndPoints.auth.google,
      method: "POST",
      data: { access_token: accessToken },
    });
    setSessionCookies(await cookies(), signedIn);
    return {
      data: { needs_onboarding: signedIn.needs_onboarding },
      error: null,
    };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleCompleteOnboarding = async (body: OnboardingBody) => {
  try {
    const data = await ApiServiceServer<User>({
      url: EndPoints.auth.onboarding,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, { redirectOnUnauth: true });
  }
};

export const handleGetMe = async () => {
  try {
    const data = await ApiServiceServer<Me>({
      url: EndPoints.auth.me,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, { redirectOnUnauth: true });
  }
};

export const handleUpdateProfile = async (body: ProfileBody) => {
  try {
    const data = await ApiServiceServer<Me>({
      url: EndPoints.auth.profile,
      method: "PATCH",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, { redirectOnUnauth: true });
  }
};

export const handleChangePassword = async (body: ChangePasswordBody) => {
  try {
    const data = await ApiServiceServer<Message>({
      url: EndPoints.auth.change_password,
      method: "POST",
      data: body,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, { redirectOnUnauth: true });
  }
};

export const handleEnrolMfa = async () => {
  try {
    const data = await ApiServiceServer<MfaEnrolment>({
      url: EndPoints.auth.mfa_enrol,
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleConfirmMfa = async (code: string) => {
  try {
    const data = await ApiServiceServer<MfaBackupCodes>({
      url: EndPoints.auth.mfa_confirm,
      method: "POST",
      data: { code },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleVerifyMfa = async (code: string) => {
  try {
    const data = await ApiServiceServer<Message>({
      url: EndPoints.auth.mfa_verify,
      method: "POST",
      data: { code },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error);
  }
};

export const handleSignOut = async () => {
  try {
    await ApiServiceServer<null>({
      url: EndPoints.auth.sign_out,
      method: "POST",
    });
  } catch {
    // The session is cleared locally whether or not the API call succeeded.
  }
  clearSessionCookies(await cookies());
  redirect(Route.auth.sign_in);
};
