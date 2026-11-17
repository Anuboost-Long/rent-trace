import clsx from "clsx";

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
}>;

export default function DataTable<T>({
  caption,
  columns,
  rows,
  rowKey,
  empty,
}: DataTableProp<T>) {
  if (rows.length === 0)
    return <div className="py-12 text-center">{empty}</div>;

  return (
    <div className="overflow-x-auto rounded-xl border border-foreground/15">
      <table className="w-full text-left text-sm">
        <caption className="sr-only">{caption}</caption>
        <thead className="border-b border-foreground/15 text-foreground/70">
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
        <tbody className="divide-y divide-foreground/15">
          {rows.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((column) => (
                <td
                  key={column.header}
                  className={clsx("px-4 py-3", column.className)}
                >
                  {column.cell(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
