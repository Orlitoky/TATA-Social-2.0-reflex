import React, { useState } from 'react';
import { useGames } from '../../context/GamesContext';
import { Send, MessageSquare, Smile, Sparkles } from 'lucide-react';

const QUICK_EMOJIS = ['👏', '🔥', '🎲', '👑', '😱', '💥', '🏆', '🎯'];

export const GameChatTray: React.FC = () => {
  const { currentRoom, sendChatMessage, activeDemoUser } = useGames();
  const [text, setText] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);

  if (!currentRoom) return null;

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    sendChatMessage(text.trim());
    setText('');
  };

  const handleEmojiClick = (emoji: string) => {
    sendChatMessage(emoji);
    setShowEmojiPicker(false);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <MessageSquare className="size-4 text-[#1E9EF5]" />
          <span className="text-xs font-bold text-[#0D1420]">Room Chat & Reactions</span>
        </div>
        <span className="text-[10px] font-bold text-slate-400">
          {currentRoom.chatMessages.length} messages
        </span>
      </div>

      {/* Messages list */}
      <div className="flex-1 p-3 overflow-y-auto space-y-2.5 max-h-56 min-h-[140px]">
        {currentRoom.chatMessages.length === 0 ? (
          <p className="text-center text-xs text-slate-400 py-4">No messages yet. Say hello!</p>
        ) : (
          currentRoom.chatMessages.map((msg) => {
            const isMe = msg.senderId === activeDemoUser.id;
            return (
              <div
                key={msg.id}
                className={`flex gap-2 items-start text-xs ${isMe ? 'flex-row-reverse' : ''}`}
              >
                {!msg.isSystem && (
                  <img
                    src={msg.senderAvatar}
                    alt={msg.senderName}
                    className="size-6 rounded-full object-cover shrink-0 mt-0.5"
                  />
                )}
                <div
                  className={`rounded-xl px-2.5 py-1.5 max-w-[80%] ${
                    msg.isSystem
                      ? 'bg-amber-50 text-amber-800 border border-amber-200/60 w-full text-center text-[11px] font-medium'
                      : isMe
                      ? 'bg-[#1E9EF5] text-white'
                      : 'bg-slate-100 text-[#0D1420]'
                  }`}
                >
                  {!msg.isSystem && (
                    <div className="flex items-center justify-between gap-2 mb-0.5">
                      <span className={`font-bold text-[10px] ${isMe ? 'text-sky-100' : 'text-slate-500'}`}>
                        {msg.senderName}
                      </span>
                      <span className={`text-[9px] ${isMe ? 'text-sky-200' : 'text-slate-400'}`}>
                        {msg.timestamp}
                      </span>
                    </div>
                  )}
                  <p className="font-medium break-words">{msg.text}</p>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Quick Emojis */}
      <div className="flex items-center justify-around px-2 py-1 bg-slate-50 border-t border-slate-100">
        {QUICK_EMOJIS.map((emoji) => (
          <button
            key={emoji}
            onClick={() => handleEmojiClick(emoji)}
            className="hover:scale-125 active:scale-95 transition-transform text-sm p-1"
          >
            {emoji}
          </button>
        ))}
      </div>

      {/* Input bar */}
      <form onSubmit={handleSend} className="flex items-center gap-1.5 p-2 bg-white border-t border-slate-200">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Send a quick chat..."
          className="flex-1 rounded-xl bg-slate-50 border border-slate-200 px-3 py-1.5 text-xs text-[#0D1420] placeholder:text-slate-400 focus:outline-hidden focus:border-[#1E9EF5] focus:bg-white"
        />
        <button
          type="submit"
          disabled={!text.trim()}
          className="flex items-center justify-center size-8 rounded-xl bg-[#1E9EF5] text-white disabled:opacity-40 hover:bg-sky-600 transition-colors shrink-0"
        >
          <Send className="size-3.5" />
        </button>
      </form>
    </div>
  );
};
