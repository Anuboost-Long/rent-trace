export type DocumentType =
  "TENANCY_AGREEMENT" | "CONDITION_REPORT" | "NOTICE" | "RECEIPT" | "OTHER";

export type Confirmation =
  "WAITING" | "CONFIRMED" | "FLAGGED" | "EXPIRED" | "ESCALATED" | "SUPERSEDED";

export type DocumentFile = {
  id: number;
  name: string;
  mime_type: string;
  size_bytes: number;
};

export type DocumentVersion = {
  id: number;
  version_no: number;
  title: string;
  description: string | null;
  document_date: string | null;
  uploaded_by_name: string;
  uploaded_at: string;
  confirmation: Confirmation | null;
  flag_reason: string | null;
  files: DocumentFile[];
};

export type PaperDocument = {
  id: number;
  document_type: DocumentType;
  unit_id: number;
  tenancy_id: number | null;
  maintenance_issue_id: number | null;
  current_version_id: number | null;
  versions: DocumentVersion[];
};

export type DocumentAudience = "tenant" | "landlord" | "admin";

export type DocumentCase = {
  id: number;
  status: "PENDING_REVIEW" | "APPROVED" | "REJECTED";
  document_id: number;
  tenancy_id: number | null;
  version_id: number;
  version_no: number;
  title: string;
  raised_by_name: string;
  raised_by_side: "TENANT" | "LANDLORD";
  reason: string;
  flag_reason: string | null;
  decision_reason: string | null;
  submitted_at: string;
};

export type DocumentCasePage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: DocumentCase[];
};

export type UploadFields = {
  document_type: DocumentType;
  title: string;
  description?: string;
  document_date?: string;
  maintenance_issue_id?: number;
};
