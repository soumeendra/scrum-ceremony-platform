import { ClerkProvider } from "@clerk/nextjs";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { QueryClientProvider } from "@/lib/query-client";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Scrum Ceremony Platform — Run Better Ceremonies",
  description:
    "Purpose-built platform for Scrum Masters to run retrospectives, planning poker, standups, and health checks with measurable outcomes.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body className={inter.className}>
          <QueryClientProvider>
            <AuthProvider>{children}</AuthProvider>
          </QueryClientProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
