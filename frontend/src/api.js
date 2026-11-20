export class ApiError extends Error {
  constructor(status, body) {
    super(body.detail || body.title || `Request failed (${status})`);
    this.status = status;
    this.body = body;
  }
}

const inflight = new Map();
const retryKeys = new Map();
let accessToken = null;
let accessExpires = 0;
let tokenPending = null;
let credentialPending = null;
let authEpoch = 0;
const publicPaths = new Set([
  "/api/auth/csrf/",
  "/api/auth/setup/",
  "/api/auth/login/",
  "/api/v1/auth/login/",
  "/api/auth/owner/register/",
  "/api/auth/password/reset/",
  "/api/auth/password/reset/confirm/",
  "/api/v1/health",
  "/health",
]);

export function clearAccessToken() {
  authEpoch++;
  accessToken = null;
  accessExpires = 0;
  tokenPending = null;
  retryKeys.clear();
}

function rememberAccess(data) {
  if (
    typeof data?.access_token !== "string" ||
    !data.access_token ||
    !(data.expires_in > 0)
  )
    throw new ApiError(0, {
      detail: "Unable to establish secure sign-in. Please log in again.",
    });
  accessToken = data.access_token;
  accessExpires = Date.now() + data.expires_in * 1000;
}

async function ensureAccess() {
  if (accessToken && accessExpires > Date.now() + 10000) return;
  if (tokenPending) return tokenPending;
  const epoch = authEpoch;
  const pending = (async () => {
    const csrf = await request("/api/auth/csrf/");
    const response = await fetch("/api/auth/token/", {
      method: "POST",
      credentials: "include",
      signal: AbortSignal.timeout(30000),
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf.csrfToken,
      },
      body: "{}",
    });
    const data = await response
      .json()
      .catch(() => ({ detail: "Unable to renew sign-in." }));
    if (epoch !== authEpoch)
      throw new ApiError(401, { detail: "Please log in again." });
    if (!response.ok) throw new ApiError(response.status, data);
    rememberAccess(data);
  })();
  tokenPending = pending;
  try {
    await pending;
  } catch (error) {
    if (epoch === authEpoch && error.status === 401) {
      clearAccessToken();
      window.dispatchEvent(new Event("clinic-session-expired"));
    }
    throw error;
  } finally {
    if (tokenPending === pending) tokenPending = null;
  }
}
export function request(path, method = "GET", body, options = {}) {
  if (method === "GET") return send(path, method, body);
  const signature = JSON.stringify([path, method, body, options]);
  if (inflight.has(signature)) return inflight.get(signature);
  const rotatingPassword = path === "/api/auth/password/change/";
  // Responses from reads started before this rotation must not expire the new login.
  if (rotatingPassword) authEpoch++;
  const previous = retryKeys.get(signature);
  const key =
    previous && previous.expires > Date.now()
      ? previous.key
      : crypto.randomUUID();
  retryKeys.set(signature, { key, expires: Date.now() + 60000 });
  for (const [id, entry] of retryKeys)
    if (entry.expires < Date.now()) retryKeys.delete(id);
  const pending = send(path, method, body, key, options)
    .then((result) => {
      retryKeys.delete(signature);
      return result;
    })
    .finally(() => {
      inflight.delete(signature);
      if (credentialPending === pending) credentialPending = null;
    });
  inflight.set(signature, pending);
  if (rotatingPassword) credentialPending = pending;
  return pending;
}
async function send(path, method, body, key, options = {}) {
  if (
    credentialPending &&
    !publicPaths.has(path) &&
    path !== "/api/auth/password/change/"
  )
    await credentialPending;
  const requestEpoch = authEpoch;
  const headers = { Accept: "application/json" };
  if (!publicPaths.has(path)) {
    await ensureAccess();
    headers.Authorization = `Bearer ${accessToken}`;
  }
  if (method !== "GET") {
    const csrf = await request("/api/auth/csrf/");
    headers["X-CSRFToken"] = csrf.csrfToken;
    headers["Content-Type"] = "application/json";
    headers["Idempotency-Key"] = key;
    if (options.version) headers["X-Record-Version"] = options.version;
  }
  let response;
  try {
    response = await fetch(path, {
      method,
      headers,
      credentials: "include",
      signal: AbortSignal.timeout(30000),
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch {
    throw new ApiError(0, {
      detail:
        "The server did not respond. Check your connection and retry; your submission key will be reused.",
    });
  }
  const data =
    response.status === 204
      ? null
      : await response.json().catch(() => ({
          detail: "The server returned an unreadable response.",
        }));
  if (!response.ok) {
    if (
      response.status === 401 &&
      method === "GET" &&
      requestEpoch !== authEpoch &&
      !options.authRetry
    ) {
      if (credentialPending) await credentialPending;
      // Retry only an obsolete read, never a mutation, using the newly issued JWT.
      return send(path, method, body, key, { ...options, authRetry: true });
    }
    if (response.status === 401 && !publicPaths.has(path)) {
      clearAccessToken();
      window.dispatchEvent(new Event("clinic-session-expired"));
    }
    if (response.status === 403 && /csrf/i.test(data.detail || "")) {
      data.detail =
        "Your security token expired. Reload the page and try again. Your change was not submitted.";
    }
    throw new ApiError(response.status, data);
  }
  if (
    [
      "/api/auth/login/",
      "/api/v1/auth/login/",
      "/api/auth/owner/register/",
    ].includes(path)
  ) {
    clearAccessToken();
    rememberAccess(data);
  }
  if (path === "/api/auth/logout/") clearAccessToken();
  if (path === "/api/auth/password/reset/confirm/") clearAccessToken();
  if (path === "/api/auth/password/change/") {
    clearAccessToken();
    await ensureAccess();
  }
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
