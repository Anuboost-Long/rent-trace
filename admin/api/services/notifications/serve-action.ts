"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type {
  AppNotification,
  NotificationFilters,
  NotificationPage,
} from "@/types/notifications/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetNotifications = async (
  params: NotificationFilters = {},
) => {
  try {
    const data = await ApiServiceServer<NotificationPage>({
      url: EndPoints.notifications.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleGetUnreadCount = async () => {
  try {
    const { unread } = await ApiServiceServer<{ unread: number }>({
      url: EndPoints.notifications.unread_count,
      method: "GET",
    });
    return unread;
  } catch {
    return null;
  }
};

export const handleMarkNotificationRead = async (id: number) => {
  try {
    const data = await ApiServiceServer<AppNotification>({
      url: EndPoints.notifications.read(id),
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleMarkAllNotificationsRead = async () => {
  try {
    const data = await ApiServiceServer<{ marked: number }>({
      url: EndPoints.notifications.read_all,
      method: "POST",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
