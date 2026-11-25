import StatusBadge from "@/components/common/status-badge";
import { StatusLabel } from "@/constants/roles";
import type { UserSummary } from "@/types/users/models";

type AccountStatusBadgeProp = Readonly<{
  status: UserSummary["account_status"];
}>;

export default function AccountStatusBadge({ status }: AccountStatusBadgeProp) {
  return (
    <StatusBadge tone={status === "ACTIVE" ? "success" : "warning"}>
      {StatusLabel[status]}
    </StatusBadge>
  );
}
