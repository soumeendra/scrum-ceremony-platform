"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MemberList } from "@/components/team/MemberList";
import { formatDate, formatRelativeTime } from "@/lib/utils";

interface Team {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  members?: TeamMember[];
}

interface TeamMember {
  id: string;
  user_id: string;
  role: string;
  name?: string;
  email?: string;
}

interface Ceremony {
  id: string;
  title: string;
  status: string;
  phase: string;
  created_at: string;
  template_name?: string;
}

export default function TeamDetailPage() {
  const params = useParams();
  const router = useRouter();
  const teamId = params.teamId as string;

  const [team, setTeam] = useState<Team | null>(null);
  const [ceremonies, setCeremonies] = useState<Ceremony[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchTeamData() {
      try {
        const [teamRes, ceremoniesRes] = await Promise.all([
          fetch(`/api/v1/teams/${teamId}`),
          fetch(`/api/v1/teams/${teamId}/ceremonies`),
        ]);

        if (!teamRes.ok) {
          throw new Error("Failed to load team");
        }

        const teamData = await teamRes.json();
        setTeam({
          ...teamData,
          members: teamData.members ?? [],
        });

        if (ceremoniesRes.ok) {
          const ceremoniesData = await ceremoniesRes.json();
          setCeremonies(ceremoniesData.items ?? []);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load team");
      } finally {
        setIsLoading(false);
      }
    }

    if (teamId) {
      fetchTeamData();
    }
  }, [teamId]);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 bg-slate-200 rounded" />
          <div className="h-4 w-96 bg-slate-200 rounded" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
            <div className="h-64 bg-slate-200 rounded-lg" />
            <div className="h-64 bg-slate-200 rounded-lg lg:col-span-2" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !team) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="p-4 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
          {error ?? "Team not found"}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-slate-900">{team.name}</h1>
            <Badge variant={team.is_active ? "success" : "secondary"}>
              {team.is_active ? "Active" : "Inactive"}
            </Badge>
          </div>
          {team.description && (
            <p className="text-slate-600">{team.description}</p>
          )}
          <p className="text-xs text-slate-400 mt-1">
            Created {formatDate(team.created_at)}
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => router.push(`/teams/${teamId}/edit`)}>
            Edit Team
          </Button>
          <Button onClick={() => router.push(`/ceremonies/create?teamId=${teamId}`)}>
            New Retro
          </Button>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Members */}
        <div>
          <MemberList members={team.members ?? []} />
        </div>

        {/* Recent Ceremonies */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Recent Ceremonies</CardTitle>
            </CardHeader>
            <CardContent>
              {ceremonies.length === 0 ? (
                <p className="text-sm text-slate-500 py-4">
                  No ceremonies yet. Start your first retrospective!
                </p>
              ) : (
                <ul className="divide-y divide-slate-100">
                  {ceremonies.map((ceremony) => (
                    <li
                      key={ceremony.id}
                      className="flex items-center justify-between py-3 cursor-pointer hover:bg-slate-50 -mx-6 px-6"
                      onClick={() => router.push(`/ceremonies/${ceremony.id}`)}
                    >
                      <div>
                        <p className="text-sm font-medium text-slate-900">
                          {ceremony.title}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" size="sm">
                            {ceremony.phase}
                          </Badge>
                          {ceremony.template_name && (
                            <span className="text-xs text-slate-400">
                              {ceremony.template_name}
                            </span>
                          )}
                        </div>
                      </div>
                      <span className="text-xs text-slate-400">
                        {formatRelativeTime(ceremony.created_at)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
