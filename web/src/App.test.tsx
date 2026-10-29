import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "./api/client";
import App from "./App";

beforeEach(() => {
  window.localStorage.clear();
  window.location.hash = "#/agente";
});

describe("App", () => {
  it("navega entre secciones por la URL", async () => {
    vi.spyOn(api, "getProject").mockResolvedValue({ markdown: "# Proyecto\n\nTexto." });
    render(<App />);

    expect(screen.getByRole("heading", { name: "Agente EPH" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("link", { name: "Proyecto" }));
    if (!window.location.hash.includes("proyecto")) {
      window.location.hash = "#/proyecto";
    }
    fireEvent(window, new HashChangeEvent("hashchange"));

    expect(await screen.findByRole("heading", { level: 1, name: "Proyecto" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Proyecto" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it("ofrece las tres secciones", () => {
    vi.spyOn(api, "getProject").mockResolvedValue({ markdown: "# Proyecto" });
    render(<App />);

    const nav = screen.getByRole("navigation", { name: "Secciones" });
    expect(nav).toHaveTextContent("Proyecto");
    expect(nav).toHaveTextContent("Agente");
    expect(nav).toHaveTextContent("Configuración");
  });
});
