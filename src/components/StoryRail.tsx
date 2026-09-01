import React, { useState } from 'react';
import { Plus, Eye, Sparkles } from 'lucide-react';
import { useSocial } from '../context/SocialContext';
import { useAuth } from '../context/AuthContext';
import { Story } from '../types';
import { CreateStoryModal } from './CreateStoryModal';
import { StoryViewerModal } from './StoryViewerModal';

export const StoryRail: React.FC = () => {
  const { stories } = useSocial();
  const { currentUser } = useAuth();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedStoryIndex, setSelectedStoryIndex] = useState<number | null>(null);

  if (!currentUser) return null;

  return (
    <>
      <section className="w-full rounded-2xl border border-slate-200 bg-white p-3.5 shadow-xs">
        <div className="mb-3 flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold text-[#0D1420]">Stories</h2>
            <span className="rounded-full bg-cyan-50 px-2 py-0.5 text-[11px] font-bold text-[#1E9EF5]">
              {stories.length} Live
            </span>
          </div>
          <span className="text-xs font-medium text-slate-400">24h disappearing</span>
        </div>

        {/* Stories Scrollable Row */}
        <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-none">
          {/* Add Story Button Tile */}
          <button
            onClick={() => setIsCreateOpen(true)}
            className="group relative flex h-44 w-28 shrink-0 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 transition-all hover:border-[#1E9EF5] hover:shadow-md text-left"
          >
            <div className="h-28 w-full overflow-hidden bg-slate-200">
              <img
                src={currentUser.avatarUrl}
                alt={currentUser.displayName}
                className="size-full object-cover transition-transform group-hover:scale-105"
              />
            </div>
            <div className="-mt-4 flex flex-1 flex-col items-center justify-center pb-2">
              <div className="flex size-8 items-center justify-center rounded-full border-2 border-white bg-[#1E9EF5] text-white shadow-xs group-hover:scale-110 transition-transform">
                <Plus className="size-4.5" />
              </div>
              <span className="mt-1 text-[11px] font-bold text-[#0D1420]">Add Story</span>
            </div>
          </button>

          {/* User Stories */}
          {stories.map((story, index) => {
            const isSeen = story.seen;
            return (
              <button
                key={story.id}
                onClick={() => setSelectedStoryIndex(index)}
                className={`group relative flex h-44 w-28 shrink-0 flex-col justify-between overflow-hidden rounded-2xl border transition-all hover:shadow-md text-left ${
                  isSeen
                    ? 'border-slate-200 ring-0'
                    : 'border-2 border-[#1E9EF5] ring-2 ring-sky-100 shadow-xs'
                }`}
                style={!story.mediaUrl ? { backgroundColor: story.backgroundColor } : undefined}
              >
                {/* Media or Color Background */}
                {story.mediaUrl ? (
                  <img
                    src={story.mediaUrl}
                    alt={story.authorName}
                    className="absolute inset-0 size-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                ) : (
                  <div className="absolute inset-0 p-2 flex items-center justify-center text-center">
                    <p className="line-clamp-4 text-[11px] font-bold text-white leading-tight">
                      {story.caption}
                    </p>
                  </div>
                )}

                {/* Dark Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />

                {/* Author Avatar Badge */}
                <div className="relative z-10 p-2">
                  <img
                    src={story.authorAvatar}
                    alt={story.authorName}
                    className={`size-8 rounded-full object-cover ring-2 ${
                      isSeen ? 'ring-white/80' : 'ring-[#22D3EE]'
                    }`}
                  />
                </div>

                {/* Story Footer Info */}
                <div className="relative z-10 p-2 text-white">
                  <p className="truncate text-xs font-bold leading-tight drop-shadow-xs">
                    {story.authorName}
                  </p>
                  <p className="truncate text-[10px] text-white/80">{story.createdAt}</p>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* Modals */}
      {isCreateOpen && <CreateStoryModal onClose={() => setIsCreateOpen(false)} />}
      {selectedStoryIndex !== null && (
        <StoryViewerModal
          initialIndex={selectedStoryIndex}
          onClose={() => setSelectedStoryIndex(null)}
        />
      )}
    </>
  );
};
