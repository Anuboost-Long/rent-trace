import { ApiRequestError } from "@/api/api-helper";
import { Route } from "@/constants/web-routes";
import type { ApiFailure } from "@/types/api/common";
import { redirect } from "next/navigation";

import { isApiKeyFailure, logApiKeyFailure } from "./api-key-failure";

const FALLBACK_MESSAGE = "Something went wrong. Try again.";

const messageOf = (value: unknown): string | undefined => {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return messageOf(value[0]);
};

const toFailure = (error: unknown): ApiFailure => {
  if (!(error instanceof ApiRequestError)) {
    return {
      status: 0,
      message: "Couldn't reach RentTrace. Check your connection and try again.",
      fields: {},
      is_unauth: false,
    };
  }

  const { status, body } = error;
  if (isApiKeyFailure(status, body)) {
    logApiKeyFailure();
    return {
      status: 503,
      message: FALLBACK_MESSAGE,
      fields: {},
      is_unauth: false,
    };
  }
  const entries =
    body && typeof body === "object" && !Array.isArray(body)
      ? Object.entries(body)
      : [];
  const fields = Object.fromEntries(
    entries
      .filter(([key]) => key !== "detail")
      .flatMap(([key, value]) => {
        const message = messageOf(value);
        return message ? [[key, message]] : [];
      }),
  );
  const detail = messageOf((body as { detail?: unknown } | null)?.detail);

  return {
    status,
    message:
      status === 429
        ? "Too many attempts. Wait a few minutes, then try again."
        : (detail ??
          messageOf(body) ??
          Object.values(fields)[0] ??
          FALLBACK_MESSAGE),
    fields,
    is_unauth: status === 401,
  };
};

export const handleSSRActionError = async (
  error: unknown,
  options?: { redirectOnUnauth?: boolean },
) => {
  const failure = toFailure(error);
  if (failure.is_unauth && options?.redirectOnUnauth) {
    redirect(Route.auth.sign_in);
  }
  return { data: null, error: failure };
};
