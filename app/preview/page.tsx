"use client"
import CompOnet from "./generatedComponent";
import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";
import { ThemeProvider } from "@govtechmy/myds-react/hooks";
export default function Preview() {
  return (
    <main className="bg-bg-white min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <ThemeProvider >
        <div className="flex justify-end items-center mb-8">
          <ThemeSwitch />
        </div>
        <div className="bg-bg-white rounded-md text-txt-black-900">
          <CompOnet />
        </div>
      </ThemeProvider>
    </main>
  );
}