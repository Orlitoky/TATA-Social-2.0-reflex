import React, { useState } from 'react';
import {
  Users,
  UserPlus,
  UserCheck,
  Search,
  MessageCircle,
  X,
  Check,
  Sparkles,
  MapPin,
  Globe,
  UserMinus,
} from 'lucide-react';
import { useSocial } from '../context/SocialContext';
import { useAuth } from '../context/AuthContext';
import { User } from '../types';

interface FriendsPageProps {
  setCurrentTab: (tab: string) => void;
}

export const FriendsPage: React.FC<FriendsPageProps> = ({ setCurrentTab }) => {
  const {
    users,
    friendRequests,
    sendFriendRequest,
    acceptFriendRequest,
    declineFriendRequest,
    removeFriend,
    toggleFollow,
    startDirectMessage,
  } = useSocial();
  const { currentUser } = useAuth();

  const [activeTab, setActiveTab] = useState<'friends' | 'requests' | 'sent' | 'suggestions'>('friends');
  const [filterQuery, setFilterQuery] = useState('');

  const otherUsers = users.filter((u) => u.id !== currentUser?.id);

  const friendsList = otherUsers.filter((u) => friendRequests.friends.includes(u.id));
  const incomingList = otherUsers.filter((u) => friendRequests.incoming.includes(u.id));
  const outgoingList = otherUsers.filter((u) => friendRequests.outgoing.includes(u.id));
  const suggestionsList = otherUsers.filter(
    (u) =>
      !friendRequests.friends.includes(u.id) &&
      !friendRequests.incoming.includes(u.id) &&
      !friendRequests.outgoing.includes(u.id)
  );

  const getDisplayedList = () => {
    let list: User[] = [];
    if (activeTab === 'friends') list = friendsList;
    if (activeTab === 'requests') list = incomingList;
    if (activeTab === 'sent') list = outgoingList;
    if (activeTab === 'suggestions') list = suggestionsList;

    if (!filterQuery.trim()) return list;
    return list.filter(
      (u) =>
        u.displayName.toLowerCase().includes(filterQuery.toLowerCase()) ||
        u.username.toLowerCase().includes(filterQuery.toLowerCase()) ||
        (u.location && u.location.toLowerCase().includes(filterQuery.toLowerCase()))
    );
  };

  const displayedList = getDisplayedList();

  return (
    <div className="flex flex-col gap-4">
      {/* Top Banner Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Friends</span>
          <p className="mt-1 text-2xl font-black text-[#0D1420]">{friendsList.length}</p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Requests</span>
          <div className="mt-1 flex items-center gap-2">
            <p className="text-2xl font-black text-[#1E9EF5]">{incomingList.length}</p>
            {incomingList.length > 0 && (
              <span className="rounded-full bg-sky-100 px-2 py-0.5 text-[10px] font-bold text-[#1E9EF5]">
                New
              </span>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Sent</span>
          <p className="mt-1 text-2xl font-black text-[#0D1420]">{outgoingList.length}</p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Following</span>
          <p className="mt-1 text-2xl font-black text-[#0D1420]">{friendRequests.following.length}</p>
        </div>
      </div>

      {/* Directory Controls & Search */}
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          {/* Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              onClick={() => setActiveTab('friends')}
              className={`rounded-xl px-3.5 py-2 text-xs font-bold transition-all ${
                activeTab === 'friends'
                  ? 'bg-sky-50 text-[#1E9EF5]'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              All Friends ({friendsList.length})
            </button>

            <button
              onClick={() => setActiveTab('requests')}
              className={`relative rounded-xl px-3.5 py-2 text-xs font-bold transition-all ${
                activeTab === 'requests'
                  ? 'bg-sky-50 text-[#1E9EF5]'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              Requests ({incomingList.length})
              {incomingList.length > 0 && (
                <span className="ml-1.5 rounded-full bg-rose-500 px-1.5 py-0.2 text-[9px] text-white">
                  {incomingList.length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('sent')}
              className={`rounded-xl px-3.5 py-2 text-xs font-bold transition-all ${
                activeTab === 'sent'
                  ? 'bg-sky-50 text-[#1E9EF5]'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              Sent ({outgoingList.length})
            </button>

            <button
              onClick={() => setActiveTab('suggestions')}
              className={`rounded-xl px-3.5 py-2 text-xs font-bold transition-all ${
                activeTab === 'suggestions'
                  ? 'bg-sky-50 text-[#1E9EF5]'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              Discover & Suggestions
            </button>
          </div>

          {/* Search Box */}
          <div className="relative min-w-[200px]">
            <Search className="absolute left-3 top-2.5 size-4 text-slate-400" />
            <input
              type="text"
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              placeholder="Filter people..."
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-1.5 pl-9 pr-3 text-xs font-medium text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:bg-white focus:outline-hidden"
            />
          </div>
        </div>
      </div>

      {/* Directory Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {displayedList.map((user) => {
          const isFriend = friendRequests.friends.includes(user.id);
          const isIncoming = friendRequests.incoming.includes(user.id);
          const isOutgoing = friendRequests.outgoing.includes(user.id);
          const isFollowing = friendRequests.following.includes(user.id);

          return (
            <div
              key={user.id}
              className="flex flex-col justify-between overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-xs transition-all hover:border-slate-300"
            >
              {/* User Header */}
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <img
                        src={user.avatarUrl}
                        alt={user.displayName}
                        className="size-12 rounded-full object-cover ring-2 ring-slate-100"
                      />
                      {user.isOnline && (
                        <span className="absolute bottom-0 right-0 size-3 rounded-full border-2 border-white bg-emerald-500" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-[#0D1420]">{user.displayName}</h3>
                      <p className="text-xs text-slate-400">@{user.username}</p>
                    </div>
                  </div>

                  {/* Follow Button */}
                  <button
                    onClick={() => toggleFollow(user.id)}
                    className={`rounded-full px-3 py-1 text-xs font-bold transition-colors ${
                      isFollowing
                        ? 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                        : 'bg-sky-50 text-[#1E9EF5] hover:bg-sky-100'
                    }`}
                  >
                    {isFollowing ? 'Following' : '+ Follow'}
                  </button>
                </div>

                {/* Bio & Details */}
                {user.bio && (
                  <p className="mt-3 text-xs leading-relaxed text-slate-600 line-clamp-2">{user.bio}</p>
                )}

                <div className="mt-3 flex flex-wrap items-center gap-3 text-[11px] text-slate-400">
                  {user.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="size-3 text-rose-500" />
                      <span>{user.location}</span>
                    </span>
                  )}
                  <span>•</span>
                  <span>{user.friendCount} mutual friends</span>
                </div>
              </div>

              {/* Action Buttons Row */}
              <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                {isFriend && (
                  <>
                    <button
                      onClick={() => {
                        startDirectMessage(user.id);
                        setCurrentTab('messages');
                      }}
                      className="flex items-center gap-1.5 rounded-xl bg-sky-50 px-3.5 py-1.5 text-xs font-bold text-[#1E9EF5] hover:bg-[#1E9EF5] hover:text-white transition-all"
                    >
                      <MessageCircle className="size-3.5" />
                      <span>Direct Message</span>
                    </button>
                    <button
                      onClick={() => removeFriend(user.id)}
                      className="flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-rose-500"
                    >
                      <UserMinus className="size-3.5" />
                      <span>Unfriend</span>
                    </button>
                  </>
                )}

                {isIncoming && (
                  <div className="flex w-full items-center gap-2">
                    <button
                      onClick={() => acceptFriendRequest(user.id)}
                      className="flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-[#1E9EF5] py-2 text-xs font-bold text-white hover:bg-sky-600 shadow-xs"
                    >
                      <Check className="size-3.5" />
                      <span>Accept Request</span>
                    </button>
                    <button
                      onClick={() => declineFriendRequest(user.id)}
                      className="flex items-center justify-center rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold text-slate-500 hover:bg-slate-50"
                    >
                      <X className="size-3.5" />
                    </button>
                  </div>
                )}

                {isOutgoing && (
                  <div className="flex w-full items-center justify-between">
                    <span className="text-xs font-semibold text-slate-400 italic">Request Pending...</span>
                    <button
                      onClick={() => declineFriendRequest(user.id)}
                      className="text-xs font-bold text-slate-500 hover:text-rose-500"
                    >
                      Cancel Request
                    </button>
                  </div>
                )}

                {!isFriend && !isIncoming && !isOutgoing && (
                  <button
                    onClick={() => sendFriendRequest(user.id)}
                    className="flex w-full items-center justify-center gap-1.5 rounded-xl bg-[#1E9EF5] py-2 text-xs font-bold text-white hover:bg-sky-600 shadow-xs transition-all"
                  >
                    <UserPlus className="size-3.5" />
                    <span>Send Friend Request</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}

        {displayedList.length === 0 && (
          <div className="col-span-full rounded-2xl border border-slate-200 bg-white p-12 text-center shadow-xs">
            <Users className="mx-auto size-8 text-slate-300" />
            <p className="mt-2 text-sm font-bold text-slate-700">No people in this list</p>
            <p className="mt-1 text-xs text-slate-400">Try switching tabs or searching with different keywords.</p>
          </div>
        )}
      </div>
    </div>
  );
};
