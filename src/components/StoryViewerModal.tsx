import React, { useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, Eye, Send, Heart } from 'lucide-react';
import { useSocial } from '../context/SocialContext';
import { ReactionType } from '../types';

const STORY_REACTIONS: { type: ReactionType; emoji: string; label: string }[] = [
  { type: 'like', emoji: '👍', label: 'Like' },
  { type: 'love', emoji: '❤️', label: 'Love' },
  { type: 'haha', emoji: '😂', label: 'Haha' },
  { type: 'wow', emoji: '😮', label: 'Wow' },
  { type: 'sad', emoji: '😢', label: 'Sad' },
  { type: 'angry', emoji: '😡', label: 'Angry' },
];

interface StoryViewerModalProps {
  initialIndex: number;
  onClose: () => void;
}

export const StoryViewerModal: React.FC<StoryViewerModalProps> = ({ initialIndex, onClose }) => {
  const { stories, reactToStory, replyToStory, markStorySeen } = useSocial();
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [replyText, setReplyText] = useState('');

  const currentStory = stories[currentIndex] || stories[0];

  useEffect(() => {
    if (currentStory && !currentStory.seen) {
      markStorySeen(currentStory.id);
    }
  }, [currentIndex, currentStory]);

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : stories.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < stories.length - 1 ? prev + 1 : 0));
  };

  const handleSendReply = (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyText.trim()) return;
    replyToStory(currentStory.id, replyText);
    setReplyText('');
  };

  if (!currentStory) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4 backdrop-blur-md">
      <div className="relative flex h-[85vh] max-h-[720px] w-full max-w-sm flex-col justify-between overflow-hidden rounded-3xl bg-[#0D1420] text-white shadow-2xl">
        {/* Story Progress Bar */}
        <div className="absolute top-2 left-2 right-2 z-20 flex gap-1.5">
          {stories.map((_, i) => (
            <div key={i} className="h-1 flex-1 rounded-full bg-white/30 overflow-hidden">
              <div
                className={`h-full bg-white transition-all duration-300 ${
                  i === currentIndex ? 'w-full' : i < currentIndex ? 'w-full' : 'w-0'
                }`}
              />
            </div>
          ))}
        </div>

        {/* Top Header */}
        <div className="relative z-20 flex items-center justify-between p-4 pt-5 bg-gradient-to-b from-black/70 to-transparent">
          <div className="flex items-center gap-2.5">
            <img
              src={currentStory.authorAvatar}
              alt={currentStory.authorName}
              className="size-9 rounded-full object-cover ring-2 ring-[#22D3EE]"
            />
            <div>
              <p className="text-xs font-bold leading-tight">{currentStory.authorName}</p>
              <p className="text-[10px] text-white/70">{currentStory.createdAt}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 rounded-full bg-black/40 px-2 py-0.5 text-[11px] font-semibold text-white/90">
              <Eye className="size-3" />
              <span>{currentStory.viewCount}</span>
            </div>
            <button
              onClick={onClose}
              className="rounded-full bg-black/40 p-1.5 text-white/80 hover:bg-black/60 hover:text-white"
            >
              <X className="size-4.5" />
            </button>
          </div>
        </div>

        {/* Main Content (Image or Color with typography) */}
        <div
          className="relative flex flex-1 items-center justify-center p-6 text-center overflow-hidden"
          style={!currentStory.mediaUrl ? { backgroundColor: currentStory.backgroundColor } : undefined}
        >
          {currentStory.mediaUrl ? (
            <img
              src={currentStory.mediaUrl}
              alt={currentStory.caption}
              className="absolute inset-0 size-full object-cover"
            />
          ) : null}

          {/* Caption */}
          {currentStory.caption && (
            <div className="relative z-10 rounded-2xl bg-black/40 px-6 py-4 backdrop-blur-xs max-w-[90%]">
              <p className="text-base font-bold leading-relaxed text-white drop-shadow-md">
                {currentStory.caption}
              </p>
            </div>
          )}

          {/* Left / Right Nav Arrows */}
          <button
            onClick={handlePrev}
            className="absolute left-2 top-1/2 -translate-y-1/2 z-20 rounded-full bg-black/40 p-2 text-white hover:bg-black/70"
          >
            <ChevronLeft className="size-5" />
          </button>
          <button
            onClick={handleNext}
            className="absolute right-2 top-1/2 -translate-y-1/2 z-20 rounded-full bg-black/40 p-2 text-white hover:bg-black/70"
          >
            <ChevronRight className="size-5" />
          </button>
        </div>

        {/* Footer: Reactions & Reply Composer */}
        <div className="relative z-20 bg-gradient-to-t from-black via-black/80 to-transparent p-4 pb-4">
          {/* Reaction Bar */}
          <div className="flex items-center justify-around gap-1 pb-3">
            {STORY_REACTIONS.map((choice) => (
              <button
                key={choice.type}
                onClick={() => reactToStory(currentStory.id, choice.type)}
                className={`rounded-full px-2.5 py-1 text-base transition-transform active:scale-125 ${
                  currentStory.myReaction === choice.type
                    ? 'bg-[#1E9EF5] scale-110 shadow-md'
                    : 'bg-white/10 hover:bg-white/20'
                }`}
                title={choice.label}
              >
                {choice.emoji}
              </button>
            ))}
          </div>

          {/* Replies Thread if any */}
          {currentStory.replies.length > 0 && (
            <div className="mb-2 max-h-24 space-y-1 overflow-y-auto rounded-xl bg-white/10 p-2 text-xs">
              {currentStory.replies.map((rep) => (
                <p key={rep.id} className="text-slate-200">
                  <strong className="text-white font-semibold">{rep.authorName}:</strong> {rep.body}
                </p>
              ))}
            </div>
          )}

          {/* Reply Form */}
          <form onSubmit={handleSendReply} className="flex items-center gap-2">
            <input
              type="text"
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              placeholder={`Reply to ${currentStory.authorName}...`}
              className="flex-1 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs text-white placeholder:text-white/50 focus:border-[#22D3EE] focus:bg-white/20 focus:outline-hidden"
            />
            <button
              type="submit"
              disabled={!replyText.trim()}
              className="flex size-9 items-center justify-center rounded-full bg-[#1E9EF5] text-white hover:bg-sky-500 disabled:opacity-50"
            >
              <Send className="size-3.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
