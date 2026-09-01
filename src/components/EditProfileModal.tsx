import React, { useState } from 'react';
import { X, Sparkles, Camera, MapPin, Globe, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const SAMPLE_AVATARS = [
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=200&auto=format&fit=crop&q=80',
];

const SAMPLE_COVERS = [
  'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=1200&auto=format&fit=crop&q=80',
];

interface EditProfileModalProps {
  onClose: () => void;
}

export const EditProfileModal: React.FC<EditProfileModalProps> = ({ onClose }) => {
  const { currentUser, updateProfile } = useAuth();

  const [displayName, setDisplayName] = useState(currentUser?.displayName || '');
  const [bio, setBio] = useState(currentUser?.bio || '');
  const [location, setLocation] = useState(currentUser?.location || '');
  const [website, setWebsite] = useState(currentUser?.website || '');
  const [avatarUrl, setAvatarUrl] = useState(currentUser?.avatarUrl || SAMPLE_AVATARS[0]);
  const [coverUrl, setCoverUrl] = useState(currentUser?.coverUrl || SAMPLE_COVERS[0]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile({
      displayName,
      bio,
      location,
      website,
      avatarUrl,
      coverUrl,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0D1420]/70 p-4 backdrop-blur-xs">
      <div className="w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl animate-in fade-in zoom-in-95">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <User className="size-5 text-[#1E9EF5]" />
            <h2 className="text-base font-bold text-[#0D1420]">Edit Profile</h2>
          </div>
          <button onClick={onClose} className="rounded-full p-1 text-slate-400 hover:bg-slate-100">
            <X className="size-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* Cover Photo Choice */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Cover Banner
            </label>
            <div className="grid grid-cols-4 gap-2">
              {SAMPLE_COVERS.map((url, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setCoverUrl(url)}
                  className={`relative aspect-video overflow-hidden rounded-xl border-2 transition-all ${
                    coverUrl === url ? 'border-[#1E9EF5] ring-2 ring-sky-200' : 'border-slate-200 opacity-70 hover:opacity-100'
                  }`}
                >
                  <img src={url} alt="Cover option" className="size-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* Avatar Photo Choice */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Profile Photo
            </label>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {SAMPLE_AVATARS.map((url, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setAvatarUrl(url)}
                  className={`relative size-12 shrink-0 overflow-hidden rounded-full border-2 transition-all ${
                    avatarUrl === url ? 'border-[#1E9EF5] ring-2 ring-sky-200' : 'border-slate-200 opacity-70 hover:opacity-100'
                  }`}
                >
                  <img src={url} alt="Avatar option" className="size-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* Display Name */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
              Display Name
            </label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2 text-sm font-medium text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
              required
            />
          </div>

          {/* Bio */}
          <div>
            <div className="flex items-center justify-between">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">Bio</label>
              <span className="text-[11px] text-slate-400">{160 - bio.length} chars remaining</span>
            </div>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value.slice(0, 160))}
              rows={3}
              placeholder="Tell the community a little about yourself..."
              className="mt-1 w-full resize-none rounded-xl border border-slate-200 p-3 text-sm text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
            />
          </div>

          {/* Location & Website */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">Location</label>
              <div className="relative mt-1">
                <MapPin className="absolute left-3 top-2.5 size-4 text-slate-400" />
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="City, Country"
                  className="w-full rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-xs font-medium text-[#0D1420] focus:border-[#1E9EF5] outline-hidden"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">Website</label>
              <div className="relative mt-1">
                <Globe className="absolute left-3 top-2.5 size-4 text-slate-400" />
                <input
                  type="text"
                  value={website}
                  onChange={(e) => setWebsite(e.target.value)}
                  placeholder="https://..."
                  className="w-full rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-xs font-medium text-[#0D1420] focus:border-[#1E9EF5] outline-hidden"
                />
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-2.5 pt-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-slate-200 px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-xl bg-[#1E9EF5] px-5 py-2 text-xs font-bold text-white shadow-md hover:bg-sky-600 active:scale-[0.98]"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
