import {
  AdminSystemStats,
  BingoGameState,
  DominoGameState,
  FaritanyGameState,
  GameChatMsg,
  GameHistoryEntry,
  GamePlayer,
  GameRoomDetailed,
  GameType,
  LudoGameState,
  RoomSettings,
} from './types';
import {
  drawFromBoneyard,
  getDominoBotMove,
  initializeDominoGame,
  passTurn,
  playDominoTile,
  startNextDominoRound,
} from './domino/dominoEngine';
import {
  getLudoBotAction,
  initializeLudoGame,
  moveLudoPiece,
  rollLudoDice,
} from './ludo/ludoEngine';
import {
  daubCardCell,
  drawNextBingoNumber,
  initializeBingoGame,
} from './bingo/bingoEngine';
import {
  advanceFaritanyPhase,
  deployFaritanyTroops,
  executeFaritanyAttack,
  getFaritanyBotAction,
  initializeFaritanyGame,
} from './faritany/faritanyEngine';
import { sounds } from './audio';

// Demo Test Accounts available for instant seat switching and multi-seat testing
export const DEMO_TEST_PLAYERS: GamePlayer[] = [
  {
    id: 'usr_me',
    name: 'Alex Rivers',
    username: 'alex_tata',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
    isBot: false,
    isReady: true,
    isHost: true,
    seatIndex: 0,
    color: '#1E9EF5', // Electric Blue
    score: 0,
    coinBalance: 10000,
    isConnected: true,
  },
  {
    id: 'usr_1',
    name: 'Sophia Chen',
    username: 'sophia.chen',
    avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80',
    isBot: false,
    isReady: true,
    isHost: false,
    seatIndex: 1,
    color: '#EF4444', // Crimson Red
    score: 0,
    coinBalance: 10000,
    isConnected: true,
  },
  {
    id: 'usr_2',
    name: 'Marcus Vance',
    username: 'marcus_dev',
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80',
    isBot: false,
    isReady: true,
    isHost: false,
    seatIndex: 2,
    color: '#10B981', // Emerald Green
    score: 0,
    coinBalance: 10000,
    isConnected: true,
  },
  {
    id: 'usr_3',
    name: 'Elena Rostova',
    username: 'elena_art',
    avatarUrl: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
    isBot: false,
    isReady: true,
    isHost: false,
    seatIndex: 3,
    color: '#F59E0B', // Amber Yellow
    score: 0,
    coinBalance: 10000,
    isConnected: true,
  },
];

export const BOT_PLAYERS: GamePlayer[] = [
  {
    id: 'bot_alpha',
    name: 'TATA AlphaBot',
    username: 'tata.alphabot',
    avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=AlphaBot',
    isBot: true,
    isReady: true,
    isHost: false,
    seatIndex: 1,
    color: '#EF4444',
    score: 0,
    coinBalance: 50000,
    isConnected: true,
  },
  {
    id: 'bot_cyber',
    name: 'TATA CyberBot',
    username: 'tata.cyberbot',
    avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=CyberBot',
    isBot: true,
    isReady: true,
    isHost: false,
    seatIndex: 2,
    color: '#10B981',
    score: 0,
    coinBalance: 50000,
    isConnected: true,
  },
  {
    id: 'bot_nexus',
    name: 'TATA NexusBot',
    username: 'tata.nexusbot',
    avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=NexusBot',
    isBot: true,
    isReady: true,
    isHost: false,
    seatIndex: 3,
    color: '#F59E0B',
    score: 0,
    coinBalance: 50000,
    isConnected: true,
  },
];

const ROOMS_STORAGE_KEY = 'tata_games_active_rooms';
const HISTORY_STORAGE_KEY = 'tata_games_history_records';

export class GameManager {
  private rooms: Record<string, GameRoomDetailed> = {};
  private activeRoomId: string | null = null;
  private currentActivePlayerId: string = 'usr_me'; // local test seat switcher
  private gameHistory: GameHistoryEntry[] = [];
  private listeners: Set<() => void> = new Set();
  private botTimer: ReturnType<typeof setInterval> | null = null;
  private channel: BroadcastChannel | null = null;
  private adminStats: AdminSystemStats = {
    activeRoomsCount: 0,
    activePlayersCount: 0,
    totalGamesPlayed: 0,
    totalCoinsWagered: 0,
    disabledGames: [],
    turnTimeScale: 1.0,
  };

  constructor() {
    this.loadFromStorage();
    if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
      try {
        this.channel = new BroadcastChannel('tata_games_sync_bus');
        this.channel.onmessage = (event) => {
          if (event.data?.type === 'SYNC_ROOMS') {
            this.rooms = event.data.rooms;
            this.notify();
          }
        };
      } catch {
        // BroadcastChannel fallback
      }
    }
    this.startBotLoop();
  }

  private loadFromStorage() {
    try {
      const savedRooms = localStorage.getItem(ROOMS_STORAGE_KEY);
      if (savedRooms) {
        this.rooms = JSON.parse(savedRooms);
      }
      const savedHist = localStorage.getItem(HISTORY_STORAGE_KEY);
      if (savedHist) {
        this.gameHistory = JSON.parse(savedHist);
      }
    } catch {
      // ignore
    }
  }

  private saveToStorage() {
    try {
      localStorage.setItem(ROOMS_STORAGE_KEY, JSON.stringify(this.rooms));
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(this.gameHistory));
      if (this.channel) {
        this.channel.postMessage({ type: 'SYNC_ROOMS', rooms: this.rooms });
      }
    } catch {
      // ignore
    }
  }

  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach((l) => l());
  }

  // Active user / test viewpoint switcher
  public setCurrentActivePlayerId(playerId: string) {
    this.currentActivePlayerId = playerId;
    this.notify();
  }

  public getCurrentActivePlayerId(): string {
    return this.currentActivePlayerId;
  }

  public getActiveRoom(): GameRoomDetailed | null {
    if (!this.activeRoomId || !this.rooms[this.activeRoomId]) return null;
    return this.rooms[this.activeRoomId];
  }

  public getAllRooms(): GameRoomDetailed[] {
    return Object.values(this.rooms);
  }

  public getGameHistory(): GameHistoryEntry[] {
    return this.gameHistory;
  }

  public getAdminStats(): AdminSystemStats {
    const all = Object.values(this.rooms);
    return {
      activeRoomsCount: all.length,
      activePlayersCount: all.reduce((sum, r) => sum + r.players.length, 0),
      totalGamesPlayed: this.gameHistory.length,
      totalCoinsWagered: this.gameHistory.reduce((sum, h) => sum + h.prizePool, 0),
      disabledGames: this.adminStats.disabledGames,
      turnTimeScale: this.adminStats.turnTimeScale,
    };
  }

  // ==================== ROOM CREATION & LOBBY ====================
  public createRoom(
    gameType: GameType,
    title: string,
    settingsPartial: Partial<RoomSettings>,
    hostPlayer: GamePlayer = DEMO_TEST_PLAYERS[0]
  ): GameRoomDetailed {
    const code = `TATA-${gameType.substring(0, 3).toUpperCase()}-${Math.floor(100 + Math.random() * 900)}`;
    const id = `room_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;

    let defaultSettings: RoomSettings;
    if (gameType === 'domino') {
      defaultSettings = {
        gameType: 'domino',
        maxPlayers: 2,
        entryFee: 100,
        isPrivate: false,
        turnTimeLimitSeconds: 25,
        allowBots: true,
        targetScore: 100,
        ...(settingsPartial as any),
      };
    } else if (gameType === 'ludo') {
      defaultSettings = {
        gameType: 'ludo',
        maxPlayers: 4,
        entryFee: 150,
        isPrivate: false,
        turnTimeLimitSeconds: 20,
        allowBots: true,
        fastMode: false,
        piecesPerPlayer: 4,
        ...(settingsPartial as any),
      };
    } else if (gameType === 'bingo') {
      defaultSettings = {
        gameType: 'bingo',
        maxPlayers: 4,
        entryFee: 50,
        isPrivate: false,
        turnTimeLimitSeconds: 5,
        allowBots: true,
        cardCost: 50,
        maxCardsPerPlayer: 2,
        drawIntervalMs: 3000,
        autoDaubDefault: true,
        ...(settingsPartial as any),
      };
    } else {
      defaultSettings = {
        gameType: 'faritany',
        maxPlayers: 4,
        entryFee: 200,
        isPrivate: false,
        turnTimeLimitSeconds: 35,
        allowBots: true,
        mapType: 'island',
        roundLimit: 25,
        victoryPercentage: 65,
        ...(settingsPartial as any),
      };
    }

    const initialHost: GamePlayer = {
      ...hostPlayer,
      isHost: true,
      isReady: true,
      seatIndex: 0,
      color: '#1E9EF5',
    };

    const room: GameRoomDetailed = {
      id,
      code,
      title: title || `${gameType.toUpperCase()} Arena #${code.split('-')[2]}`,
      gameType,
      status: 'waiting',
      hostId: initialHost.id,
      players: [initialHost],
      settings: defaultSettings,
      createdAt: Date.now(),
      chatMessages: [
        {
          id: `msg_${Date.now()}`,
          senderId: 'system',
          senderName: 'TATA Arbiter',
          senderAvatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=TataArbiter',
          text: `Welcome to ${gameType.toUpperCase()}! Ready up to start.`,
          timestamp: 'Just now',
          isSystem: true,
        },
      ],
      rematchVotes: [],
    };

    this.rooms[id] = room;
    this.activeRoomId = id;
    this.saveToStorage();
    this.notify();
    sounds.playClick();
    return room;
  }

  // Quick Play Helper: creates room and fills with bots/demo players immediately
  public startQuickPlay(gameType: GameType, fillWithBots: boolean = true): GameRoomDetailed {
    const room = this.createRoom(
      gameType,
      `⚡ Quick Play ${gameType.toUpperCase()}`,
      { maxPlayers: gameType === 'domino' ? 2 : 4, allowBots: true },
      DEMO_TEST_PLAYERS[0]
    );

    const needed = (room.settings.maxPlayers || 2) - 1;
    for (let i = 0; i < needed; i++) {
      if (fillWithBots) {
        const bot = { ...BOT_PLAYERS[i % BOT_PLAYERS.length], seatIndex: i + 1, isReady: true };
        room.players.push(bot);
      } else {
        const demo = { ...DEMO_TEST_PLAYERS[(i + 1) % DEMO_TEST_PLAYERS.length], seatIndex: i + 1, isReady: true };
        room.players.push(demo);
      }
    }

    this.startGame(room.id);
    return room;
  }

  public joinRoomByCode(code: string, player: GamePlayer = DEMO_TEST_PLAYERS[1]): boolean {
    const cleanCode = code.trim().toUpperCase();
    const room = Object.values(this.rooms).find((r) => r.code === cleanCode);
    if (!room) return false;

    if (room.players.some((p) => p.id === player.id)) {
      this.activeRoomId = room.id;
      this.notify();
      return true;
    }

    if (room.players.length >= room.settings.maxPlayers) {
      return false;
    }

    const nextSeat = room.players.length;
    const colors = ['#1E9EF5', '#EF4444', '#10B981', '#F59E0B'];
    const newPlayer: GamePlayer = {
      ...player,
      seatIndex: nextSeat,
      color: colors[nextSeat % colors.length],
      isHost: false,
      isReady: true,
    };

    room.players.push(newPlayer);
    this.activeRoomId = room.id;
    this.saveToStorage();
    this.notify();
    sounds.playClick();
    return true;
  }

  public addBotToRoom(roomId: string): boolean {
    const room = this.rooms[roomId];
    if (!room || room.players.length >= room.settings.maxPlayers) return false;

    const usedBotIds = new Set(room.players.filter((p) => p.isBot).map((p) => p.id));
    const availableBot = BOT_PLAYERS.find((b) => !usedBotIds.has(b.id)) || BOT_PLAYERS[0];

    const nextSeat = room.players.length;
    const colors = ['#1E9EF5', '#EF4444', '#10B981', '#F59E0B'];
    const botPlayer: GamePlayer = {
      ...availableBot,
      id: `${availableBot.id}_${Date.now()}`,
      seatIndex: nextSeat,
      color: colors[nextSeat % colors.length],
      isHost: false,
      isReady: true,
    };

    room.players.push(botPlayer);
    this.saveToStorage();
    this.notify();
    sounds.playClick();
    return true;
  }

  public removePlayer(roomId: string, playerId: string) {
    const room = this.rooms[roomId];
    if (!room) return;

    room.players = room.players.filter((p) => p.id !== playerId);
    if (room.players.length === 0) {
      delete this.rooms[roomId];
      if (this.activeRoomId === roomId) this.activeRoomId = null;
    } else {
      if (room.hostId === playerId) {
        room.hostId = room.players[0].id;
        room.players[0].isHost = true;
      }
    }
    this.saveToStorage();
    this.notify();
  }

  public toggleReady(roomId: string, playerId: string) {
    const room = this.rooms[roomId];
    if (!room) return;
    const p = room.players.find((x) => x.id === playerId);
    if (p) {
      p.isReady = !p.isReady;
      this.saveToStorage();
      this.notify();
      sounds.playClick();
    }
  }

  public setActiveRoom(roomId: string | null) {
    this.activeRoomId = roomId;
    this.notify();
  }

  public sendChatMessage(roomId: string, text: string, sender: GamePlayer) {
    const room = this.rooms[roomId];
    if (!room || !text.trim()) return;

    const msg: GameChatMsg = {
      id: `msg_${Date.now()}`,
      senderId: sender.id,
      senderName: sender.name,
      senderAvatar: sender.avatarUrl,
      text: text.trim(),
      timestamp: 'Just now',
    };

    room.chatMessages.push(msg);
    if (room.chatMessages.length > 50) room.chatMessages.shift();
    this.saveToStorage();
    this.notify();
    sounds.playClick();
  }

  // ==================== START GAME ENGINE ====================
  public startGame(roomId: string) {
    const room = this.rooms[roomId];
    if (!room) return;

    const playerIds = room.players.map((p) => p.id);
    room.status = 'in_progress';
    room.startedAt = Date.now();
    room.rematchVotes = [];

    if (room.gameType === 'domino') {
      const targetScore = (room.settings as any).targetScore || 100;
      room.dominoState = initializeDominoGame(playerIds, targetScore);
    } else if (room.gameType === 'ludo') {
      const pieces = (room.settings as any).piecesPerPlayer || 4;
      room.ludoState = initializeLudoGame(playerIds, pieces);
    } else if (room.gameType === 'bingo') {
      const cardCost = (room.settings as any).cardCost || 50;
      room.bingoState = initializeBingoGame(playerIds, 2, cardCost);
    } else if (room.gameType === 'faritany') {
      room.faritanyState = initializeFaritanyGame(playerIds);
    }

    this.saveToStorage();
    this.notify();
    sounds.playWin();
  }

  // ==================== DOMINO ACTIONS ====================
  public dominoPlayTile(roomId: string, playerId: string, tileIndex: number, side: 'left' | 'right' | 'start') {
    const room = this.rooms[roomId];
    if (!room || !room.dominoState) return;

    const playerIds = room.players.map((p) => p.id);
    const targetScore = (room.settings as any).targetScore || 100;
    room.dominoState = playDominoTile(room.dominoState, playerId, tileIndex, side, playerIds, targetScore);

    sounds.playTileSnap();
    this.checkDominoFinished(room);
    this.saveToStorage();
    this.notify();
  }

  public dominoDraw(roomId: string, playerId: string) {
    const room = this.rooms[roomId];
    if (!room || !room.dominoState) return;

    const playerIds = room.players.map((p) => p.id);
    room.dominoState = drawFromBoneyard(room.dominoState, playerId, playerIds);

    sounds.playClick();
    this.saveToStorage();
    this.notify();
  }

  public dominoPass(roomId: string, playerId: string) {
    const room = this.rooms[roomId];
    if (!room || !room.dominoState) return;

    const playerIds = room.players.map((p) => p.id);
    room.dominoState = passTurn(room.dominoState, playerId, playerIds);

    sounds.playClick();
    this.saveToStorage();
    this.notify();
  }

  public dominoNextRound(roomId: string) {
    const room = this.rooms[roomId];
    if (!room || !room.dominoState) return;

    const playerIds = room.players.map((p) => p.id);
    const targetScore = (room.settings as any).targetScore || 100;
    room.dominoState = startNextDominoRound(room.dominoState, playerIds, targetScore);

    this.saveToStorage();
    this.notify();
    sounds.playClick();
  }

  private checkDominoFinished(room: GameRoomDetailed) {
    if (room.dominoState?.matchWinnerId) {
      room.status = 'finished';
      room.finishedAt = Date.now();
      this.recordMatchResult(room, room.dominoState.matchWinnerId);
    }
  }

  // ==================== LUDO ACTIONS ====================
  public ludoRoll(roomId: string, playerId: string) {
    const room = this.rooms[roomId];
    if (!room || !room.ludoState) return;

    const playerIds = room.players.map((p) => p.id);
    room.ludoState = rollLudoDice(room.ludoState, playerId, playerIds);

    sounds.playDiceRoll();
    this.saveToStorage();
    this.notify();
  }

  public ludoMove(roomId: string, playerId: string, pieceId: number) {
    const room = this.rooms[roomId];
    if (!room || !room.ludoState) return;

    const playerIds = room.players.map((p) => p.id);
    room.ludoState = moveLudoPiece(room.ludoState, playerId, pieceId, playerIds);

    sounds.playClick();
    if (room.ludoState.matchWinnerId) {
      room.status = 'finished';
      room.finishedAt = Date.now();
      this.recordMatchResult(room, room.ludoState.matchWinnerId);
    }
    this.saveToStorage();
    this.notify();
  }

  // ==================== BINGO ACTIONS ====================
  public bingoDrawNumber(roomId: string) {
    const room = this.rooms[roomId];
    if (!room || !room.bingoState) return;

    room.bingoState = drawNextBingoNumber(room.bingoState);
    sounds.playBallPop();

    if (room.bingoState.bingoWinnerId) {
      room.status = 'finished';
      room.finishedAt = Date.now();
      this.recordMatchResult(room, room.bingoState.bingoWinnerId);
    }
    this.saveToStorage();
    this.notify();
  }

  public bingoDaub(roomId: string, cardId: string, row: number, col: number) {
    const room = this.rooms[roomId];
    if (!room || !room.bingoState) return;

    room.bingoState = daubCardCell(room.bingoState, cardId, row, col);
    sounds.playClick();

    if (room.bingoState.bingoWinnerId) {
      room.status = 'finished';
      room.finishedAt = Date.now();
      this.recordMatchResult(room, room.bingoState.bingoWinnerId);
    }
    this.saveToStorage();
    this.notify();
  }

  // ==================== FARITANY ACTIONS ====================
  public faritanyNextPhase(roomId: string, playerId: string) {
    const room = this.rooms[roomId];
    if (!room || !room.faritanyState) return;

    const playerIds = room.players.map((p) => p.id);
    room.faritanyState = advanceFaritanyPhase(room.faritanyState, playerId, playerIds);

    sounds.playClick();
    if (room.faritanyState.matchWinnerId) {
      room.status = 'finished';
      room.finishedAt = Date.now();
      this.recordMatchResult(room, room.faritanyState.matchWinnerId);
    }
    this.saveToStorage();
    this.notify();
  }

  public faritanyReinforce(roomId: string, playerId: string, territoryId: string, count: number) {
    const room = this.rooms[roomId];
    if (!room || !room.faritanyState) return;

    room.faritanyState = deployFaritanyTroops(room.faritanyState, playerId, territoryId, count);
    sounds.playClick();
    this.saveToStorage();
    this.notify();
  }

  public faritanyAttack(roomId: string, playerId: string, fromId: string, toId: string) {
    const room = this.rooms[roomId];
    if (!room || !room.faritanyState) return;

    room.faritanyState = executeFaritanyAttack(room.faritanyState, playerId, fromId, toId);
    sounds.playCapture();

    if (room.faritanyState.matchWinnerId) {
      room.status = 'finished';
      room.finishedAt = Date.now();
      this.recordMatchResult(room, room.faritanyState.matchWinnerId);
    }
    this.saveToStorage();
    this.notify();
  }

  // ==================== REMATCH & RESET ====================
  public voteRematch(roomId: string, playerId: string) {
    const room = this.rooms[roomId];
    if (!room) return;

    if (!room.rematchVotes.includes(playerId)) {
      room.rematchVotes.push(playerId);
    }

    if (room.rematchVotes.length >= Math.ceil(room.players.length / 2)) {
      // Trigger new match!
      this.startGame(roomId);
    } else {
      this.saveToStorage();
      this.notify();
    }
  }

  public resetMatch(roomId: string) {
    const room = this.rooms[roomId];
    if (!room) return;
    this.startGame(roomId);
  }

  // ==================== HISTORY & RECORDING ====================
  private recordMatchResult(room: GameRoomDetailed, winnerId: string) {
    const winner = room.players.find((p) => p.id === winnerId);
    const prize = room.players.length * (room.settings.entryFee || 100);

    const entry: GameHistoryEntry = {
      id: `hist_${Date.now()}`,
      roomId: room.id,
      roomCode: room.code,
      gameType: room.gameType,
      playedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      durationSeconds: room.startedAt ? Math.round((Date.now() - room.startedAt) / 1000) : 60,
      players: room.players.map((p) => ({
        id: p.id,
        name: p.name,
        avatarUrl: p.avatarUrl,
        score: p.score,
        isWinner: p.id === winnerId,
        coinsWon: p.id === winnerId ? prize : 0,
      })),
      winnerName: winner ? winner.name : 'Unknown',
      prizePool: prize,
    };

    this.gameHistory.unshift(entry);
    if (this.gameHistory.length > 50) this.gameHistory.pop();
    this.saveToStorage();
    sounds.playWin();
  }

  // ==================== BOT AUTOMATION LOOP ====================
  private startBotLoop() {
    if (this.botTimer) clearInterval(this.botTimer);

    this.botTimer = setInterval(() => {
      const room = this.getActiveRoom();
      if (!room || room.status !== 'in_progress') return;

      const playerIds = room.players.map((p) => p.id);

      // DOMINO BOT
      if (room.gameType === 'domino' && room.dominoState && !room.dominoState.isRoundOver) {
        const turnPid = room.dominoState.currentTurnPlayerId;
        const currentP = room.players.find((p) => p.id === turnPid);
        if (currentP?.isBot) {
          const move = getDominoBotMove(room.dominoState, turnPid, playerIds);
          if (move.action === 'play' && move.tileIndex !== undefined && move.side) {
            this.dominoPlayTile(room.id, turnPid, move.tileIndex, move.side);
          } else if (move.action === 'draw') {
            this.dominoDraw(room.id, turnPid);
          } else {
            this.dominoPass(room.id, turnPid);
          }
        }
      }

      // LUDO BOT
      if (room.gameType === 'ludo' && room.ludoState && !room.ludoState.matchWinnerId) {
        const turnPid = room.ludoState.currentTurnPlayerId;
        const currentP = room.players.find((p) => p.id === turnPid);
        if (currentP?.isBot) {
          const action = getLudoBotAction(room.ludoState, turnPid, playerIds);
          if (action.action === 'roll') {
            this.ludoRoll(room.id, turnPid);
          } else if (action.action === 'move' && action.pieceId !== undefined) {
            this.ludoMove(room.id, turnPid, action.pieceId);
          }
        }
      }

      // BINGO AUTOMATIC DRAW ENGINE
      if (room.gameType === 'bingo' && room.bingoState && room.bingoState.isDrawing) {
        if (Date.now() >= room.bingoState.turnDeadline) {
          this.bingoDrawNumber(room.id);
        }
      }

      // FARITANY BOT
      if (room.gameType === 'faritany' && room.faritanyState && !room.faritanyState.matchWinnerId) {
        const turnPid = room.faritanyState.currentTurnPlayerId;
        const currentP = room.players.find((p) => p.id === turnPid);
        if (currentP?.isBot) {
          const botAction = getFaritanyBotAction(room.faritanyState, turnPid, playerIds);
          if (botAction.type === 'phase') {
            this.faritanyNextPhase(room.id, turnPid);
          } else if (botAction.type === 'reinforce' && botAction.territoryId && botAction.count) {
            this.faritanyReinforce(room.id, turnPid, botAction.territoryId, botAction.count);
          } else if (botAction.type === 'attack' && botAction.fromId && botAction.toId) {
            this.faritanyAttack(room.id, turnPid, botAction.fromId, botAction.toId);
          }
        }
      }
    }, 1200);
  }
}

export const gameManager = new GameManager();
