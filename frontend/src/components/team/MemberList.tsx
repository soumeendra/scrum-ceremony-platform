"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface TeamMember {
  id: string;
  user_id: string;
  role: string;
  name?: string;
  email?: string;
}

interface MemberListProps {
  members: TeamMember[];
}

const ROLE_LABELS: Record<string, { label: string; variant: "default" | "secondary" | "accent" }> = {
  scrum_master: { label: "Scrum Master", variant: "accent" },
  product_owner: { label: "Product Owner", variant: "default" },
  member: { label: "Member", variant: "secondary" },
};

export function MemberList({ members }: MemberListProps) {
  if (members.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Members</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">No members yet.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Members ({members.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="divide-y divide-slate-100">
          {members.map((member) => {
            const roleInfo = ROLE_LABELS[member.role] ?? ROLE_LABELS.member;
            return (
              <li key={member.id} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-sm font-medium text-slate-600">
                    {(member.name ?? member.user_id).charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">
                      {member.name ?? member.user_id}
                    </p>
                    {member.email && (
                      <p className="text-xs text-slate-500">{member.email}</p>
                    )}
                  </div>
                </div>
                <Badge variant={roleInfo.variant} size="sm">
                  {roleInfo.label}
                </Badge>
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
}
