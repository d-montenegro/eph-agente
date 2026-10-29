import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ResultTable from "./ResultTable";

describe("ResultTable", () => {
  it("muestra columnas, filas y nulos", () => {
    render(
      <ResultTable
        columns={["sexo", "tasa"]}
        rows={[
          ["Mujer", 0.0827],
          ["Varón", null],
        ]}
      />,
    );

    expect(screen.getByRole("columnheader", { name: "sexo" })).toBeInTheDocument();
    expect(screen.getByText("Mujer")).toBeInTheDocument();
    expect(screen.getByText("0,0827")).toBeInTheDocument();
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("avisa cuando el resultado está truncado", () => {
    render(<ResultTable columns={["x"]} rows={[[1]]} truncated />);

    expect(screen.getByText(/truncado/i)).toBeInTheDocument();
  });

  it("muestra un mensaje si no hay filas", () => {
    render(<ResultTable columns={["x"]} rows={[]} />);

    expect(screen.getByText("Sin filas")).toBeInTheDocument();
  });
});
