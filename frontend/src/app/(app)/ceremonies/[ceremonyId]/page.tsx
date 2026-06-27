import { Board } from "@/components/board";

export default async function CeremonyPage({
  params,
}: {
  params: Promise<{ ceremonyId: string }>;
}) {
  const { ceremonyId } = await params;

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      <Board ceremonyId={ceremonyId} templateId={null} />
    </div>
  );
}
