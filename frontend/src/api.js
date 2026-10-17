export class ApiError extends Error {
  constructor(status, body) {
    super(body.detail || body.title || `Request failed (${status})`);
    this.status = status;
    this.body = body;
  }
}

export async function request(path, method = "GET", body) {
  const headers = { Accept: "application/json" };
  if (method !== "GET") {
    const csrf = await request("/api/auth/csrf/");
    headers["X-CSRFToken"] = csrf.csrfToken;
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(path, {
    method,
    headers,
    credentials: "include",
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const data =
    response.status === 204
      ? null
      : await response.json().catch(() => ({
          detail: "The server returned an unreadable response.",
        }));
  if (!response.ok) throw new ApiError(response.status, data);
  return data;
}

export async function listAll(resource) {
  const result = [];
  for (let page = 1; ; page++) {
    const data = await request(
      `/api/v1/${resource}/?page=${page}&page_size=100`,
    );
    if (Array.isArray(data)) return data;
    result.push(...data.results);
    if (page >= data.total_pages) return result;
  }
}
