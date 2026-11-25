import type { ApiFailure } from "@/types/api/common";

import NoAccess from "./no-access";

const FORBIDDEN = 403;

// What a page shows when loading its data failed: the No access panel for a missing
// permission, otherwise the error message.
export default function LoadError({ error }: Readonly<{ error: ApiFailure }>) {
  if (error.status === FORBIDDEN) return <NoAccess />;
  return (
    <p role="alert" className="text-error">
      {error.message}
    </p>
  );
}
