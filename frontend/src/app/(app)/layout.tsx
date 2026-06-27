import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import Link from "next/link";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { userId } = await auth();

  if (!userId) {
    redirect("/sign-in");
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-bold text-slate-900">
            SCP
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/teams" className="text-sm text-slate-600 hover:text-slate-900">
              Teams
            </Link>
            <Link href="/analytics" className="text-sm text-slate-600 hover:text-slate-900">
              Analytics
            </Link>
          </div>
        </div>
      </nav>
      <main>{children}</main>
    </div>
  );
}
