import { ACCESS_COOKIE } from "@/api/services/auth/session-cookies";
import { cookies, headers } from "next/headers";

export class ApiRequestError extends Error {
  constructor(
    public status: number,
    public body: unknown,
  ) {
    super(`API request failed with ${status}`);
  }
}

type Config = {
  url: string;
  method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  data?: unknown;
  params?: Record<string, string | number | undefined>;
};

export const ApiServiceServer = async <T>({
  url,
  method,
  data,
  params,
}: Config) => {
  const [headerList, cookieStore] = await Promise.all([headers(), cookies()]);
  const clientIp = headerList.get("x-forwarded-for")?.split(",")[0]?.trim();
  const accessToken = cookieStore.get(ACCESS_COOKIE)?.value;

  const query = new URLSearchParams(
    Object.entries(params ?? {}).flatMap(([key, value]) =>
      value === undefined || value === "" ? [] : [[key, String(value)]],
    ),
  ).toString();

  const response = await fetch(query ? `${url}?${query}` : url, {
    method,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": process.env.API_KEY ?? "",
      "User-Agent": headerList.get("user-agent") ?? "",
      ...(clientIp && { "X-Forwarded-For": clientIp }),
      ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
    },
    body: data === undefined ? undefined : JSON.stringify(data),
  });

  const body = await response.json().catch(() => null);
  if (!response.ok) throw new ApiRequestError(response.status, body);
  return body as T;
};

export const ApiUploadServer = async <T>({
  url,
  formData,
}: {
  url: string;
  formData: FormData;
}) => {
  const [headerList, cookieStore] = await Promise.all([headers(), cookies()]);
  const accessToken = cookieStore.get(ACCESS_COOKIE)?.value;

  const response = await fetch(url, {
    method: "POST",
    cache: "no-store",
    headers: {
      "X-API-Key": process.env.API_KEY ?? "",
      "User-Agent": headerList.get("user-agent") ?? "",
      ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
    },
    body: formData,
  });

  const body = await response.json().catch(() => null);
  if (!response.ok) throw new ApiRequestError(response.status, body);
  return body as T;
};
