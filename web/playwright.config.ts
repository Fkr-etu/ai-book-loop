import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  fullyParallel: true,
  workers: process.env.CI ? 3 : undefined,
  timeout: 15 * 1000,
  expect: {
    timeout: 4 * 1000
  },
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    viewport: { width: 1400, height: 900 },
    actionTimeout: 8 * 1000,
    navigationTimeout: 8 * 1000
  },
  forbidOnly: false,
  retries: 0,
  reporter: "list",
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ],
  webServer: {
    command: "npm run start",
    url: "http://localhost:3000",
    reuseExistingServer: true,
    timeout: 120 * 1000
  }
});
