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
    localStorage.clear();
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
    expect(screen.getByRole("region", { name: "Historial de consultas" })).toHaveTextContent(
      "¿Cuántas personas hay?",
    );
  });

  it("muestra una tabla cuando el resultado no es escalar", async () => {
    localStorage.clear();
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
    localStorage.clear();
    vi.spyOn(api, "askAgent").mockRejectedValue(new ApiError(502, "El modelo no respondió"));
    render(<AgentPage />);

    fireEvent.change(screen.getByLabelText("Pregunta"), { target: { value: "¿?" } });
    fireEvent.click(screen.getByRole("button", { name: "Consultar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("El modelo no respondió");
  });
});

it("recupera y borra el historial del navegador", async () => {
  localStorage.setItem(
    "eph-agent-history-v1",
    JSON.stringify([
      {
        id: "1",
        question: "Consulta anterior",
        createdAt: "2026-10-31T12:00:00Z",
        answer,
      },
    ]),
  );
  render(<AgentPage />);

  fireEvent.click(screen.getByRole("button", { name: /Consulta anterior/ }));
  expect(screen.getByLabelText("Pregunta")).toHaveValue("Consulta anterior");
  expect(screen.getByText("Hay 43.739 personas en la muestra.")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Borrar historial" }));
  expect(screen.getByText("Todavía no hay consultas guardadas.")).toBeInTheDocument();
  expect(localStorage.getItem("eph-agent-history-v1")).toBeNull();
});

it("envía debug y muestra la traza del loop", async () => {
  localStorage.clear();
  const trace = [
    {
      turn: 1,
      elapsed_ms: 12,
      content: null,
      tool_calls: [{ name: "describir_tabla", arguments: { nombre: "personas" } }],
      tool_results: [
        {
          name: "describir_tabla",
          result: {
            view: "personas",
            columns: [
              {
                column: "sexo",
                source_column: "CH04",
                description: "Sexo de la persona",
                possible_values: ["Varón", "Mujer"],
                notes: "CH04 = 1 → Varón; CH04 = 2 → Mujer.",
              },
            ],
          },
        },
      ],
    },
    {
      turn: 2,
      elapsed_ms: 8,
      content: null,
      tool_calls: [
        {
          name: "ejecutar_sql",
          arguments: { query: "SELECT COUNT(*) FROM personas WHERE sexo = 'Varón'" },
        },
      ],
      tool_results: [{ name: "ejecutar_sql", result: { row_count: 1 } }],
    },
  ];
  const spy = vi
    .spyOn(api, "askAgent")
    .mockResolvedValue({
      ...answer,
      sql: "SELECT COUNT(*) FROM personas WHERE sexo = 'Varón'",
      trace,
    });
  render(<AgentPage />);

  fireEvent.change(screen.getByLabelText("Pregunta"), {
    target: { value: "¿Cuántas personas hay?" },
  });
  fireEvent.click(screen.getByLabelText(/Modo debugging/));
  fireEvent.click(screen.getByRole("button", { name: "Consultar" }));

  await screen.findByText("Hay 43.739 personas en la muestra.");
  expect(spy).toHaveBeenCalledWith(
    "¿Cuántas personas hay?",
    true,
    expect.any(String),
    expect.any(AbortSignal),
  );
  expect(screen.getByText(/Traza de depuración/)).toBeInTheDocument();
  expect(screen.getByRole("region", { name: "Recorrido de la consulta" })).toHaveTextContent(
    "personas",
  );
  expect(screen.getByRole("region", { name: "Recorrido de la consulta" })).toHaveTextContent(
    "individual",
  );
  expect(screen.getByText(/Debug · 2 llamadas/)).toBeInTheDocument();
  expect(screen.getAllByText(/CH04 = 1 → Varón/).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/"nombre": "personas"/).length).toBeGreaterThan(0);
});

it("restaura el modo debugging y la traza desde el historial", () => {
  const tracedAnswer = {
    ...answer,
    trace: [
      {
        turn: 1,
        tool_calls: [{ name: "ejecutar_sql", arguments: { query: answer.sql } }],
      },
    ],
  };
  localStorage.setItem(
    "eph-agent-history-v1",
    JSON.stringify([
      {
        id: "debug-1",
        question: "Consulta con debug",
        createdAt: "2026-11-05T12:00:00Z",
        answer: tracedAnswer,
        debug: true,
      },
    ]),
  );
  render(<AgentPage />);

  fireEvent.click(screen.getByRole("button", { name: /Consulta con debug/ }));

  expect(screen.getByLabelText(/Modo debugging/)).toBeChecked();
  expect(screen.getByText(/Traza de depuración/)).toBeInTheDocument();
  expect(screen.getByRole("region", { name: "Recorrido de la consulta" })).toHaveTextContent(
    "individual",
  );
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

it("permite detener una consulta en curso", async () => {
  localStorage.clear();
  vi.spyOn(api, "askAgent").mockImplementation((_question, _debug, _requestId, signal) =>
    new Promise((_resolve, reject) => {
      signal?.addEventListener("abort", () =>
        reject(new DOMException("Cancelada", "AbortError")),
      );
    }),
  );
  const cancel = vi.spyOn(api, "cancelAgent").mockResolvedValue({ cancelled: true });
  render(<AgentPage />);

  fireEvent.change(screen.getByLabelText("Pregunta"), { target: { value: "Cancelar esto" } });
  fireEvent.click(screen.getByRole("button", { name: "Consultar" }));
  fireEvent.click(await screen.findByRole("button", { name: "Detener consulta" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("Consulta detenida");
  expect(cancel).toHaveBeenCalledWith(expect.any(String));
  expect(screen.queryByRole("button", { name: "Detener consulta" })).not.toBeInTheDocument();
});
