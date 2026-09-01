import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  Post,
  Story,
  Conversation,
  NotificationItem,
  User,
  ReactionType,
  MediaItem,
  Comment,
  GameRoom,
} from '../types';
import {
  SEED_POSTS,
  SEED_STORIES,
  SEED_USERS,
  SEED_CONVERSATIONS,
  SEED_NOTIFICATIONS,
  SEED_GAMES,
} from '../data/seedData';
import { useAuth } from './AuthContext';
import confetti from 'canvas-confetti';

interface SocialContextType {
  posts: Post[];
  stories: Story[];
  users: User[];
  conversations: Conversation[];
  activeConversationId: string | null;
  notifications: NotificationItem[];
  gameRooms: GameRoom[];
  searchQuery: string;
  isSearchOpen: boolean;
  isNotificationsOpen: boolean;
  friendRequests: { incoming: string[]; outgoing: string[]; friends: string[]; following: string[] };

  // Post Actions
  createPost: (body: string, media: MediaItem[], privacy: Post['privacy'], location?: string) => void;
  editPost: (postId: string, newBody: string) => void;
  deletePost: (postId: string) => void;
  reactToPost: (postId: string, reaction: ReactionType) => void;
  addComment: (postId: string, body: string, parentId?: string) => void;
  sharePost: (postId: string, quoteMessage?: string) => void;

  // Story Actions
  createStory: (caption: string, backgroundColor: string, mediaUrl?: string) => void;
  reactToStory: (storyId: string, reaction: ReactionType) => void;
  replyToStory: (storyId: string, replyText: string) => void;
  markStorySeen: (storyId: string) => void;

  // Messages Actions
  setActiveConversationId: (id: string | null) => void;
  sendMessage: (conversationId: string, text: string, mediaUrl?: string) => void;
  startDirectMessage: (userId: string) => string;

  // Friend & People Actions
  sendFriendRequest: (userId: string) => void;
  acceptFriendRequest: (userId: string) => void;
  declineFriendRequest: (userId: string) => void;
  removeFriend: (userId: string) => void;
  toggleFollow: (userId: string) => void;

  // Search & Notifications
  setSearchQuery: (q: string) => void;
  setIsSearchOpen: (open: boolean) => void;
  setIsNotificationsOpen: (open: boolean) => void;
  markNotificationsRead: () => void;

  // Games
  joinGameRoom: (roomId: string) => boolean;
  createGameRoom: (title: string, gameType: GameRoom['gameType'], entryFee: number) => void;
  playMiniGameTurn: (roomId: string) => { won: boolean; coins: number; message: string };
}

const SocialContext = createContext<SocialContextType | undefined>(undefined);

export const SocialProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { currentUser, addCoins } = useAuth();

  const [posts, setPosts] = useState<Post[]>(() => {
    const saved = localStorage.getItem('tata_posts');
    return saved ? JSON.parse(saved) : SEED_POSTS;
  });

  const [stories, setStories] = useState<Story[]>(() => {
    const saved = localStorage.getItem('tata_stories');
    return saved ? JSON.parse(saved) : SEED_STORIES;
  });

  const [users, setUsers] = useState<User[]>(SEED_USERS);
  const [conversations, setConversations] = useState<Conversation[]>(() => {
    const saved = localStorage.getItem('tata_conversations');
    return saved ? JSON.parse(saved) : SEED_CONVERSATIONS;
  });

  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>(SEED_NOTIFICATIONS);
  const [gameRooms, setGameRooms] = useState<GameRoom[]>(SEED_GAMES);

  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);

  const [friendRequests, setFriendRequests] = useState<{
    incoming: string[];
    outgoing: string[];
    friends: string[];
    following: string[];
  }>(() => {
    const saved = localStorage.getItem('tata_friendships');
    return saved
      ? JSON.parse(saved)
      : {
          incoming: ['usr_4'],
          outgoing: ['usr_5'],
          friends: ['usr_1', 'usr_2'],
          following: ['usr_1', 'usr_2', 'usr_3'],
        };
  });

  useEffect(() => {
    localStorage.setItem('tata_posts', JSON.stringify(posts));
  }, [posts]);

  useEffect(() => {
    localStorage.setItem('tata_stories', JSON.stringify(stories));
  }, [stories]);

  useEffect(() => {
    localStorage.setItem('tata_conversations', JSON.stringify(conversations));
  }, [conversations]);

  useEffect(() => {
    localStorage.setItem('tata_friendships', JSON.stringify(friendRequests));
  }, [friendRequests]);

  // Post Methods
  const createPost = (
    body: string,
    media: MediaItem[],
    privacy: Post['privacy'] = 'public',
    location?: string
  ) => {
    if (!currentUser) return;
    const newPost: Post = {
      id: `post_${Date.now()}`,
      authorId: currentUser.id,
      authorName: currentUser.displayName,
      authorUsername: currentUser.username,
      authorAvatar: currentUser.avatarUrl,
      body,
      createdAt: 'Just now',
      privacy,
      location,
      media,
      reactions: { like: 0, love: 0, haha: 0, wow: 0, sad: 0, angry: 0 },
      comments: [],
      shareCount: 0,
    };
    setPosts((prev) => [newPost, ...prev]);
    addCoins(10, 'Created a new community post', 'signup_bonus');
  };

  const editPost = (postId: string, newBody: string) => {
    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? { ...p, body: newBody, isEdited: true } : p))
    );
  };

  const deletePost = (postId: string) => {
    setPosts((prev) => prev.filter((p) => p.id !== postId));
  };

  const reactToPost = (postId: string, reaction: ReactionType) => {
    setPosts((prev) =>
      prev.map((p) => {
        if (p.id !== postId) return p;
        const currentReaction = p.myReaction;
        const newReactions = { ...p.reactions };

        if (currentReaction === reaction) {
          // Toggle off
          newReactions[reaction] = Math.max(0, newReactions[reaction] - 1);
          return { ...p, reactions: newReactions, myReaction: undefined };
        }

        // Decrement previous if existed
        if (currentReaction) {
          newReactions[currentReaction] = Math.max(0, newReactions[currentReaction] - 1);
        }
        // Increment new reaction
        newReactions[reaction] = (newReactions[reaction] || 0) + 1;
        return { ...p, reactions: newReactions, myReaction: reaction };
      })
    );
  };

  const addComment = (postId: string, body: string, parentId?: string) => {
    if (!currentUser || !body.trim()) return;
    const newComment: Comment = {
      id: `comm_${Date.now()}`,
      postId,
      authorId: currentUser.id,
      authorName: currentUser.displayName,
      authorUsername: currentUser.username,
      authorAvatar: currentUser.avatarUrl,
      body,
      createdAt: 'Just now',
      parentId,
      depth: parentId ? 1 : 0,
    };

    setPosts((prev) =>
      prev.map((p) => {
        if (p.id !== postId) return p;
        return { ...p, comments: [...p.comments, newComment] };
      })
    );
  };

  const sharePost = (postId: string, quoteMessage?: string) => {
    if (!currentUser) return;
    const target = posts.find((p) => p.id === postId);
    if (!target) return;

    const sharedPost: Post = {
      id: `post_${Date.now()}`,
      authorId: currentUser.id,
      authorName: currentUser.displayName,
      authorUsername: currentUser.username,
      authorAvatar: currentUser.avatarUrl,
      body: quoteMessage || '',
      createdAt: 'Just now',
      privacy: 'public',
      media: target.media,
      reactions: { like: 0, love: 0, haha: 0, wow: 0, sad: 0, angry: 0 },
      comments: [],
      shareCount: 0,
      sharedPost: {
        authorUsername: target.authorUsername,
        body: target.body,
      },
    };

    // Increment original share count
    setPosts((prev) => [
      sharedPost,
      ...prev.map((p) => (p.id === postId ? { ...p, shareCount: p.shareCount + 1 } : p)),
    ]);
  };

  // Story Methods
  const createStory = (caption: string, backgroundColor: string, mediaUrl?: string) => {
    if (!currentUser) return;
    const newStory: Story = {
      id: `story_${Date.now()}`,
      authorId: currentUser.id,
      authorName: currentUser.displayName,
      authorAvatar: currentUser.avatarUrl,
      caption,
      backgroundColor,
      mediaUrl,
      mediaType: mediaUrl ? 'image' : undefined,
      createdAt: 'Just now',
      seen: false,
      viewCount: 1,
      replies: [],
    };
    setStories((prev) => [newStory, ...prev]);
    addCoins(15, 'Shared a story', 'signup_bonus');
  };

  const reactToStory = (storyId: string, reaction: ReactionType) => {
    setStories((prev) =>
      prev.map((s) => (s.id === storyId ? { ...s, myReaction: reaction } : s))
    );
  };

  const replyToStory = (storyId: string, replyText: string) => {
    if (!currentUser || !replyText.trim()) return;
    setStories((prev) =>
      prev.map((s) => {
        if (s.id !== storyId) return s;
        return {
          ...s,
          replies: [
            ...s.replies,
            {
              id: `rep_${Date.now()}`,
              authorName: currentUser.displayName,
              authorAvatar: currentUser.avatarUrl,
              body: replyText,
              createdAt: 'Just now',
            },
          ],
        };
      })
    );
  };

  const markStorySeen = (storyId: string) => {
    setStories((prev) =>
      prev.map((s) => (s.id === storyId ? { ...s, seen: true, viewCount: s.viewCount + 1 } : s))
    );
  };

  // Direct Messaging
  const sendMessage = (conversationId: string, text: string, mediaUrl?: string) => {
    if (!currentUser || (!text.trim() && !mediaUrl)) return;
    const newMsg = {
      id: `msg_${Date.now()}`,
      conversationId,
      senderId: currentUser.id,
      body: text,
      mediaUrl,
      createdAt: 'Just now',
      receipt: 'delivered' as const,
    };

    setConversations((prev) =>
      prev.map((conv) => {
        if (conv.id !== conversationId) return conv;
        return {
          ...conv,
          lastMessage: text || 'Sent an attachment',
          lastMessageAt: 'Just now',
          messages: [...conv.messages, newMsg],
        };
      })
    );

    // Realistic auto-reply simulation after 1.5s
    setTimeout(() => {
      setConversations((prev) =>
        prev.map((conv) => {
          if (conv.id !== conversationId) return conv;
          const replyMsg = {
            id: `msg_reply_${Date.now()}`,
            conversationId,
            senderId: conv.participant.id,
            body: `Thanks for the message! Always great connecting on TATA. ✨`,
            createdAt: 'Just now',
            receipt: 'delivered' as const,
          };
          return {
            ...conv,
            lastMessage: replyMsg.body,
            lastMessageAt: 'Just now',
            messages: [...conv.messages, replyMsg],
          };
        })
      );
    }, 1500);
  };

  const startDirectMessage = (userId: string): string => {
    const existing = conversations.find((c) => c.participant.id === userId);
    if (existing) {
      setActiveConversationId(existing.id);
      return existing.id;
    }
    const targetUser = users.find((u) => u.id === userId) || SEED_USERS[0];
    const newConv: Conversation = {
      id: `conv_${Date.now()}`,
      participant: targetUser,
      lastMessage: 'Say hello...',
      lastMessageAt: 'Just now',
      unreadCount: 0,
      messages: [],
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
    return newConv.id;
  };

  // Friend actions
  const sendFriendRequest = (userId: string) => {
    setFriendRequests((prev) => ({
      ...prev,
      outgoing: [...prev.outgoing, userId],
    }));
  };

  const acceptFriendRequest = (userId: string) => {
    setFriendRequests((prev) => ({
      ...prev,
      incoming: prev.incoming.filter((id) => id !== userId),
      friends: [...prev.friends, userId],
    }));
    addCoins(25, 'Made a new friend on TATA', 'signup_bonus');
    confetti({ particleCount: 50, spread: 60 });
  };

  const declineFriendRequest = (userId: string) => {
    setFriendRequests((prev) => ({
      ...prev,
      incoming: prev.incoming.filter((id) => id !== userId),
    }));
  };

  const removeFriend = (userId: string) => {
    setFriendRequests((prev) => ({
      ...prev,
      friends: prev.friends.filter((id) => id !== userId),
    }));
  };

  const toggleFollow = (userId: string) => {
    setFriendRequests((prev) => {
      const isFollowing = prev.following.includes(userId);
      return {
        ...prev,
        following: isFollowing
          ? prev.following.filter((id) => id !== userId)
          : [...prev.following, userId],
      };
    });
  };

  const markNotificationsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  // Games
  const joinGameRoom = (roomId: string): boolean => {
    const room = gameRooms.find((r) => r.id === roomId);
    if (!room || !currentUser) return false;
    if (currentUser.coinBalance < room.entryFee) {
      alert(`You need at least ${room.entryFee} TATA coins to enter this room.`);
      return false;
    }
    setGameRooms((prev) =>
      prev.map((r) =>
        r.id === roomId ? { ...r, playersCount: Math.min(r.maxPlayers, r.playersCount + 1) } : r
      )
    );
    return true;
  };

  const createGameRoom = (title: string, gameType: GameRoom['gameType'], entryFee: number) => {
    if (!currentUser) return;
    const newRoom: GameRoom = {
      id: `game_${Date.now()}`,
      title,
      gameType,
      hostName: currentUser.displayName,
      hostAvatar: currentUser.avatarUrl,
      entryFee,
      prizePool: entryFee * 2,
      playersCount: 1,
      maxPlayers: gameType === 'chess' || gameType === 'dice' ? 2 : 4,
      status: 'waiting',
    };
    setGameRooms((prev) => [newRoom, ...prev]);
  };

  const playMiniGameTurn = (roomId: string) => {
    const room = gameRooms.find((r) => r.id === roomId);
    const fee = room ? room.entryFee : 50;
    const prize = room ? room.prizePool : 150;
    const won = Math.random() > 0.4; // 60% win probability for fun demo

    if (won) {
      addCoins(prize, `Victory in ${room?.title || 'Mini-Game'}!`, 'game_win');
      confetti({ particleCount: 70, spread: 70, origin: { y: 0.6 } });
      return { won: true, coins: prize, message: `Spectacular! You won ${prize} TATA coins! 🏆` };
    } else {
      addCoins(-fee, `Entry fee for ${room?.title || 'Mini-Game'}`, 'game_win');
      return { won: false, coins: -fee, message: `Close match! Better luck next round.` };
    }
  };

  return (
    <SocialContext.Provider
      value={{
        posts,
        stories,
        users,
        conversations,
        activeConversationId,
        notifications,
        gameRooms,
        searchQuery,
        isSearchOpen,
        isNotificationsOpen,
        friendRequests,
        createPost,
        editPost,
        deletePost,
        reactToPost,
        addComment,
        sharePost,
        createStory,
        reactToStory,
        replyToStory,
        markStorySeen,
        setActiveConversationId,
        sendMessage,
        startDirectMessage,
        sendFriendRequest,
        acceptFriendRequest,
        declineFriendRequest,
        removeFriend,
        toggleFollow,
        setSearchQuery,
        setIsSearchOpen,
        setIsNotificationsOpen,
        markNotificationsRead,
        joinGameRoom,
        createGameRoom,
        playMiniGameTurn,
      }}
    >
      {children}
    </SocialContext.Provider>
  );
};

export const useSocial = () => {
  const context = useContext(SocialContext);
  if (!context) {
    throw new Error('useSocial must be used within a SocialProvider');
  }
  return context;
};
