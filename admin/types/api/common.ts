export type ApiFailure = {
  status: number;
  message: string;
  fields: Record<string, string>;
  is_unauth: boolean;
};

export type ActionResult<T> =
  { data: T; error: null } | { data: null; error: ApiFailure };
