"use client";
import Button from "@/components/common/button";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { LandlordTypes, TenantUploadTypes } from "@/constants/documents";
import useDocumentActions from "@/hooks/form/useDocumentActions";
import type { DocumentAudience, PaperDocument } from "@/types/documents/models";
import { Plus } from "lucide-react";
import { useState } from "react";

import DocumentItem from "./document-item";
import UploadDialog from "./upload-dialog";

type DocumentsSectionProp = Readonly<{
  audience: DocumentAudience;
  documents: PaperDocument[];
  tenancyId: number;
  unitId: number;
  canUpload: boolean;
  heading?: string;
  issueId?: number;
}>;

type Dialog =
  | { kind: "upload" }
  | { kind: "version"; document: PaperDocument }
  | { kind: "flag"; versionId: number }
  | { kind: "escalate"; document: PaperDocument; versionId: number };

export default function DocumentsSection({
  audience,
  documents,
  tenancyId,
  unitId,
  canUpload,
  heading = "Papers",
  issueId,
}: DocumentsSectionProp) {
  const actions = useDocumentActions({
    audience: audience === "tenant" ? "tenant" : "landlord",
    tenancyId,
    unitId,
    issueId,
  });
  const [dialog, setDialog] = useState<Dialog | null>(null);

  if (documents.length === 0 && !canUpload) return null;

  const close = () => {
    setDialog(null);
    actions.clearError();
  };
  const finish = async (done: Promise<boolean>) => {
    if (await done) close();
  };

  return (
    <section aria-labelledby="documents-heading" className="mt-12">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3">
        <h2 id="documents-heading" className="text-lg font-semibold">
          {heading}
        </h2>
        {canUpload && audience !== "admin" && (
          <Button
            size="sm"
            className="gap-2"
            onClick={() => setDialog({ kind: "upload" })}
          >
            <Plus aria-hidden className="size-4" />
            {issueId
              ? "Add a receipt"
              : audience === "tenant"
                ? "Upload a paper"
                : "Publish a paper"}
          </Button>
        )}
      </div>

      {documents.length === 0 ? (
        <p className="mt-3 max-w-[65ch] text-body-sm text-fg-secondary">
          {issueId
            ? "Receipts for this repair appear here."
            : audience === "tenant"
              ? "Papers about this tenancy appear here. You can upload a notice or a receipt."
              : "Publish the tenancy agreement, notices and receipts here. Tenants see them on their tenancy."}
        </p>
      ) : (
        <ul className="mt-2 divide-y divide-default">
          {documents.map((document) => {
            const latest = document.versions.at(-1);
            const waiting = latest?.confirmation === "WAITING";
            const stuck =
              latest?.confirmation === "FLAGGED" ||
              latest?.confirmation === "EXPIRED";
            return (
              <DocumentItem
                key={document.id}
                document={document}
                audience={audience}
                tenancyId={tenancyId}
                actions={
                  latest && (
                    <>
                      {audience === "tenant" && waiting && (
                        <>
                          <Button
                            size="sm"
                            pending={actions.pending}
                            onClick={() => actions.confirm(latest.id)}
                          >
                            Confirm
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() =>
                              setDialog({ kind: "flag", versionId: latest.id })
                            }
                          >
                            Flag a problem
                          </Button>
                        </>
                      )}
                      {audience !== "admin" && stuck && (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() =>
                            setDialog({
                              kind: "escalate",
                              document,
                              versionId: latest.id,
                            })
                          }
                        >
                          Ask an admin to decide
                        </Button>
                      )}
                      {audience === "landlord" && canUpload && (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() =>
                            setDialog({ kind: "version", document })
                          }
                        >
                          New version
                        </Button>
                      )}
                    </>
                  )
                }
              />
            );
          })}
        </ul>
      )}

      {dialog?.kind === "upload" && (
        <UploadDialog
          heading={
            issueId
              ? "Add a receipt"
              : audience === "tenant"
                ? "Upload a paper"
                : "Publish a paper"
          }
          confirmLabel={audience === "tenant" ? "Upload" : "Publish"}
          types={
            issueId
              ? null
              : audience === "tenant"
                ? TenantUploadTypes
                : LandlordTypes
          }
          pending={actions.pending}
          error={actions.error}
          onSubmit={(fields, file) => finish(actions.upload(fields, file))}
          onCancel={close}
        />
      )}
      {dialog?.kind === "version" && (
        <UploadDialog
          heading="Publish a new version"
          confirmLabel="Publish version"
          types={null}
          initialTitle={dialog.document.versions.at(-1)?.title}
          pending={actions.pending}
          error={actions.error}
          onSubmit={(fields, file) =>
            finish(actions.addVersion(dialog.document.id, fields, file))
          }
          onCancel={close}
        />
      )}
      {dialog?.kind === "flag" && (
        <ConfirmDialog
          open
          title="Flag a problem?"
          message="Your landlord is told and can publish a corrected version. Say what is wrong."
          confirmLabel="Flag it"
          reasonLabel="What is wrong with it?"
          pending={actions.pending}
          error={actions.error?.message}
          onConfirm={(reason) => finish(actions.flag(dialog.versionId, reason))}
          onCancel={close}
        />
      )}
      {dialog?.kind === "escalate" && (
        <ConfirmDialog
          open
          title="Ask an admin to decide?"
          message="An admin reads both sides and makes the final call. Tell them why you need one."
          confirmLabel="Ask an admin to decide"
          reasonLabel="Reason"
          pending={actions.pending}
          error={actions.error?.message}
          onConfirm={(reason) =>
            finish(
              actions.escalate(dialog.document.id, dialog.versionId, reason),
            )
          }
          onCancel={close}
        />
      )}
    </section>
  );
}
