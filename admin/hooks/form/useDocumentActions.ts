"use client";
import {
  handleAddDocumentVersion,
  handleAnswerDocumentVersion,
  handleLandlordEscalateVersion,
  handlePublishDocument,
  handleUploadTenantDocument,
} from "@/api/services/documents/serve-action";
import useApiError from "@/hooks/useApiError";
import type { DocumentAudience, UploadFields } from "@/types/documents/models";
import { toast } from "@/utils/toast";
import { useRouter } from "next/navigation";
import { useState } from "react";

type Scope = Readonly<{
  audience: Exclude<DocumentAudience, "admin">;
  tenancyId: number;
  unitId: number;
  issueId?: number;
}>;

const toFormData = (
  fields: Record<string, string | number | undefined>,
  file: File,
) => {
  const formData = new FormData();
  for (const [key, value] of Object.entries(fields)) {
    if (value !== undefined && value !== "") formData.set(key, String(value));
  }
  formData.set("file", file);
  return formData;
};

const useDocumentActions = ({
  audience,
  tenancyId,
  unitId,
  issueId,
}: Scope) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const run = async (
    request: Promise<{ error: Parameters<typeof setError>[0] }>,
    done: string,
  ) => {
    setPending(true);
    setError(null);
    const { error } = await request;
    setPending(false);
    setError(error);
    if (!error) {
      toast.success(done);
      router.refresh();
    }
    return !error;
  };

  const upload = (given: UploadFields, file: File) => {
    const fields: UploadFields = issueId
      ? { ...given, document_type: "RECEIPT", maintenance_issue_id: issueId }
      : given;
    return audience === "tenant"
      ? run(
          handleUploadTenantDocument(
            tenancyId,
            toFormData({ ...fields }, file),
          ),
          "Paper uploaded",
        )
      : run(
          handlePublishDocument(
            toFormData(
              {
                ...fields,
                unit_id: unitId,
                tenancy_id: tenancyId > 0 ? tenancyId : undefined,
              },
              file,
            ),
          ),
          "Paper published",
        );
  };

  return {
    pending,
    error,
    clearError: () => setError(null),
    upload,
    addVersion: (documentId: number, fields: UploadFields, file: File) =>
      run(
        handleAddDocumentVersion(documentId, toFormData({ ...fields }, file)),
        "New version published",
      ),
    confirm: (versionId: number) =>
      run(
        handleAnswerDocumentVersion(
          tenancyId,
          versionId,
          "confirm",
          crypto.randomUUID(),
        ),
        "Paper confirmed",
      ),
    flag: (versionId: number, reason: string) =>
      run(
        handleAnswerDocumentVersion(
          tenancyId,
          versionId,
          "flag",
          crypto.randomUUID(),
          reason,
        ),
        "Paper flagged",
      ),
    escalate: (documentId: number, versionId: number, reason: string) =>
      run(
        audience === "tenant"
          ? handleAnswerDocumentVersion(
              tenancyId,
              versionId,
              "escalate",
              crypto.randomUUID(),
              reason,
            )
          : handleLandlordEscalateVersion(documentId, versionId, reason),
        "Sent to an admin",
      ),
  };
};

export default useDocumentActions;
