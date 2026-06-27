import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="container mx-auto px-4 py-24 text-center">
        <h1 className="text-5xl font-bold text-slate-900 mb-6">
          Run Better Ceremonies
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-12">
          The ceremony operating system for Scrum Masters. Retrospectives,
          planning poker, standups, and health checks — with measurable outcomes.
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg">Get Started Free</Button>
          <Button variant="outline" size="lg">Watch Demo</Button>
        </div>
      </div>
    </div>
  );
}
