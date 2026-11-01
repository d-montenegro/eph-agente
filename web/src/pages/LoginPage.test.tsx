import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { api, ApiError } from "../api/client";
import LoginPage from "./LoginPage";

describe("LoginPage", () => {
  it("envía las credenciales y avisa al padre", async () => {
    const spy = vi.spyOn(api, "login").mockResolvedValue({ username: "jairo" });
    const onLogin = vi.fn();
    render(<LoginPage onLogin={onLogin} />);

    fireEvent.change(screen.getByLabelText("Usuario"), { target: { value: "jairo" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "diaa2026" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    await waitFor(() => expect(onLogin).toHaveBeenCalledWith({ username: "jairo" }));
    expect(spy).toHaveBeenCalledWith("jairo", "diaa2026");
  });

  it("muestra el error de credenciales", async () => {
    vi.spyOn(api, "login").mockRejectedValue(
      new ApiError(401, "Usuario o contraseña incorrectos"),
    );
    render(<LoginPage onLogin={vi.fn()} />);

    fireEvent.change(screen.getByLabelText("Usuario"), { target: { value: "jairo" } });
    fireEvent.change(screen.getByLabelText("Contraseña"), { target: { value: "mal" } });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Usuario o contraseña incorrectos",
    );
  });
});
