import React, { useState } from 'react';
import { GameChatMsg, GamePlayer } from '../types';
import { Send, Smile, Sparkles, MessageCircle, X } from 'lucide-react';
import { sounds } from '../audio';

interface InGameChatProps {
  messages: GameChatMsg[];
  currentPlayer: GamePlayer;
  onSendMessage: (text: string) => void;
  onClose?: () => void;
}

const QUICK_REACTIONS = [
  'Good move! 👏',
  'GG! 🏆',
  'Watch this! 🔥',
  'Nice roll! 🎲',
  'Bingo! 🎉',
  'Domino! 🀄',
  'Unlucky! 😅',
  'Rematch next? ⚔️',
];

export const InGameChat: React.FC<InGameChatProps> = ({
  messages,
  currentPlayer,
  onSendMessage,
  onClose,
}) => {
  const [inputText, setInputText] = useState('');

  const handleSend = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim()) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const handleQuickReaction = (text: string) => {
    onSendMessage(text);
  };

  return (
    <div className="flex flex-col h-full max-h-[420px] rounded-2xl border border-slate-200 bg-white shadow-lg overflow-hidden">
      {/* Chat Header */}
      <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/80 px-3.5 py-2.5">
        <div className="flex items-center gap-2">
          <MessageCircle className="size-4 text-[#1E9EF5]" />
          <span className="text-xs font-bold text-[#0D1420]">Match Chat & Taunts</span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 rounded-lg p-1 hover:bg-slate-200/50"
          >
            <X className="size-4" />
          </button>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5 text-xs bg-slate-50/30">
        {messages.map((m) => {
          if (m.isSystem) {
            return (
              <div
                key={m.id}
                className="rounded-xl bg-sky-50/80 border border-sky-100/60 p-2 text-center text-[11px] font-semibold text-sky-700"
              >
                {m.text}
              </div>
            );
          }

          const isMe = m.senderId === currentPlayer.id;

          return (
            <div
              key={m.id}
              className={`flex items-start gap-2 ${isMe ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <img
                src={m.senderAvatar}
                alt={m.senderName}
                className="size-6 rounded-full object-cover ring-1 ring-slate-200 shrink-0 mt-0.5"
              />
              <div
                className={`max-w-[80%] rounded-2xl px-3 py-1.5 shadow-2xs ${
                  isMe
                    ? 'bg-[#1E9EF5] text-white rounded-tr-xs'
                    : 'bg-white border border-slate-200 text-[#0D1420] rounded-tl-xs'
                }`}
              >
                {!isMe && (
                  <p className="text-[10px] font-bold text-slate-400 mb-0.5">{m.senderName}</p>
                )}
                <p className="text-xs font-medium leading-relaxed break-words">{m.text}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Reaction Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto p-2 border-t border-slate-100 bg-white scrollbar-none">
        {QUICK_REACTIONS.map((reaction, idx) => (
          <button
            key={idx}
            onClick={() => handleQuickReaction(reaction)}
            className="shrink-0 rounded-full border border-slate-200 bg-slate-50 hover:bg-sky-50 hover:border-sky-200 hover:text-[#1E9EF5] px-2.5 py-1 text-[11px] font-semibold text-slate-700 transition-colors"
          >
            {reaction}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-slate-100 p-2 bg-white">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Send a message..."
          className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-[#0D1420] placeholder:text-slate-400 focus:bg-white focus:border-[#1E9EF5] outline-hidden"
        />
        <button
          type="submit"
          className="flex size-8 items-center justify-center rounded-xl bg-[#1E9EF5] text-white hover:bg-sky-600 transition-colors shrink-0 shadow-xs"
        >
          <Send className="size-3.5" />
        </button>
      </form>
    </div>
  );
};
