from communications.tests.base import ContactRequestApiTestCase
from notifications.models import Notification, NotificationKind
from notifications.services.shared import notify

URL = "/api/notifications/"


class InboxTests(ContactRequestApiTestCase):
    def tell(self, person, title="Something happened", **extra):
        notify(
            [person],
            kind=NotificationKind.CONTACT_REQUEST_RECEIVED,
            title=title,
            body="Details",
            **extra,
        )
        return Notification.objects.filter(recipient=person).order_by("-id").first()

    def test_lists_only_my_notifications_newest_first(self):
        self.tell(self.lou, "First")
        self.tell(self.amy, "Not mine")
        self.tell(self.lou, "Second")
        self.as_user(self.lou)

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["title"] for row in response.data["results"]], ["Second", "First"])
        self.assertEqual(response.data["count"], 2)

    def test_a_row_names_what_it_is_about_without_a_link_or_contact_details(self):
        mine = self.tell(self.lou, subject_id=42)
        self.as_user(self.lou)

        row = self.client.get(URL).data["results"][0]

        self.assertEqual(
            (row["id"], row["kind"], row["subject_id"], row["read_at"]),
            (mine.pk, "CONTACT_REQUEST_RECEIVED", 42, None),
        )
        self.assertNotIn("link", row)

    def test_counts_and_filters_unread(self):
        first = self.tell(self.lou, "First")
        self.tell(self.lou, "Second")
        self.as_user(self.lou)
        self.post(f"{URL}{first.pk}/read/")

        count = self.client.get(f"{URL}unread-count/")
        unread = self.client.get(URL, {"unread": "true"})

        self.assertEqual(count.data, {"unread": 1})
        self.assertEqual([row["title"] for row in unread.data["results"]], ["Second"])
        self.assertEqual(self.client.get(URL).data["count"], 2)

    def test_marking_one_read_is_idempotent(self):
        mine = self.tell(self.lou)
        self.as_user(self.lou)

        first = self.post(f"{URL}{mine.pk}/read/")
        again = self.post(f"{URL}{mine.pk}/read/")

        self.assertEqual(first.status_code, 200)
        self.assertIsNotNone(first.data["read_at"])
        self.assertEqual(again.data["read_at"], first.data["read_at"])

    def test_marking_all_read_only_touches_my_own(self):
        self.tell(self.lou)
        self.tell(self.lou)
        theirs = self.tell(self.amy)
        self.as_user(self.lou)

        response = self.post(f"{URL}read-all/")

        self.assertEqual(response.data, {"marked": 2})
        self.assertEqual(self.client.get(f"{URL}unread-count/").data, {"unread": 0})
        theirs.refresh_from_db()
        self.assertIsNone(theirs.read_at)

    def test_someone_elses_notification_is_not_found_and_stays_unread(self):
        theirs = self.tell(self.amy)
        self.as_user(self.lou)

        self.assertEqual(self.post(f"{URL}{theirs.pk}/read/").status_code, 404)
        theirs.refresh_from_db()
        self.assertIsNone(theirs.read_at)

    def test_every_role_has_an_inbox(self):
        admin = self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.tell(admin)

        self.assertEqual(self.client.get(f"{URL}unread-count/").data, {"unread": 1})
        self.as_user(self.tina)
        self.assertEqual(self.client.get(f"{URL}unread-count/").data, {"unread": 0})

    def test_needs_sign_in(self):
        self.client.credentials()
        self.assertEqual(self.client.get(URL).status_code, 401)
        self.assertEqual(self.client.get(f"{URL}unread-count/").status_code, 401)
