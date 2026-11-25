"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import { useAtomValue } from "jotai";
import { useSyncExternalStore } from "react";

const subscribe = () => () => {};

const partOfDay = (hour: number) =>
  hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

// The server can't know the viewer's time of day, so it renders "Welcome" and the browser
// switches to "Good morning" and so on straight away.
export default function Greeting() {
  const user = useAtomValue(UserAtom);
  const opener = useSyncExternalStore(
    subscribe,
    () => partOfDay(new Date().getHours()),
    () => "Welcome",
  );
  return (
    <h1 className="mb-6 text-display">
      {opener}
      {user ? `, ${user.first_name}` : ""}
    </h1>
  );
}
