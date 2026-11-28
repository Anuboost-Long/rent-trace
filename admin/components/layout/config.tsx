"use client";
import LoadingHost from "@/components/common/loading/loading-host";
import ToastHost from "@/components/common/toast/toast-host";
import { createStore, Provider } from "jotai";
import { useState } from "react";

export default function Config({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const [store] = useState(createStore);

  return (
    <Provider store={store}>
      {children}
      <LoadingHost />
      <ToastHost />
    </Provider>
  );
}
