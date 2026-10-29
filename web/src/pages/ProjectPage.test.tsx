import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../api/client";
import ProjectPage from "./ProjectPage";

const MARKDOWN = "# Proyecto\n\nTexto inicial.";

beforeEach(() => {
  window.localStorage.clear();
});

describe("ProjectPage", () => {
  it("carga la versión del repositorio y la previsualiza", async () => {
    vi.spyOn(api, "getProject").mockResolvedValue({ markdown: MARKDOWN });
    render(<ProjectPage />);

    expect(await screen.findByRole("heading", { level: 1, name: "Proyecto" })).toBeInTheDocument();
    expect(screen.getByText("Texto inicial.")).toBeInTheDocument();
  });

  it("guarda el borrador en localStorage", async () => {
    vi.spyOn(api, "getProject").mockResolvedValue({ markdown: MARKDOWN });
    render(<ProjectPage />);
    await screen.findByRole("heading", { level: 1, name: "Proyecto" });

    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Borrador del proyecto"), {
      target: { value: "# Borrador nuevo" },
    });

    expect(window.localStorage.getItem("eph-proyecto-draft")).toBe("# Borrador nuevo");
  });

  it("restaura la versión del repositorio y limpia el borrador", async () => {
    const spy = vi.spyOn(api, "getProject").mockResolvedValue({ markdown: MARKDOWN });
    render(<ProjectPage />);
    await screen.findByRole("heading", { level: 1, name: "Proyecto" });

    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Borrador del proyecto"), {
      target: { value: "# Cambio local" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Restaurar versión del repositorio" }));

    await waitFor(() => expect(window.localStorage.getItem("eph-proyecto-draft")).toBeNull());
    expect(spy).toHaveBeenCalledTimes(2);
    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    expect(screen.getByLabelText("Borrador del proyecto")).toHaveValue(MARKDOWN);
  });

  it("entra en modo presentación", async () => {
    vi.spyOn(api, "getProject").mockResolvedValue({ markdown: MARKDOWN });
    render(<ProjectPage />);
    await screen.findByRole("heading", { level: 1, name: "Proyecto" });

    fireEvent.click(screen.getByRole("button", { name: "Modo presentación" }));

    expect(screen.getByRole("button", { name: "Salir de la presentación" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1, name: "Proyecto" })).toBeInTheDocument();
  });
});
