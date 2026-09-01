import React, { useState } from 'react';
import { StoryRail } from '../components/StoryRail';
import { PostComposer } from '../components/PostComposer';
import { PostCard } from '../components/PostCard';
import { useSocial } from '../context/SocialContext';
import { Sparkles, Users, Flame, RefreshCw } from 'lucide-react';

export const HomePage: React.FC = () => {
  const { posts, friendRequests } = useSocial();
  const [activeFeedTab, setActiveFeedTab] = useState<'all' | 'friends' | 'trending'>('all');

  const filteredPosts = posts.filter((post) => {
    if (activeFeedTab === 'friends') {
      return friendRequests.friends.includes(post.authorId) || post.authorId === 'usr_me';
    }
    if (activeFeedTab === 'trending') {
      const totalReactions = Object.values(post.reactions).reduce((a, b) => a + b, 0);
      return totalReactions >= 10;
    }
    return true;
  });

  return (
    <div className="flex flex-col gap-4">
      {/* 24h Stories Carousel */}
      <StoryRail />

      {/* Post Composer Card */}
      <PostComposer />

      {/* Feed Filters Header */}
      <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-2.5 shadow-xs">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setActiveFeedTab('all')}
            className={`flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold transition-all ${
              activeFeedTab === 'all'
                ? 'bg-sky-50 text-[#1E9EF5]'
                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
            }`}
          >
            <Sparkles className="size-3.5" />
            <span>All Posts</span>
          </button>

          <button
            onClick={() => setActiveFeedTab('friends')}
            className={`flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold transition-all ${
              activeFeedTab === 'friends'
                ? 'bg-sky-50 text-[#1E9EF5]'
                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
            }`}
          >
            <Users className="size-3.5" />
            <span>Friends Only</span>
          </button>

          <button
            onClick={() => setActiveFeedTab('trending')}
            className={`flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-bold transition-all ${
              activeFeedTab === 'trending'
                ? 'bg-sky-50 text-[#1E9EF5]'
                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
            }`}
          >
            <Flame className="size-3.5 text-amber-500" />
            <span>Trending</span>
          </button>
        </div>

        <span className="text-[11px] font-semibold text-slate-400">
          {filteredPosts.length} {filteredPosts.length === 1 ? 'post' : 'posts'}
        </span>
      </div>

      {/* Post Stream */}
      <div className="flex flex-col gap-4">
        {filteredPosts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}

        {filteredPosts.length === 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-xs">
            <p className="text-sm font-semibold text-slate-600">No posts in this feed category yet.</p>
            <p className="mt-1 text-xs text-slate-400">Be the first to share an update!</p>
          </div>
        )}
      </div>
    </div>
  );
};
