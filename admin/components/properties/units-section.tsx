"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import {
  OccupancyLabel,
  PropertyAccess,
  PropertyRoutes,
  UnitTypeLabel,
} from "@/constants/properties";
import useUnitActions from "@/hooks/form/useUnitActions";
import type {
  PropertyAudience,
  PropertyFile,
  PropertyUnit,
} from "@/types/properties/models";
import { fileUrl } from "@/utils/property-files";
import { formatRent } from "@/utils/rent";
import { useAtomValue } from "jotai";
import { ChevronRight, ImageIcon, Plus } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

import UnitForm from "./unit-form";

type UnitsSectionProp = Readonly<{
  audience: PropertyAudience;
  propertyId: number;
  units: PropertyUnit[];
  files: PropertyFile[];
}>;

const plural = (count: number, word: string) =>
  `${count} ${word}${count === 1 ? "" : "s"}`;

export default function UnitsSection({
  audience,
  propertyId,
  units,
  files,
}: UnitsSectionProp) {
  const me = useAtomValue(UserAtom);
  const canManage = me?.permissions.includes(PropertyAccess[audience].update);
  const { pending, error, clearError, saveUnit } = useUnitActions(
    propertyId,
    audience,
  );
  const [adding, setAdding] = useState(false);
  const propertyCover = files.find(
    (file) => file.unit_id === null && file.is_cover,
  );

  const closeForm = () => {
    setAdding(false);
    clearError();
  };

  return (
    <section aria-labelledby="units-heading" className="mt-10">
      <div className="flex items-center justify-between gap-4">
        <h2 id="units-heading" className="text-lg font-semibold">
          Units
        </h2>
        {canManage && !adding && (
          <Button
            variant="quiet"
            size="sm"
            className="gap-2"
            onClick={() => setAdding(true)}
          >
            <Plus aria-hidden className="size-4" />
            Add unit
          </Button>
        )}
      </div>

      {units.length === 0 ? (
        <p className="mt-3 text-foreground/70">
          No units yet. A unit is the part of the property that gets rented,
          such as the whole house or one room.
        </p>
      ) : (
        <ul className="mt-3 divide-y divide-foreground/15 rounded-xl border border-foreground/15">
          {units.map((unit) => {
            const unitFiles = files.filter((file) => file.unit_id === unit.id);
            const unitCover = unitFiles.find((file) => file.is_cover);
            const shownCover = unitCover ?? propertyCover;
            const photos = unitFiles.filter((file) => file.kind === "PHOTO");
            const documents = unitFiles.length - photos.length;
            return (
              <li key={unit.id}>
                <Link
                  href={PropertyRoutes[audience].unit(propertyId, unit.id)}
                  className="flex items-center gap-4 p-4 hover:bg-foreground/3 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-foreground"
                >
                  <span className="relative flex size-12 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-foreground/15 bg-foreground/5">
                    {shownCover ? (
                      <Image
                        src={fileUrl(
                          audience,
                          propertyId,
                          shownCover.id,
                          unitCover ? unit.id : null,
                        )}
                        alt=""
                        fill
                        unoptimized
                        sizes="48px"
                        className="object-cover"
                      />
                    ) : (
                      <ImageIcon
                        aria-hidden
                        className="size-5 text-foreground/50"
                        strokeWidth={1.5}
                      />
                    )}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block font-medium">
                      {unit.name}
                      {unit.unit_number && (
                        <span className="text-foreground/60">
                          {" "}
                          · {unit.unit_number}
                        </span>
                      )}
                    </span>
                    <span className="block text-sm text-foreground/70">
                      {UnitTypeLabel[unit.unit_type]} ·{" "}
                      {OccupancyLabel[unit.occupancy_status]}
                      {unit.rent_amount &&
                        unit.rent_frequency &&
                        ` · ${formatRent(unit.rent_amount, unit.rent_frequency)}`}
                      {unit.is_public && " · Public"}
                    </span>
                    <span className="block text-sm text-foreground/60">
                      {plural(photos.length, "photo")}
                      {documents > 0 && `, ${plural(documents, "document")}`}
                    </span>
                  </span>
                  <ChevronRight
                    aria-hidden
                    className="size-4 shrink-0 text-foreground/50"
                  />
                </Link>
              </li>
            );
          })}
        </ul>
      )}

      {adding && (
        <UnitForm
          unit={null}
          pending={pending}
          error={error}
          onCancel={closeForm}
          onSubmit={async (body) => {
            if (await saveUnit(null, body)) closeForm();
          }}
        />
      )}
    </section>
  );
}
