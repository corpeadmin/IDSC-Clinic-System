import { test, expect } from "@playwright/test";
import process from "node:process";

test("website uses revocable bearer JWTs and restores them after reload", async ({
  page,
  request,
}) => {
  const protectedHeaders = [];
  page.on("request", (req) => {
    if (new URL(req.url()).pathname === "/api/v1/dashboard/")
      protectedHeaders.push(req.headers().authorization);
  });
  await page.goto("/");
  await page.getByLabel(/^Username/).fill(process.env.CLINIC_TEST_USERNAME);
  await page.getByLabel(/^Password/).fill(process.env.CLINIC_TEST_PASSWORD);
  const login = page.waitForResponse("**/api/v1/auth/login/");
  await page.getByRole("button", { name: "Log in", exact: true }).click();
  const { access_token: token } = await (await login).json();
  expect(token.split(".")).toHaveLength(3);
  await expect(
    page.getByRole("heading", { name: "Dashboard", exact: true }),
  ).toBeVisible();
  expect(
    protectedHeaders.some((value) => value === `Bearer ${token}`),
  ).toBeTruthy();
  const headers = { Authorization: `Bearer ${token}` };
  // Independent API context has no browser login cookies.
  expect((await request.get("/api/v1/dashboard/", { headers })).status()).toBe(
    200,
  );
  const storage = await page.evaluate(() =>
    JSON.stringify([
      Object.entries(localStorage),
      Object.entries(sessionStorage),
    ]),
  );
  expect(storage).not.toContain(token);
  const renewal = page.waitForResponse("**/api/auth/token/");
  await page.reload();
  expect((await renewal).status()).toBe(200);
  await expect(
    page.getByRole("heading", { name: "Dashboard", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Log out", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Log in", exact: true }),
  ).toBeVisible();
  expect((await request.get("/api/v1/dashboard/", { headers })).status()).toBe(
    401,
  );
});
