import react from "@vitejs/plugin-react"
import { readFileSync } from "node:fs"
import { join } from "node:path"
import { defineConfig } from "vitest/config"

function inlineStylesheet() {
  let root = ""

  return {
    name: "inline-production-stylesheet",
    apply: "build" as const,
    configResolved(config: { root: string }) {
      root = config.root
    },
    transformIndexHtml: {
      order: "pre" as const,
      handler(html: string) {
        const css = readFileSync(join(root, "src", "index.css"), "utf8")
        return html.replace("</head>", `<style>${css}</style></head>`)
      },
    },
  }
}

export default defineConfig({
  plugins: [react(), inlineStylesheet()],
  test: {
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    environment: "jsdom",
    setupFiles: ["./src/test/setupTests.ts"],
    restoreMocks: true,
    clearMocks: true,
  },
})
