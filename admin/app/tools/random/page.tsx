import type { Metadata } from "next";

import RandomGenerator from "./random-generator";

export const metadata: Metadata = {
  title: "Random value generator · RentTrace",
  robots: { index: false, follow: false },
};

export default function RandomPage() {
  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-12">
      <p className="text-xl font-bold">RentTrace</p>
      <h1 className="mt-6 text-heading">Random value generator</h1>
      <p className="mt-1 mb-6 text-fg-secondary">
        Made in your browser. Nothing is sent to a server or saved.
      </p>
      <RandomGenerator />
    </main>
  );
}
