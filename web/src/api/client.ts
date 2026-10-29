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

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? detail;
    } catch {
      // La respuesta de error no era JSON.
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

export const api = {
  getProject(): Promise<{ markdown: string }> {
    return request<{ markdown: string }>("/api/project");
  },
  askAgent(question: string): Promise<AgentAnswer> {
    return request<AgentAnswer>("/api/agent/ask", {
      method: "POST",
      body: JSON.stringify({ question }),
    });
  },
  getProviders(): Promise<ProvidersResponse> {
    return request<ProvidersResponse>("/api/providers");
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
