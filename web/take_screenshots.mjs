import { chromium } from "@playwright/test";

async function run() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

  const routes = [
    { url: "http://localhost:3000/studio", name: "studio_desk" },
    { url: "http://localhost:3000/studio/outline", name: "studio_outline" },
    { url: "http://localhost:3000/studio/characters", name: "studio_characters" },
    { url: "http://localhost:3000/studio/lore", name: "studio_lore" },
    { url: "http://localhost:3000/studio/lore-graph", name: "studio_lore_graph" },
    { url: "http://localhost:3000/studio/intention-lab", name: "studio_intention_lab" },
    { url: "http://localhost:3000/studio/validation-loop", name: "studio_validation_loop" },
    { url: "http://localhost:3000/pricing", name: "pricing" },
    { url: "http://localhost:3000/login", name: "login" },
    { url: "http://localhost:3000/setup", name: "setup" }
  ];

  for (const r of routes) {
    console.log(`Capturing ${r.url}...`);
    await page.goto(r.url, { waitUntil: "networkidle" });
    await page.screenshot({ path: `web/screenshot_${r.name}.png` });
  }

  await browser.close();
  console.log("Screenshots captured successfully.");
}

run().catch(console.error);
