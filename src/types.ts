export type ReactionType = 'like' | 'love' | 'haha' | 'wow' | 'sad' | 'angry';

export interface User {
  id: string;
  username: string;
  displayName: string;
  email: string;
  avatarUrl: string;
  coverUrl?: string;
  bio?: string;
  location?: string;
  website?: string;
  coinBalance: number;
  joinedDate: string;
  isOnline: boolean;
  postCount: number;
  friendCount: number;
  followerCount: number;
  followingCount: number;
}

export interface MediaItem {
  id: string;
  type: 'image' | 'video';
  url: string;
}

export interface Comment {
  id: string;
  postId: string;
  authorId: string;
  authorName: string;
  authorUsername: string;
  authorAvatar: string;
  body: string;
  createdAt: string;
  parentId?: string;
  depth: number;
}

export interface Post {
  id: string;
  authorId: string;
  authorName: string;
  authorUsername: string;
  authorAvatar: string;
  body: string;
  createdAt: string;
  privacy: 'public' | 'friends' | 'private';
  location?: string;
  isEdited?: boolean;
  media: MediaItem[];
  reactions: Record<ReactionType, number>;
  myReaction?: ReactionType;
  comments: Comment[];
  shareCount: number;
  sharedPost?: {
    authorUsername: string;
    body: string;
  };
}

export interface StoryReply {
  id: string;
  authorName: string;
  authorAvatar: string;
  body: string;
  createdAt: string;
}

export interface Story {
  id: string;
  authorId: string;
  authorName: string;
  authorAvatar: string;
  caption: string;
  backgroundColor: string;
  mediaUrl?: string;
  mediaType?: 'image' | 'video';
  createdAt: string;
  seen?: boolean;
  viewCount: number;
  myReaction?: ReactionType;
  replies: StoryReply[];
}

export interface DirectMessage {
  id: string;
  conversationId: string;
  senderId: string;
  body: string;
  createdAt: string;
  receipt: 'sent' | 'delivered' | 'read';
  mediaUrl?: string;
}

export interface Conversation {
  id: string;
  participant: User;
  lastMessage: string;
  lastMessageAt: string;
  unreadCount: number;
  messages: DirectMessage[];
}

export interface NotificationItem {
  id: string;
  actor: string;
  actorAvatar: string;
  text: string;
  timeLabel: string;
  icon: 'heart' | 'message-circle' | 'user-plus' | 'coins' | 'share-2';
  read: boolean;
  link?: string;
}

export interface FriendRelationship {
  userId: string;
  status: 'friend' | 'incoming' | 'outgoing' | 'none';
  isFollowing: boolean;
}

export interface GameRoom {
  id: string;
  title: string;
  gameType: 'trivia' | 'chess' | 'dice' | 'words';
  hostName: string;
  hostAvatar: string;
  entryFee: number;
  prizePool: number;
  playersCount: number;
  maxPlayers: number;
  status: 'waiting' | 'in_progress' | 'finished';
}

export interface CoinTransaction {
  id: string;
  type: 'signup_bonus' | 'daily_reward' | 'game_win' | 'gift_received' | 'gift_sent';
  amount: number;
  description: string;
  timestamp: string;
}
