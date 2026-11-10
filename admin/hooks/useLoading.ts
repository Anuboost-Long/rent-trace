"use client";
import { LoadingAtom } from "@/api/services/loading/jotai";
import { useSetAtom } from "jotai";

const useLoading = () => {
  const setLoading = useSetAtom(LoadingAtom);

  const showLoading = (message = "") => setLoading({ visible: true, message });
  const hideLoading = () => setLoading({ visible: false, message: "" });

  const withLoading = async <T>(task: Promise<T>, message?: string) => {
    showLoading(message);
    try {
      return await task;
    } finally {
      hideLoading();
    }
  };

  return { showLoading, hideLoading, withLoading };
};

export default useLoading;
