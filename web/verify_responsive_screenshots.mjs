import { chromium } from "@playwright/test";

async function run() {
  const browser = await chromium.launch();

  // Mobile Context (iPhone 12 / 390x844)
  const mobileContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true
  });
  const mobilePage = await mobileContext.newPage();

  console.log("Capturing mobile pages...");
  await mobilePage.goto("http://localhost:3000/studio", { waitUntil: "networkidle" });
  await mobilePage.screenshot({ path: "web/screenshot_mobile_studio.png" });

  // Open mobile sidebar drawer
  const toggleBtn = mobilePage.getByRole("button", { name: "Toggle Studio Sidebar" });
  if (await toggleBtn.isVisible()) {
    await toggleBtn.click();
    await mobilePage.screenshot({ path: "web/screenshot_mobile_studio_sidebar_open.png" });
  }

  await mobilePage.goto("http://localhost:3000/dashboard", { waitUntil: "networkidle" });
  await mobilePage.screenshot({ path: "web/screenshot_mobile_dashboard.png" });

  await mobilePage.goto("http://localhost:3000/pricing", { waitUntil: "networkidle" });
  await mobilePage.screenshot({ path: "web/screenshot_mobile_pricing.png" });

  await mobileContext.close();

  // Desktop Context (1400x900)
  const desktopContext = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const desktopPage = await desktopContext.newPage();

  console.log("Capturing desktop pages...");
  await desktopPage.goto("http://localhost:3000/studio", { waitUntil: "networkidle" });
  await desktopPage.screenshot({ path: "web/screenshot_desktop_studio.png" });

  await desktopContext.close();
  await browser.close();

  console.log("Responsive screenshots captured successfully.");
}

run().catch(console.error);
