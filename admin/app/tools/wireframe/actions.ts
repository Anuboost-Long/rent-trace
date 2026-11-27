"use server";
import { BaseUrl } from "@/api/api-config";
import {
  ApiRequestError,
  ApiServiceServer,
  ApiUploadServer,
} from "@/api/api-helper";

import { isAllowedPath } from "./allowed-path";
import { requireWireframe } from "./enabled";

export type CallResult = { status: number; body: unknown };

const run = async (path: string, send: () => Promise<unknown>) => {
  await requireWireframe();
  if (!isAllowedPath(path)) return { status: 400, body: "Path not allowed." };
  try {
    return { status: 200, body: await send() };
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return { status: error.status, body: error.body };
    }
    return { status: 500, body: String(error) };
  }
};

export const callJson = async (call: {
  method: "GET" | "POST";
  path: string;
  query?: Record<string, string | number>;
  json?: unknown;
}): Promise<CallResult> =>
  run(call.path, () =>
    ApiServiceServer({
      url: `${BaseUrl}/${call.path}`,
      method: call.method,
      params: call.query,
      data: call.json,
    }),
  );

export const callUpload = async (
  path: string,
  formData: FormData,
): Promise<CallResult> =>
  run(path, () => ApiUploadServer({ url: `${BaseUrl}/${path}`, formData }));
