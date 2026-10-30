import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { api, type ProviderProfile, type ProvidersResponse } from "../api/client";
import SettingsPage from "./SettingsPage";

const localProfile: ProviderProfile = {
  name: "local",
  base_url: "http://127.0.0.1:20128/v1",
  model: "auto",
  api_mode: "chat_completions",
  timeout_seconds: 30,
  max_retries: 1,
  enabled: true,
  hosted: false,
  api_key_env: "EPH_LLM_API_KEY",
  has_api_key: false,
};

const providers: ProvidersResponse = {
  mode: "local",
  selected: null,
  profiles: [localProfile],
};

describe("SettingsPage", () => {
  it("lista perfiles y prueba la conexión con estados diferenciados", async () => {
    vi.spyOn(api, "getProviders").mockResolvedValue(providers);
    const testSpy = vi.spyOn(api, "testProvider").mockResolvedValue({
      ok: false,
      status: "unreachable",
      latency_ms: 12,
      models: [],
      detail: "sin conexión",
      tools_supported: null,
    });
    render(<SettingsPage />);

    expect(await screen.findByRole("heading", { name: "local" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Probar conexión" }));

    expect(testSpy).toHaveBeenCalledWith("local", true);
    expect(await screen.findByText("Servidor inaccesible")).toBeInTheDocument();
  });

  it("exige probar la conexión antes de seleccionar", async () => {
    vi.spyOn(api, "getProviders").mockResolvedValue(providers);
    render(<SettingsPage />);
    await screen.findByRole("heading", { name: "local" });

    expect(screen.getByRole("button", { name: "Usar" })).toBeDisabled();
  });

  it("selecciona un perfil después de probar la conexión", async () => {
    vi.spyOn(api, "getProviders").mockResolvedValue(providers);
    vi.spyOn(api, "testProvider").mockResolvedValue({
      ok: true,
      status: "ok",
      latency_ms: 20,
      models: ["auto"],
      detail: null,
      tools_supported: true,
    });
    const selectSpy = vi.spyOn(api, "selectProvider").mockResolvedValue(localProfile);
    render(<SettingsPage />);
    await screen.findByRole("heading", { name: "local" });

    fireEvent.click(screen.getByRole("button", { name: "Probar conexión" }));
    await screen.findByText("Conectado");
    fireEvent.click(screen.getByRole("button", { name: "Usar" }));

    expect(selectSpy).toHaveBeenCalledWith("local");
    expect(await screen.findByText("Seleccionado")).toBeInTheDocument();
  });

  it("avisa cuando el modo hosted restringe destinos", async () => {
    vi.spyOn(api, "getProviders").mockResolvedValue({ ...providers, mode: "hosted" });
    render(<SettingsPage />);

    expect(
      await screen.findByText(/solo se permiten destinos de la lista blanca/i),
    ).toBeInTheDocument();
  });
});

it("agrega un perfil personalizado en modo local", async () => {
  const custom: ProviderProfile = {
    ...localProfile,
    name: "mi-ollama",
    base_url: "http://127.0.0.1:11434/v1",
    model: "qwen2.5:7b",
    api_key_env: null,
    has_api_key: true,
  };
  vi.spyOn(api, "getProviders")
    .mockResolvedValueOnce(providers)
    .mockResolvedValueOnce({ ...providers, profiles: [...providers.profiles, custom] });
  const addSpy = vi.spyOn(api, "addCustomProvider").mockResolvedValue(custom);
  render(<SettingsPage />);
  await screen.findByRole("heading", { name: "local" });

  fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "mi-ollama" } });
  fireEvent.change(screen.getByLabelText("URL base"), {
    target: { value: "http://127.0.0.1:11434/v1" },
  });
  fireEvent.change(screen.getByLabelText("Modelo"), {
    target: { value: "qwen2.5:7b" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Agregar perfil" }));

  await screen.findByText(/Perfil "mi-ollama" agregado/);
  expect(addSpy).toHaveBeenCalledWith(
    expect.objectContaining({
      name: "mi-ollama",
      base_url: "http://127.0.0.1:11434/v1",
      model: "qwen2.5:7b",
    }),
  );
  expect(await screen.findByRole("heading", { name: "mi-ollama" })).toBeInTheDocument();
});

it("no muestra el formulario personalizado en modo hosted", async () => {
  vi.spyOn(api, "getProviders").mockResolvedValue({ ...providers, mode: "hosted" });
  render(<SettingsPage />);

  expect(
    await screen.findByText(/solo se permiten destinos de la lista blanca/i),
  ).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Agregar perfil" })).not.toBeInTheDocument();
});
