import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import { Search } from "lucide-react";
import Form from "next/form";

type UsersFilterProp = Readonly<{
  q?: string;
  role?: string;
  status?: string;
}>;

// Searching keeps the chip that is selected.
export default function UsersFilter({ q, role, status }: UsersFilterProp) {
  return (
    <Form scroll={false} action={Route.admin.users} role="search">
      {role && <input type="hidden" name="role" value={role} />}
      {status && <input type="hidden" name="status" value={status} />}
      <TextInput
        name="q"
        type="search"
        aria-label="Search name or email"
        placeholder="Search name or email"
        defaultValue={q}
        className="w-72 max-w-full"
        rightSlot={
          <button
            type="submit"
            aria-label="Search"
            className="text-icon-secondary hover:text-fg-primary"
          >
            <Search aria-hidden className="size-4" />
          </button>
        }
      />
    </Form>
  );
}
