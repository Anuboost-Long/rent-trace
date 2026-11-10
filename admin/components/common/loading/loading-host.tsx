"use client";
import { LoadingAtom } from "@/api/services/loading/jotai";
import { useAtomValue } from "jotai";

import LoadingModal from "./loading-modal";

export default function LoadingHost() {
  const { visible, message } = useAtomValue(LoadingAtom);
  return <LoadingModal visible={visible} message={message || undefined} />;
}
