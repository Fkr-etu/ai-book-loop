"use client";

import { StudioLayout } from "@/components/StudioLayout";
import { ChapterToolbar } from "./components/ChapterToolbar";
import { ManuscriptEditor } from "./components/ManuscriptEditor";
import { StudioSidebar } from "./components/StudioSidebar";
import { useStudioChapter } from "./hooks/useStudioChapter";

export default function StudioDeskPage() {
  const controller = useStudioChapter();

  return (
    <StudioLayout>
      <div className="flex min-h-[calc(100vh-61px)] flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        <main className="flex-1 overflow-y-auto bg-[#f8f5f0] p-4 sm:p-6 md:p-10">
          <div className="mx-auto flex w-full max-w-[760px] flex-col">
            <ChapterToolbar controller={controller} />
            <ManuscriptEditor controller={controller} />
          </div>
        </main>
        <StudioSidebar controller={controller} />
      </div>
    </StudioLayout>
  );
}
