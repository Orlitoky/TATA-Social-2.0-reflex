import React, { useState } from 'react';
import { Image, Globe, Users, Lock, MapPin, Send, X, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSocial } from '../context/SocialContext';
import { MediaItem, Post } from '../types';

const SAMPLE_POST_IMAGES = [
  'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=80',
];

export const PostComposer: React.FC = () => {
  const { currentUser } = useAuth();
  const { createPost } = useSocial();

  const [body, setBody] = useState('');
  const [privacy, setPrivacy] = useState<Post['privacy']>('public');
  const [location, setLocation] = useState('');
  const [showLocationInput, setShowLocationInput] = useState(false);
  const [showImagePicker, setShowImagePicker] = useState(false);
  const [selectedMedia, setSelectedMedia] = useState<MediaItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!currentUser) return null;

  const handleAddMedia = (url: string) => {
    if (selectedMedia.some((m) => m.url === url)) return;
    const item: MediaItem = {
      id: `med_${Date.now()}_${Math.random().toString(36).substring(7)}`,
      type: 'image',
      url,
    };
    setSelectedMedia((prev) => [...prev, item]);
  };

  const handleRemoveMedia = (id: string) => {
    setSelectedMedia((prev) => prev.filter((m) => m.id !== id));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!body.trim() && selectedMedia.length === 0) return;

    setIsSubmitting(true);
    createPost(body, selectedMedia, privacy, location.trim() || undefined);
    setBody('');
    setSelectedMedia([]);
    setLocation('');
    setShowLocationInput(false);
    setShowImagePicker(false);
    setIsSubmitting(false);
  };

  return (
    <div className="w-full rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
      <div className="flex gap-3">
        <img
          src={currentUser.avatarUrl}
          alt={currentUser.displayName}
          className="size-10 rounded-full object-cover ring-2 ring-[#1E9EF5]/20 shrink-0"
        />
        <div className="flex-1">
          {/* Post Text Area */}
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder={`What's happening, ${currentUser.displayName.split(' ')[0]}?`}
            rows={2}
            className="w-full resize-none rounded-xl border-0 bg-transparent p-0 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 focus:ring-0 focus:outline-hidden"
          />

          {/* Location Tag Input if active */}
          {showLocationInput && (
            <div className="mt-2 flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-1.5 text-xs text-slate-600">
              <MapPin className="size-3.5 text-[#1E9EF5]" />
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Add location (e.g., San Francisco, CA)"
                className="w-full bg-transparent text-xs font-medium text-[#0D1420] outline-hidden placeholder:text-slate-400"
              />
              <button onClick={() => setShowLocationInput(false)} className="text-slate-400 hover:text-slate-600">
                <X className="size-3.5" />
              </button>
            </div>
          )}

          {/* Selected Media Previews */}
          {selectedMedia.length > 0 && (
            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
              {selectedMedia.map((m) => (
                <div key={m.id} className="relative aspect-video overflow-hidden rounded-xl border border-slate-200">
                  <img src={m.url} alt="Upload" className="size-full object-cover" />
                  <button
                    type="button"
                    onClick={() => handleRemoveMedia(m.id)}
                    className="absolute top-1.5 right-1.5 rounded-full bg-black/60 p-1 text-white hover:bg-black"
                  >
                    <X className="size-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Sample Photo Picker Drawer */}
          {showImagePicker && (
            <div className="mt-3 rounded-xl border border-slate-100 bg-slate-50 p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  Select Photo Attachment
                </span>
                <button onClick={() => setShowImagePicker(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="size-3.5" />
                </button>
              </div>
              <div className="grid grid-cols-4 gap-2">
                {SAMPLE_POST_IMAGES.map((url, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleAddMedia(url)}
                    className="relative aspect-video overflow-hidden rounded-lg border border-slate-200 hover:border-[#1E9EF5] hover:scale-105 transition-all"
                  >
                    <img src={url} alt="Sample attachment" className="size-full object-cover" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Action Toolbar */}
          <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3">
            <div className="flex items-center gap-1 sm:gap-2">
              {/* Photo Button */}
              <button
                type="button"
                onClick={() => setShowImagePicker(!showImagePicker)}
                className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
                  showImagePicker ? 'bg-sky-100 text-[#1E9EF5]' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
                }`}
              >
                <Image className="size-3.5 text-[#1E9EF5]" />
                <span className="hidden sm:inline">Photo</span>
              </button>

              {/* Location Button */}
              <button
                type="button"
                onClick={() => setShowLocationInput(!showLocationInput)}
                className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
                  showLocationInput ? 'bg-sky-100 text-[#1E9EF5]' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
                }`}
              >
                <MapPin className="size-3.5 text-rose-500" />
                <span className="hidden sm:inline">Location</span>
              </button>

              {/* Privacy Selector */}
              <div className="relative inline-block">
                <select
                  value={privacy}
                  onChange={(e) => setPrivacy(e.target.value as Post['privacy'])}
                  className="rounded-full border-0 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 focus:ring-0 focus:outline-hidden cursor-pointer"
                >
                  <option value="public">🌐 Public</option>
                  <option value="friends">👥 Friends</option>
                  <option value="private">🔒 Only Me</option>
                </select>
              </div>
            </div>

            {/* Post Button */}
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || (!body.trim() && selectedMedia.length === 0)}
              className="flex items-center gap-1.5 rounded-xl bg-[#1E9EF5] px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-sky-600 active:scale-[0.98] disabled:opacity-50 transition-all"
            >
              <Send className="size-3.5" />
              <span>Post (+10 coins)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
