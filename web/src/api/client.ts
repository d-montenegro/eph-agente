export type QueryResult = {
  columns: string[];
  rows: Array<Array<string | number | null>>;
  row_count: number;
  truncated: boolean;
  sql: string;
  elapsed_ms: number;
};

export type AgentAnswer = {
  result: {
    kind: "scalar" | "table";
    value: string | number | null;
    columns: string[];
    rows: Array<Array<string | number | null>>;
  };
  sql: string | null;
  assumptions: string[];
  warnings: string[];
  answer: string;
  profile: string;
  model: string;
  sample_size: number;
  trace?: Array<Record<string, unknown>> | null;
};

export type ProviderProfile = {
  name: string;
  base_url: string;
  model: string;
  api_mode: string;
  timeout_seconds: number;
  max_retries: number;
  enabled: boolean;
  hosted: boolean;
  api_key_env: string | null;
  has_api_key: boolean;
};

export type ProvidersResponse = {
  mode: string;
  selected: string | null;
  profiles: ProviderProfile[];
};

export type CustomProviderInput = {
  name: string;
  base_url: string;
  model: string;
  api_key?: string;
  api_key_env?: string;
  timeout_seconds?: number;
};

export type AuthUser = {
  username: string;
};

export type ProviderHealth = {
  ok: boolean;
  status: string;
  latency_ms: number;
  models: string[];
  detail: string | null;
  tools_supported: boolean | null;
};

export class ApiError extends Error {
  status: number;
  detail: unknown;
  trace: Array<Record<string, unknown>> | null;

  constructor(
    status: number,
    message: string,
    detail: unknown = null,
    trace: Array<Record<string, unknown>> | null = null,
  ) {
    super(message);
    this.status = status;
    this.detail = detail;
    this.trace = trace;
    this.name = "ApiError";
  }
}

const BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("/api/auth/")) {
      window.dispatchEvent(new Event("eph:unauthorized"));
    }
    let message = response.statusText;
    let detail: unknown = null;
    let trace: Array<Record<string, unknown>> | null = null;
    try {
      const payload = (await response.json()) as { detail?: unknown };
      detail = payload.detail ?? payload;
      if (typeof detail === "string") {
        message = detail;
      } else if (detail && typeof detail === "object") {
        const object = detail as { message?: unknown; trace?: unknown };
        if (typeof object.message === "string") message = object.message;
        if (Array.isArray(object.trace)) {
          trace = object.trace as Array<Record<string, unknown>>;
        }
      }
    } catch {
      // La respuesta de error no era JSON.
    }
    throw new ApiError(response.status, message || "Error del servidor", detail, trace);
  }
  return (await response.json()) as T;
}

export const api = {
  me(): Promise<AuthUser> {
    return request<AuthUser>("/api/auth/me");
  },
  login(username: string, password: string): Promise<AuthUser> {
    return request<AuthUser>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  },
  logout(): Promise<{ ok: boolean }> {
    return request<{ ok: boolean }>("/api/auth/logout", { method: "POST" });
  },
  getProject(): Promise<{ markdown: string }> {
    return request<{ markdown: string }>("/api/project");
  },
  askAgent(
    question: string,
    debug = false,
    requestId?: string,
    signal?: AbortSignal,
  ): Promise<AgentAnswer> {
    return request<AgentAnswer>("/api/agent/ask", {
      method: "POST",
      body: JSON.stringify({ question, debug, request_id: requestId }),
      signal,
    });
  },
  cancelAgent(requestId: string): Promise<{ cancelled: boolean }> {
    return request<{ cancelled: boolean }>(`/api/agent/cancel/${encodeURIComponent(requestId)}`, {
      method: "POST",
    });
  },
  getProviders(): Promise<ProvidersResponse> {
    return request<ProvidersResponse>("/api/providers");
  },
  addCustomProvider(input: CustomProviderInput): Promise<ProviderProfile> {
    return request<ProviderProfile>("/api/providers/custom", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },
  selectProvider(profile: string): Promise<ProviderProfile> {
    return request<ProviderProfile>("/api/providers/select", {
      method: "POST",
      body: JSON.stringify({ profile }),
    });
  },
  testProvider(profile: string, checkTools = true): Promise<ProviderHealth> {
    return request<ProviderHealth>("/api/providers/test", {
      method: "POST",
      body: JSON.stringify({ profile, check_tools: checkTools }),
    });
  },
};
