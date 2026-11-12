"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import {
  OccupancyLabel,
  PropertyAccess,
  PropertyRoutes,
  UnitTypeLabel,
} from "@/constants/properties";
import useUnitActions from "@/hooks/form/useUnitActions";
import type { PropertyAudience, PropertyUnit } from "@/types/properties/models";
import { formatRent } from "@/utils/rent";
import { useAtomValue } from "jotai";
import { Pencil, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import UnitForm from "./unit-form";

type UnitPanelProp = Readonly<{
  audience: PropertyAudience;
  propertyId: number;
  unit: PropertyUnit;
}>;

export default function UnitPanel({
  audience,
  propertyId,
  unit,
}: UnitPanelProp) {
  const router = useRouter();
  const me = useAtomValue(UserAtom);
  const canManage = me?.permissions.includes(PropertyAccess[audience].update);
  const { pending, error, clearError, saveUnit, removeUnit } = useUnitActions(
    propertyId,
    audience,
  );
  const [editing, setEditing] = useState(false);
  const [confirming, setConfirming] = useState(false);

  const details: [string, string][] = [
    ["Type", UnitTypeLabel[unit.unit_type]],
    ["Unit number", unit.unit_number ?? "—"],
    [
      "Rent",
      unit.rent_amount && unit.rent_frequency
        ? formatRent(unit.rent_amount, unit.rent_frequency)
        : "Not set",
    ],
    [
      "People allowed",
      unit.max_occupants ? `Up to ${unit.max_occupants}` : "No limit",
    ],
    ["Occupancy", OccupancyLabel[unit.occupancy_status]],
    ["Shown publicly", unit.is_public ? "Yes" : "No"],
    ["Description", unit.description ?? "—"],
  ];

  const stopEditing = () => {
    setEditing(false);
    clearError();
  };

  return (
    <>
      <div className="mt-4 mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">{unit.name}</h1>
        {canManage && !editing && (
          <div className="flex gap-2">
            <Button
              variant="quiet"
              className="gap-2"
              onClick={() => setEditing(true)}
            >
              <Pencil aria-hidden className="size-4" />
              Edit
            </Button>
            <Button
              variant="quiet"
              className="gap-2"
              onClick={() => setConfirming(true)}
            >
              <Trash2 aria-hidden className="size-4" />
              Delete
            </Button>
          </div>
        )}
      </div>

      {editing ? (
        <UnitForm
          unit={unit}
          pending={pending}
          error={error}
          onCancel={stopEditing}
          onSubmit={async (body) => {
            if (await saveUnit(unit.id, body)) setEditing(false);
          }}
        />
      ) : (
        <dl className="divide-y divide-foreground/15 rounded-xl border border-foreground/15">
          {details.map(([label, value]) => (
            <div
              key={label}
              className="grid gap-1 p-4 sm:grid-cols-[12rem_1fr]"
            >
              <dt className="text-sm text-foreground/70">{label}</dt>
              <dd className="whitespace-pre-line">{value}</dd>
            </div>
          ))}
        </dl>
      )}

      <ConfirmDialog
        open={confirming}
        title={`Delete ${unit.name}?`}
        message="The unit and its photos and files are removed from this property. A unit with tenancies can't be deleted."
        confirmLabel="Delete"
        pending={pending}
        error={error?.message}
        onConfirm={async () => {
          if (await removeUnit(unit.id)) {
            router.replace(PropertyRoutes[audience].detail(propertyId));
          }
        }}
        onCancel={() => {
          setConfirming(false);
          clearError();
        }}
      />
    </>
  );
}
