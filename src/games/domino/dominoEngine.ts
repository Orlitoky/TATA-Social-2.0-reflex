import { DominoGameState, DominoTile, PlacedDominoTile } from '../types';

export function createDoubleSixDeck(): DominoTile[] {
  const deck: DominoTile[] = [];
  for (let i = 0; i <= 6; i++) {
    for (let j = i; j <= 6; j++) {
      deck.push([i, j]);
    }
  }
  return deck;
}

export function shuffleDeck<T>(array: T[]): T[] {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export function initializeDominoGame(playerIds: string[], targetScore: number = 100): DominoGameState {
  const fullDeck = shuffleDeck(createDoubleSixDeck());
  const tilesPerPlayer = playerIds.length === 2 ? 7 : playerIds.length === 3 ? 6 : 5;
  
  const playerHands: Record<string, DominoTile[]> = {};
  let deckIndex = 0;

  for (const pid of playerIds) {
    playerHands[pid] = fullDeck.slice(deckIndex, deckIndex + tilesPerPlayer);
    deckIndex += tilesPerPlayer;
  }

  const boneyard = fullDeck.slice(deckIndex);

  // Find who has the highest double to start
  let startingPlayerId = playerIds[0];
  let highestDouble = -1;

  for (const pid of playerIds) {
    for (const [l, r] of playerHands[pid]) {
      if (l === r && l > highestDouble) {
        highestDouble = l;
        startingPlayerId = pid;
      }
    }
  }

  const roundScores: Record<string, number> = {};
  for (const pid of playerIds) {
    roundScores[pid] = 0;
  }

  return {
    boneyard,
    playerHands,
    placedChain: [],
    openLeft: null,
    openRight: null,
    currentTurnPlayerId: startingPlayerId,
    turnDeadline: Date.now() + 25000,
    roundNumber: 1,
    roundScores,
    lastActionSummary: 'Round 1 started. Place the first tile!',
    isRoundOver: false,
    roundWinnerId: null,
    roundWinReason: undefined,
    matchWinnerId: null,
  };
}

export function getLegalMovesForPlayer(hand: DominoTile[], openLeft: number | null, openRight: number | null): {
  tileIndex: number;
  tile: DominoTile;
  canPlayLeft: boolean;
  canPlayRight: boolean;
}[] {
  if (openLeft === null && openRight === null) {
    // First tile on empty board: all tiles are legal
    return hand.map((tile, idx) => ({
      tileIndex: idx,
      tile,
      canPlayLeft: true,
      canPlayRight: true,
    }));
  }

  const legal: { tileIndex: number; tile: DominoTile; canPlayLeft: boolean; canPlayRight: boolean }[] = [];

  hand.forEach((tile, idx) => {
    const [a, b] = tile;
    const canPlayLeft = openLeft !== null && (a === openLeft || b === openLeft);
    const canPlayRight = openRight !== null && (a === openRight || b === openRight);

    if (canPlayLeft || canPlayRight) {
      legal.push({
        tileIndex: idx,
        tile,
        canPlayLeft,
        canPlayRight,
      });
    }
  });

  return legal;
}

export function playDominoTile(
  state: DominoGameState,
  playerId: string,
  tileIndex: number,
  side: 'left' | 'right' | 'start',
  playerIds: string[],
  targetScore: number = 100
): DominoGameState {
  if (state.currentTurnPlayerId !== playerId || state.isRoundOver) {
    return state;
  }

  const hand = [...state.playerHands[playerId]];
  const tile = hand[tileIndex];
  if (!tile) return state;

  hand.splice(tileIndex, 1);
  const newHands = { ...state.playerHands, [playerId]: hand };

  const [a, b] = tile;
  let newOpenLeft = state.openLeft;
  let newOpenRight = state.openRight;
  let newPlacedChain = [...state.placedChain];

  if (state.placedChain.length === 0) {
    // Starting tile
    newOpenLeft = a;
    newOpenRight = b;
    newPlacedChain.push({
      id: `tile_${Date.now()}_${Math.random()}`,
      tile,
      placedBy: playerId,
      endConnected: 'start',
      orientation: a === b ? 'vertical' : 'horizontal',
      rotation: 0,
      displayLeftVal: a,
      displayRightVal: b,
    });
  } else if (side === 'left' && state.openLeft !== null) {
    const isMatchingA = a === state.openLeft;
    const isMatchingB = b === state.openLeft;
    if (!isMatchingA && !isMatchingB) return state;

    // If 'b' matches openLeft, tile stays [a, b] so 'a' becomes new openLeft.
    // If 'a' matches openLeft, flip tile to [b, a] so 'b' becomes new openLeft.
    const newOuterVal = isMatchingB ? a : b;
    const displayLeft = newOuterVal;
    const displayRight = state.openLeft;
    newOpenLeft = newOuterVal;

    newPlacedChain.unshift({
      id: `tile_${Date.now()}_${Math.random()}`,
      tile,
      placedBy: playerId,
      endConnected: 'left',
      orientation: a === b ? 'vertical' : 'horizontal',
      rotation: 0,
      displayLeftVal: displayLeft,
      displayRightVal: displayRight,
    });
  } else if (side === 'right' && state.openRight !== null) {
    const isMatchingA = a === state.openRight;
    const isMatchingB = b === state.openRight;
    if (!isMatchingA && !isMatchingB) return state;

    // If 'a' matches openRight, tile stays [a, b] so 'b' becomes new openRight.
    // If 'b' matches openRight, flip tile to [b, a] so 'a' becomes new openRight.
    const newOuterVal = isMatchingA ? b : a;
    const displayLeft = state.openRight;
    const displayRight = newOuterVal;
    newOpenRight = newOuterVal;

    newPlacedChain.push({
      id: `tile_${Date.now()}_${Math.random()}`,
      tile,
      placedBy: playerId,
      endConnected: 'right',
      orientation: a === b ? 'vertical' : 'horizontal',
      rotation: 0,
      displayLeftVal: displayLeft,
      displayRightVal: displayRight,
    });
  } else {
    return state;
  }

  // Check Round Win Condition 1: Domino! (Player placed their last tile)
  if (hand.length === 0) {
    let earnedPoints = 0;
    for (const pid of playerIds) {
      if (pid !== playerId) {
        earnedPoints += newHands[pid].reduce((sum, [l, r]) => sum + l + r, 0);
      }
    }
    const newScores = {
      ...state.roundScores,
      [playerId]: (state.roundScores[playerId] || 0) + Math.max(earnedPoints, 5),
    };
    const isMatchWon = newScores[playerId] >= targetScore;

    return {
      ...state,
      playerHands: newHands,
      placedChain: newPlacedChain,
      openLeft: newOpenLeft,
      openRight: newOpenRight,
      isRoundOver: true,
      roundWinnerId: playerId,
      roundWinReason: `DOMINO! Scored +${earnedPoints} points from remaining player tiles!`,
      roundScores: newScores,
      matchWinnerId: isMatchWon ? playerId : null,
      lastActionSummary: `Player placed [${tile[0]}|${tile[1]}] and declared DOMINO!`,
    };
  }

  // Check Round Win Condition 2: Locked Game (No player can move and boneyard is empty)
  const isBoneyardEmpty = state.boneyard.length === 0;
  let anyPlayerHasLegalMove = false;
  if (isBoneyardEmpty) {
    for (const pid of playerIds) {
      const pLegal = getLegalMovesForPlayer(newHands[pid], newOpenLeft, newOpenRight);
      if (pLegal.length > 0) {
        anyPlayerHasLegalMove = true;
        break;
      }
    }
  } else {
    anyPlayerHasLegalMove = true;
  }

  if (isBoneyardEmpty && !anyPlayerHasLegalMove) {
    // Locked board: find player with lowest pip sum
    let lowestPips = 9999;
    let lockedWinnerId = playerId;
    const pipSums: Record<string, number> = {};

    for (const pid of playerIds) {
      const sum = newHands[pid].reduce((s, [l, r]) => s + l + r, 0);
      pipSums[pid] = sum;
      if (sum < lowestPips) {
        lowestPips = sum;
        lockedWinnerId = pid;
      }
    }

    let pointsWon = 0;
    for (const pid of playerIds) {
      if (pid !== lockedWinnerId) {
        pointsWon += pipSums[pid];
      }
    }

    const newScores = {
      ...state.roundScores,
      [lockedWinnerId]: (state.roundScores[lockedWinnerId] || 0) + Math.max(pointsWon, 5),
    };
    const isMatchWon = newScores[lockedWinnerId] >= targetScore;

    return {
      ...state,
      playerHands: newHands,
      placedChain: newPlacedChain,
      openLeft: newOpenLeft,
      openRight: newOpenRight,
      isRoundOver: true,
      roundWinnerId: lockedWinnerId,
      roundWinReason: `Board is locked! Won with lowest pips (${lowestPips} pips)!`,
      roundScores: newScores,
      matchWinnerId: isMatchWon ? lockedWinnerId : null,
      lastActionSummary: 'Board locked. Round concluded.',
    };
  }

  // Advance turn to next player
  const currentIdx = playerIds.indexOf(playerId);
  const nextPlayerId = playerIds[(currentIdx + 1) % playerIds.length];

  return {
    ...state,
    playerHands: newHands,
    placedChain: newPlacedChain,
    openLeft: newOpenLeft,
    openRight: newOpenRight,
    currentTurnPlayerId: nextPlayerId,
    turnDeadline: Date.now() + 25000,
    lastActionSummary: `Played [${tile[0]}|${tile[1]}] on ${side}. Next turn!`,
  };
}

export function drawFromBoneyard(state: DominoGameState, playerId: string, playerIds: string[]): DominoGameState {
  if (state.currentTurnPlayerId !== playerId || state.isRoundOver || state.boneyard.length === 0) {
    return state;
  }

  const boneyard = [...state.boneyard];
  const drawnTile = boneyard.pop()!;
  const newHand = [...state.playerHands[playerId], drawnTile];

  return {
    ...state,
    boneyard,
    playerHands: {
      ...state.playerHands,
      [playerId]: newHand,
    },
    turnDeadline: Date.now() + 20000,
    lastActionSummary: `Player drew a tile from the boneyard (${boneyard.length} remaining).`,
  };
}

export function passTurn(state: DominoGameState, playerId: string, playerIds: string[]): DominoGameState {
  if (state.currentTurnPlayerId !== playerId || state.isRoundOver) {
    return state;
  }

  const currentIdx = playerIds.indexOf(playerId);
  const nextPlayerId = playerIds[(currentIdx + 1) % playerIds.length];

  return {
    ...state,
    currentTurnPlayerId: nextPlayerId,
    turnDeadline: Date.now() + 25000,
    lastActionSummary: `Player passed their turn.`,
  };
}

export function startNextDominoRound(state: DominoGameState, playerIds: string[], targetScore: number = 100): DominoGameState {
  const fullDeck = shuffleDeck(createDoubleSixDeck());
  const tilesPerPlayer = playerIds.length === 2 ? 7 : playerIds.length === 3 ? 6 : 5;
  
  const playerHands: Record<string, DominoTile[]> = {};
  let deckIndex = 0;

  for (const pid of playerIds) {
    playerHands[pid] = fullDeck.slice(deckIndex, deckIndex + tilesPerPlayer);
    deckIndex += tilesPerPlayer;
  }

  const boneyard = fullDeck.slice(deckIndex);
  const nextLeader = state.roundWinnerId || playerIds[0];

  return {
    ...state,
    boneyard,
    playerHands,
    placedChain: [],
    openLeft: null,
    openRight: null,
    currentTurnPlayerId: nextLeader,
    turnDeadline: Date.now() + 25000,
    roundNumber: state.roundNumber + 1,
    isRoundOver: false,
    roundWinnerId: null,
    roundWinReason: undefined,
    lastActionSummary: `Round ${state.roundNumber + 1} began! Lead the play.`,
  };
}

// Bot Decision Logic
export function getDominoBotMove(
  state: DominoGameState,
  botPlayerId: string,
  playerIds: string[]
): { action: 'play' | 'draw' | 'pass'; tileIndex?: number; side?: 'left' | 'right' | 'start' } {
  const hand = state.playerHands[botPlayerId] || [];
  const legal = getLegalMovesForPlayer(hand, state.openLeft, state.openRight);

  if (legal.length > 0) {
    // Pick the tile with highest pip sum or double
    legal.sort((a, b) => {
      const sumA = a.tile[0] + a.tile[1] + (a.tile[0] === a.tile[1] ? 10 : 0);
      const sumB = b.tile[0] + b.tile[1] + (b.tile[0] === b.tile[1] ? 10 : 0);
      return sumB - sumA;
    });

    const chosen = legal[0];
    const side = chosen.canPlayRight ? 'right' : 'left';
    return {
      action: 'play',
      tileIndex: chosen.tileIndex,
      side: state.placedChain.length === 0 ? 'start' : side,
    };
  }

  if (state.boneyard.length > 0) {
    return { action: 'draw' };
  }

  return { action: 'pass' };
}
