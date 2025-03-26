import type { Config } from "tailwindcss";
import colors from "tailwindcss/colors";
import tailwindCSSAnimate from "tailwindcss-animate";
import { preset } from "@govtechmy/myds-style";

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './api/**/*.{js,ts,jsx,tsx,mdx}',
    'node_modules/@govtechmy/myds-react/dist/**/*.{js,jsx,ts,tsx}',
  ],
  darkMode: "selector",
  presets: [preset],
  plugins: [tailwindCSSAnimate],
};
export default config;