import React, { useState } from 'react';
import {
  Radio,
  Search,
  Users,
  MessageCircle,
  Bell,
  LogOut,
  X,
  FileText,
  User as UserIcon,
  Sparkles,
  Gamepad2,
  Wallet,
  Menu,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSocial } from '../context/SocialContext';

interface HeaderProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ currentTab, setCurrentTab }) => {
  const { currentUser, logout } = useAuth();
  const {
    searchQuery,
    setSearchQuery,
    isSearchOpen,
    setIsSearchOpen,
    isNotificationsOpen,
    setIsNotificationsOpen,
    notifications,
    markNotificationsRead,
    users,
    posts,
    conversations,
    startDirectMessage,
  } = useSocial();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const unreadMessagesCount = conversations.reduce((acc, c) => acc + (c.unreadCount || 0), 0);
  const unreadNotificationsCount = notifications.filter((n) => !n.read).length;

  const filteredPeople = searchQuery.trim()
    ? users.filter(
        (u) =>
          u.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          u.username.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  const filteredPosts = searchQuery.trim()
    ? posts.filter(
        (p) =>
          p.body.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.authorName.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur-md">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
          {/* Brand Logo */}
          <button
            onClick={() => setCurrentTab('home')}
            className="flex items-center gap-2.5 text-left focus:outline-hidden"
          >
            <div className="flex size-10 items-center justify-center rounded-2xl bg-[#1E9EF5] text-white shadow-sm shadow-sky-200">
              <Radio className="size-5 animate-pulse" />
            </div>
            <div className="hidden sm:block">
              <span className="text-xl font-extrabold tracking-tight text-[#0D1420]">
                TATA<span className="text-[#1E9EF5]">.</span>
              </span>
              <span className="ml-1 rounded-md bg-sky-50 px-1.5 py-0.5 text-[10px] font-bold text-[#1E9EF5]">
                2.0
              </span>
            </div>
          </button>

          {/* Global Search Bar */}
          <div className="relative hidden md:block max-w-md flex-1">
            <div className="relative">
              <Search className="absolute left-3.5 top-3 size-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setIsSearchOpen(true);
                }}
                onFocus={() => setIsSearchOpen(true)}
                placeholder="Search people, tags, and posts..."
                className="w-full rounded-full border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-9 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:bg-white focus:ring-3 focus:ring-sky-100 outline-hidden transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setIsSearchOpen(false);
                  }}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-600"
                >
                  <X className="size-4" />
                </button>
              )}
            </div>

            {/* Live Search Suggestions Dropdown */}
            {isSearchOpen && searchQuery.trim() && (
              <div className="absolute top-full left-0 mt-2 w-full rounded-2xl border border-slate-200 bg-white p-2 shadow-xl z-50">
                <div className="flex items-center justify-between border-b border-slate-100 px-3 py-2 text-xs font-bold uppercase tracking-wider text-slate-400">
                  <span>Results for "{searchQuery}"</span>
                  <button onClick={() => setIsSearchOpen(false)} className="text-slate-400 hover:text-slate-600">
                    <X className="size-3.5" />
                  </button>
                </div>

                <div className="max-h-80 overflow-y-auto">
                  {filteredPeople.length > 0 && (
                    <div className="py-2">
                      <span className="px-3 text-[11px] font-bold text-slate-400 uppercase">People</span>
                      {filteredPeople.map((user) => (
                        <div
                          key={user.id}
                          onClick={() => {
                            startDirectMessage(user.id);
                            setCurrentTab('messages');
                            setIsSearchOpen(false);
                          }}
                          className="mt-1 flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 hover:bg-sky-50"
                        >
                          <img src={user.avatarUrl} alt={user.displayName} className="size-8 rounded-full object-cover" />
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-semibold text-[#0D1420]">{user.displayName}</p>
                            <p className="truncate text-xs text-slate-400">@{user.username}</p>
                          </div>
                          <span className="text-xs font-semibold text-[#1E9EF5]">Message</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {filteredPosts.length > 0 && (
                    <div className="border-t border-slate-100 py-2">
                      <span className="px-3 text-[11px] font-bold text-slate-400 uppercase">Posts</span>
                      {filteredPosts.slice(0, 4).map((post) => (
                        <div
                          key={post.id}
                          onClick={() => {
                            setCurrentTab('home');
                            setIsSearchOpen(false);
                          }}
                          className="mt-1 flex cursor-pointer items-start gap-3 rounded-xl px-3 py-2 hover:bg-sky-50"
                        >
                          <FileText className="mt-0.5 size-4 text-[#1E9EF5] shrink-0" />
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-xs font-semibold text-[#0D1420]">
                              {post.authorName}: <span className="font-normal text-slate-600">{post.body}</span>
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {filteredPeople.length === 0 && filteredPosts.length === 0 && (
                    <p className="p-4 text-center text-xs text-slate-500">No matching people or posts found.</p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Action Icons & User Account */}
          <div className="flex items-center gap-2">
            {/* Friends Directory Link */}
            <button
              onClick={() => setCurrentTab('friends')}
              title="Friends & Directory"
              className={`relative flex size-10 items-center justify-center rounded-full transition-colors ${
                currentTab === 'friends' ? 'bg-sky-100 text-[#1E9EF5]' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
              }`}
            >
              <Users className="size-5" />
            </button>

            {/* Messages Chat Link */}
            <button
              onClick={() => setCurrentTab('messages')}
              title="Direct Messages"
              className={`relative flex size-10 items-center justify-center rounded-full transition-colors ${
                currentTab === 'messages' ? 'bg-sky-100 text-[#1E9EF5]' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
              }`}
            >
              <MessageCircle className="size-5" />
              {unreadMessagesCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 flex size-4.5 items-center justify-center rounded-full bg-[#1E9EF5] text-[10px] font-bold text-white shadow-xs">
                  {unreadMessagesCount}
                </span>
              )}
            </button>

            {/* Notifications Menu */}
            <div className="relative">
              <button
                onClick={() => {
                  setIsNotificationsOpen(!isNotificationsOpen);
                  if (!isNotificationsOpen) markNotificationsRead();
                }}
                title="Activity & Notifications"
                className={`relative flex size-10 items-center justify-center rounded-full transition-colors ${
                  isNotificationsOpen ? 'bg-sky-100 text-[#1E9EF5]' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
                }`}
              >
                <Bell className="size-5" />
                {unreadNotificationsCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 flex size-4.5 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white animate-bounce">
                    {unreadNotificationsCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              {isNotificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl border border-slate-200 bg-white p-3 shadow-2xl z-50">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                    <div className="flex items-center gap-2">
                      <Sparkles className="size-4 text-[#1E9EF5]" />
                      <h3 className="text-sm font-bold text-[#0D1420]">Recent Activity</h3>
                    </div>
                    <button
                      onClick={() => setIsNotificationsOpen(false)}
                      className="text-slate-400 hover:text-slate-600"
                    >
                      <X className="size-4" />
                    </button>
                  </div>

                  <div className="mt-2 max-h-96 divide-y divide-slate-100 overflow-y-auto">
                    {notifications.map((n) => (
                      <div key={n.id} className="flex items-start gap-3 py-3 hover:bg-slate-50 rounded-xl px-2">
                        <img src={n.actorAvatar} alt={n.actor} className="size-9 rounded-full object-cover shrink-0" />
                        <div className="min-w-0 flex-1">
                          <p className="text-xs text-[#0D1420]">
                            <strong className="font-semibold text-[#0D1420]">{n.actor}</strong> {n.text}
                          </p>
                          <span className="mt-0.5 block text-[10px] font-medium text-slate-400">{n.timeLabel}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Profile Avatar & Info Button */}
            {currentUser && (
              <button
                onClick={() => setCurrentTab('profile')}
                className="flex items-center gap-2.5 rounded-full p-1 hover:bg-slate-100 transition-colors"
              >
                <img
                  src={currentUser.avatarUrl}
                  alt={currentUser.displayName}
                  className="size-9 rounded-full object-cover ring-2 ring-[#1E9EF5]/30"
                />
                <div className="hidden lg:block text-left pr-2">
                  <p className="text-xs font-bold text-[#0D1420] leading-tight truncate max-w-[110px]">
                    {currentUser.displayName}
                  </p>
                  <p className="text-[11px] font-medium text-slate-400 leading-tight">
                    @{currentUser.username}
                  </p>
                </div>
              </button>
            )}

            {/* Log out */}
            <button
              onClick={logout}
              title="Log out"
              className="hidden sm:flex size-10 items-center justify-center rounded-full text-slate-400 hover:bg-rose-50 hover:text-rose-500 transition-colors"
            >
              <LogOut className="size-4.5" />
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Bottom Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around border-t border-slate-200 bg-white/95 px-2 py-2 backdrop-blur-md md:hidden shadow-lg">
        <button
          onClick={() => setCurrentTab('home')}
          className={`flex flex-col items-center gap-1 text-[10px] font-semibold ${
            currentTab === 'home' ? 'text-[#1E9EF5]' : 'text-slate-500'
          }`}
        >
          <Radio className="size-5" />
          <span>Home</span>
        </button>

        <button
          onClick={() => setCurrentTab('friends')}
          className={`flex flex-col items-center gap-1 text-[10px] font-semibold ${
            currentTab === 'friends' ? 'text-[#1E9EF5]' : 'text-slate-500'
          }`}
        >
          <Users className="size-5" />
          <span>People</span>
        </button>

        <button
          onClick={() => setCurrentTab('messages')}
          className={`relative flex flex-col items-center gap-1 text-[10px] font-semibold ${
            currentTab === 'messages' ? 'text-[#1E9EF5]' : 'text-slate-500'
          }`}
        >
          <MessageCircle className="size-5" />
          {unreadMessagesCount > 0 && (
            <span className="absolute -top-1 right-2 flex size-4 items-center justify-center rounded-full bg-[#1E9EF5] text-[9px] font-bold text-white">
              {unreadMessagesCount}
            </span>
          )}
          <span>Chats</span>
        </button>

        <button
          onClick={() => setCurrentTab('games')}
          className={`flex flex-col items-center gap-1 text-[10px] font-semibold ${
            currentTab === 'games' ? 'text-[#1E9EF5]' : 'text-slate-500'
          }`}
        >
          <Gamepad2 className="size-5" />
          <span>Games</span>
        </button>

        <button
          onClick={() => setCurrentTab('wallet')}
          className={`flex flex-col items-center gap-1 text-[10px] font-semibold ${
            currentTab === 'wallet' ? 'text-[#1E9EF5]' : 'text-slate-500'
          }`}
        >
          <Wallet className="size-5" />
          <span>Coins</span>
        </button>

        <button
          onClick={() => setCurrentTab('profile')}
          className={`flex flex-col items-center gap-1 text-[10px] font-semibold ${
            currentTab === 'profile' ? 'text-[#1E9EF5]' : 'text-slate-500'
          }`}
        >
          <UserIcon className="size-5" />
          <span>Profile</span>
        </button>
      </nav>
    </>
  );
};
