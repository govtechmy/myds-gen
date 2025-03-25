

import { Sandpack, SandpackCodeEditor, SandpackFileExplorer, SandpackLayout, SandpackPreview, SandpackProvider, SandpackTranspiledCode } from "@codesandbox/sandpack-react";

export default function Sandpackeditor({ code }: { code: string }) {
  const files = {
    "styles.css": `@import "@govtechmy/myds-style/full.css";
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
    "tailwind.config.ts": `
import type { Config } from "tailwindcss";
import { preset } from "@govtechmy/myds-style";

const config: Config = {
  content: [
      "**/*",
      "node_modules/@govtechmy/myds-react/dist/**/*.{js,jsx,ts,tsx}",
    ],
    darkMode: "selector",
    presets: [preset],
  };
  export default config;
  `,

    "index.tsx": `import React from 'react';
import ReactDOM from 'react-dom/client';
  import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";
  import { ThemeProvider } from "@govtechmy/myds-react/hooks";
  import "./styles.css";

  import App from "./App";

  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
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
    </React.StrictMode>
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
    "App.tsx": code
  }

  return (
    <Sandpack

      files={files}
      // theme="auto" 
      template="vite-react-ts"
      customSetup={{
        dependencies: {
          "@govtechmy/myds-react": "^0.0.21",
          "@govtechmy/myds-style": "^0.0.9",
          "postcss": "^8.5.3",
          "tailwindcss": "3",
          "typescript": "5.7.3",
          "autoprefixer": "10.4.20",
        }
      }}

      options={{ editorHeight: "85vh", visibleFiles: ["/App.tsx"], activeFile: "/App.tsx", showConsoleButton: true, resizablePanels: true, recompileMode: "immediate", showInlineErrors: true }}
    />
  )
}