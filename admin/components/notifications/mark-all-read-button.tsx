"use client";
import { handleMarkAllNotificationsRead } from "@/api/services/notifications/serve-action";
import Button from "@/components/common/button";
import { CheckCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "@/utils/toast";

export default function MarkAllReadButton({
  disabled,
}: Readonly<{ disabled: boolean }>) {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  const markAll = async () => {
    setPending(true);
    const { error } = await handleMarkAllNotificationsRead();
    setPending(false);
    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("All notifications marked as read");
    router.refresh();
  };

  return (
    <Button
      variant="quiet"
      className="gap-2"
      pending={pending}
      disabled={disabled}
      onClick={markAll}
    >
      <CheckCheck aria-hidden className="size-4" />
      Mark all as read
    </Button>
  );
}
