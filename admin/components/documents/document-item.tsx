import LocalTime from "@/components/common/local-time";
import StatusBadge from "@/components/common/status-badge";
import {
  ConfirmationLabel,
  ConfirmationTone,
  DocumentTypeLabel,
  fileSize,
} from "@/constants/documents";
import type {
  DocumentAudience,
  DocumentVersion,
  PaperDocument,
} from "@/types/documents/models";
import { FileText } from "lucide-react";

type DocumentItemProp = Readonly<{
  document: PaperDocument;
  audience: DocumentAudience;
  tenancyId: number;
  actions: React.ReactNode;
}>;

function Files({
  version,
  audience,
  tenancyId,
}: Readonly<{
  version: DocumentVersion;
  audience: DocumentAudience;
  tenancyId: number;
}>) {
  return (
    <ul className="mt-2 flex flex-wrap gap-2">
      {version.files.map((file) => (
        <li key={file.id}>
          <a
            href={`/document-files/${audience}/${file.id}?tenancy=${tenancyId}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-9 items-center gap-2 rounded-lg border border-strong px-3 text-body-sm hover:bg-subtle focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
          >
            <FileText aria-hidden className="size-4 text-fg-secondary" />
            <span className="max-w-48 truncate">{file.name}</span>
            <span className="text-caption text-fg-tertiary">
              {fileSize(file.size_bytes)}
            </span>
          </a>
        </li>
      ))}
    </ul>
  );
}

export default function DocumentItem({
  document,
  audience,
  tenancyId,
  actions,
}: DocumentItemProp) {
  const versions = document.versions;
  const latest = versions.at(-1);
  if (!latest) return null;
  const earlier = versions.slice(0, -1).reverse();

  return (
    <li className="py-4">
      <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-3">
        <div className="min-w-0 max-w-[65ch] flex-1">
          <p className="text-caption text-fg-tertiary">
            {DocumentTypeLabel[document.document_type]}
          </p>
          <p className="font-medium">{latest.title}</p>
          {latest.description && (
            <p className="mt-1 whitespace-pre-line text-fg-secondary">
              {latest.description}
            </p>
          )}
          <p className="mt-1 text-body-sm text-fg-secondary">
            Version {latest.version_no} · {latest.uploaded_by_name} ·{" "}
            <LocalTime iso={latest.uploaded_at} />
          </p>
          <Files version={latest} audience={audience} tenancyId={tenancyId} />
          {latest.flag_reason && (
            <p className="mt-2 text-body-sm">
              <span className="text-fg-secondary">Flagged because: </span>
              {latest.flag_reason}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-2">
          {latest.confirmation && (
            <StatusBadge tone={ConfirmationTone[latest.confirmation]}>
              {ConfirmationLabel[latest.confirmation]}
            </StatusBadge>
          )}
          <div className="flex flex-wrap justify-end gap-2">{actions}</div>
        </div>
      </div>
      {earlier.length > 0 && (
        <details className="mt-3 text-body-sm">
          <summary className="cursor-pointer text-fg-secondary">
            Earlier versions · {earlier.length}
          </summary>
          <ul className="mt-2 space-y-3 border-l border-default pl-4">
            {earlier.map((version) => (
              <li key={version.id}>
                <p>
                  Version {version.version_no} · {version.title}
                  {version.confirmation && (
                    <span className="text-fg-secondary">
                      {" "}
                      · {ConfirmationLabel[version.confirmation]}
                    </span>
                  )}
                </p>
                <Files
                  version={version}
                  audience={audience}
                  tenancyId={tenancyId}
                />
              </li>
            ))}
          </ul>
        </details>
      )}
    </li>
  );
}
