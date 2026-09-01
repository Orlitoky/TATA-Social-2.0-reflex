import React, { useState } from 'react';
import {
  Calendar,
  MapPin,
  Globe,
  Edit3,
  Coins,
  Sparkles,
  Camera,
  Share2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSocial } from '../context/SocialContext';
import { PostCard } from '../components/PostCard';
import { EditProfileModal } from '../components/EditProfileModal';
import { PostComposer } from '../components/PostComposer';

export const ProfilePage: React.FC = () => {
  const { currentUser } = useAuth();
  const { posts, friendRequests } = useSocial();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'posts' | 'media' | 'about'>('posts');

  if (!currentUser) return null;

  const myPosts = posts.filter((p) => p.authorId === currentUser.id);
  const myMediaPosts = myPosts.filter((p) => p.media && p.media.length > 0);

  return (
    <div className="flex flex-col gap-4">
      {/* Profile Header Hero Card */}
      <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xs">
        {/* Cover Photo */}
        <div className="relative h-44 sm:h-56 w-full overflow-hidden bg-gradient-to-r from-sky-400 via-indigo-500 to-purple-600">
          {currentUser.coverUrl && (
            <img
              src={currentUser.coverUrl}
              alt="Profile Cover"
              className="size-full object-cover"
            />
          )}
          <button
            onClick={() => setIsEditModalOpen(true)}
            className="absolute bottom-3 right-3 flex items-center gap-1.5 rounded-xl bg-black/60 px-3 py-1.5 text-xs font-bold text-white backdrop-blur-xs hover:bg-black/80 transition-colors"
          >
            <Camera className="size-3.5" />
            <span>Change Cover</span>
          </button>
        </div>

        {/* Profile Info Row */}
        <div className="relative px-5 pb-5 pt-0 sm:px-8">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
            {/* Avatar */}
            <div className="-mt-16 sm:-mt-20 relative inline-block">
              <img
                src={currentUser.avatarUrl}
                alt={currentUser.displayName}
                className="size-28 sm:size-32 rounded-full border-4 border-white object-cover shadow-md"
              />
              <button
                onClick={() => setIsEditModalOpen(true)}
                className="absolute bottom-1 right-1 flex size-8 items-center justify-center rounded-full border-2 border-white bg-[#1E9EF5] text-white shadow-xs hover:bg-sky-600"
              >
                <Camera className="size-4" />
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2.5">
              <button
                onClick={() => setIsEditModalOpen(true)}
                className="flex items-center gap-1.5 rounded-xl border border-slate-200 px-4 py-2 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors"
              >
                <Edit3 className="size-3.5" />
                <span>Edit Profile</span>
              </button>
              <button
                onClick={() => {
                  navigator.clipboard?.writeText(window.location.href);
                  alert('Profile URL copied to clipboard!');
                }}
                className="flex items-center gap-1.5 rounded-xl bg-sky-50 px-3.5 py-2 text-xs font-bold text-[#1E9EF5] hover:bg-sky-100 transition-colors"
              >
                <Share2 className="size-3.5" />
                <span>Share</span>
              </button>
            </div>
          </div>

          {/* User Names & Bio */}
          <div className="mt-3">
            <h1 className="text-xl sm:text-2xl font-black text-[#0D1420]">
              {currentUser.displayName}
            </h1>
            <p className="text-xs sm:text-sm font-medium text-slate-400">
              @{currentUser.username}
            </p>

            {currentUser.bio && (
              <p className="mt-2.5 max-w-2xl text-xs sm:text-sm leading-relaxed text-slate-700">
                {currentUser.bio}
              </p>
            )}

            {/* Metadata Badges */}
            <div className="mt-3.5 flex flex-wrap items-center gap-4 text-xs font-medium text-slate-500">
              {currentUser.location && (
                <div className="flex items-center gap-1 text-rose-500 font-semibold">
                  <MapPin className="size-3.5" />
                  <span>{currentUser.location}</span>
                </div>
              )}
              {currentUser.website && (
                <a
                  href={currentUser.website}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-[#1E9EF5] hover:underline"
                >
                  <Globe className="size-3.5" />
                  <span>{currentUser.website.replace('https://', '')}</span>
                </a>
              )}
              <div className="flex items-center gap-1 text-slate-400">
                <Calendar className="size-3.5" />
                <span>Joined {currentUser.joinedDate}</span>
              </div>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-2 border-t border-slate-100 pt-4 text-center">
            <div className="p-2">
              <span className="block text-lg font-black text-[#0D1420]">{myPosts.length}</span>
              <span className="text-[11px] font-bold text-slate-400 uppercase">Posts</span>
            </div>
            <div className="p-2">
              <span className="block text-lg font-black text-[#0D1420]">
                {friendRequests.friends.length}
              </span>
              <span className="text-[11px] font-bold text-slate-400 uppercase">Friends</span>
            </div>
            <div className="p-2">
              <span className="block text-lg font-black text-[#0D1420]">
                {currentUser.followerCount}
              </span>
              <span className="text-[11px] font-bold text-slate-400 uppercase">Followers</span>
            </div>
            <div className="p-2">
              <span className="flex items-center justify-center gap-1 text-lg font-black text-[#1E9EF5]">
                <Coins className="size-4" />
                {currentUser.coinBalance.toLocaleString()}
              </span>
              <span className="text-[11px] font-bold text-slate-400 uppercase">TATA Coins</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-xs">
        <button
          onClick={() => setActiveTab('posts')}
          className={`rounded-xl px-4 py-2 text-xs font-bold transition-all ${
            activeTab === 'posts' ? 'bg-sky-50 text-[#1E9EF5]' : 'text-slate-600 hover:bg-slate-50'
          }`}
        >
          Timeline Posts ({myPosts.length})
        </button>
        <button
          onClick={() => setActiveTab('media')}
          className={`rounded-xl px-4 py-2 text-xs font-bold transition-all ${
            activeTab === 'media' ? 'bg-sky-50 text-[#1E9EF5]' : 'text-slate-600 hover:bg-slate-50'
          }`}
        >
          Photos & Media ({myMediaPosts.length})
        </button>
      </div>

      {/* Timeline Stream */}
      {activeTab === 'posts' && (
        <div className="flex flex-col gap-4">
          <PostComposer />

          {myPosts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}

          {myPosts.length === 0 && (
            <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-xs">
              <Sparkles className="mx-auto size-7 text-[#1E9EF5]" />
              <p className="mt-2 text-sm font-bold text-slate-700">No posts shared yet</p>
              <p className="mt-1 text-xs text-slate-400">Share your first update above to earn 10 TATA coins!</p>
            </div>
          )}
        </div>
      )}

      {/* Photos Grid */}
      {activeTab === 'media' && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {myMediaPosts.flatMap((p) => p.media).map((media, idx) => (
            <div key={idx} className="relative aspect-square overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 shadow-xs">
              <img src={media.url} alt="User media upload" className="size-full object-cover hover:scale-105 transition-transform" />
            </div>
          ))}

          {myMediaPosts.length === 0 && (
            <div className="col-span-full rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-xs">
              <p className="text-sm font-bold text-slate-600">No photo posts yet</p>
            </div>
          )}
        </div>
      )}

      {/* Edit Profile Modal */}
      {isEditModalOpen && <EditProfileModal onClose={() => setIsEditModalOpen(false)} />}
    </div>
  );
};
