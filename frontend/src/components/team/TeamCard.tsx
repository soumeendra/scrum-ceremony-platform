"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatRelativeTime } from "@/lib/utils";

interface Team {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  member_count?: number;
  last_activity?: string;
  created_at?: string;
}

interface TeamCardProps {
  team: Team;
}

export function TeamCard({ team }: TeamCardProps) {
  const router = useRouter();

  return (
    <Card
      className="cursor-pointer transition-shadow hover:shadow-md"
      onClick={() => router.push(`/teams/${team.id}`)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{team.name}</CardTitle>
          <Badge variant={team.is_active ? "success" : "secondary"}>
            {team.is_active ? "Active" : "Inactive"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {team.description && (
          <p className="text-sm text-slate-500 mb-3 line-clamp-2">
            {team.description}
          </p>
        )}
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>{team.member_count ?? 0} members</span>
          {team.last_activity && (
            <span>Last activity {formatRelativeTime(team.last_activity)}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
