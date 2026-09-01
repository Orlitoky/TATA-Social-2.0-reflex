import React, { useState } from 'react';
import { useGames } from '../../context/GamesContext';
import { useSocial } from '../../context/SocialContext';
import { X, Copy, Check, Send, Users, Sparkles } from 'lucide-react';

interface InviteFriendsModalProps {
  onClose: () => void;
}

export const InviteFriendsModal: React.FC<InviteFriendsModalProps> = ({ onClose }) => {
  const { currentRoom } = useGames();
  const { users } = useSocial();
  const [copied, setCopied] = useState(false);
  const [invitedIds, setInvitedIds] = useState<string[]>([]);

  if (!currentRoom) return null;

  const roomUrl = `${window.location.origin}/?join=${currentRoom.code}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(currentRoom.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleInvite = (userId: string) => {
    setInvitedIds((prev) => [...prev, userId]);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs">
      <div className="w-full max-w-md rounded-3xl bg-white p-5 sm:p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="flex size-8 items-center justify-center rounded-xl bg-sky-100 text-[#1E9EF5]">
              <Users className="size-4.5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#0D1420]">Invite Friends to Play</h3>
              <p className="text-xs text-slate-400">Share your room code or invite platform buddies</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex size-8 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100"
          >
            <X className="size-4" />
          </button>
        </div>

        {/* Room Code Card */}
        <div className="mt-4 rounded-2xl bg-gradient-to-r from-sky-50 via-cyan-50 to-white p-4 border border-sky-100">
          <span className="text-[11px] font-bold text-[#1E9EF5] uppercase tracking-wider">Room Code</span>
          <div className="mt-1 flex items-center justify-between">
            <span className="text-2xl font-black tracking-widest text-[#0D1420] font-mono">
              {currentRoom.code}
            </span>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1E9EF5] text-white text-xs font-bold hover:bg-sky-600 transition-all shadow-xs"
            >
              {copied ? <Check className="size-3.5 text-white" /> : <Copy className="size-3.5" />}
              <span>{copied ? 'Copied Code' : 'Copy Code'}</span>
            </button>
          </div>
        </div>

        {/* Friend List */}
        <div className="mt-4">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">
            Online Friends ({users.length})
          </span>
          <div className="max-h-60 overflow-y-auto space-y-2 divide-y divide-slate-50">
            {users.map((friend) => {
              const isInvited = invitedIds.includes(friend.id);
              const isInRoom = currentRoom.players.some((p) => p.id === friend.id);

              return (
                <div key={friend.id} className="flex items-center justify-between pt-2">
                  <div className="flex items-center gap-2.5">
                    <img
                      src={friend.avatarUrl}
                      alt={friend.displayName}
                      className="size-9 rounded-full object-cover ring-2 ring-slate-100"
                    />
                    <div>
                      <p className="text-xs font-bold text-[#0D1420]">{friend.displayName}</p>
                      <p className="text-[10px] text-slate-400">@{friend.username}</p>
                    </div>
                  </div>

                  {isInRoom ? (
                    <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-lg">
                      In Room
                    </span>
                  ) : isInvited ? (
                    <span className="text-xs font-semibold text-slate-400 bg-slate-100 px-2.5 py-1 rounded-lg">
                      Sent ✓
                    </span>
                  ) : (
                    <button
                      onClick={() => handleInvite(friend.id)}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-[#1E9EF5] hover:text-white text-[#0D1420] text-xs font-bold transition-colors"
                    >
                      <Send className="size-3" />
                      <span>Invite</span>
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="mt-5 pt-3 border-t border-slate-100 text-center">
          <button
            onClick={onClose}
            className="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
