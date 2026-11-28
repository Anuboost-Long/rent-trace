"use client";
import { handleSendContactRequest } from "@/api/services/contact-requests/serve-action";
import type { SendContactRequestBody } from "@/types/contact-requests/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useSendContactRequest = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const send = async (body: SendContactRequestBody) => {
    setPending(true);
    setError(null);
    const { error } = await handleSendContactRequest(body);
    setPending(false);
    setError(error);
    if (!error) {
      toast.success("Request sent");
      router.refresh();
    }
  };

  return { pending, error, send };
};

export default useSendContactRequest;
