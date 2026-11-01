import { mkdirSync } from "node:fs";
import { expect, test } from "@playwright/test";

const shots = "/opt/cursor/artifacts/screenshots";
mkdirSync(shots, { recursive: true });

test("home page names the reference and the license", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "The C language, set so you can learn it." })).toBeVisible();
  await expect(page.getByText("CC BY-SA 3.0").first()).toBeVisible();
  await page.screenshot({ path: `${shots}/home.png` });
  await page.getByLabel("Search the reference").fill("pointer");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page).toHaveURL(/\/search\/\?q=pointer/);
});

test("pointer page shows upstream text, attribution, and added notes", async ({ page }) => {
  await page.goto("/reference/c/language/pointer/");
  await expect(page.getByRole("heading", { name: "Pointer declaration" })).toBeVisible();
  await expect(page.getByText("CC BY-SA 3.0").first()).toBeVisible();
  await expect(page.getByText("Added on c.umutabali.com").first()).toBeVisible();
  await expect(page.getByRole("link", { name: "array" }).first()).toHaveAttribute("href", "/reference/c/language/array/");
  await expect(page.getByText("Related topics")).toBeVisible();
  await page.screenshot({ path: `${shots}/reference-pointer.png` });
});

test("full-text search ranks strlen", async ({ page }) => {
  await page.goto("/search/?q=strlen");
  await expect(page.getByRole("link", { name: "strlen, strnlen_s" }).first()).toBeVisible();
  await page.screenshot({ path: `${shots}/search.png` });
});

test("graph canvas renders", async ({ page }) => {
  await page.goto("/graph/");
  await expect(page.getByRole("heading", { name: "Topic graph" })).toBeVisible();
  await expect(page.locator(".react-flow")).toBeVisible();
  await page.screenshot({ path: `${shots}/graph.png` });
});

test("stack diagram responds to malloc", async ({ page }) => {
  await page.goto("/diagrams/stack-heap/");
  await expect(page.getByRole("heading", { name: "Stack and heap" })).toBeVisible();
  await page.getByRole("button", { name: "malloc" }).click();
  await expect(page.getByText("block 1")).toBeVisible();
  await page.screenshot({ path: `${shots}/diagram-stack-heap.png` });
});
