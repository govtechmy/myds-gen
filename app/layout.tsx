import "./globals.css";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "MYDS-Gen",
  description: "Discover the potential of the Malaysian Design System",
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
