import React, { useState } from 'react';
import {
  Globe,
  Users,
  Lock,
  MapPin,
  MoreHorizontal,
  Edit3,
  Trash2,
  MessageCircle,
  Share2,
  Send,
  CornerDownRight,
  X,
  Sparkles,
} from 'lucide-react';
import { Post, ReactionType, Comment } from '../types';
import { useAuth } from '../context/AuthContext';
import { useSocial } from '../context/SocialContext';
import { ShareModal } from './ShareModal';

const REACTIONS_LIST: { type: ReactionType; emoji: string; label: string }[] = [
  { type: 'like', emoji: '👍', label: 'Like' },
  { type: 'love', emoji: '❤️', label: 'Love' },
  { type: 'haha', emoji: '😂', label: 'Haha' },
  { type: 'wow', emoji: '😮', label: 'Wow' },
  { type: 'sad', emoji: '😢', label: 'Sad' },
  { type: 'angry', emoji: '😡', label: 'Angry' },
];

interface PostCardProps {
  post: Post;
}

export const PostCard: React.FC<PostCardProps> = ({ post }) => {
  const { currentUser } = useAuth();
  const { reactToPost, addComment, deletePost, editPost } = useSocial();

  const [showComments, setShowComments] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [replyingToComment, setReplyingToComment] = useState<Comment | null>(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedBody, setEditedBody] = useState(post.body);

  const isOwner = currentUser?.id === post.authorId;

  const totalReactions = Object.values(post.reactions).reduce((a, b) => a + b, 0);

  const handleSendComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    addComment(post.id, commentText, replyingToComment?.id);
    setCommentText('');
    setReplyingToComment(null);
    setShowComments(true);
  };

  const handleSaveEdit = () => {
    if (!editedBody.trim()) return;
    editPost(post.id, editedBody);
    setIsEditing(false);
  };

  return (
    <>
      <article className="w-full rounded-2xl border border-slate-200 bg-white p-4 sm:p-5 shadow-xs transition-all hover:border-slate-300">
        {/* Post Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <img
              src={post.authorAvatar}
              alt={post.authorName}
              className="size-10 rounded-full object-cover ring-1 ring-slate-200"
            />
            <div className="min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <h3 className="truncate text-sm font-bold text-[#0D1420]">{post.authorName}</h3>
                <span className="truncate text-xs font-medium text-slate-400">@{post.authorUsername}</span>
              </div>
              <div className="flex items-center gap-2 text-[11px] font-medium text-slate-400">
                <span>{post.createdAt}</span>
                <span>•</span>
                {post.privacy === 'public' && <span title="Public"><Globe className="size-3" /></span>}
                {post.privacy === 'friends' && <span title="Friends"><Users className="size-3" /></span>}
                {post.privacy === 'private' && <span title="Only Me"><Lock className="size-3" /></span>}
                {post.location && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-0.5 text-rose-500 font-semibold">
                      <MapPin className="size-3" />
                      <span>{post.location}</span>
                    </span>
                  </>
                )}
                {post.isEdited && <span className="italic text-slate-400">(edited)</span>}
              </div>
            </div>
          </div>

          {/* Owner Dropdown Menu */}
          {isOwner && (
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="rounded-full p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              >
                <MoreHorizontal className="size-4.5" />
              </button>

              {showMenu && (
                <div className="absolute right-0 top-full mt-1 w-36 rounded-xl border border-slate-200 bg-white p-1 shadow-lg z-30">
                  <button
                    onClick={() => {
                      setIsEditing(true);
                      setShowMenu(false);
                    }}
                    className="flex w-full items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    <Edit3 className="size-3.5 text-slate-500" />
                    <span>Edit Post</span>
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Delete this post?')) deletePost(post.id);
                      setShowMenu(false);
                    }}
                    className="flex w-full items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50"
                  >
                    <Trash2 className="size-3.5" />
                    <span>Delete</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Post Content */}
        <div className="mt-3">
          {isEditing ? (
            <div className="space-y-2">
              <textarea
                value={editedBody}
                onChange={(e) => setEditedBody(e.target.value)}
                rows={3}
                className="w-full rounded-xl border border-slate-200 p-2.5 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-1 focus:ring-sky-200 outline-hidden"
              />
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="rounded-lg border border-slate-200 px-3 py-1 text-xs font-bold text-slate-600"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="rounded-lg bg-[#1E9EF5] px-3 py-1 text-xs font-bold text-white shadow-xs"
                >
                  Save
                </button>
              </div>
            </div>
          ) : (
            <p className="text-sm font-normal leading-relaxed text-slate-800 whitespace-pre-line">
              {post.body}
            </p>
          )}

          {/* Shared Post Quote Banner */}
          {post.sharedPost && (
            <div className="mt-3 rounded-2xl border border-slate-200 bg-slate-50 p-3.5">
              <span className="text-xs font-bold text-[#1E9EF5]">@{post.sharedPost.authorUsername}</span>
              <p className="mt-1 text-xs text-slate-700">{post.sharedPost.body}</p>
            </div>
          )}

          {/* Media Grid */}
          {post.media.length > 0 && (
            <div
              className={`mt-3 grid gap-2 overflow-hidden rounded-2xl border border-slate-100 ${
                post.media.length === 1 ? 'grid-cols-1' : 'grid-cols-2'
              }`}
            >
              {post.media.map((item, idx) => (
                <div key={item.id} className="relative aspect-video max-h-96 w-full overflow-hidden bg-slate-100">
                  <img
                    src={item.url}
                    alt={`Post attachment ${idx + 1}`}
                    className="size-full object-cover transition-transform hover:scale-102"
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Reaction Stats & Counts Bar */}
        <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-xs text-slate-500">
          <div className="flex items-center gap-1.5">
            {totalReactions > 0 ? (
              <span className="font-semibold text-slate-700">
                {post.myReaction ? 'You and ' : ''}
                {totalReactions} {totalReactions === 1 ? 'reaction' : 'reactions'}
              </span>
            ) : (
              <span>Be the first to react</span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowComments(!showComments)}
              className="font-medium hover:text-[#1E9EF5] hover:underline"
            >
              {post.comments.length} {post.comments.length === 1 ? 'comment' : 'comments'}
            </button>
            <span>•</span>
            <button
              onClick={() => setShowShareModal(true)}
              className="font-medium hover:text-[#1E9EF5] hover:underline"
            >
              {post.shareCount} shares
            </button>
          </div>
        </div>

        {/* Interactive Reaction & Action Bar */}
        <div className="mt-2 flex items-center justify-between border-t border-slate-100 pt-2">
          {/* Reaction Buttons */}
          <div className="flex items-center gap-1">
            {REACTIONS_LIST.map((choice) => {
              const count = post.reactions[choice.type] || 0;
              const isActive = post.myReaction === choice.type;
              return (
                <button
                  key={choice.type}
                  onClick={() => reactToPost(post.id, choice.type)}
                  title={choice.label}
                  className={`flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold transition-transform active:scale-120 ${
                    isActive
                      ? 'bg-sky-100 text-[#1E9EF5] font-bold scale-105'
                      : 'hover:bg-slate-100 text-slate-600'
                  }`}
                >
                  <span className="text-sm">{choice.emoji}</span>
                  {count > 0 && <span className="text-[11px]">{count}</span>}
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-1">
            {/* Comment Trigger */}
            <button
              onClick={() => setShowComments(!showComments)}
              className="flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100"
            >
              <MessageCircle className="size-4 text-slate-500" />
              <span className="hidden sm:inline">Comment</span>
            </button>

            {/* Share Trigger */}
            <button
              onClick={() => setShowShareModal(true)}
              className="flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100"
            >
              <Share2 className="size-4 text-slate-500" />
              <span className="hidden sm:inline">Share</span>
            </button>
          </div>
        </div>

        {/* Comments Section */}
        {showComments && (
          <div className="mt-3 border-t border-slate-100 pt-3">
            {/* Comments List */}
            {post.comments.length > 0 && (
              <div className="space-y-2.5 mb-3 max-h-72 overflow-y-auto pr-1">
                {post.comments.map((comment) => (
                  <div
                    key={comment.id}
                    className={`flex items-start gap-2.5 ${comment.depth > 0 ? 'ml-6 border-l-2 border-slate-200 pl-3' : ''}`}
                  >
                    <img
                      src={comment.authorAvatar}
                      alt={comment.authorName}
                      className="size-7 rounded-full object-cover shrink-0 mt-0.5"
                    />
                    <div className="flex-1 rounded-2xl bg-slate-50 p-2.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[#0D1420]">{comment.authorName}</span>
                        <span className="text-[10px] text-slate-400">{comment.createdAt}</span>
                      </div>
                      <p className="mt-1 text-slate-700 leading-relaxed">{comment.body}</p>
                      <button
                        onClick={() => setReplyingToComment(comment)}
                        className="mt-1.5 flex items-center gap-1 text-[11px] font-bold text-[#1E9EF5] hover:underline"
                      >
                        <CornerDownRight className="size-3" />
                        <span>Reply</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Replying Banner */}
            {replyingToComment && (
              <div className="mb-2 flex items-center justify-between rounded-lg bg-sky-50 px-3 py-1.5 text-xs text-sky-700">
                <span>Replying to <strong>{replyingToComment.authorName}</strong></span>
                <button onClick={() => setReplyingToComment(null)} className="hover:text-sky-900">
                  <X className="size-3.5" />
                </button>
              </div>
            )}

            {/* Comment Form */}
            {currentUser && (
              <form onSubmit={handleSendComment} className="flex items-center gap-2">
                <img
                  src={currentUser.avatarUrl}
                  alt={currentUser.displayName}
                  className="size-7 rounded-full object-cover shrink-0"
                />
                <input
                  type="text"
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  placeholder={
                    replyingToComment
                      ? `Reply to @${replyingToComment.authorUsername}...`
                      : 'Write a comment...'
                  }
                  className="flex-1 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-xs text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:bg-white focus:outline-hidden"
                />
                <button
                  type="submit"
                  disabled={!commentText.trim()}
                  className="flex size-8 items-center justify-center rounded-full bg-[#1E9EF5] text-white hover:bg-sky-600 disabled:opacity-50"
                >
                  <Send className="size-3" />
                </button>
              </form>
            )}
          </div>
        )}
      </article>

      {/* Share Modal */}
      {showShareModal && <ShareModal post={post} onClose={() => setShowShareModal(false)} />}
    </>
  );
};
