"use client";
import {
  handleConfirmMfa,
  handleEnrolMfa,
  handleVerifyMfa,
} from "@/api/services/auth/serve-action";
import type { ActionResult } from "@/types/api/common";
import type { MfaEnrolment } from "@/types/auth/models";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";

const useMfa = () => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();
  const [enrolment, setEnrolment] = useState<MfaEnrolment | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[] | null>(null);

  const run = async <T>(request: Promise<ActionResult<T>>) => {
    setPending(true);
    setError(null);
    const { data, error } = await request;
    setPending(false);
    setError(error);
    return data;
  };

  const startEnrolment = async () => {
    const data = await run(handleEnrolMfa());
    if (data) setEnrolment(data);
  };

  const confirmEnrolment = async (code: string) => {
    const data = await run(handleConfirmMfa(code));
    if (data) setBackupCodes(data.backup_codes);
  };

  const verifyCode = async (code: string) => {
    const data = await run(handleVerifyMfa(code));
    return data !== null;
  };

  return {
    pending,
    error,
    enrolment,
    backupCodes,
    startEnrolment,
    confirmEnrolment,
    verifyCode,
  };
};

export default useMfa;
