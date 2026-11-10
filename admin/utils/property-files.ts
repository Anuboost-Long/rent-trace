import type { PropertyFileKind } from "@/types/properties/models";

export const MAX_FILE_BYTES = 10_000_000;

export const ACCEPT: Record<PropertyFileKind, string> = {
  PHOTO: "image/jpeg,image/png",
  DOCUMENT: "application/pdf",
};

const ALLOWED_TYPES: Record<PropertyFileKind, string[]> = {
  PHOTO: ["image/jpeg", "image/png"],
  DOCUMENT: ["application/pdf"],
};

const WRONG_TYPE: Record<PropertyFileKind, string> = {
  PHOTO: "Photos must be JPEG or PNG images.",
  DOCUMENT: "Documents must be PDF files.",
};

export const problemWithFile = (file: File, kind: PropertyFileKind) => {
  if (file.size === 0 || file.size > MAX_FILE_BYTES) {
    return "Files must be between 1 byte and 10 MB.";
  }
  return ALLOWED_TYPES[kind].includes(file.type) ? null : WRONG_TYPE[kind];
};

export const formatBytes = (bytes: number) =>
  bytes < 1_000_000
    ? `${Math.max(1, Math.round(bytes / 1000))} KB`
    : `${(bytes / 1_000_000).toFixed(1)} MB`;

export const fileUrl = (
  audience: string,
  propertyId: number,
  fileId: number,
  unitId?: number | null,
) =>
  unitId
    ? `/property-files/${audience}/${propertyId}/units/${unitId}/${fileId}`
    : `/property-files/${audience}/${propertyId}/${fileId}`;

export const ACCEPT_ALL = `${ACCEPT.PHOTO},${ACCEPT.DOCUMENT}`;

export const NOT_SUPPORTED = "Only JPEG, PNG and PDF files can be added.";

export const kindOfFile = (file: File): PropertyFileKind | null =>
  (Object.keys(ALLOWED_TYPES) as PropertyFileKind[]).find((kind) =>
    ALLOWED_TYPES[kind].includes(file.type),
  ) ?? null;
