// Real proxy smoke: no intercepted API responses or fabricated browser data.
import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
const require = createRequire(
  new URL("../../frontend/package.json", import.meta.url),
);
const { chromium } = require("@playwright/test");
const axe = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const browser = await chromium.launch({ channel: "msedge", headless: true });
const results = [];
try {
  for (const width of [375, 768, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    for (const route of [
      "/",
      "/demo",
      "/evidence/local",
      "/evidence/global",
      "/evidence/stability",
      "/evidence/subgroups",
      "/evidence/feasibility",
      "/review",
      "/audit-history",
      "/model-card",
      "/sign-in",
    ]) {
      const response = await page.goto("http://127.0.0.1:18080" + route);
      assert.equal(response.status(), 200);
      await page.getByRole("heading", { level: 1 }).first().waitFor();
      await page.waitForFunction(
        () => !document.querySelector('[role="status"]'),
      );
      assert.ok(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      );
      await page.evaluate(axe);
      const violations = await page.evaluate(
        async () =>
          (
            await window.axe.run({
              runOnly: {
                type: "tag",
                values: ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"],
              },
            })
          ).violations,
      );
      assert.deepEqual(violations, [], `${route} at ${width}px`);
      results.push({ route, width, axeViolations: violations.length });
    }
    await page.goto("http://127.0.0.1:18080/");
    await page.keyboard.press("Tab");
    assert.equal(
      await page
        .getByRole("link", { name: "Skip to content" })
        .evaluate((element) => element === document.activeElement),
      true,
    );
    await page.keyboard.press("Enter");
    assert.equal(
      await page
        .getByRole("main")
        .evaluate((element) => element === document.activeElement),
      true,
    );
    await page.emulateMedia({ colorScheme: "dark", reducedMotion: "reduce" });
    await page.goto("http://127.0.0.1:18080/evidence/local");
    await page.getByRole("table").waitFor();
    assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
    assert.deepEqual(errors, []);
    await page.close();
  }
  writeFileSync(
    new URL(
      "../../artifacts/stage3-verification/proxy-browser.json",
      import.meta.url,
    ),
    JSON.stringify(
      { results, keyboard: "passed", darkReducedMotion: "passed" },
      null,
      2,
    ),
  );
  console.log(
    `${results.length} real proxy route/viewport accessibility checks passed; keyboard and dark/reduced-motion smoke passed.`,
  );
} finally {
  await browser.close();
}
