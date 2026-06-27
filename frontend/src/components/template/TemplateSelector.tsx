"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Template {
  id: string;
  name: string;
  description?: string;
  ceremony_type: string;
  structure?: {
    phases?: string[];
    columns?: string[];
    scope?: string;
  };
}

interface TemplateSelectorProps {
  templates: Template[];
  selectedId: string | null;
  onSelect: (templateId: string) => void;
}

export function TemplateSelector({ templates, selectedId, onSelect }: TemplateSelectorProps) {
  if (templates.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <p>No templates available. Create one to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {templates.map((template) => {
        const isSelected = selectedId === template.id;
        const columns = template.structure?.columns ?? [];

        return (
          <Card
            key={template.id}
            className={cn(
              "cursor-pointer transition-all",
              isSelected
                ? "ring-2 ring-slate-900 border-slate-900"
                : "hover:border-slate-400 hover:shadow-sm"
            )}
            onClick={() => onSelect(template.id)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">{template.name}</CardTitle>
                {isSelected && <Badge variant="default">Selected</Badge>}
              </div>
              {template.description && (
                <CardDescription className="text-xs">
                  {template.description}
                </CardDescription>
              )}
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-1.5">
                {columns.map((col) => (
                  <Badge key={col} variant="outline" size="sm">
                    {col}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
