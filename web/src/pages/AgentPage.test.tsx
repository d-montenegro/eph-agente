import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { api, ApiError, type AgentAnswer } from "../api/client";
import AgentPage from "./AgentPage";

const answer: AgentAnswer = {
  result: {
    kind: "scalar",
    value: 43_739,
    columns: ["total"],
    rows: [[43_739]],
  },
  sql: "SELECT * FROM (\nSELECT COUNT(*) AS total FROM personas\n) AS _guard LIMIT 1001",
  assumptions: ["Se contaron personas sin ponderar."],
  warnings: [],
  answer: "Hay 43.739 personas en la muestra.",
  profile: "local",
  model: "modelo-prueba",
  sample_size: 1,
};

describe("AgentPage", () => {
  it("muestra respuesta, valor, supuestos y SQL", async () => {
    vi.spyOn(api, "askAgent").mockResolvedValue(answer);
    render(<AgentPage />);

    fireEvent.change(screen.getByLabelText("Pregunta"), {
      target: { value: "¿Cuántas personas hay?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Consultar" }));

    expect(await screen.findByText("Hay 43.739 personas en la muestra.")).toBeInTheDocument();
    expect(screen.getByTestId("scalar")).toHaveTextContent("43.739");
    expect(screen.getByText("Se contaron personas sin ponderar.")).toBeInTheDocument();
    expect(screen.getByText(/SELECT COUNT/)).toBeInTheDocument();
    expect(screen.getByText("modelo-prueba")).toBeInTheDocument();
  });

  it("muestra una tabla cuando el resultado no es escalar", async () => {
    vi.spyOn(api, "askAgent").mockResolvedValue({
      ...answer,
      result: {
        kind: "table",
        value: null,
        columns: ["sexo", "tasa"],
        rows: [
          ["Mujer", 0.0827],
          ["Varón", 0.0747],
        ],
      },
    });
    render(<AgentPage />);

    fireEvent.change(screen.getByLabelText("Pregunta"), { target: { value: "por sexo" } });
    fireEvent.click(screen.getByRole("button", { name: "Consultar" }));

    expect(await screen.findByRole("columnheader", { name: "sexo" })).toBeInTheDocument();
    expect(screen.getByText("Mujer")).toBeInTheDocument();
  });

  it("muestra el error del backend", async () => {
    vi.spyOn(api, "askAgent").mockRejectedValue(new ApiError(502, "El modelo no respondió"));
    render(<AgentPage />);

    fireEvent.change(screen.getByLabelText("Pregunta"), { target: { value: "¿?" } });
    fireEvent.click(screen.getByRole("button", { name: "Consultar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("El modelo no respondió");
  });
});
