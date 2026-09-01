export type GameType = 'domino' | 'ludo' | 'loto' | 'faritany';

export type RoomStatus = 'lobby' | 'playing' | 'finished';

export interface RoomPlayer {
  id: string;
  displayName: string;
  username: string;
  avatarUrl: string;
  isReady: boolean;
  isBot: boolean;
  isHost: boolean;
  color?: string;
  score: number;
  rank?: number;
  disconnected?: boolean;
}

export interface GameChatMessage {
  id: string;
  senderId: string;
  senderName: string;
  senderAvatar: string;
  text: string;
  timestamp: string;
  isSystem?: boolean;
}

export interface RoomSettings {
  targetScore?: number; // Domino (e.g. 50, 100, 150)
  maxPlayers: number;
  entryFee: number;
  turnTimeSeconds: number; // e.g. 20, 30, 45
  autoDaub?: boolean; // Loto/Bingo
  mapPreset?: string; // Faritany
  botDifficulty?: 'easy' | 'medium' | 'hard';
}

export interface GameRoom {
  id: string;
  code: string;
  title: string;
  gameType: GameType;
  isPrivate: boolean;
  hostId: string;
  maxPlayers: number;
  players: RoomPlayer[];
  status: RoomStatus;
  entryFee: number;
  prizePool: number;
  createdAt: string;
  winnerId?: string;
  winnerName?: string;
  settings: RoomSettings;
  chatMessages: GameChatMessage[];
}

// ==================== DOMINO TYPES ====================
export interface DominoTile {
  id: string;
  left: number;  // 0 to 6
  right: number; // 0 to 6
}

export interface PlacedDomino {
  tile: DominoTile;
  placedBy: string;
  position: 'left' | 'right' | 'start';
  orientation: 'horizontal' | 'vertical';
  flipped: boolean;
  renderLeft: number;
  renderRight: number;
}

export interface DominoGameState {
  boneyard: DominoTile[];
  playerHands: Record<string, DominoTile[]>;
  boardChain: PlacedDomino[];
  leftOpenPip: number | null;
  rightOpenPip: number | null;
  currentTurnPlayerId: string;
  turnTimeLeft: number;
  roundNumber: number;
  targetScore: number;
  scores: Record<string, number>;
  consecutivePasses: number;
  roundWinnerId?: string | null;
  roundSummary?: string;
  matchWinnerId?: string | null;
  logs: string[];
}

// ==================== LUDO TYPES ====================
export type LudoColor = 'red' | 'green' | 'yellow' | 'blue';

export interface LudoToken {
  id: number; // 0, 1, 2, 3
  color: LudoColor;
  playerId: string;
  // step:
  // -1: in home yard
  // 0..51: on track (relative to each color's track start)
  // 52..57: home column
  // 58: reached home center (finished)
  step: number;
  isFinished: boolean;
}

export interface LudoGameState {
  tokens: LudoToken[];
  colorOrder: LudoColor[];
  playerColors: Record<string, LudoColor>;
  currentColorIndex: number;
  currentTurnPlayerId: string;
  diceRoll: number | null;
  hasRolledDice: boolean;
  canRollDice: boolean;
  eligibleTokenIds: number[];
  extraTurn: boolean;
  consecutiveSixes: number;
  turnTimeLeft: number;
  winners: string[]; // Player IDs in order of 1st, 2nd, 3rd, 4th finish
  matchFinished: boolean;
  logs: string[];
}

// ==================== LOTO / BINGO TYPES ====================
export interface BingoCard {
  id: string;
  playerId: string;
  numbers: (number | null)[][]; // 5x5 grid with numbers 1..75 (middle is free = 0) or 3x9 grid
  daubed: boolean[][];
}

export type BingoPattern = 'line' | 'corners' | 'full_house';

export interface BingoWinClaim {
  playerId: string;
  playerName: string;
  pattern: BingoPattern;
  prizeAmount: number;
  cardId: string;
  timestamp: string;
}

export interface LotoGameState {
  cards: BingoCard[];
  calledNumbers: number[];
  currentBall: number | null;
  isDrawing: boolean;
  drawSpeedSeconds: number;
  autoDaub: boolean;
  roundHistory: number[];
  claims: BingoWinClaim[];
  isGameOver: boolean;
  winnerIds: string[];
  logs: string[];
}

// ==================== FARITANY STRATEGY TYPES ====================
export interface Territory {
  id: string;
  name: string;
  shortCode: string;
  region: 'North' | 'Central' | 'East' | 'West' | 'South';
  ownerId: string | null;
  troops: number;
  defenseBonus: number;
  incomeBonus: number;
  capital?: boolean;
  svgPath: string;
  centerX: number;
  centerY: number;
  adjacentIds: string[];
}

export type FaritanyPhase = 'reinforce' | 'deploy' | 'attack' | 'fortify';

export interface BattleReport {
  attackerId: string;
  attackerTerritoryId: string;
  defenderId: string | null;
  defenderTerritoryId: string;
  attackerRolls: number[];
  defenderRolls: number[];
  attackerLosses: number;
  defenderLosses: number;
  conquered: boolean;
  timestamp: string;
}

export interface FaritanyFaction {
  id: string;
  playerId: string;
  name: string;
  color: string;
  accent: string;
  iconName: string;
  eliminated: boolean;
}

export interface FaritanyGameState {
  territories: Record<string, Territory>;
  factions: Record<string, FaritanyFaction>;
  playerOrder: string[];
  currentTurnIndex: number;
  currentTurnPlayerId: string;
  phase: FaritanyPhase;
  turnNumber: number;
  reinforcementsAvailable: number;
  turnTimeLeft: number;
  lastBattleReport?: BattleReport | null;
  winnerId?: string | null;
  logs: string[];
}

// ==================== ADMIN & LEDGER TYPES ====================
export interface GameAdminSettings {
  dominoEnabled: boolean;
  ludoEnabled: boolean;
  lotoEnabled: boolean;
  faritanyEnabled: boolean;
  defaultTurnSeconds: number;
  defaultBotDifficulty: 'easy' | 'medium' | 'hard';
  welcomeCoins: number;
  maintenanceMode: boolean;
}

export interface TestUserAccount {
  id: string;
  displayName: string;
  username: string;
  avatarUrl: string;
  coinBalance: number;
  isBot: boolean;
}
