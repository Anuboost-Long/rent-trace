import type { LandlordContact } from "@/types/contact-requests/models";

export default function ContactCard({
  contact,
}: Readonly<{ contact: LandlordContact }>) {
  return (
    <div>
      <p className="font-medium">{contact.name}</p>
      <p>
        <a
          href={`mailto:${contact.email}`}
          className="underline underline-offset-2"
        >
          {contact.email}
        </a>
      </p>
      {contact.phone_number && (
        <p>
          <a
            href={`tel:${contact.phone_number}`}
            className="underline underline-offset-2"
          >
            {contact.phone_number}
          </a>
        </p>
      )}
    </div>
  );
}
