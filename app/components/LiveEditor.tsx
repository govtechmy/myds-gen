

import { SandpackCodeEditor, SandpackFileExplorer, SandpackLayout, SandpackPreview, SandpackProvider } from "@codesandbox/sandpack-react";

export default function Sandpackeditor({ code }: { code: string }) {
  const files = {
    "/styles.css": `@import "@govtechmy/myds-style/full.css";
@tailwind base;
@tailwind components;
@tailwind utilities;
`,
        "postcss.config.js": `module.exports = {
      plugins: {
        tailwindcss: {},
        autoprefixer: {},
      },
    }
    `,
    "tailwind.config.js": `

import { preset } from "@govtechmy/myds-style";

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "public/index.html",
    "./App.tsx",
    "src/**/*.{js,jsx,ts,tsx}",
    "node_modules/@govtechmy/myds-react/dist/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: "selector",
  presets: [preset],
};
`,
    "/index.tsx": `import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";
import { ThemeProvider } from "@govtechmy/myds-react/hooks";
import "./styles.css";

import App from "./App";

const root = createRoot(document.getElementById("root") as HTMLElement);
root.render(
  <StrictMode >
    <main className="bg-bg-white min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <ThemeProvider>
        <div className="flex justify-end items-center mb-8">
          <ThemeSwitch />
        </div>
        <div className="rounded-md text-txt-black-900">
          <App />
        </div>
      </ThemeProvider>
    </ main>
  </StrictMode>
);
`,
"index.html": `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<body>
   <script src="https://cdn.tailwindcss.com"></script>
   <div id="root"></div>
      <script type="module" src="/index.tsx"></script>
</body>
</html><!DOCTYPE html>
`,
    "/App.tsx": code
  }

  return (
    <SandpackProvider
      files={files}
      // theme="auto" 
      template="vite-react-ts"
      customSetup={{
        dependencies: {
          "@govtechmy/myds-react": "0.0.18",
          "@govtechmy/myds-style": "0.0.9",
          "@types/node": "22.5.5",
          "@types/react": "18.3.8",
          "@types/react-dom": "18.3.0",
          "postcss": "^8.4.47",
          "react": "18.3.1",
          "react-dom": "18.3.1",
          "tailwindcss": "3.4.12",
          "typescript": "^5.8.2",
          "autoprefixer": "10.4.20",
        },
        devDependencies: {
          "@govtechmy/myds-react": "0.0.18",
          "@govtechmy/myds-style": "0.0.9",
          "@types/node": "22.5.5",
          "@types/react": "18.3.8",
          "@types/react-dom": "18.3.0",
          "postcss": "^8.4.47",
          "react": "18.3.1",
          "react-dom": "18.3.1",
          "tailwindcss": "3.4.12",
          "typescript": "^5.8.2",
          "autoprefixer": "10.4.20",
        },
      }}
      options={{ externalResources: ["https://cdn.tailwindcss.com"], visibleFiles: ["/App.tsx"], activeFile: "/App.tsx" }}
    >
      <SandpackLayout style={{
        display: "grid",
        gridTemplateColumns: "1fr 4fr 10fr", 
        gridTemplateAreas: '"files editor preview"',
        width: "100%",
        gap: "0.1rem"
      }}>
        <SandpackFileExplorer style={{ height:"50vh" , minWidth: 0 }} />
        <SandpackCodeEditor closableTabs showTabs style={{ height:"50vh"  , minWidth: 0 }} />
        <SandpackPreview showOpenInCodeSandbox={true} showNavigator style={{ height:"50vh" , minWidth: 300 }} />
      </SandpackLayout>
    </SandpackProvider>
  )
}