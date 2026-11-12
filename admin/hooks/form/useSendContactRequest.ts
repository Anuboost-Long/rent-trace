"use client";
import { handleSendContactRequest } from "@/api/services/contact-requests/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type { SendContactRequestBody } from "@/types/contact-requests/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useSendContactRequest = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const send = async (body: SendContactRequestBody) => {
    setPending(true);
    setError(null);
    const { error } = await handleSendContactRequest(body);
    setPending(false);
    setError(error);
    if (!error) router.refresh();
  };

  return { pending, error, send };
};

export default useSendContactRequest;
