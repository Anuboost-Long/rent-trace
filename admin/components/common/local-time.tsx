"use client";

import { formatInstant } from "@/utils/format-date";
import { useSyncExternalStore } from "react";

const subscribe = () => () => {};

type LocalTimeProps = Readonly<{ iso: string | null; withTime?: boolean }>;

export default function LocalTime({ iso, withTime }: LocalTimeProps) {
  const local = useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );
  return (
    <time dateTime={iso ?? undefined}>
      {formatInstant(iso, { withTime, local })}
    </time>
  );
}
