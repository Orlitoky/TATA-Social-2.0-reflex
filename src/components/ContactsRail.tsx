import React from 'react';
import { Users, UserPlus, MessageCircle, Gamepad2, Sparkles } from 'lucide-react';
import { useSocial } from '../context/SocialContext';
import { useAuth } from '../context/AuthContext';

interface ContactsRailProps {
  setCurrentTab: (tab: string) => void;
}

export const ContactsRail: React.FC<ContactsRailProps> = ({ setCurrentTab }) => {
  const { users, startDirectMessage, friendRequests, sendFriendRequest, acceptFriendRequest } = useSocial();
  const { currentUser } = useAuth();

  const otherUsers = users.filter((u) => u.id !== currentUser?.id);
  const onlineUsers = otherUsers.filter((u) => u.isOnline);
  const suggestedUsers = otherUsers.filter(
    (u) =>
      !friendRequests.friends.includes(u.id) &&
      !friendRequests.outgoing.includes(u.id) &&
      !friendRequests.incoming.includes(u.id)
  );

  return (
    <aside className="hidden xl:flex w-72 shrink-0 flex-col gap-4">
      {/* Online Contacts */}
      <div className="rounded-2xl border border-slate-200 bg-white p-3.5 shadow-xs">
        <div className="flex items-center justify-between px-1 pb-2">
          <div className="flex items-center gap-2">
            <Users className="size-4 text-[#1E9EF5]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#0D1420]">
              Contacts ({onlineUsers.length})
            </h3>
          </div>
          <span className="flex size-2 rounded-full bg-emerald-500 animate-pulse" />
        </div>

        <div className="mt-1 flex flex-col gap-1">
          {onlineUsers.map((user) => (
            <div
              key={user.id}
              onClick={() => {
                startDirectMessage(user.id);
                setCurrentTab('messages');
              }}
              className="flex cursor-pointer items-center justify-between rounded-xl px-2 py-2 hover:bg-sky-50 transition-colors"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="relative shrink-0">
                  <img src={user.avatarUrl} alt={user.displayName} className="size-9 rounded-full object-cover" />
                  <span className="absolute bottom-0 right-0 size-2.5 rounded-full border-2 border-white bg-emerald-500" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-bold text-[#0D1420]">{user.displayName}</p>
                  <p className="truncate text-[10px] text-slate-400">@{user.username}</p>
                </div>
              </div>
              <button
                title="Send Message"
                className="flex size-7 items-center justify-center rounded-full text-slate-400 hover:bg-white hover:text-[#1E9EF5] hover:shadow-xs transition-all"
              >
                <MessageCircle className="size-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Suggested People / Who to Follow */}
      <div className="rounded-2xl border border-slate-200 bg-white p-3.5 shadow-xs">
        <div className="flex items-center justify-between px-1 pb-2">
          <div className="flex items-center gap-2">
            <UserPlus className="size-4 text-[#1E9EF5]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#0D1420]">Suggested for you</h3>
          </div>
          <button
            onClick={() => setCurrentTab('friends')}
            className="text-[11px] font-semibold text-[#1E9EF5] hover:underline"
          >
            See all
          </button>
        </div>

        <div className="mt-1 flex flex-col gap-2.5">
          {suggestedUsers.slice(0, 3).map((user) => (
            <div key={user.id} className="flex items-center justify-between gap-2 rounded-xl p-1">
              <div className="flex items-center gap-2.5 min-w-0">
                <img src={user.avatarUrl} alt={user.displayName} className="size-9 rounded-full object-cover shrink-0" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-bold text-[#0D1420]">{user.displayName}</p>
                  <p className="truncate text-[10px] text-slate-400">{user.location || `@${user.username}`}</p>
                </div>
              </div>
              <button
                onClick={() => sendFriendRequest(user.id)}
                className="flex shrink-0 items-center gap-1 rounded-full bg-sky-50 px-2.5 py-1 text-xs font-bold text-[#1E9EF5] hover:bg-[#1E9EF5] hover:text-white transition-all shadow-xs"
              >
                <UserPlus className="size-3" />
                <span>Add</span>
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Mini-Games Spotlight Widget */}
      <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-indigo-900 to-slate-900 p-4 text-white shadow-xs">
        <div className="flex items-center gap-2 text-sky-400">
          <Gamepad2 className="size-4.5" />
          <span className="text-xs font-bold uppercase tracking-wider">TATA Arcade</span>
        </div>
        <p className="mt-1.5 text-xs font-medium text-slate-200 leading-relaxed">
          Challenge friends to Speed Chess or Trivia Blitz to win virtual coin jackpots!
        </p>
        <button
          onClick={() => setCurrentTab('games')}
          className="mt-3 flex w-full items-center justify-center gap-1.5 rounded-xl bg-[#1E9EF5] py-2 text-xs font-bold text-white hover:bg-sky-400 transition-colors shadow-xs"
        >
          <Sparkles className="size-3.5" />
          <span>Enter Game Lobby</span>
        </button>
      </div>
    </aside>
  );
};
