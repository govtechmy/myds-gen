"use client";

import React, { useEffect, useRef, useState } from "react";
import sdk, { VM } from "@stackblitz/sdk";

interface StackBlitzEditorProps {
  code: string;
}

const projectFiles = (appCode: string) => ({
  "index.html": `<!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8" />
     <link rel="icon" type="image/svg+xml" href="/vite.svg" />
     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
     <title>MYDS StackBlitz</title>
   </head>
   <body>
     <div id="root"></div>
     <script type="module" src="/src/index.tsx"></script>
   </body>
   </html>
     `,
  "package.json": JSON.stringify(
    {
      name: "vite-react-ts-myds",
      private: true,
      version: "0.0.0",
      scripts: {
        dev: "vite",
        build: "tsc && vite build",
        preview: "vite preview",
      },
      dependencies: {
        "@govtechmy/myds-react": "^0.0.22",
        "@govtechmy/myds-style": "^0.0.10",
        react: "^18.2.0",
        "react-dom": "^18.2.0",
      },
      devDependencies: {
        "@types/react": "^18.2.43",
        "@types/react-dom": "^18.2.17",
        "@vitejs/plugin-react": "^4.2.1",
        autoprefixer: "^10.4.19",
        postcss: "^8.4.38",
        tailwindcss: "^3.4.3",
        typescript: "^5.2.2",
        vite: "^5.0.8",
      },
    },
    null,
    2
  ),
  "vite.config.ts": `import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'

   
   export default defineConfig({
     plugins: [react()],
   })
     `,
  "tailwind.config.js": `
   import { preset } from "@govtechmy/myds-style";

   /** @type {import('tailwindcss').Config} */
   export default {
     content: [
       "./index.html",
       "./src/**/*.{js,ts,jsx,tsx}",
       "../node_modules/@govtechmy/myds-react/dist/**/*.{js,jsx,ts,tsx}",
     ],
     darkMode: "selector",
     presets: [preset],
   };
   `,
  "postcss.config.js": `module.exports = {
     plugins: {
       tailwindcss: {},
       autoprefixer: {},
     },
   }
   `,
  "tsconfig.json": JSON.stringify(
    {
      compilerOptions: {
        target: "ES2020",
        useDefineForClassFields: true,
        lib: ["ES2020", "DOM", "DOM.Iterable"],
        module: "ESNext",
        skipLibCheck: true,
        moduleResolution: "bundler",
        allowImportingTsExtensions: true,
        resolveJsonModule: true,
        isolatedModules: true,
        noEmit: true,
        jsx: "react-jsx",
        strict: true,
        noUnusedLocals: true,
        noUnusedParameters: true,
        noFallthroughCasesInSwitch: true,
        allowSyntheticDefaultImports: true,
        forceConsistentCasingInFileNames: true,
      },
      include: [
        "src",
        "vite.config.ts",
        "tailwind.config.js",
        "postcss.config.js",
      ],
      references: [{ path: "./tsconfig.node.json" }],
    },
    null,
    2
  ),
  "tsconfig.node.json": JSON.stringify(
    {
      compilerOptions: {
        composite: true,
        skipLibCheck: true,
        module: "ESNext",
        moduleResolution: "bundler",
        allowSyntheticDefaultImports: true,
      },
      include: ["vite.config.ts"],
    },
    null,
    2
  ),

  "src/index.tsx": `import React from 'react';
   import ReactDOM from 'react-dom/client';
   import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";
   import { ThemeProvider } from "@govtechmy/myds-react/hooks";
   import './styles.css'; 

   import App from './App'; 

   ReactDOM.createRoot(document.getElementById('root')!).render(
     <React.StrictMode>
       <main className="bg-bg-white dark:bg-bg-dark min-h-screen py-12 px-4 sm:px-6 lg:px-8"> {/* Add dark mode class */}
         <ThemeProvider>
           <div className="flex justify-end items-center mb-8">
             {/* Add ThemeSwitch inside the embed for consistency */}
             <ThemeSwitch />
           </div>
           <div className="rounded-md text-txt-black-900 dark:text-txt-dark"> {/* Add dark mode class */}
             <App />
           </div>
         </ThemeProvider>
       </main>
     </React.StrictMode>
   );
   `,
  "src/App.tsx": appCode,
  "src/styles.css": `@import "@govtechmy/myds-style/full.css";

   /* Add Tailwind directives */
   @tailwind base;
   @tailwind components;
   @tailwind utilities;

   /* Optional: Add any other base styles here */
   body {
     margin: 0;
     font-family: sans-serif; /* Or your preferred font */
   }
   `,
});

export default function StackBlitzEditor({ code }: StackBlitzEditorProps) {
  const embedId = "stackblitz-embed";
  const vmRef = useRef<VM | null>(null);
  const [isVmReady, setIsVmReady] = useState(false);
  const isInitialMount = useRef(true);
  const initialCodeRef = useRef(code);

  useEffect(() => {
    console.log("[Mount Effect] Running...");

    initialCodeRef.current = code;
    console.log("[Mount Effect] Stored initial code.");

    let isCancelled = false;

    async function embedAndGetVm() {
      try {
        console.log("[Mount Effect] Starting sdk.embedProject...");

        const vm = await sdk.embedProject(
          embedId,
          {
            files: projectFiles(initialCodeRef.current),
            title: "MYDS Generated Component",
            description:
              "Component generated based on prompt and rendered with MYDS.",
            template: "node",
            settings: {
              compile: { trigger: "auto", clearConsole: true },
            },
          },
          {
            clickToLoad: false,
            openFile: "src/App.tsx",
            view: "default",
            height: "100%",
            theme: "light",
            hideExplorer: false,
            forceEmbedLayout: true,
            showSidebar: true,
          }
        );

        if (isCancelled) {
          console.log("[Mount Effect] Cancelled after embedProject.");
          return;
        }
        console.log(
          "[Mount Effect] sdk.embedProject SUCCESS, VM instance obtained."
        );

        vmRef.current = vm;
        setIsVmReady(true);
        console.log("[Mount Effect] Set isVmReady = true");
      } catch (error) {
        if (!isCancelled) {
          console.error("[Mount Effect] Error during embedProject:", error);
          setIsVmReady(false);
        } else {
          console.log(
            "[Mount Effect] Error caught but component unmounted:",
            error
          );
        }
      }
    }

    embedAndGetVm();
    return () => {
      isCancelled = true;
      console.log(
        "[Mount Effect] Cleanup: Setting isCancelled=true, resetting state."
      );
      isInitialMount.current = true;
      // vmRef.current?.preview?.destroy();
      vmRef.current = null;
      setIsVmReady(false);
    };
  }, []);

  useEffect(() => {
    console.log(
      `[Update Effect] Running. Code changed: ${
        code !== initialCodeRef.current
      }. InitialMount: ${isInitialMount.current}. isVmReady: ${isVmReady}.`
    );

    if (isInitialMount.current) {
      isInitialMount.current = false;
      console.log("[Update Effect] Setting isInitialMount = false.");
      return;
    }

    if (vmRef.current && isVmReady) {
      console.log("[Update Effect] VM is ready. Applying FS diff...");
      vmRef.current
        .applyFsDiff({
          create: { "src/App.tsx": code },
          destroy: [],
        })
        .then(() => {
          console.log("[Update Effect] FS Diff applied successfully.");
        })
        .catch((error) => {
          console.error("[Update Effect] Error applying FS Diff:", error);
          setIsVmReady(false);
          console.log(
            "[Update Effect] Set isVmReady = false due to FS Diff error."
          );
        });
    } else {
      if (!isVmReady) {
        console.log("[Update Effect] Skipping FS diff: VM not ready yet.");
      } else if (!vmRef.current) {
        console.log(
          "[Update Effect] Skipping FS diff: VM ref is null (this should not happen if isVmReady is true)."
        );
      }
    }
  }, [code, isVmReady]);

  return (
    <div
      id={embedId}
      style={{ width: "100%", border: "1px solid #ccc", minHeight: "85vh" }}
    >
      Loading StackBlitz Editor...
    </div>
  );
}
