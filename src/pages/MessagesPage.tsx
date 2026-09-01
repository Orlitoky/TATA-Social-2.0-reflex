import React, { useState, useRef, useEffect } from 'react';
import {
  Search,
  Send,
  Image,
  Check,
  CheckCheck,
  Phone,
  Video,
  Info,
  MoreVertical,
  X,
  Sparkles,
} from 'lucide-react';
import { useSocial } from '../context/SocialContext';
import { useAuth } from '../context/AuthContext';

const SAMPLE_ATTACHMENTS = [
  'https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=600&auto=format&fit=crop&q=80',
];

export const MessagesPage: React.FC = () => {
  const { conversations, activeConversationId, setActiveConversationId, sendMessage } = useSocial();
  const { currentUser } = useAuth();

  const [messageInput, setMessageInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAttachmentPicker, setShowAttachmentPicker] = useState(false);
  const [selectedAttachment, setSelectedAttachment] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeConversation =
    conversations.find((c) => c.id === activeConversationId) || conversations[0] || null;

  useEffect(() => {
    if (!activeConversationId && conversations.length > 0) {
      setActiveConversationId(conversations[0].id);
    }
  }, [conversations, activeConversationId, setActiveConversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConversation?.messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeConversation || (!messageInput.trim() && !selectedAttachment)) return;

    sendMessage(activeConversation.id, messageInput, selectedAttachment || undefined);
    setMessageInput('');
    setSelectedAttachment(null);
    setShowAttachmentPicker(false);
  };

  const filteredConversations = conversations.filter((c) =>
    c.participant.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.participant.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex h-[calc(100vh-140px)] min-h-[550px] w-full overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xs">
      {/* Left Sidebar: Conversations List */}
      <div className="flex w-full sm:w-80 md:w-96 flex-col border-r border-slate-200 bg-slate-50/50">
        {/* Search Bar */}
        <div className="p-3.5 border-b border-slate-200">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 size-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full rounded-xl border border-slate-200 bg-white py-2 pl-9 pr-3 text-xs font-medium text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:ring-1 focus:ring-sky-100 outline-hidden"
            />
          </div>
        </div>

        {/* Conversations Scrollable List */}
        <div className="flex-1 overflow-y-auto divide-y divide-slate-100 p-1.5">
          {filteredConversations.map((conv) => {
            const isSelected = activeConversation?.id === conv.id;
            return (
              <div
                key={conv.id}
                onClick={() => setActiveConversationId(conv.id)}
                className={`flex cursor-pointer items-center gap-3 rounded-2xl p-3 transition-all ${
                  isSelected ? 'bg-white shadow-xs ring-1 ring-slate-200' : 'hover:bg-slate-100/70'
                }`}
              >
                <div className="relative shrink-0">
                  <img
                    src={conv.participant.avatarUrl}
                    alt={conv.participant.displayName}
                    className="size-11 rounded-full object-cover ring-1 ring-slate-200"
                  />
                  {conv.participant.isOnline && (
                    <span className="absolute bottom-0 right-0 size-3 rounded-full border-2 border-white bg-emerald-500" />
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <p className="truncate text-xs font-bold text-[#0D1420]">
                      {conv.participant.displayName}
                    </p>
                    <span className="text-[10px] text-slate-400 shrink-0">{conv.lastMessageAt}</span>
                  </div>
                  <p className="mt-0.5 truncate text-xs font-normal text-slate-500">
                    {conv.lastMessage || 'No messages yet'}
                  </p>
                </div>

                {conv.unreadCount > 0 && (
                  <span className="flex size-4.5 items-center justify-center rounded-full bg-[#1E9EF5] text-[10px] font-bold text-white">
                    {conv.unreadCount}
                  </span>
                )}
              </div>
            );
          })}

          {filteredConversations.length === 0 && (
            <p className="p-6 text-center text-xs text-slate-400">No conversations found.</p>
          )}
        </div>
      </div>

      {/* Right Pane: Active Chat Room */}
      {activeConversation ? (
        <div className="hidden sm:flex flex-1 flex-col bg-white">
          {/* Chat Header */}
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3.5">
            <div className="flex items-center gap-3">
              <div className="relative">
                <img
                  src={activeConversation.participant.avatarUrl}
                  alt={activeConversation.participant.displayName}
                  className="size-10 rounded-full object-cover"
                />
                {activeConversation.participant.isOnline && (
                  <span className="absolute bottom-0 right-0 size-2.5 rounded-full border-2 border-white bg-emerald-500" />
                )}
              </div>
              <div>
                <h3 className="text-sm font-bold text-[#0D1420]">
                  {activeConversation.participant.displayName}
                </h3>
                <p className="text-[11px] font-medium text-slate-400">
                  {activeConversation.participant.isOnline ? (
                    <span className="text-emerald-600 font-semibold">Active now</span>
                  ) : (
                    <span>Offline</span>
                  )}
                  <span> • @{activeConversation.participant.username}</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => alert(`Calling ${activeConversation.participant.displayName}... (Demo feature)`)}
                className="rounded-full p-2 text-slate-400 hover:bg-slate-50 hover:text-[#1E9EF5]"
              >
                <Phone className="size-4.5" />
              </button>
              <button
                onClick={() => alert(`Starting video with ${activeConversation.participant.displayName}... (Demo feature)`)}
                className="rounded-full p-2 text-slate-400 hover:bg-slate-50 hover:text-[#1E9EF5]"
              >
                <Video className="size-4.5" />
              </button>
            </div>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
            <div className="text-center">
              <span className="rounded-full bg-slate-100 px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                End-to-end encrypted session
              </span>
            </div>

            {activeConversation.messages.map((msg) => {
              const isMine = msg.senderId === currentUser?.id;
              return (
                <div
                  key={msg.id}
                  className={`flex items-end gap-2 ${isMine ? 'justify-end' : 'justify-start'}`}
                >
                  {!isMine && (
                    <img
                      src={activeConversation.participant.avatarUrl}
                      alt={activeConversation.participant.displayName}
                      className="size-7 rounded-full object-cover shrink-0 mb-1"
                    />
                  )}

                  <div className={`max-w-[75%] sm:max-w-md ${isMine ? 'items-end' : 'items-start'}`}>
                    <div
                      className={`rounded-2xl px-4 py-2.5 text-xs sm:text-sm font-medium leading-relaxed ${
                        isMine
                          ? 'bg-[#1E9EF5] text-white rounded-br-xs shadow-xs'
                          : 'bg-slate-100 text-[#0D1420] rounded-bl-xs'
                      }`}
                    >
                      {msg.body && <p>{msg.body}</p>}
                      {msg.mediaUrl && (
                        <img
                          src={msg.mediaUrl}
                          alt="Attachment"
                          className="mt-2 max-h-48 rounded-xl object-cover"
                        />
                      )}
                    </div>

                    <div
                      className={`mt-1 flex items-center gap-1 text-[10px] text-slate-400 ${
                        isMine ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <span>{msg.createdAt}</span>
                      {isMine && (
                        <span>
                          {msg.receipt === 'read' ? (
                            <CheckCheck className="size-3 text-[#1E9EF5]" />
                          ) : (
                            <Check className="size-3" />
                          )}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          {/* Attachment Preview Box */}
          {selectedAttachment && (
            <div className="relative mx-4 mb-2 inline-block max-w-xs overflow-hidden rounded-xl border border-slate-200">
              <img src={selectedAttachment} alt="Preview" className="h-20 w-32 object-cover" />
              <button
                onClick={() => setSelectedAttachment(null)}
                className="absolute top-1 right-1 rounded-full bg-black/60 p-1 text-white hover:bg-black"
              >
                <X className="size-3" />
              </button>
            </div>
          )}

          {/* Attachment Picker Tray */}
          {showAttachmentPicker && (
            <div className="mx-4 mb-2 rounded-xl border border-slate-200 bg-slate-50 p-2">
              <div className="flex items-center justify-between mb-1.5 px-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Attach Photo</span>
                <button onClick={() => setShowAttachmentPicker(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="size-3.5" />
                </button>
              </div>
              <div className="flex gap-2">
                {SAMPLE_ATTACHMENTS.map((url, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setSelectedAttachment(url);
                      setShowAttachmentPicker(false);
                    }}
                    className="relative h-14 w-20 overflow-hidden rounded-lg border hover:border-[#1E9EF5]"
                  >
                    <img src={url} alt="Attachment choice" className="size-full object-cover" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message Composer Bar */}
          <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-slate-200 p-3.5">
            <button
              type="button"
              onClick={() => setShowAttachmentPicker(!showAttachmentPicker)}
              className="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-[#1E9EF5]"
            >
              <Image className="size-5" />
            </button>

            <input
              type="text"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 rounded-full border border-slate-200 bg-slate-50 px-4 py-2.5 text-xs sm:text-sm text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:bg-white focus:outline-hidden"
            />

            <button
              type="submit"
              disabled={!messageInput.trim() && !selectedAttachment}
              className="flex size-10 items-center justify-center rounded-full bg-[#1E9EF5] text-white shadow-xs hover:bg-sky-600 active:scale-95 disabled:opacity-40 transition-all"
            >
              <Send className="size-4" />
            </button>
          </form>
        </div>
      ) : (
        <div className="hidden sm:flex flex-1 items-center justify-center p-8 text-center text-slate-400">
          Select a conversation from the left to start messaging.
        </div>
      )}
    </div>
  );
};
