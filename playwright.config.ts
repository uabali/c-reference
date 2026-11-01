import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "tests/e2e",
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: "http://127.0.0.1:43123",
    ...devices["Desktop Chrome"],
  },
  webServer: {
    command: "npx serve out -l 43123",
    url: "http://127.0.0.1:43123",
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
