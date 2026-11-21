import { test, expect } from "@playwright/test";
import process from "node:process";
import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

test("forgot-password email link resets credentials once and revokes old access", async ({
  page,
  request,
}) => {
  const outbox = process.env.CLINIC_TEST_EMAIL_OUTBOX;
  test.skip(
    !outbox,
    "Requires an isolated file email backend/outbox; never use a real mailbox.",
  );
  const username = `recover_${Date.now()}`;
  const email = `${username}@example.test`;
  const original = "DisposableGarden!49183";
  const replacement = "DifferentForest!71923";
  async function post(context, url, data) {
    const csrf = await context.get("/api/auth/csrf/");
    return context.post(url, {
      headers: { "X-CSRFToken": (await csrf.json()).csrfToken },
      data,
    });
  }
  await post(request, "/api/auth/login/", {
    username: process.env.CLINIC_TEST_USERNAME,
    password: process.env.CLINIC_TEST_PASSWORD,
  });
  const created = await post(request, "/api/v1/users/", {
    username,
    email,
    password: original,
  });
  expect(created.status()).toBe(201);
  const userId = (await created.json()).user_id;
  try {
    const oldLogin = await post(page.request, "/api/auth/login/", {
      username,
      password: original,
    });
    const oldToken = (await oldLogin.json()).access_token;
    await page.context().clearCookies();
    expect(
      (
        await request.get("/api/v1/dashboard/", {
          headers: { Authorization: `Bearer ${oldToken}` },
        })
      ).status(),
    ).toBe(200);
    await page.goto("/");
    await page.getByRole("button", { name: "Forgot password?" }).click();
    const dialog = page.getByRole("dialog", { name: "Forgot password" });
    await expect(dialog.getByLabel("Email address")).toBeFocused();
    await dialog
      .getByLabel("Email address")
      .fill(`unknown_${Date.now()}@example.test`);
    await dialog.getByRole("button", { name: "Send reset link" }).click();
    await expect(dialog.getByRole("alert")).toContainText(
      "No active Clinic account was found",
    );
    await expect(dialog.getByRole("status")).toHaveCount(0);
    await dialog.getByLabel("Email address").fill(email);
    const before = new Set(existsSync(outbox) ? readdirSync(outbox) : []);
    await dialog.getByRole("button", { name: "Send reset link" }).click();
    await expect(dialog.getByRole("status")).toContainText(
      "Check your inbox and spam folder",
    );
    let message = "";
    await expect
      .poll(() => {
        for (const file of readdirSync(outbox)) {
          if (before.has(file)) continue;
          // The file backend contains MIME data, not an already-decoded inbox body.
          const body = readFileSync(join(outbox, file), "utf8")
            .replace(/=\r?\n/g, "")
            .replace(/=([0-9A-F]{2})/gi, (_, hex) =>
              String.fromCharCode(parseInt(hex, 16)),
            );
          if (body.includes(email)) message = body;
        }
        return !!message;
      })
      .toBeTruthy();
    const link = message.match(
      /https?:\/\/[^\s<>]+#reset-password\?[^\s<>]+/,
    )[0];
    const params = Object.fromEntries(
      new URLSearchParams(new URL(link).hash.split("?")[1]),
    );
    await page.goto(link);
    await expect(
      page.getByRole("heading", { name: "Reset your password", exact: true }),
    ).toBeVisible();
    expect(page.url()).not.toContain(params.token);
    await page.getByLabel("New password", { exact: true }).fill(replacement);
    await page
      .getByLabel("Confirm new password", { exact: true })
      .fill("Mismatch!73192");
    await page
      .getByRole("button", { name: "Reset password", exact: true })
      .click();
    await expect(page.getByText("The passwords do not match.")).toBeVisible();
    await page
      .getByLabel("Confirm new password", { exact: true })
      .fill(replacement);
    const resetResponse = page.waitForResponse(
      "**/api/auth/password/reset/confirm/",
    );
    await page
      .getByRole("button", { name: "Reset password", exact: true })
      .click();
    const response = await resetResponse;
    expect(response.status(), JSON.stringify(await response.json())).toBe(200);
    await expect(
      page.getByRole("heading", { name: "Password reset complete" }),
    ).toBeVisible();
    expect(
      (
        await request.get("/api/v1/dashboard/", {
          headers: { Authorization: `Bearer ${oldToken}` },
        })
      ).status(),
    ).toBe(401);
    expect(
      (
        await post(page.request, "/api/auth/password/reset/confirm/", {
          ...params,
          new_password: replacement,
          confirm_password: replacement,
        })
      ).status(),
    ).toBe(400);
    await page.getByRole("button", { name: "Back to login" }).click();
    await page.getByLabel(/^Username/).fill(username);
    await page.getByLabel(/^Password/).fill(original);
    await page.getByRole("button", { name: "Log in", exact: true }).click();
    await expect(page.getByText("Invalid username or password.")).toBeVisible();
    await page.getByLabel(/^Password/).fill(replacement);
    await page.getByRole("button", { name: "Log in", exact: true }).click();
    await expect(
      page.getByRole("heading", { name: "Dashboard", exact: true }),
    ).toBeVisible();
    await page.goto(link);
    await page
      .getByLabel("New password", { exact: true })
      .fill("AnotherGarden!49183");
    await page
      .getByLabel("Confirm new password", { exact: true })
      .fill("AnotherGarden!49183");
    await page
      .getByRole("button", { name: "Reset password", exact: true })
      .click();
    await expect(page.getByRole("alert")).toContainText(
      "invalid or has expired",
    );
  } finally {
    const csrf = await request.get("/api/auth/csrf/");
    await request.delete(`/api/v1/users/${userId}/`, {
      headers: { "X-CSRFToken": (await csrf.json()).csrfToken },
      data: { current_password: process.env.CLINIC_TEST_PASSWORD },
    });
  }
});
