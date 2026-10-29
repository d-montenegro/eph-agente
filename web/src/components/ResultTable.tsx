type Value = string | number | null;

type Props = {
  columns: string[];
  rows: Value[][];
  truncated?: boolean;
  caption?: string;
};

export function formatValue(value: Value): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    return new Intl.NumberFormat("es-AR", { maximumFractionDigits: 6 }).format(value);
  }
  return String(value);
}

export default function ResultTable({ columns, rows, truncated, caption }: Props) {
  if (!columns.length) return null;
  return (
    <figure className="result-table">
      <table>
        <caption>{caption ?? "Resultado"}</caption>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column} scope="col">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="muted">
                Sin filas
              </td>
            </tr>
          ) : (
            rows.map((row, index) => (
              <tr key={index}>
                {row.map((value, cell) => (
                  <td key={cell}>{formatValue(value)}</td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
      {truncated && <p className="notice">Resultado truncado al límite de filas.</p>}
    </figure>
  );
}
