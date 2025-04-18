import "./globals.css";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "MYDS - Jen",
  description: "Discover the possibilities of the Malaysian Design System",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-bg-white min-h-screen">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
