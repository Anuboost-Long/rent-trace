import type { Metadata } from "next";

import { requireWireframe } from "./enabled";
import GoForm from "./go-form";

export const metadata: Metadata = {
  title: "API wireframe · RentTrace",
  robots: { index: false, follow: false },
};

export default async function Page() {
  await requireWireframe();
  return (
    <main>
      <h1>API wireframe</h1>
      <p>
        Bare forms for the reviews and documents APIs. Sign in as the role you
        want to try first; the API&apos;s own permissions still apply.
      </p>
      <GoForm />
    </main>
  );
}
