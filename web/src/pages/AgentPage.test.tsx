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

it("envía debug y muestra la traza del loop", async () => {
  const trace = [
    {
      turn: 1,
      elapsed_ms: 12,
      content: null,
      tool_calls: [{ name: "ejecutar_sql", arguments: { query: "SELECT 1" } }],
      tool_results: [{ name: "ejecutar_sql", result: { row_count: 1 } }],
    },
  ];
  const spy = vi
    .spyOn(api, "askAgent")
    .mockResolvedValue({ ...answer, trace });
  render(<AgentPage />);

  fireEvent.change(screen.getByLabelText("Pregunta"), {
    target: { value: "¿Cuántas personas hay?" },
  });
  fireEvent.click(screen.getByLabelText(/Modo debugging/));
  fireEvent.click(screen.getByRole("button", { name: "Consultar" }));

  await screen.findByText("Hay 43.739 personas en la muestra.");
  expect(spy).toHaveBeenCalledWith("¿Cuántas personas hay?", true);
  expect(screen.getByText(/Traza de depuración/)).toBeInTheDocument();
});

it("muestra la traza cuando el agente falla en modo debugging", async () => {
  vi.spyOn(api, "askAgent").mockRejectedValue(
    new ApiError(502, "No se pudo completar la consulta", null, [
      { turn: 1, tool_calls: [{ name: "ejecutar_sql", arguments: {} }] },
    ]),
  );
  render(<AgentPage />);

  fireEvent.change(screen.getByLabelText("Pregunta"), { target: { value: "¿?" } });
  fireEvent.click(screen.getByLabelText(/Modo debugging/));
  fireEvent.click(screen.getByRole("button", { name: "Consultar" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo completar");
  expect(screen.getByText(/Traza del error/)).toBeInTheDocument();
});
