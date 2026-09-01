import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import {
  GameType,
  GameRoom,
  RoomPlayer,
  GameChatMessage,
  DominoGameState,
  LudoGameState,
  LotoGameState,
  FaritanyGameState,
  TestUserAccount,
  BingoPattern,
} from '../types/games';
import { initDominoRound, getLegalMovesForTile, getBestBotDominoMove, getPlayerHandPipSum } from '../utils/dominoEngine';
import { initLudoGame, getEligibleTokens, checkLudoCapture, getBestBotLudoMove, COLOR_START_OFFSETS } from '../utils/ludoEngine';
import { initLotoGame, checkBingoPattern } from '../utils/bingoEngine';
import { initFaritanyGame, resolveFaritanyBattle, calculateFaritanyIncome, executeBotFaritanyTurn } from '../utils/faritanyEngine';
import { gameAudio } from '../utils/gameAudio';
import confetti from 'canvas-confetti';

export const TEST_PROFILES: TestUserAccount[] = [
  {
    id: 'user_1',
    displayName: 'Alex Rivers',
    username: 'alex',
    avatarUrl: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
    coinBalance: 2450,
    isBot: false,
  },
  {
    id: 'user_2',
    displayName: 'Sophia Chen',
    username: 'sophia',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
    coinBalance: 1800,
    isBot: false,
  },
  {
    id: 'user_3',
    displayName: 'Marcus Vance',
    username: 'marcus',
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150',
    coinBalance: 3100,
    isBot: false,
  },
  {
    id: 'user_4',
    displayName: 'Elena Rostova',
    username: 'elena',
    avatarUrl: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150',
    coinBalance: 950,
    isBot: false,
  },
  {
    id: 'bot_alpha',
    displayName: 'TATA Bot Alpha',
    username: 'bot_alpha',
    avatarUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150',
    coinBalance: 5000,
    isBot: true,
  },
  {
    id: 'bot_beta',
    displayName: 'TATA Bot Beta',
    username: 'bot_beta',
    avatarUrl: 'https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?w=150',
    coinBalance: 5000,
    isBot: true,
  },
];

interface GamesContextType {
  activeDemoUser: TestUserAccount;
  setActiveDemoUser: (user: TestUserAccount) => void;
  publicRooms: GameRoom[];
  currentRoom: GameRoom | null;
  isMuted: boolean;
  setIsMuted: (muted: boolean) => void;
  // Game states
  dominoState: DominoGameState | null;
  ludoState: LudoGameState | null;
  lotoState: LotoGameState | null;
  faritanyState: FaritanyGameState | null;
  // Room navigation & controls
  createRoom: (gameType: GameType, title: string, isPrivate: boolean, settings: any) => Promise<GameRoom>;
  joinRoom: (roomIdOrCode: string) => Promise<boolean>;
  leaveRoom: () => void;
  quickPlay: (gameType: GameType) => void;
  playWithBots: (gameType: GameType) => void;
  toggleReady: () => void;
  addBot: (botProfile?: TestUserAccount) => void;
  kickPlayer: (playerId: string) => void;
  startGame: () => void;
  rematch: () => void;
  resetMatch: () => void;
  sendChatMessage: (text: string) => void;
  // Domino actions
  playDominoTile: (tileId: string, side?: 'left' | 'right' | 'start') => void;
  drawDominoBoneyard: () => void;
  passDominoTurn: () => void;
  // Ludo actions
  rollLudoDice: () => void;
  moveLudoToken: (tokenId: number) => void;
  // Loto / Bingo actions
  daubBingoNumber: (cardId: string, row: number, col: number) => void;
  claimBingoWin: (cardId: string, pattern: BingoPattern) => void;
  nextBingoBall: () => void;
  toggleBingoAutoDraw: () => void;
  toggleAutoDaub: () => void;
  // Faritany actions
  deployFaritanyTroops: (territoryId: string, count?: number) => void;
  attackFaritany: (sourceId: string, targetId: string, troops?: number) => void;
  fortifyFaritany: (sourceId: string, targetId: string, count?: number) => void;
  endFaritanyPhase: () => void;
  // Admin & Ledger
  adminGrantCoins: (userId: string, amount: number, reason?: string) => void;
  adminCloseRoom: (roomId: string) => void;
}

const GamesContext = createContext<GamesContextType | undefined>(undefined);

export const GamesProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeDemoUser, setActiveDemoUser] = useState<TestUserAccount>(TEST_PROFILES[0]);
  const [publicRooms, setPublicRooms] = useState<GameRoom[]>([]);
  const [currentRoom, setCurrentRoom] = useState<GameRoom | null>(null);
  const [isMuted, setIsMutedState] = useState(false);

  // Active game sub-states
  const [dominoState, setDominoState] = useState<DominoGameState | null>(null);
  const [ludoState, setLudoState] = useState<LudoGameState | null>(null);
  const [lotoState, setLotoState] = useState<LotoGameState | null>(null);
  const [faritanyState, setFaritanyState] = useState<FaritanyGameState | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const channelRef = useRef<BroadcastChannel | null>(null);

  const setIsMuted = (muted: boolean) => {
    setIsMutedState(muted);
    gameAudio.setMuted(muted);
  };

  // Fetch active rooms from server API
  const refreshRooms = useCallback(async () => {
    try {
      const res = await fetch('/api/games/rooms');
      if (res.ok) {
        const data = await res.json();
        if (data.rooms) {
          setPublicRooms(data.rooms);
        }
      }
    } catch {
      // Fallback
    }
  }, []);

  useEffect(() => {
    refreshRooms();
    const interval = setInterval(refreshRooms, 5000);
    return () => clearInterval(interval);
  }, [refreshRooms]);

  // Setup BroadcastChannel for instantaneous multi-tab demo sync
  useEffect(() => {
    if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
      const channel = new BroadcastChannel('tata_games_sync');
      channelRef.current = channel;

      channel.onmessage = (event) => {
        const { type, payload } = event.data;
        if (type === 'ROOM_UPDATE') {
          if (currentRoom && currentRoom.id === payload.id) {
            setCurrentRoom(payload);
          }
          refreshRooms();
        } else if (type === 'GAME_STATE_UPDATE') {
          if (payload.domino) setDominoState(payload.domino);
          if (payload.ludo) setLudoState(payload.ludo);
          if (payload.loto) setLotoState(payload.loto);
          if (payload.faritany) setFaritanyState(payload.faritany);
        }
      };

      return () => {
        channel.close();
      };
    }
  }, [currentRoom, refreshRooms]);

  // Connect WebSocket when inside a room
  useEffect(() => {
    if (!currentRoom) return;

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(
          JSON.stringify({
            type: 'JOIN_ROOM',
            roomId: currentRoom.id,
            user: activeDemoUser,
          })
        );
      };

      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data.type === 'ROOM_STATE' && data.room) {
            setCurrentRoom(data.room);
          } else if (data.type === 'NEW_CHAT_MESSAGE' && data.message) {
            setCurrentRoom((prev) =>
              prev ? { ...prev, chatMessages: [...prev.chatMessages, data.message] } : null
            );
          }
        } catch {
          // ignore
        }
      };

      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'LEAVE_ROOM', roomId: currentRoom.id, user: activeDemoUser }));
          ws.close();
        }
      };
    } catch {
      // WS fallback to local
    }
  }, [currentRoom?.id, activeDemoUser]);

  // Sync state broadcast helper
  const broadcastRoomUpdate = (updatedRoom: GameRoom) => {
    setCurrentRoom(updatedRoom);
    channelRef.current?.postMessage({ type: 'ROOM_UPDATE', payload: updatedRoom });
  };

  const broadcastGameUpdate = (states: {
    domino?: DominoGameState | null;
    ludo?: LudoGameState | null;
    loto?: LotoGameState | null;
    faritany?: FaritanyGameState | null;
  }) => {
    if (states.domino !== undefined) setDominoState(states.domino);
    if (states.ludo !== undefined) setLudoState(states.ludo);
    if (states.loto !== undefined) setLotoState(states.loto);
    if (states.faritany !== undefined) setFaritanyState(states.faritany);

    channelRef.current?.postMessage({
      type: 'GAME_STATE_UPDATE',
      payload: states,
    });
  };

  // ==================== ROOM SYSTEM CONTROLS ====================

  const createRoom = async (
    gameType: GameType,
    title: string,
    isPrivate: boolean,
    settings: any
  ): Promise<GameRoom> => {
    const code = Math.random().toString(36).substring(2, 8).toUpperCase();
    const newRoom: GameRoom = {
      id: `room_${gameType}_${Date.now()}`,
      code,
      title: title || `${gameType.toUpperCase()} Battle`,
      gameType,
      isPrivate,
      hostId: activeDemoUser.id,
      maxPlayers: settings?.maxPlayers || (gameType === 'domino' ? 2 : 4),
      players: [
        {
          id: activeDemoUser.id,
          displayName: activeDemoUser.displayName,
          username: activeDemoUser.username,
          avatarUrl: activeDemoUser.avatarUrl,
          isReady: true,
          isBot: false,
          isHost: true,
          score: 0,
        },
      ],
      status: 'lobby',
      entryFee: settings?.entryFee || 50,
      prizePool: settings?.entryFee || 50,
      createdAt: new Date().toISOString(),
      settings: {
        turnTimeSeconds: 30,
        targetScore: 100,
        ...settings,
      },
      chatMessages: [
        {
          id: `msg_${Date.now()}`,
          senderId: 'system',
          senderName: 'TATA Arbiter',
          senderAvatar: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150',
          text: `Welcome! Room code is ${code}. Ready up to start.`,
          timestamp: 'Just now',
          isSystem: true,
        },
      ],
    };

    try {
      await fetch('/api/games/rooms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newRoom, host: activeDemoUser }),
      });
    } catch {
      // Local fallback
    }

    setCurrentRoom(newRoom);
    refreshRooms();
    return newRoom;
  };

  const joinRoom = async (roomIdOrCode: string): Promise<boolean> => {
    const target = publicRooms.find(
      (r) =>
        r.id === roomIdOrCode ||
        r.code.toUpperCase() === roomIdOrCode.trim().toUpperCase()
    );

    if (!target) return false;

    // Check if player is already in room
    let updatedPlayers = [...target.players];
    const existing = updatedPlayers.find((p) => p.id === activeDemoUser.id);
    if (!existing) {
      if (updatedPlayers.length >= target.maxPlayers) {
        return false;
      }
      updatedPlayers.push({
        id: activeDemoUser.id,
        displayName: activeDemoUser.displayName,
        username: activeDemoUser.username,
        avatarUrl: activeDemoUser.avatarUrl,
        isReady: false,
        isBot: false,
        isHost: false,
        score: 0,
      });
    }

    const updatedRoom: GameRoom = {
      ...target,
      players: updatedPlayers,
      prizePool: target.entryFee * updatedPlayers.length,
    };

    broadcastRoomUpdate(updatedRoom);
    return true;
  };

  const leaveRoom = () => {
    if (!currentRoom) return;
    const updatedPlayers = currentRoom.players.filter((p) => p.id !== activeDemoUser.id);
    if (updatedPlayers.length === 0) {
      setCurrentRoom(null);
    } else {
      const isHostLeaving = currentRoom.hostId === activeDemoUser.id;
      const newHost = isHostLeaving ? updatedPlayers[0] : null;
      if (newHost) newHost.isHost = true;

      const updated: GameRoom = {
        ...currentRoom,
        hostId: newHost ? newHost.id : currentRoom.hostId,
        players: updatedPlayers,
      };
      broadcastRoomUpdate(updated);
    }
    setCurrentRoom(null);
    setDominoState(null);
    setLudoState(null);
    setLotoState(null);
    setFaritanyState(null);
  };

  const toggleReady = () => {
    if (!currentRoom) return;
    const updatedPlayers = currentRoom.players.map((p) =>
      p.id === activeDemoUser.id ? { ...p, isReady: !p.isReady } : p
    );
    broadcastRoomUpdate({ ...currentRoom, players: updatedPlayers });
  };

  const addBot = (botProfile?: TestUserAccount) => {
    if (!currentRoom || currentRoom.players.length >= currentRoom.maxPlayers) return;
    const bot =
      botProfile ||
      (currentRoom.players.some((p) => p.id === 'bot_alpha')
        ? TEST_PROFILES[5] // Bot Beta
        : TEST_PROFILES[4]); // Bot Alpha

    if (currentRoom.players.some((p) => p.id === bot.id)) return;

    const newPlayer: RoomPlayer = {
      id: bot.id,
      displayName: bot.displayName,
      username: bot.username,
      avatarUrl: bot.avatarUrl,
      isReady: true,
      isBot: true,
      isHost: false,
      score: 0,
    };

    const updated: GameRoom = {
      ...currentRoom,
      players: [...currentRoom.players, newPlayer],
      prizePool: currentRoom.entryFee * (currentRoom.players.length + 1),
    };
    broadcastRoomUpdate(updated);
  };

  const kickPlayer = (playerId: string) => {
    if (!currentRoom || currentRoom.hostId !== activeDemoUser.id) return;
    const updated: GameRoom = {
      ...currentRoom,
      players: currentRoom.players.filter((p) => p.id !== playerId),
    };
    broadcastRoomUpdate(updated);
  };

  const sendChatMessage = (text: string) => {
    if (!currentRoom || !text.trim()) return;
    const msg: GameChatMessage = {
      id: `msg_${Date.now()}`,
      senderId: activeDemoUser.id,
      senderName: activeDemoUser.displayName,
      senderAvatar: activeDemoUser.avatarUrl,
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const updated = {
      ...currentRoom,
      chatMessages: [...currentRoom.chatMessages, msg],
    };
    broadcastRoomUpdate(updated);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'CHAT_MESSAGE',
          roomId: currentRoom.id,
          user: activeDemoUser,
          data: { text: text.trim() },
        })
      );
    }
  };

  // ==================== LAUNCH / START GAME ====================

  const startGame = () => {
    if (!currentRoom) return;
    const playerIds = currentRoom.players.map((p) => p.id);

    const updatedRoom: GameRoom = {
      ...currentRoom,
      status: 'playing',
    };
    broadcastRoomUpdate(updatedRoom);

    // Initialize specific game engine
    if (currentRoom.gameType === 'domino') {
      const initDomino = initDominoRound(playerIds, currentRoom.settings.targetScore || 100);
      broadcastGameUpdate({ domino: initDomino });
      gameAudio.playTileClick();
    } else if (currentRoom.gameType === 'ludo') {
      const initLudo = initLudoGame(playerIds);
      broadcastGameUpdate({ ludo: initLudo });
      gameAudio.playDiceRoll();
    } else if (currentRoom.gameType === 'loto') {
      const initLoto = initLotoGame(playerIds, {}, currentRoom.settings.autoDaub ?? true);
      broadcastGameUpdate({ loto: initLoto });
      gameAudio.playBingoBall();
    } else if (currentRoom.gameType === 'faritany') {
      const initFaritany = initFaritanyGame(playerIds);
      broadcastGameUpdate({ faritany: initFaritany });
      gameAudio.playBattleClash();
    }
  };

  // Instant Quick Play (auto-creates or pairs, fills bots if needed and starts)
  const quickPlay = (gameType: GameType) => {
    const requiredPlayers = gameType === 'domino' ? 2 : 4;
    const title = `⚡ Quick ${gameType.toUpperCase()} Duel`;
    const code = Math.random().toString(36).substring(2, 8).toUpperCase();

    const players: RoomPlayer[] = [
      {
        id: activeDemoUser.id,
        displayName: activeDemoUser.displayName,
        username: activeDemoUser.username,
        avatarUrl: activeDemoUser.avatarUrl,
        isReady: true,
        isBot: false,
        isHost: true,
        score: 0,
      },
    ];

    // Add smart bots to fill room
    for (let i = 1; i < requiredPlayers; i++) {
      const bot = TEST_PROFILES[3 + i] || TEST_PROFILES[4];
      players.push({
        id: bot.id,
        displayName: bot.displayName,
        username: bot.username,
        avatarUrl: bot.avatarUrl,
        isReady: true,
        isBot: true,
        isHost: false,
        score: 0,
      });
    }

    const room: GameRoom = {
      id: `quick_${gameType}_${Date.now()}`,
      code,
      title,
      gameType,
      isPrivate: false,
      hostId: activeDemoUser.id,
      maxPlayers: requiredPlayers,
      players,
      status: 'playing',
      entryFee: 50,
      prizePool: 50 * requiredPlayers,
      createdAt: new Date().toISOString(),
      settings: {
        maxPlayers: requiredPlayers,
        entryFee: 50,
        turnTimeSeconds: 25,
        targetScore: 100,
        autoDaub: true,
      },
      chatMessages: [
        {
          id: `msg_qp`,
          senderId: 'system',
          senderName: 'TATA Quick Play',
          senderAvatar: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150',
          text: 'Quick match launched! Good luck!',
          timestamp: 'Just now',
          isSystem: true,
        },
      ],
    };

    setCurrentRoom(room);
    const pids = players.map((p) => p.id);

    if (gameType === 'domino') {
      const d = initDominoRound(pids, 100);
      broadcastGameUpdate({ domino: d, ludo: null, loto: null, faritany: null });
      gameAudio.playTileClick();
    } else if (gameType === 'ludo') {
      const l = initLudoGame(pids);
      broadcastGameUpdate({ ludo: l, domino: null, loto: null, faritany: null });
      gameAudio.playDiceRoll();
    } else if (gameType === 'loto') {
      const b = initLotoGame(pids, {}, true);
      broadcastGameUpdate({ loto: b, domino: null, ludo: null, faritany: null });
      gameAudio.playBingoBall();
    } else if (gameType === 'faritany') {
      const f = initFaritanyGame(pids);
      broadcastGameUpdate({ faritany: f, domino: null, ludo: null, loto: null });
      gameAudio.playBattleClash();
    }
  };

  // Play with Bots mode
  const playWithBots = (gameType: GameType) => {
    quickPlay(gameType);
  };

  // Rematch
  const rematch = () => {
    if (!currentRoom) return;
    startGame();
  };

  // Reset Match
  const resetMatch = () => {
    if (!currentRoom) return;
    startGame();
  };

  // ==================== DOMINO ACTIONS ====================

  const playDominoTile = (tileId: string, preferredSide: 'left' | 'right' | 'start' = 'start') => {
    if (!dominoState || !currentRoom) return;
    const hand = dominoState.playerHands[dominoState.currentTurnPlayerId] || [];
    const tile = hand.find((t) => t.id === tileId);
    if (!tile) return;

    const legalMoves = getLegalMovesForTile(
      tile,
      dominoState.boardChain,
      dominoState.leftOpenPip,
      dominoState.rightOpenPip
    );

    if (legalMoves.length === 0) return;

    let chosenMove = legalMoves.find((m) => m.side === preferredSide) || legalMoves[0];

    // Build placed domino
    const renderLeft = chosenMove.flip ? tile.right : tile.left;
    const renderRight = chosenMove.flip ? tile.left : tile.right;

    let newChain = [...dominoState.boardChain];
    let newLeftOpen = dominoState.leftOpenPip;
    let newRightOpen = dominoState.rightOpenPip;

    if (chosenMove.side === 'start') {
      newChain.push({
        tile,
        placedBy: dominoState.currentTurnPlayerId,
        position: 'start',
        orientation: tile.left === tile.right ? 'vertical' : 'horizontal',
        flipped: false,
        renderLeft: tile.left,
        renderRight: tile.right,
      });
      newLeftOpen = tile.left;
      newRightOpen = tile.right;
    } else if (chosenMove.side === 'left') {
      newChain.unshift({
        tile,
        placedBy: dominoState.currentTurnPlayerId,
        position: 'left',
        orientation: tile.left === tile.right ? 'vertical' : 'horizontal',
        flipped: chosenMove.flip,
        renderLeft,
        renderRight,
      });
      newLeftOpen = renderLeft;
    } else if (chosenMove.side === 'right') {
      newChain.push({
        tile,
        placedBy: dominoState.currentTurnPlayerId,
        position: 'right',
        orientation: tile.left === tile.right ? 'vertical' : 'horizontal',
        flipped: chosenMove.flip,
        renderLeft,
        renderRight,
      });
      newRightOpen = renderRight;
    }

    const updatedHand = hand.filter((t) => t.id !== tileId);
    const updatedHands = {
      ...dominoState.playerHands,
      [dominoState.currentTurnPlayerId]: updatedHand,
    };

    gameAudio.playTileClick();

    // Check if player won round (emptied hand)
    if (updatedHand.length === 0) {
      gameAudio.playVictory();
      confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });

      const winnerId = dominoState.currentTurnPlayerId;
      let pointsEarned = 0;
      Object.keys(updatedHands).forEach((pid) => {
        if (pid !== winnerId) {
          pointsEarned += getPlayerHandPipSum(updatedHands[pid]);
        }
      });

      const newScores = {
        ...dominoState.scores,
        [winnerId]: (dominoState.scores[winnerId] || 0) + pointsEarned,
      };

      const matchWinner = newScores[winnerId] >= dominoState.targetScore ? winnerId : null;

      broadcastGameUpdate({
        domino: {
          ...dominoState,
          boardChain: newChain,
          playerHands: updatedHands,
          leftOpenPip: newLeftOpen,
          rightOpenPip: newRightOpen,
          scores: newScores,
          roundWinnerId: winnerId,
          roundSummary: `Player emptied their hand! +${pointsEarned} points won.`,
          matchWinnerId: matchWinner,
          logs: [`Domino! Player ${winnerId} won the round (+${pointsEarned} pts).`, ...dominoState.logs],
        },
      });
      return;
    }

    // Advance turn to next player
    const playerIds = currentRoom.players.map((p) => p.id);
    const currentIdx = playerIds.indexOf(dominoState.currentTurnPlayerId);
    const nextPlayerId = playerIds[(currentIdx + 1) % playerIds.length];

    const nextState: DominoGameState = {
      ...dominoState,
      boardChain: newChain,
      playerHands: updatedHands,
      leftOpenPip: newLeftOpen,
      rightOpenPip: newRightOpen,
      currentTurnPlayerId: nextPlayerId,
      consecutivePasses: 0,
      turnTimeLeft: 30,
      logs: [`Played [${tile.left}|${tile.right}]. Next turn: ${nextPlayerId}.`, ...dominoState.logs],
    };

    broadcastGameUpdate({ domino: nextState });
  };

  const drawDominoBoneyard = () => {
    if (!dominoState || dominoState.boneyard.length === 0) return;
    const [drawn, ...remainingBoneyard] = dominoState.boneyard;
    const hand = dominoState.playerHands[dominoState.currentTurnPlayerId] || [];

    gameAudio.playTileClick();

    const updatedState: DominoGameState = {
      ...dominoState,
      boneyard: remainingBoneyard,
      playerHands: {
        ...dominoState.playerHands,
        [dominoState.currentTurnPlayerId]: [...hand, drawn],
      },
      logs: [`Drew 1 tile from the boneyard.`, ...dominoState.logs],
    };

    broadcastGameUpdate({ domino: updatedState });
  };

  const passDominoTurn = () => {
    if (!dominoState || !currentRoom) return;
    const playerIds = currentRoom.players.map((p) => p.id);
    const currentIdx = playerIds.indexOf(dominoState.currentTurnPlayerId);
    const nextPlayerId = playerIds[(currentIdx + 1) % playerIds.length];
    const newPasses = dominoState.consecutivePasses + 1;

    // Check if game is blocked (everyone passed consecutively)
    if (newPasses >= playerIds.length) {
      // Find lowest hand pip sum
      let minPip = 999;
      let roundWinner = playerIds[0];
      playerIds.forEach((pid) => {
        const sum = getPlayerHandPipSum(dominoState.playerHands[pid] || []);
        if (sum < minPip) {
          minPip = sum;
          roundWinner = pid;
        }
      });

      let pointsEarned = 0;
      playerIds.forEach((pid) => {
        if (pid !== roundWinner) {
          pointsEarned += getPlayerHandPipSum(dominoState.playerHands[pid] || []);
        }
      });

      const newScores = {
        ...dominoState.scores,
        [roundWinner]: (dominoState.scores[roundWinner] || 0) + pointsEarned,
      };

      const matchWinner = newScores[roundWinner] >= dominoState.targetScore ? roundWinner : null;

      broadcastGameUpdate({
        domino: {
          ...dominoState,
          consecutivePasses: newPasses,
          roundWinnerId: roundWinner,
          roundSummary: `Board blocked! Winner has lowest remaining pips (${minPip} pips). +${pointsEarned} pts.`,
          scores: newScores,
          matchWinnerId: matchWinner,
          logs: [`Board blocked! ${roundWinner} won with lowest pips.`, ...dominoState.logs],
        },
      });
      return;
    }

    broadcastGameUpdate({
      domino: {
        ...dominoState,
        currentTurnPlayerId: nextPlayerId,
        consecutivePasses: newPasses,
        turnTimeLeft: 30,
        logs: [`Turn passed to ${nextPlayerId}.`, ...dominoState.logs],
      },
    });
  };

  // Bot automated turn runner for Domino
  useEffect(() => {
    if (!dominoState || !currentRoom || dominoState.roundWinnerId || dominoState.matchWinnerId) return;
    const currentTurnUser = currentRoom.players.find((p) => p.id === dominoState.currentTurnPlayerId);
    if (!currentTurnUser || !currentTurnUser.isBot) return;

    const timer = setTimeout(() => {
      const hand = dominoState.playerHands[dominoState.currentTurnPlayerId] || [];
      const bestMove = getBestBotDominoMove(
        hand,
        dominoState.boardChain,
        dominoState.leftOpenPip,
        dominoState.rightOpenPip
      );

      if (bestMove) {
        playDominoTile(bestMove.tile.id, bestMove.side);
      } else if (dominoState.boneyard.length > 0) {
        drawDominoBoneyard();
      } else {
        passDominoTurn();
      }
    }, 1200);

    return () => clearTimeout(timer);
  }, [dominoState?.currentTurnPlayerId, dominoState?.boneyard.length]);

  // ==================== LUDO ACTIONS ====================

  const rollLudoDice = () => {
    if (!ludoState || !ludoState.canRollDice) return;
    const roll = Math.floor(Math.random() * 6) + 1;
    gameAudio.playDiceRoll();

    const currentColor = ludoState.colorOrder[ludoState.currentColorIndex];
    const eligible = getEligibleTokens(ludoState.tokens, currentColor, roll);
    const isConsecutiveSix = roll === 6 ? ludoState.consecutiveSixes + 1 : 0;

    // 3 consecutive sixes penalty
    if (isConsecutiveSix >= 3) {
      const nextIdx = (ludoState.currentColorIndex + 1) % ludoState.colorOrder.length;
      const nextColor = ludoState.colorOrder[nextIdx];
      const nextPlayerId = Object.keys(ludoState.playerColors).find(
        (k) => ludoState.playerColors[k] === nextColor
      ) || '';

      broadcastGameUpdate({
        ludo: {
          ...ludoState,
          diceRoll: roll,
          hasRolledDice: true,
          canRollDice: true,
          eligibleTokenIds: [],
          consecutiveSixes: 0,
          currentColorIndex: nextIdx,
          currentTurnPlayerId: nextPlayerId,
          logs: [`3 consecutive sixes! Turn passed to ${nextColor}.`, ...ludoState.logs],
        },
      });
      return;
    }

    // No moves possible -> auto pass
    if (eligible.length === 0) {
      setTimeout(() => {
        if (!ludoState) return;
        const nextIdx = (ludoState.currentColorIndex + 1) % ludoState.colorOrder.length;
        const nextColor = ludoState.colorOrder[nextIdx];
        const nextPlayerId = Object.keys(ludoState.playerColors).find(
          (k) => ludoState.playerColors[k] === nextColor
        ) || '';

        broadcastGameUpdate({
          ludo: {
            ...ludoState,
            diceRoll: roll,
            hasRolledDice: true,
            canRollDice: true,
            eligibleTokenIds: [],
            currentColorIndex: nextIdx,
            currentTurnPlayerId: nextPlayerId,
            logs: [`Rolled a ${roll}, no moves available. Next turn: ${nextColor}.`, ...ludoState.logs],
          },
        });
      }, 800);
      return;
    }

    broadcastGameUpdate({
      ludo: {
        ...ludoState,
        diceRoll: roll,
        hasRolledDice: true,
        canRollDice: false,
        eligibleTokenIds: eligible,
        consecutiveSixes: isConsecutiveSix,
      },
    });
  };

  const moveLudoToken = (tokenId: number) => {
    if (!ludoState || !ludoState.diceRoll || !ludoState.eligibleTokenIds.includes(tokenId)) return;
    const currentColor = ludoState.colorOrder[ludoState.currentColorIndex];
    const roll = ludoState.diceRoll;

    let updatedTokens = [...ludoState.tokens];
    const tokenIndex = updatedTokens.findIndex((t) => t.color === currentColor && t.id === tokenId);
    if (tokenIndex === -1) return;

    const token = updatedTokens[tokenIndex];
    let nextStep = token.step;

    if (token.step === -1) {
      // Out of yard
      nextStep = 0;
      gameAudio.playTokenStep();
    } else {
      nextStep = token.step + roll;
      gameAudio.playTokenStep();
    }

    const isFinished = nextStep === 58;
    if (isFinished) {
      gameAudio.playVictory();
    }

    // Check captures
    let extraRollAwarded = roll === 6 || isFinished;
    const { capturedToken } = checkLudoCapture(token, nextStep, updatedTokens);

    if (capturedToken) {
      gameAudio.playTokenCapture();
      extraRollAwarded = true;
      const capturedIdx = updatedTokens.findIndex(
        (t) => t.color === capturedToken.color && t.id === capturedToken.id
      );
      if (capturedIdx !== -1) {
        updatedTokens[capturedIdx] = { ...updatedTokens[capturedIdx], step: -1 };
      }
    }

    updatedTokens[tokenIndex] = {
      ...token,
      step: nextStep,
      isFinished,
    };

    // Check if player finished all 4 tokens
    const playerFinishedTokens = updatedTokens.filter((t) => t.color === currentColor && t.isFinished);
    let updatedWinners = [...ludoState.winners];
    const playerId = ludoState.currentTurnPlayerId;

    if (playerFinishedTokens.length === 4 && !updatedWinners.includes(playerId)) {
      updatedWinners.push(playerId);
      confetti({ particleCount: 100, spread: 80, origin: { y: 0.6 } });
    }

    const matchFinished = updatedWinners.length >= ludoState.colorOrder.length - 1;

    let nextIdx = ludoState.currentColorIndex;
    let nextPlayerId = ludoState.currentTurnPlayerId;

    if (!extraRollAwarded) {
      nextIdx = (ludoState.currentColorIndex + 1) % ludoState.colorOrder.length;
      const nextColor = ludoState.colorOrder[nextIdx];
      nextPlayerId = Object.keys(ludoState.playerColors).find(
        (k) => ludoState.playerColors[k] === nextColor
      ) || '';
    }

    broadcastGameUpdate({
      ludo: {
        ...ludoState,
        tokens: updatedTokens,
        diceRoll: null,
        hasRolledDice: false,
        canRollDice: true,
        eligibleTokenIds: [],
        currentColorIndex: nextIdx,
        currentTurnPlayerId: nextPlayerId,
        winners: updatedWinners,
        matchFinished,
        logs: [
          `Moved ${currentColor} token #${tokenId} to step ${nextStep}.${
            capturedToken ? ' Captured opponent!' : ''
          }${extraRollAwarded ? ' Bonus roll!' : ''}`,
          ...ludoState.logs,
        ],
      },
    });
  };

  // Bot automated turn runner for Ludo
  useEffect(() => {
    if (!ludoState || !currentRoom || ludoState.matchFinished) return;
    const currentTurnUser = currentRoom.players.find((p) => p.id === ludoState.currentTurnPlayerId);
    if (!currentTurnUser || !currentTurnUser.isBot) return;

    if (ludoState.canRollDice) {
      const rollTimer = setTimeout(() => {
        rollLudoDice();
      }, 1000);
      return () => clearTimeout(rollTimer);
    }

    if (ludoState.hasRolledDice && ludoState.eligibleTokenIds.length > 0 && ludoState.diceRoll) {
      const moveTimer = setTimeout(() => {
        const currentColor = ludoState.colorOrder[ludoState.currentColorIndex];
        const bestToken = getBestBotLudoMove(ludoState.tokens, currentColor, ludoState.diceRoll!);
        if (bestToken !== null) {
          moveLudoToken(bestToken);
        }
      }, 1000);
      return () => clearTimeout(moveTimer);
    }
  }, [
    ludoState?.currentTurnPlayerId,
    ludoState?.canRollDice,
    ludoState?.hasRolledDice,
    ludoState?.eligibleTokenIds,
  ]);

  // ==================== LOTO / BINGO ACTIONS ====================

  const daubBingoNumber = (cardId: string, row: number, col: number) => {
    if (!lotoState) return;
    const cardIndex = lotoState.cards.findIndex((c) => c.id === cardId);
    if (cardIndex === -1) return;

    const card = lotoState.cards[cardIndex];
    const num = card.numbers[row][col];

    // Only allow daubing if number was called (or free space 0)
    if (num !== null && num !== 0 && !lotoState.calledNumbers.includes(num)) {
      return;
    }

    const newDaubed = card.daubed.map((r, rIdx) =>
      r.map((val, cIdx) => (rIdx === row && cIdx === col ? true : val))
    );

    const updatedCards = [...lotoState.cards];
    updatedCards[cardIndex] = { ...card, daubed: newDaubed };

    gameAudio.playTokenStep();

    broadcastGameUpdate({
      loto: {
        ...lotoState,
        cards: updatedCards,
      },
    });
  };

  const claimBingoWin = (cardId: string, pattern: BingoPattern) => {
    if (!lotoState || !currentRoom) return;
    const card = lotoState.cards.find((c) => c.id === cardId);
    if (!card) return;

    const check = checkBingoPattern(card, pattern);
    if (!check.satisfied) {
      return;
    }

    gameAudio.playBingoFanfare();
    confetti({ particleCount: 120, spread: 90, origin: { y: 0.5 } });

    const prize = pattern === 'full_house' ? 250 : pattern === 'corners' ? 100 : 50;
    const claim = {
      playerId: activeDemoUser.id,
      playerName: activeDemoUser.displayName,
      pattern,
      prizeAmount: prize,
      cardId,
      timestamp: new Date().toLocaleTimeString(),
    };

    const isGameOver = pattern === 'full_house';

    broadcastGameUpdate({
      loto: {
        ...lotoState,
        claims: [...lotoState.claims, claim],
        isGameOver,
        winnerIds: isGameOver ? [...lotoState.winnerIds, activeDemoUser.id] : lotoState.winnerIds,
        logs: [`🎉 BINGO CLAIM! ${activeDemoUser.displayName} achieved ${pattern}! (+${prize} coins)`, ...lotoState.logs],
      },
    });
  };

  const nextBingoBall = () => {
    if (!lotoState || lotoState.isGameOver) return;
    const remaining = [];
    for (let i = 1; i <= 75; i++) {
      if (!lotoState.calledNumbers.includes(i)) remaining.push(i);
    }
    if (remaining.length === 0) return;

    const ball = remaining[Math.floor(Math.random() * remaining.length)];
    gameAudio.playBingoBall();

    // Auto-daub for cards if enabled
    let updatedCards = lotoState.cards;
    if (lotoState.autoDaub) {
      updatedCards = lotoState.cards.map((c) => ({
        ...c,
        daubed: c.numbers.map((r, rIdx) =>
          r.map((num, cIdx) => (num === ball ? true : c.daubed[rIdx][cIdx]))
        ),
      }));
    }

    broadcastGameUpdate({
      loto: {
        ...lotoState,
        cards: updatedCards,
        calledNumbers: [...lotoState.calledNumbers, ball],
        currentBall: ball,
        logs: [`Ball called: ${ball}`, ...lotoState.logs],
      },
    });
  };

  const toggleBingoAutoDraw = () => {
    if (!lotoState) return;
    broadcastGameUpdate({
      loto: {
        ...lotoState,
        isDrawing: !lotoState.isDrawing,
      },
    });
  };

  const toggleAutoDaub = () => {
    if (!lotoState) return;
    broadcastGameUpdate({
      loto: {
        ...lotoState,
        autoDaub: !lotoState.autoDaub,
      },
    });
  };

  // Automated Bingo Drum loop when isDrawing is true
  useEffect(() => {
    if (!lotoState || !lotoState.isDrawing || lotoState.isGameOver) return;
    const interval = setInterval(() => {
      nextBingoBall();
    }, lotoState.drawSpeedSeconds * 1000);
    return () => clearInterval(interval);
  }, [lotoState?.isDrawing, lotoState?.calledNumbers.length, lotoState?.isGameOver]);

  // ==================== FARITANY ACTIONS ====================

  const deployFaritanyTroops = (territoryId: string, count: number = 1) => {
    if (!faritanyState) return;
    const terr = faritanyState.territories[territoryId];
    if (!terr || terr.ownerId !== faritanyState.currentTurnPlayerId || faritanyState.reinforcementsAvailable < count) {
      return;
    }

    gameAudio.playTokenStep();

    const updatedTerritories = {
      ...faritanyState.territories,
      [territoryId]: {
        ...terr,
        troops: terr.troops + count,
      },
    };

    const remainingReinforcements = faritanyState.reinforcementsAvailable - count;

    broadcastGameUpdate({
      faritany: {
        ...faritanyState,
        territories: updatedTerritories,
        reinforcementsAvailable: remainingReinforcements,
        phase: remainingReinforcements === 0 ? 'attack' : 'deploy',
        logs: [`Deployed ${count} troops to ${terr.name}.`, ...faritanyState.logs],
      },
    });
  };

  const attackFaritany = (sourceId: string, targetId: string, troops: number = 2) => {
    if (!faritanyState) return;
    const source = faritanyState.territories[sourceId];
    const target = faritanyState.territories[targetId];

    if (!source || !target || source.ownerId !== faritanyState.currentTurnPlayerId || target.ownerId === source.ownerId) {
      return;
    }

    if (source.troops <= 1) return;

    gameAudio.playBattleClash();

    const report = resolveFaritanyBattle(source, target, troops);

    let updatedTerritories = { ...faritanyState.territories };

    if (report.conquered) {
      gameAudio.playVictory();
      confetti({ particleCount: 50, spread: 60 });
      updatedTerritories[targetId] = {
        ...target,
        ownerId: source.ownerId,
        troops: Math.max(1, troops - report.attackerLosses),
      };
      updatedTerritories[sourceId] = {
        ...source,
        troops: source.troops - troops,
      };
    } else {
      updatedTerritories[targetId] = {
        ...target,
        troops: Math.max(1, target.troops - report.defenderLosses),
      };
      updatedTerritories[sourceId] = {
        ...source,
        troops: Math.max(1, source.troops - report.attackerLosses),
      };
    }

    // Check winner
    const owners = new Set(Object.values(updatedTerritories).map((t) => t.ownerId).filter(Boolean));
    const winnerId = owners.size === 1 ? Array.from(owners)[0] as string : null;

    broadcastGameUpdate({
      faritany: {
        ...faritanyState,
        territories: updatedTerritories,
        lastBattleReport: report,
        winnerId,
        logs: [
          `Attacked ${target.name} from ${source.name}.${report.conquered ? ' CONQUERED!' : ''}`,
          ...faritanyState.logs,
        ],
      },
    });
  };

  const fortifyFaritany = (sourceId: string, targetId: string, count: number = 1) => {
    if (!faritanyState) return;
    const source = faritanyState.territories[sourceId];
    const target = faritanyState.territories[targetId];

    if (!source || !target || source.ownerId !== target.ownerId || source.troops <= count) {
      return;
    }

    gameAudio.playTokenStep();

    const updatedTerritories = {
      ...faritanyState.territories,
      [sourceId]: { ...source, troops: source.troops - count },
      [targetId]: { ...target, troops: target.troops + count },
    };

    endFaritanyPhase();

    broadcastGameUpdate({
      faritany: {
        ...faritanyState,
        territories: updatedTerritories,
        logs: [`Fortified ${count} troops from ${source.name} to ${target.name}.`, ...faritanyState.logs],
      },
    });
  };

  const endFaritanyPhase = () => {
    if (!faritanyState) return;

    if (faritanyState.phase === 'reinforce') {
      broadcastGameUpdate({ faritany: { ...faritanyState, phase: 'deploy' } });
    } else if (faritanyState.phase === 'deploy') {
      broadcastGameUpdate({ faritany: { ...faritanyState, phase: 'attack' } });
    } else if (faritanyState.phase === 'attack') {
      broadcastGameUpdate({ faritany: { ...faritanyState, phase: 'fortify' } });
    } else if (faritanyState.phase === 'fortify') {
      // Advance to next player turn
      const nextIdx = (faritanyState.currentTurnIndex + 1) % faritanyState.playerOrder.length;
      const nextPlayerId = faritanyState.playerOrder[nextIdx];
      const newIncome = calculateFaritanyIncome(nextPlayerId, faritanyState.territories);

      broadcastGameUpdate({
        faritany: {
          ...faritanyState,
          currentTurnIndex: nextIdx,
          currentTurnPlayerId: nextPlayerId,
          phase: 'deploy',
          turnNumber: faritanyState.turnNumber + 1,
          reinforcementsAvailable: newIncome,
          logs: [`Turn ${faritanyState.turnNumber + 1}: ${nextPlayerId} to reinforce (+${newIncome} troops).`, ...faritanyState.logs],
        },
      });
    }
  };

  // Bot automated turn runner for Faritany
  useEffect(() => {
    if (!faritanyState || !currentRoom || faritanyState.winnerId) return;
    const currentTurnUser = currentRoom.players.find((p) => p.id === faritanyState.currentTurnPlayerId);
    if (!currentTurnUser || !currentTurnUser.isBot) return;

    const timer = setTimeout(() => {
      const botUpdates = executeBotFaritanyTurn(faritanyState, faritanyState.currentTurnPlayerId);
      const nextIdx = (faritanyState.currentTurnIndex + 1) % faritanyState.playerOrder.length;
      const nextPlayerId = faritanyState.playerOrder[nextIdx];
      const newIncome = calculateFaritanyIncome(nextPlayerId, (botUpdates.territories as any) || faritanyState.territories);

      broadcastGameUpdate({
        faritany: {
          ...faritanyState,
          ...botUpdates,
          currentTurnIndex: nextIdx,
          currentTurnPlayerId: nextPlayerId,
          phase: 'deploy',
          turnNumber: faritanyState.turnNumber + 1,
          reinforcementsAvailable: newIncome,
        },
      });
    }, 1500);

    return () => clearTimeout(timer);
  }, [faritanyState?.currentTurnPlayerId]);

  // ==================== ADMIN & LEDGER ====================

  const adminGrantCoins = async (userId: string, amount: number, reason: string = 'Admin test grant') => {
    try {
      await fetch('/api/admin/coins', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, amount, reason }),
      });
      gameAudio.playCoin();
    } catch {
      // Fallback
    }
  };

  const adminCloseRoom = (roomId: string) => {
    if (currentRoom?.id === roomId) {
      leaveRoom();
    }
    setPublicRooms((prev) => prev.filter((r) => r.id !== roomId));
  };

  return (
    <GamesContext.Provider
      value={{
        activeDemoUser,
        setActiveDemoUser,
        publicRooms,
        currentRoom,
        isMuted,
        setIsMuted,
        dominoState,
        ludoState,
        lotoState,
        faritanyState,
        createRoom,
        joinRoom,
        leaveRoom,
        quickPlay,
        playWithBots,
        toggleReady,
        addBot,
        kickPlayer,
        startGame,
        rematch,
        resetMatch,
        sendChatMessage,
        playDominoTile,
        drawDominoBoneyard,
        passDominoTurn,
        rollLudoDice,
        moveLudoToken,
        daubBingoNumber,
        claimBingoWin,
        nextBingoBall,
        toggleBingoAutoDraw,
        toggleAutoDaub,
        deployFaritanyTroops,
        attackFaritany,
        fortifyFaritany,
        endFaritanyPhase,
        adminGrantCoins,
        adminCloseRoom,
      }}
    >
      {children}
    </GamesContext.Provider>
  );
};

export const useGames = () => {
  const context = useContext(GamesContext);
  if (!context) {
    throw new Error('useGames must be used within a GamesProvider');
  }
  return context;
};
