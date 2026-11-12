export type TenantCondition = {
  id: number;
  title: string;
  description: string | null;
  observed_at: string;
};

export type UnitCondition = TenantCondition & {
  unit_id: number;
  is_shown_to_tenants: boolean;
  version_no: number;
  updated_at: string;
};

export type ConditionBody = {
  title: string;
  description: string;
  observed_at: string;
  is_shown_to_tenants?: boolean;
};
