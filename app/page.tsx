"use client"
import { WarningIcon } from "@govtechmy/myds-react/icon";
import { ThemeProvider } from "@govtechmy/myds-react/hooks";
import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";

export default function Home() {
  return (
    <main className="bg-bg-white">
      <ThemeProvider >
        <div className="bg-gray-50 dark:bg-gray-900 min-h-screen flex flex-col items-center justify-center">
          <div className="flex flex-col items-center justify-center px-4 py-8 sm:px-6 lg:px-8">
            <div className="max-w-md text-center">
              <div className="flex justify-center">
                <div className="p-4 rounded-full bg-warning-100 dark:bg-warning-900">
                  <WarningIcon className="h-12 w-12 text-warning-500 dark:text-warning-300" />
                </div>
              </div>
              <h1 className="mt-6 text-3xl font-semibold text-gray-900 dark:text-white">
                404 - Page Not Found
              </h1>
              <p className="mt-4 text-base text-gray-500 dark:text-gray-400">
                We're sorry, but the page you requested could not be found.
              </p>
            </div>
            <div className="mt-8">
              <ThemeSwitch />
            </div>
          </div>
        </div>
      </ThemeProvider>
    </main>
  );
}
