import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SqlPanel from "./SqlPanel";

const writeText = vi.fn().mockResolvedValue(undefined);

beforeEach(() => {
  writeText.mockClear();
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: { writeText },
  });
});

describe("SqlPanel", () => {
  it("muestra el SQL y lo copia", async () => {
    render(<SqlPanel sql="SELECT COUNT(*) FROM personas" />);

    expect(screen.getByText(/SELECT COUNT/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Copiar" }));

    expect(writeText).toHaveBeenCalledWith("SELECT COUNT(*) FROM personas");
    expect(await screen.findByRole("button", { name: "Copiado" })).toBeInTheDocument();
  });

  it("indica cuando no se ejecutó SQL", () => {
    render(<SqlPanel sql={null} />);

    expect(screen.getByText("No se ejecutó SQL.")).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
