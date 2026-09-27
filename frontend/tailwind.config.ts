import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: { extend: { colors: { ink: "#0b1117", panel: "#111a22", line: "#20303a", mint: "#64e6b3", coral: "#ff796d" } } },
  plugins: [],
};
export default config;
