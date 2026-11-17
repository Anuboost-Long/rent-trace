const API_KEY_FAILURE_CODE = "invalid_api_key";

export const isApiKeyFailure = (status: number, body: unknown) =>
  status === 401 &&
  typeof body === "object" &&
  body !== null &&
  (body as { code?: unknown }).code === API_KEY_FAILURE_CODE;

export const logApiKeyFailure = () =>
  console.error(
    "The back end rejected our API key. Check that API_KEY is the same in the admin app and the back end.",
  );
