export type NotificationKind =
  | "REVIEW_EVENT"
  | "CONTACT_REQUEST_RECEIVED"
  | "CONTACT_REQUEST_CANCELLED"
  | "CONTACT_REQUEST_ACCEPTED"
  | "CONTACT_REQUEST_DECLINED"
  | "CONTACT_REQUEST_REVOKED"
  | "TENANCY_INVITATION_RECEIVED"
  | "TENANCY_INVITATION_ACCEPTED"
  | "TENANCY_STARTED"
  | "TENANCY_ENDED"
  | "TENANCY_CANCELLED"
  | "TENANCY_HOUSEMATE_REQUESTED"
  | "TENANCY_HOUSEMATE_APPROVED"
  | "TENANCY_HOUSEMATE_DECLINED"
  | "TENANCY_TERMS_CHANGED"
  | "TENANCY_TERMS_PROPOSED"
  | "TENANCY_TERMS_APPLIED"
  | "TENANCY_TERMS_DECLINED"
  | "MAINTENANCE_REPORTED"
  | "MAINTENANCE_ACKNOWLEDGED"
  | "MAINTENANCE_STARTED"
  | "MAINTENANCE_CLOSURE_PROPOSED"
  | "MAINTENANCE_CLOSURE_REJECTED"
  | "MAINTENANCE_CLOSED";

export type AppNotification = {
  id: number;
  kind: NotificationKind;
  subject_id: number | null;
  title: string;
  body: string;
  created_at: string;
  read_at: string | null;
};

export type NotificationPage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: AppNotification[];
};

export type NotificationFilters = { unread?: "true"; page?: number };
