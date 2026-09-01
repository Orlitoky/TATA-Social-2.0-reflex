import React, { useState } from 'react';
import { X, Image as ImageIcon, Sparkles, Send } from 'lucide-react';
import { useSocial } from '../context/SocialContext';

const STORY_COLORS = ['#1E9EF5', '#22D3EE', '#0D1420', '#0EA5A5', '#2563EB'];

const SAMPLE_STORY_IMAGES = [
  'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=800&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=800&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
];

interface CreateStoryModalProps {
  onClose: () => void;
}

export const CreateStoryModal: React.FC<CreateStoryModalProps> = ({ onClose }) => {
  const { createStory } = useSocial();
  const [caption, setCaption] = useState('');
  const [selectedColor, setSelectedColor] = useState(STORY_COLORS[0]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!caption.trim() && !selectedImage) return;

    setIsSubmitting(true);
    createStory(caption, selectedColor, selectedImage || undefined);
    setIsSubmitting(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0D1420]/70 p-4 backdrop-blur-xs">
      <div className="w-full max-w-md overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div className="flex items-center gap-2">
            <Sparkles className="size-5 text-[#1E9EF5]" />
            <h2 className="text-base font-bold text-[#0D1420]">Create 24h Story</h2>
          </div>
          <button onClick={onClose} className="rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600">
            <X className="size-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5">
          {/* Story Live Preview Box */}
          <div
            className="relative flex h-48 w-full flex-col items-center justify-center rounded-2xl p-4 transition-all overflow-hidden"
            style={!selectedImage ? { backgroundColor: selectedColor } : undefined}
          >
            {selectedImage ? (
              <>
                <img src={selectedImage} alt="Story Background" className="absolute inset-0 size-full object-cover" />
                <div className="absolute inset-0 bg-black/40" />
                <button
                  type="button"
                  onClick={() => setSelectedImage(null)}
                  className="absolute top-2 right-2 rounded-full bg-black/60 p-1 text-white hover:bg-black"
                >
                  <X className="size-4" />
                </button>
              </>
            ) : null}

            <p className="relative z-10 text-center text-sm font-bold text-white drop-shadow-md px-4 line-clamp-4">
              {caption || 'Type your story caption below...'}
            </p>
          </div>

          {/* Caption Text Input */}
          <div className="mt-4">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">Caption / Message</label>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="What's happening right now?"
              rows={2}
              className="mt-1 w-full resize-none rounded-xl border border-slate-200 p-3 text-sm text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
            />
          </div>

          {/* Background Color Palette */}
          {!selectedImage && (
            <div className="mt-3">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">Background Tone</label>
              <div className="mt-1.5 flex items-center gap-2">
                {STORY_COLORS.map((color) => (
                  <button
                    key={color}
                    type="button"
                    onClick={() => setSelectedColor(color)}
                    className={`size-8 rounded-full transition-transform ${
                      selectedColor === color ? 'scale-115 ring-3 ring-[#0D1420] ring-offset-2' : 'hover:scale-105'
                    }`}
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Optional Photo Background Chooser */}
          <div className="mt-4">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">Attach Photo Moment</label>
            <div className="mt-1.5 flex gap-2 overflow-x-auto pb-1">
              {SAMPLE_STORY_IMAGES.map((imgUrl, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setSelectedImage(imgUrl)}
                  className={`relative size-14 shrink-0 overflow-hidden rounded-xl border-2 transition-all ${
                    selectedImage === imgUrl ? 'border-[#1E9EF5] ring-2 ring-sky-200' : 'border-slate-200 hover:opacity-80'
                  }`}
                >
                  <img src={imgUrl} alt="Sample" className="size-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* Submit Action */}
          <div className="mt-6 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-slate-200 px-4 py-2.5 text-xs font-bold text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || (!caption.trim() && !selectedImage)}
              className="flex items-center gap-2 rounded-xl bg-[#1E9EF5] px-6 py-2.5 text-xs font-bold text-white shadow-md shadow-sky-200 hover:bg-sky-600 active:scale-[0.98] disabled:opacity-50"
            >
              <Send className="size-3.5" />
              <span>{isSubmitting ? 'Sharing...' : 'Share to Stories (+15 coins)'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
