export type GameType = 'domino' | 'ludo' | 'bingo' | 'faritany';

export type RoomStatus = 'waiting' | 'in_progress' | 'finished';

export interface GamePlayer {
  id: string;
  name: string;
  username: string;
  avatarUrl: string;
  isBot: boolean;
  isReady: boolean;
  isHost: boolean;
  seatIndex: number; // 0, 1, 2, 3
  color: string; // Hex color or name (e.g. blue, red, green, yellow)
  score: number;
  coinBalance: number;
  isConnected: boolean;
}

export interface GameChatMsg {
  id: string;
  senderId: string;
  senderName: string;
  senderAvatar: string;
  text: string;
  timestamp: string;
  isSystem?: boolean;
}

export interface BaseRoomSettings {
  maxPlayers: number;
  entryFee: number;
  isPrivate: boolean;
  privateCode?: string;
  turnTimeLimitSeconds: number;
  allowBots: boolean;
}

export interface DominoRoomSettings extends BaseRoomSettings {
  targetScore: 50 | 100 | 120 | 150;
  maxRounds?: number;
}

export interface LudoRoomSettings extends BaseRoomSettings {
  fastMode: boolean;
  piecesPerPlayer: 2 | 4;
}

export interface BingoRoomSettings extends BaseRoomSettings {
  cardCost: number;
  maxCardsPerPlayer: number;
  drawIntervalMs: number;
  autoDaubDefault: boolean;
}

export interface FaritanyRoomSettings extends BaseRoomSettings {
  mapType: 'island' | 'continent';
  roundLimit: number;
  victoryPercentage: number;
}

export type RoomSettings =
  | ({ gameType: 'domino' } & DominoRoomSettings)
  | ({ gameType: 'ludo' } & LudoRoomSettings)
  | ({ gameType: 'bingo' } & BingoRoomSettings)
  | ({ gameType: 'faritany' } & FaritanyRoomSettings);

// ==================== DOMINO TYPES ====================
export type DominoTile = [number, number]; // e.g. [6, 6], [0, 4]

export interface PlacedDominoTile {
  id: string;
  tile: DominoTile;
  placedBy: string; // playerId
  endConnected: 'left' | 'right' | 'start';
  orientation: 'horizontal' | 'vertical';
  rotation: number;
  displayLeftVal: number;
  displayRightVal: number;
}

export interface DominoGameState {
  boneyard: DominoTile[];
  playerHands: Record<string, DominoTile[]>; // playerId -> tiles
  placedChain: PlacedDominoTile[];
  openLeft: number | null;
  openRight: number | null;
  currentTurnPlayerId: string;
  turnDeadline: number; // timestamp
  roundNumber: number;
  roundScores: Record<string, number>; // cumulative match score
  lastActionSummary: string;
  isRoundOver: boolean;
  roundWinnerId: string | null;
  roundWinReason?: string;
  matchWinnerId: string | null;
}

// ==================== LUDO TYPES ====================
export interface LudoPiece {
  id: number; // 0, 1, 2, 3
  playerId: string;
  stepIndex: number; // -1 = yard/homebase, 0..51 = track, 52..57 = home corridor, 58 = finished/home
  isFinished: boolean;
}

export interface LudoGameState {
  pieces: Record<string, LudoPiece[]>; // playerId -> 4 pieces
  currentTurnPlayerId: string;
  currentDiceValue: number | null;
  canRoll: boolean;
  mustMovePieceIds: number[];
  consecutiveSixes: number;
  turnDeadline: number;
  rankings: string[]; // playerIds in order of completion
  matchWinnerId: string | null;
  lastActionSummary: string;
}

// ==================== BINGO / LOTO TYPES ====================
export type BingoGrid = (number | null)[][]; // 5x5 grid, null = free center space (row 2, col 2)

export interface BingoCard {
  id: string;
  playerId: string;
  grid: BingoGrid;
  marked: boolean[][]; // 5x5 booleans
  hasCompletedLine: boolean;
  hasBingo: boolean;
}

export interface BingoGameState {
  drawnNumbers: number[];
  currentDrawnNumber: number | null;
  isDrawing: boolean;
  cards: BingoCard[];
  winningLinePlayerIds: string[];
  bingoWinnerId: string | null;
  prizePool: number;
  linePrize: number;
  bingoPrize: number;
  turnDeadline: number;
  autoDaub: Record<string, boolean>; // playerId -> boolean
  lastActionSummary: string;
}

// ==================== FARITANY TYPES ====================
export interface Territory {
  id: string;
  name: string;
  code: string;
  region: string;
  polygon: string; // SVG path or center coordinates
  center: [number, number]; // [x, y] for label & troop count
  adjacentIds: string[];
  ownerId: string | null; // null = neutral
  troops: number;
  goldProduction: number;
  defenseBonus: number;
}

export type FaritanyPhase = 'harvest' | 'reinforce' | 'attack' | 'fortify';

export interface FaritanyBattleLog {
  id: string;
  attackerId: string;
  defenderId: string | null;
  fromTerritory: string;
  toTerritory: string;
  attackerDice: number[];
  defenderDice: number[];
  attackerLosses: number;
  defenderLosses: number;
  conquered: boolean;
}

export interface FaritanyGameState {
  territories: Record<string, Territory>;
  playerResources: Record<string, { gold: number; energy: number; reinforcedThisTurn: number }>;
  currentTurnPlayerId: string;
  currentPhase: FaritanyPhase;
  turnNumber: number;
  maxTurns: number;
  selectedTerritoryId: string | null;
  targetTerritoryId: string | null;
  battleLog: FaritanyBattleLog[];
  turnDeadline: number;
  matchWinnerId: string | null;
  lastActionSummary: string;
}

// ==================== ROOM & STORE TYPES ====================
export interface GameRoomDetailed {
  id: string;
  code: string;
  title: string;
  gameType: GameType;
  status: RoomStatus;
  hostId: string;
  players: GamePlayer[];
  settings: RoomSettings;
  createdAt: number;
  startedAt?: number;
  finishedAt?: number;
  chatMessages: GameChatMsg[];
  dominoState?: DominoGameState;
  ludoState?: LudoGameState;
  bingoState?: BingoGameState;
  faritanyState?: FaritanyGameState;
  rematchVotes: string[]; // playerIds that voted for rematch
}

export interface GameHistoryEntry {
  id: string;
  roomId: string;
  roomCode: string;
  gameType: GameType;
  playedAt: string;
  durationSeconds: number;
  players: {
    id: string;
    name: string;
    avatarUrl: string;
    score: number;
    isWinner: boolean;
    coinsWon: number;
  }[];
  winnerName: string;
  prizePool: number;
}

export interface AdminSystemStats {
  activeRoomsCount: number;
  activePlayersCount: number;
  totalGamesPlayed: number;
  totalCoinsWagered: number;
  disabledGames: GameType[];
  turnTimeScale: number;
}
