"use client";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import CheckInput from "@/components/common/inputs/check-input";
import SelectInput from "@/components/common/inputs/select-input";
import TextArea from "@/components/common/inputs/text-area-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { Route } from "@/constants/web-routes";
import usePropertyProviders from "@/hooks/form/usePropertyProviders";
import type {
  PropertyProvider,
  ServiceCategory,
  ServiceProvider,
} from "@/types/providers/models";
import { Plus } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

type PropertyProvidersProp = Readonly<{
  propertyId: number;
  linked: PropertyProvider[];
  available: ServiceProvider[];
  hasSavedProviders: boolean;
  categories: ServiceCategory[];
}>;

type Dialog =
  | { kind: "add" }
  | { kind: "notes" | "unlink"; provider: PropertyProvider }
  | null;

const tradesOf = (provider: Pick<ServiceProvider, "categories">) =>
  provider.categories.map((category) => category.name).join(", ");

export default function PropertyProviders({
  propertyId,
  linked,
  available,
  hasSavedProviders,
  categories,
}: PropertyProvidersProp) {
  const { pending, error, clearError, link, update, unlink } =
    usePropertyProviders(propertyId);
  const [dialog, setDialog] = useState<Dialog>(null);
  const [picked, setPicked] = useState<number[]>([]);
  const [trade, setTrade] = useState("");
  const [notes, setNotes] = useState("");

  const close = () => {
    setDialog(null);
    setPicked([]);
    setTrade("");
    clearError();
  };

  const confirmAdd = async () => {
    if (await link(picked)) close();
  };

  const confirmNotes = async (provider: PropertyProvider) => {
    if (await update(provider.id, { contract_notes: notes.trim() || null })) {
      close();
    }
  };

  const confirmUnlink = async (provider: PropertyProvider) => {
    if (await unlink(provider.id)) close();
  };

  const shown = trade
    ? available.filter((provider) =>
        provider.categories.some((category) => category.code === trade),
      )
    : available;

  const togglePicked = (id: number) =>
    setPicked((current) =>
      current.includes(id)
        ? current.filter((value) => value !== id)
        : [...current, id],
    );

  return (
    <section aria-labelledby="providers-heading" className="mt-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="providers-heading" className="text-lg font-semibold">
          Tradespeople
        </h2>
        <Can permission="providers.manage">
          <Button
            variant="quiet"
            className="gap-2"
            onClick={() => setDialog({ kind: "add" })}
          >
            <Plus aria-hidden className="size-4" />
            Add from my tradespeople
          </Button>
        </Can>
      </div>
      <p className="mt-1 text-sm text-fg-secondary">
        Tenants here see these contacts, preferred ones first. You pick from the
        tradespeople you have already saved.
      </p>
      {linked.length === 0 ? (
        <p className="mt-3 rounded-xl border border-default p-4 text-fg-secondary">
          No tradespeople linked to this property yet.
        </p>
      ) : (
        <ul className="mt-3 divide-y divide-default rounded-xl border border-default">
          {linked.map((provider) => (
            <li
              key={provider.id}
              className="flex flex-wrap items-start justify-between gap-3 p-4"
            >
              <div className="min-w-0">
                <p className="font-medium">
                  {provider.business_name}
                  {provider.is_recommended && (
                    <span className="ml-2 text-sm font-normal text-fg-secondary">
                      Preferred
                    </span>
                  )}
                </p>
                <p className="text-sm text-fg-secondary">
                  {[tradesOf(provider), provider.phone_number, provider.email]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
                {provider.contract_notes && (
                  <p className="mt-1 text-sm whitespace-pre-line">
                    {provider.contract_notes}
                  </p>
                )}
              </div>
              <Can permission="providers.manage">
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="quiet"
                    disabled={pending}
                    onClick={() =>
                      update(provider.id, {
                        is_recommended: !provider.is_recommended,
                      })
                    }
                  >
                    {provider.is_recommended
                      ? "Remove preferred"
                      : "Mark preferred"}
                  </Button>
                  <Button
                    variant="quiet"
                    onClick={() => {
                      setNotes(provider.contract_notes ?? "");
                      setDialog({ kind: "notes", provider });
                    }}
                  >
                    Notes
                  </Button>
                  <Button
                    variant="quiet"
                    onClick={() => setDialog({ kind: "unlink", provider })}
                  >
                    Unlink
                  </Button>
                </div>
              </Can>
            </li>
          ))}
        </ul>
      )}
      {error && !dialog && (
        <p role="alert" className="mt-3 text-sm text-error">
          {error.message}
        </p>
      )}

      {dialog?.kind === "add" && (
        <ConfirmDialog
          open
          title="Add from my tradespeople"
          message="Pick the tradespeople who work on this property. They stay on your list and on your other properties."
          confirmLabel={picked.length > 0 ? `Add ${picked.length}` : "Add"}
          confirmDisabled={picked.length === 0}
          pending={pending}
          error={error?.message}
          onConfirm={confirmAdd}
          onCancel={close}
        >
          {available.length === 0 ? (
            <p className="text-sm text-fg-secondary">
              {hasSavedProviders
                ? "Everyone on your list is already linked to this property."
                : "You have not saved any tradespeople yet."}{" "}
              <Link
                href={Route.landlord.provider_new}
                className="underline underline-offset-2"
              >
                Add a tradesperson
              </Link>
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              <SelectInput
                label="Trade"
                name="trade"
                value={trade}
                onValueChange={setTrade}
                options={[
                  { value: "", label: "All trades" },
                  ...categories.map(({ code, name }) => ({
                    value: code,
                    label: name,
                  })),
                ]}
              />
              {shown.length === 0 ? (
                <p className="text-sm text-fg-secondary">
                  No saved tradespeople for this trade.
                </p>
              ) : (
                <ul className="max-h-64 divide-y divide-default overflow-y-auto rounded-lg border border-default">
                  {shown.map((provider) => (
                    <li key={provider.id} className="p-3">
                      <CheckInput
                        label={provider.business_name}
                        name={`provider_${provider.id}`}
                        checked={picked.includes(provider.id)}
                        onChange={() => togglePicked(provider.id)}
                      />
                      {tradesOf(provider) && (
                        <p className="pl-6 text-xs text-fg-tertiary">
                          {tradesOf(provider)}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </ConfirmDialog>
      )}

      {dialog?.kind === "notes" && (
        <ConfirmDialog
          open
          title={`Notes for ${dialog.provider.business_name}`}
          message="Private to you. Tenants never see these."
          confirmLabel="Save notes"
          pending={pending}
          error={error?.message}
          onConfirm={() => confirmNotes(dialog.provider)}
          onCancel={close}
        >
          <TextArea
            label="Contract notes"
            name="contract_notes"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
          />
        </ConfirmDialog>
      )}

      {dialog?.kind === "unlink" && (
        <ConfirmDialog
          open
          title={`Unlink ${dialog.provider.business_name}?`}
          message="They stay on your list and on your other properties. Tenants here will no longer see them."
          confirmLabel="Unlink"
          pending={pending}
          error={error?.message}
          onConfirm={() => confirmUnlink(dialog.provider)}
          onCancel={close}
        />
      )}
    </section>
  );
}
