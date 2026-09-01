import { LudoColor, LudoToken, LudoGameState } from '../types/games';

export const LUDO_COLORS: LudoColor[] = ['red', 'green', 'yellow', 'blue'];

// Start track offset for each color on global 52-step circuit
export const COLOR_START_OFFSETS: Record<LudoColor, number> = {
  red: 0,
  green: 13,
  yellow: 26,
  blue: 39,
};

// Global safe indices (start spots + star spots)
export const SAFE_TRACK_POSITIONS = [0, 8, 13, 21, 26, 34, 39, 47];

export function getGlobalTrackIndex(color: LudoColor, step: number): number | null {
  if (step < 0 || step > 51) return null; // in yard or home stretch
  const offset = COLOR_START_OFFSETS[color];
  return (offset + step) % 52;
}

export function isSafePosition(globalIndex: number): boolean {
  return SAFE_TRACK_POSITIONS.includes(globalIndex);
}

export function initLudoGame(playerIds: string[]): LudoGameState {
  const activeColors: LudoColor[] = playerIds.length === 2 
    ? ['red', 'yellow'] // 2-player opposite colors
    : playerIds.length === 3 
    ? ['red', 'green', 'yellow']
    : ['red', 'green', 'yellow', 'blue'];

  const playerColors: Record<string, LudoColor> = {};
  const colorOrder: LudoColor[] = [];

  playerIds.forEach((pid, i) => {
    const col = activeColors[i];
    playerColors[pid] = col;
    colorOrder.push(col);
  });

  const tokens: LudoToken[] = [];
  colorOrder.forEach((col) => {
    const ownerId = Object.keys(playerColors).find((k) => playerColors[k] === col) || '';
    for (let tid = 0; tid < 4; tid++) {
      tokens.push({
        id: tid,
        color: col,
        playerId: ownerId,
        step: -1, // in yard
        isFinished: false,
      });
    }
  });

  return {
    tokens,
    colorOrder,
    playerColors,
    currentColorIndex: 0,
    currentTurnPlayerId: playerIds[0],
    diceRoll: null,
    hasRolledDice: false,
    canRollDice: true,
    eligibleTokenIds: [],
    extraTurn: false,
    consecutiveSixes: 0,
    turnTimeLeft: 20,
    winners: [],
    matchFinished: false,
    logs: ['Ludo match initialized! Roll 6 to move out from the yard.'],
  };
}

// Calculate which tokens can move for a given dice roll
export function getEligibleTokens(
  tokens: LudoToken[],
  color: LudoColor,
  roll: number
): number[] {
  const playerTokens = tokens.filter((t) => t.color === color);
  const eligible: number[] = [];

  for (const token of playerTokens) {
    if (token.isFinished) continue;

    // In home yard -> only roll of 6 can deploy
    if (token.step === -1) {
      if (roll === 6) {
        eligible.push(token.id);
      }
      continue;
    }

    // On track or in home stretch -> can move if step + roll <= 58
    if (token.step + roll <= 58) {
      eligible.push(token.id);
    }
  }

  return eligible;
}

// Check if a move results in capturing an opponent token
export function checkLudoCapture(
  movingToken: LudoToken,
  targetStep: number,
  allTokens: LudoToken[]
): { capturedToken: LudoToken | null; capturedGlobalIndex: number | null } {
  if (targetStep < 0 || targetStep > 51) return { capturedToken: null, capturedGlobalIndex: null };

  const targetGlobalPos = getGlobalTrackIndex(movingToken.color, targetStep);
  if (targetGlobalPos === null || isSafePosition(targetGlobalPos)) {
    return { capturedToken: null, capturedGlobalIndex: null };
  }

  // Find any opponent token on the same global track position
  const opponent = allTokens.find(
    (t) =>
      t.color !== movingToken.color &&
      !t.isFinished &&
      t.step >= 0 &&
      t.step <= 51 &&
      getGlobalTrackIndex(t.color, t.step) === targetGlobalPos
  );

  if (opponent) {
    return { capturedToken: opponent, capturedGlobalIndex: targetGlobalPos };
  }

  return { capturedToken: null, capturedGlobalIndex: null };
}

// AI Bot evaluation for Ludo
export function getBestBotLudoMove(
  tokens: LudoToken[],
  color: LudoColor,
  roll: number
): number | null {
  const eligible = getEligibleTokens(tokens, color, roll);
  if (eligible.length === 0) return null;
  if (eligible.length === 1) return eligible[0];

  const myTokens = tokens.filter((t) => t.color === color);

  let bestTokenId = eligible[0];
  let highestScore = -999;

  for (const tid of eligible) {
    const token = myTokens.find((t) => t.id === tid);
    if (!token) continue;

    let moveScore = 0;

    // Prioritize getting token out of yard on a 6
    if (token.step === -1 && roll === 6) {
      moveScore += 50;
    }

    const nextStep = token.step === -1 ? 0 : token.step + roll;

    // Prioritize finishing a token
    if (nextStep === 58) {
      moveScore += 100;
    }

    // Prioritize entering home path safely
    if (nextStep >= 52 && token.step < 52) {
      moveScore += 40;
    }

    // Check for capturing an opponent
    const { capturedToken } = checkLudoCapture(token, nextStep, tokens);
    if (capturedToken) {
      moveScore += 80;
    }

    // Advancing tokens that are furthest along
    moveScore += nextStep;

    if (moveScore > highestScore) {
      highestScore = moveScore;
      bestTokenId = tid;
    }
  }

  return bestTokenId;
}
