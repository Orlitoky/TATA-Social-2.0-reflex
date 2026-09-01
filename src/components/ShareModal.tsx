import React, { useState } from 'react';
import { X, Share2, Send } from 'lucide-react';
import { Post } from '../types';
import { useSocial } from '../context/SocialContext';

interface ShareModalProps {
  post: Post;
  onClose: () => void;
}

export const ShareModal: React.FC<ShareModalProps> = ({ post, onClose }) => {
  const { sharePost } = useSocial();
  const [quote, setQuote] = useState('');

  const handleShare = (e: React.FormEvent) => {
    e.preventDefault();
    sharePost(post.id, quote.trim() || undefined);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0D1420]/70 p-4 backdrop-blur-xs">
      <div className="w-full max-w-lg rounded-3xl border border-slate-200 bg-white p-5 shadow-2xl animate-in fade-in zoom-in-95">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Share2 className="size-5 text-[#1E9EF5]" />
            <h2 className="text-base font-bold text-[#0D1420]">Share to TATA Feed</h2>
          </div>
          <button onClick={onClose} className="rounded-full p-1 text-slate-400 hover:bg-slate-100">
            <X className="size-5" />
          </button>
        </div>

        <form onSubmit={handleShare} className="mt-4">
          <textarea
            value={quote}
            onChange={(e) => setQuote(e.target.value)}
            placeholder="Add your thoughts about this post..."
            rows={2}
            className="w-full resize-none rounded-xl border border-slate-200 p-3 text-sm text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
          />

          {/* Original Post Preview Box */}
          <div className="mt-3 rounded-2xl border border-slate-200 bg-slate-50 p-3.5">
            <div className="flex items-center gap-2 mb-1.5">
              <img src={post.authorAvatar} alt={post.authorName} className="size-6 rounded-full object-cover" />
              <span className="text-xs font-bold text-[#0D1420]">{post.authorName}</span>
              <span className="text-[11px] text-slate-400">@{post.authorUsername}</span>
            </div>
            <p className="text-xs text-slate-700 line-clamp-3">{post.body}</p>
          </div>

          <div className="mt-5 flex justify-end gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-slate-200 px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center gap-2 rounded-xl bg-[#1E9EF5] px-5 py-2 text-xs font-bold text-white shadow-md hover:bg-sky-600 active:scale-[0.98]"
            >
              <Send className="size-3.5" />
              <span>Share Now</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
