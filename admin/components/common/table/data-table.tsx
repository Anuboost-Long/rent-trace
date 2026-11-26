import clsx from "clsx";
import Link from "next/link";

export type Column<T> = {
  header: string;
  cell: (row: T) => React.ReactNode;
  className?: string;
};

type DataTableProp<T> = Readonly<{
  caption: string;
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string | number;
  empty: React.ReactNode;
  // Makes the whole row a link: the first cell holds the link and stretches it over the row.
  rowHref?: (row: T) => string;
}>;

export default function DataTable<T>({
  caption,
  columns,
  rows,
  rowKey,
  empty,
  rowHref,
}: DataTableProp<T>) {
  if (rows.length === 0)
    return (
      <div className="rounded-xl border border-default bg-background py-12 text-center">
        {empty}
      </div>
    );

  return (
    <div className="overflow-x-auto rounded-xl border border-default bg-background">
      <table className="w-full text-left text-body-sm">
        <caption className="sr-only">{caption}</caption>
        <thead className="border-b border-default bg-subtle text-caption text-fg-secondary">
          <tr>
            {columns.map((column) => (
              <th
                key={column.header}
                scope="col"
                className={clsx("px-4 py-3 font-medium", column.className)}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-default">
          {rows.map((row) => {
            const href = rowHref?.(row);
            return (
              <tr
                key={rowKey(row)}
                className={clsx(
                  href &&
                    "relative hover:bg-subtle has-focus-visible:bg-subtle",
                )}
              >
                {columns.map((column, index) => (
                  <td
                    key={column.header}
                    className={clsx("px-4 py-3", column.className)}
                  >
                    {href && index === 0 ? (
                      <Link
                        href={href}
                        className="outline-hidden after:absolute after:inset-0"
                      >
                        {column.cell(row)}
                      </Link>
                    ) : (
                      column.cell(row)
                    )}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
