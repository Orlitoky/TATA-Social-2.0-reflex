import { User, Post, Story, Conversation, NotificationItem, GameRoom, CoinTransaction } from '../types';

export const CURRENT_USER: User = {
  id: 'usr_me',
  username: 'alex_tata',
  displayName: 'Alex Rivers',
  email: 'alex@tata.social',
  avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
  coverUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&auto=format&fit=crop&q=80',
  bio: 'Building creative digital experiences ✨ Photography, technology & coffee enthusiast. Welcome to my TATA space!',
  location: 'San Francisco, CA',
  website: 'https://alexrivers.design',
  coinBalance: 750,
  joinedDate: 'September 2024',
  isOnline: true,
  postCount: 12,
  friendCount: 184,
  followerCount: 520,
  followingCount: 240,
};

export const SEED_USERS: User[] = [
  {
    id: 'usr_1',
    username: 'sophia.chen',
    displayName: 'Sophia Chen',
    email: 'sophia@example.com',
    avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
    coverUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&auto=format&fit=crop&q=80',
    bio: 'Product Designer @ Studio • Hiking, ceramics & vinyl records 🎵',
    location: 'Seattle, WA',
    website: 'https://sophiachen.me',
    coinBalance: 1200,
    joinedDate: 'August 2024',
    isOnline: true,
    postCount: 28,
    friendCount: 310,
    followerCount: 890,
    followingCount: 320,
  },
  {
    id: 'usr_2',
    username: 'marcus_dev',
    displayName: 'Marcus Vance',
    email: 'marcus@example.com',
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
    coverUrl: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&auto=format&fit=crop&q=80',
    bio: 'Open source contributor & distributed systems engineer. Chess master in training ♟️',
    location: 'Austin, TX',
    website: 'https://marcusv.io',
    coinBalance: 950,
    joinedDate: 'July 2024',
    isOnline: true,
    postCount: 45,
    friendCount: 195,
    followerCount: 640,
    followingCount: 180,
  },
  {
    id: 'usr_3',
    username: 'elena_art',
    displayName: 'Elena Rostova',
    email: 'elena@example.com',
    avatarUrl: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
    coverUrl: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=1200&auto=format&fit=crop&q=80',
    bio: 'Visual artist & illustrator. Exploring digital watercolor and generative patterns 🎨✨',
    location: 'New York, NY',
    website: 'https://elenarostova.art',
    coinBalance: 2400,
    joinedDate: 'June 2024',
    isOnline: false,
    postCount: 64,
    friendCount: 420,
    followerCount: 1450,
    followingCount: 390,
  },
  {
    id: 'usr_4',
    username: 'david_k',
    displayName: 'David Kim',
    email: 'david@example.com',
    avatarUrl: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80',
    coverUrl: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&auto=format&fit=crop&q=80',
    bio: 'AI researcher & avid trail runner 🏃‍♂️ Exploring deep learning for generative audio.',
    location: 'Toronto, Canada',
    coinBalance: 620,
    joinedDate: 'September 2024',
    isOnline: true,
    postCount: 19,
    friendCount: 142,
    followerCount: 380,
    followingCount: 150,
  },
  {
    id: 'usr_5',
    username: 'chloe_nomad',
    displayName: 'Chloe Dubois',
    email: 'chloe@example.com',
    avatarUrl: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=200&auto=format&fit=crop&q=80',
    coverUrl: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200&auto=format&fit=crop&q=80',
    bio: 'Documentary photographer traveling the globe ✈️ Capturing light and honest stories.',
    location: 'Kyoto, Japan',
    website: 'https://chloedubois.photo',
    coinBalance: 1800,
    joinedDate: 'May 2024',
    isOnline: false,
    postCount: 88,
    friendCount: 560,
    followerCount: 2900,
    followingCount: 410,
  }
];

export const SEED_POSTS: Post[] = [
  {
    id: 'post_1',
    authorId: 'usr_1',
    authorName: 'Sophia Chen',
    authorUsername: 'sophia.chen',
    authorAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
    body: "Just wrapped up our new design system release! Focus on clean contrast, deliberate whitespace, and micro-interactions that feel weightless. Here are a few snapshots from the component library ✨",
    createdAt: '20 mins ago',
    privacy: 'public',
    location: 'Studio Headquarters',
    media: [
      {
        id: 'med_1_1',
        type: 'image',
        url: 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=80'
      },
      {
        id: 'med_1_2',
        type: 'image',
        url: 'https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800&auto=format&fit=crop&q=80'
      }
    ],
    reactions: { like: 24, love: 18, haha: 0, wow: 6, sad: 0, angry: 0 },
    myReaction: 'love',
    comments: [
      {
        id: 'comm_1_1',
        postId: 'post_1',
        authorId: 'usr_2',
        authorName: 'Marcus Vance',
        authorUsername: 'marcus_dev',
        authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
        body: 'The typography scales and elevation tokens look immaculate! Great work team.',
        createdAt: '15 mins ago',
        depth: 0,
      },
      {
        id: 'comm_1_2',
        postId: 'post_1',
        authorId: 'usr_1',
        authorName: 'Sophia Chen',
        authorUsername: 'sophia.chen',
        authorAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
        body: 'Thanks Marcus! Took a lot of iterations on the neutral palette.',
        createdAt: '10 mins ago',
        parentId: 'comm_1_1',
        depth: 1,
      }
    ],
    shareCount: 5,
  },
  {
    id: 'post_2',
    authorId: 'usr_5',
    authorName: 'Chloe Dubois',
    authorUsername: 'chloe_nomad',
    authorAvatar: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=200&auto=format&fit=crop&q=80',
    body: 'Sunrise hike through the mist in Arashiyama bamboo forest. The silence at 5:30 AM is completely magical 🎋⛩️',
    createdAt: '2 hours ago',
    privacy: 'public',
    location: 'Kyoto, Japan',
    media: [
      {
        id: 'med_2_1',
        type: 'image',
        url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1000&auto=format&fit=crop&q=80'
      },
      {
        id: 'med_2_2',
        type: 'image',
        url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=1000&auto=format&fit=crop&q=80'
      },
      {
        id: 'med_2_3',
        type: 'image',
        url: 'https://images.unsplash.com/photo-1478436127897-769e00d2c715?w=1000&auto=format&fit=crop&q=80'
      }
    ],
    reactions: { like: 67, love: 52, haha: 1, wow: 34, sad: 0, angry: 0 },
    myReaction: 'like',
    comments: [
      {
        id: 'comm_2_1',
        postId: 'post_2',
        authorId: 'usr_3',
        authorName: 'Elena Rostova',
        authorUsername: 'elena_art',
        authorAvatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
        body: 'The atmospheric lighting in the first photo is so evocative! Adding this to my watercolor reference board.',
        createdAt: '1 hour ago',
        depth: 0,
      }
    ],
    shareCount: 14,
  },
  {
    id: 'post_3',
    authorId: 'usr_2',
    authorName: 'Marcus Vance',
    authorUsername: 'marcus_dev',
    authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
    body: 'Pro tip for fast full-text search: SQLite with FTS5 or Postgres GIN indexes paired with tsvector can handle millions of documents with sub-10ms latency without needing dedicated clusters for 90% of use cases. Keep architectures delightfully lean.',
    createdAt: '4 hours ago',
    privacy: 'public',
    media: [],
    reactions: { like: 43, love: 12, haha: 3, wow: 9, sad: 0, angry: 0 },
    comments: [],
    shareCount: 8,
  },
  {
    id: 'post_4',
    authorId: 'usr_me',
    authorName: 'Alex Rivers',
    authorUsername: 'alex_tata',
    authorAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
    body: 'Experimenting with generative UI components in TATA Social 2.0. Clean lines, real-time messaging, and virtual coins make everything so vibrant!',
    createdAt: '6 hours ago',
    privacy: 'public',
    location: 'San Francisco, CA',
    media: [
      {
        id: 'med_4_1',
        type: 'image',
        url: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1000&auto=format&fit=crop&q=80'
      }
    ],
    reactions: { like: 19, love: 14, haha: 0, wow: 4, sad: 0, angry: 0 },
    comments: [
      {
        id: 'comm_4_1',
        postId: 'post_4',
        authorId: 'usr_4',
        authorName: 'David Kim',
        authorUsername: 'david_k',
        authorAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80',
        body: 'Super smooth! Loving the live feedback and feed responsiveness.',
        createdAt: '5 hours ago',
        depth: 0,
      }
    ],
    shareCount: 2,
  }
];

export const SEED_STORIES: Story[] = [
  {
    id: 'story_1',
    authorId: 'usr_1',
    authorName: 'Sophia Chen',
    authorAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
    caption: 'Late night prototyping session ☕️💻',
    backgroundColor: '#1E9EF5',
    mediaUrl: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&auto=format&fit=crop&q=80',
    mediaType: 'image',
    createdAt: '2h ago',
    seen: false,
    viewCount: 48,
    replies: [
      {
        id: 'rep_1',
        authorName: 'Marcus Vance',
        authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
        body: 'Don’t forget to sleep!',
        createdAt: '1h ago',
      }
    ],
  },
  {
    id: 'story_2',
    authorId: 'usr_3',
    authorName: 'Elena Rostova',
    authorAvatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
    caption: 'Studio palette of the day 🎨 Acrylic on raw canvas',
    backgroundColor: '#0EA5A5',
    mediaUrl: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=600&auto=format&fit=crop&q=80',
    mediaType: 'image',
    createdAt: '4h ago',
    seen: false,
    viewCount: 92,
    replies: [],
  },
  {
    id: 'story_3',
    authorId: 'usr_4',
    authorName: 'David Kim',
    authorAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80',
    caption: 'Morning 10k trail run completed 🏃‍♂️ Golden hour sunshine',
    backgroundColor: '#2563EB',
    mediaUrl: 'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=600&auto=format&fit=crop&q=80',
    mediaType: 'image',
    createdAt: '6h ago',
    seen: true,
    viewCount: 65,
    replies: [],
  },
  {
    id: 'story_4',
    authorId: 'usr_5',
    authorName: 'Chloe Dubois',
    authorAvatar: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=200&auto=format&fit=crop&q=80',
    caption: 'Matcha green tea tasting in Uji 🍵',
    backgroundColor: '#0D1420',
    mediaUrl: 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80',
    mediaType: 'image',
    createdAt: '8h ago',
    seen: true,
    viewCount: 130,
    replies: [],
  },
  {
    id: 'story_5',
    authorId: 'usr_2',
    authorName: 'Marcus Vance',
    authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
    caption: 'Building with simplicity yields the most resilient software.',
    backgroundColor: '#1E9EF5',
    createdAt: '10h ago',
    seen: true,
    viewCount: 77,
    replies: [],
  }
];

export const SEED_CONVERSATIONS: Conversation[] = [
  {
    id: 'conv_1',
    participant: SEED_USERS[0], // Sophia Chen
    lastMessage: 'Let me know what you think of the new design tokens!',
    lastMessageAt: '12:45 PM',
    unreadCount: 1,
    messages: [
      {
        id: 'msg_1_1',
        conversationId: 'conv_1',
        senderId: 'usr_1',
        body: 'Hey Alex! Hope your week is going great.',
        createdAt: '12:30 PM',
        receipt: 'read',
      },
      {
        id: 'msg_1_2',
        conversationId: 'conv_1',
        senderId: 'usr_me',
        body: 'Hey Sophia! Loving the new color contrasts in the feed.',
        createdAt: '12:35 PM',
        receipt: 'read',
      },
      {
        id: 'msg_1_3',
        conversationId: 'conv_1',
        senderId: 'usr_1',
        body: 'Let me know what you think of the new design tokens!',
        createdAt: '12:45 PM',
        receipt: 'delivered',
      }
    ],
  },
  {
    id: 'conv_2',
    participant: SEED_USERS[1], // Marcus Vance
    lastMessage: 'Up for a speed chess match in the game lounge?',
    lastMessageAt: '10:15 AM',
    unreadCount: 0,
    messages: [
      {
        id: 'msg_2_1',
        conversationId: 'conv_2',
        senderId: 'usr_2',
        body: 'Hey Alex! Did you see the new database benchmarks?',
        createdAt: '10:00 AM',
        receipt: 'read',
      },
      {
        id: 'msg_2_2',
        conversationId: 'conv_2',
        senderId: 'usr_me',
        body: 'Yes! Sub-10ms response times are incredible.',
        createdAt: '10:10 AM',
        receipt: 'read',
      },
      {
        id: 'msg_2_3',
        conversationId: 'conv_2',
        senderId: 'usr_2',
        body: 'Up for a speed chess match in the game lounge?',
        createdAt: '10:15 AM',
        receipt: 'read',
      }
    ],
  },
  {
    id: 'conv_3',
    participant: SEED_USERS[2], // Elena Rostova
    lastMessage: 'Sent you the high-res wallpaper export!',
    lastMessageAt: 'Yesterday',
    unreadCount: 0,
    messages: [
      {
        id: 'msg_3_1',
        conversationId: 'conv_3',
        senderId: 'usr_3',
        body: 'Sent you the high-res wallpaper export!',
        createdAt: 'Yesterday',
        receipt: 'read',
      }
    ],
  }
];

export const SEED_NOTIFICATIONS: NotificationItem[] = [
  {
    id: 'notif_1',
    actor: 'Sophia Chen',
    actorAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
    text: 'liked your post about generative UI components',
    timeLabel: '10 mins ago',
    icon: 'heart',
    read: false,
  },
  {
    id: 'notif_2',
    actor: 'David Kim',
    actorAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80',
    text: 'commented on your timeline update',
    timeLabel: '2 hours ago',
    icon: 'message-circle',
    read: false,
  },
  {
    id: 'notif_3',
    actor: 'Marcus Vance',
    actorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
    text: 'accepted your friend request',
    timeLabel: '1 day ago',
    icon: 'user-plus',
    read: true,
  },
  {
    id: 'notif_4',
    actor: 'TATA Rewards',
    actorAvatar: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80',
    text: 'You received 100 TATA Coins daily streak bonus!',
    timeLabel: '1 day ago',
    icon: 'coins',
    read: true,
  }
];

export const SEED_GAMES: GameRoom[] = [
  {
    id: 'game_1',
    title: 'Tech & Pop Culture Trivia Blitz',
    gameType: 'trivia',
    hostName: 'Marcus Vance',
    hostAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
    entryFee: 50,
    prizePool: 200,
    playersCount: 3,
    maxPlayers: 4,
    status: 'waiting',
  },
  {
    id: 'game_2',
    title: '5-Minute Speed Chess Championship',
    gameType: 'chess',
    hostName: 'David Kim',
    hostAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80',
    entryFee: 100,
    prizePool: 200,
    playersCount: 1,
    maxPlayers: 2,
    status: 'waiting',
  },
  {
    id: 'game_3',
    title: 'High-Roller Dice Duel',
    gameType: 'dice',
    hostName: 'Elena Rostova',
    hostAvatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
    entryFee: 150,
    prizePool: 300,
    playersCount: 2,
    maxPlayers: 2,
    status: 'in_progress',
  },
  {
    id: 'game_4',
    title: 'Speedy Word Scramble Sprint',
    gameType: 'words',
    hostName: 'Sophia Chen',
    hostAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
    entryFee: 25,
    prizePool: 100,
    playersCount: 4,
    maxPlayers: 4,
    status: 'in_progress',
  }
];

export const SEED_COIN_HISTORY: CoinTransaction[] = [
  {
    id: 'tx_1',
    type: 'signup_bonus',
    amount: 500,
    description: 'Welcome to TATA Social signup grant',
    timestamp: 'Sep 1, 2024',
  },
  {
    id: 'tx_2',
    type: 'daily_reward',
    amount: 100,
    description: 'Day 1 Login Streak Reward',
    timestamp: 'Sep 2, 2024',
  },
  {
    id: 'tx_3',
    type: 'game_win',
    amount: 150,
    description: '1st place in Trivia Blitz Lobby #104',
    timestamp: 'Sep 3, 2024',
  }
];
