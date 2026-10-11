import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  // Optional local API token (off by default). Read from the shell env or
  // backend/.env so it is configured in one place. The proxy adds it to
  // requests server-side, so it is never bundled into browser JS.
  const env = loadEnv(mode, "../backend", "RMF_BUDDY_");
  const token = (process.env.RMF_BUDDY_TOKEN ?? env.RMF_BUDDY_TOKEN ?? "").trim();
  const apiProxy = {
    target: "http://127.0.0.1:8911",
    ...(token ? { headers: { "X-RMF-Buddy-Token": token } } : {}),
  };

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: { "/api": apiProxy },
    },
    preview: {
      proxy: { "/api": apiProxy },
    },
  };
});
