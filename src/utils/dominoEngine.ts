import { DominoTile, PlacedDomino, DominoGameState } from '../types/games';

// Generate standard 28 Double-Six Domino tiles
export function generateDoubleSixSet(): DominoTile[] {
  const tiles: DominoTile[] = [];
  for (let i = 0; i <= 6; i++) {
    for (let j = i; j <= 6; j++) {
      tiles.push({
        id: `tile_${i}_${j}`,
        left: i,
        right: j,
      });
    }
  }
  return shuffleArray(tiles);
}

export function shuffleArray<T>(array: T[]): T[] {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export function getTilePipSum(tile: DominoTile): number {
  return tile.left + tile.right;
}

export function getPlayerHandPipSum(hand: DominoTile[]): number {
  return hand.reduce((sum, t) => sum + getTilePipSum(t), 0);
}

// Find legal moves for a given tile on the current domino board chain
export function getLegalMovesForTile(
  tile: DominoTile,
  boardChain: PlacedDomino[],
  leftOpenPip: number | null,
  rightOpenPip: number | null
): { side: 'left' | 'right' | 'start'; flip: boolean }[] {
  if (boardChain.length === 0) {
    return [{ side: 'start', flip: false }];
  }

  const moves: { side: 'left' | 'right' | 'start'; flip: boolean }[] = [];

  if (leftOpenPip !== null) {
    if (tile.right === leftOpenPip) {
      moves.push({ side: 'left', flip: false });
    } else if (tile.left === leftOpenPip) {
      moves.push({ side: 'left', flip: true });
    }
  }

  if (rightOpenPip !== null) {
    if (tile.left === rightOpenPip) {
      moves.push({ side: 'right', flip: false });
    } else if (tile.right === rightOpenPip) {
      moves.push({ side: 'right', flip: true });
    }
  }

  return moves;
}

export function hasAnyLegalMove(
  hand: DominoTile[],
  boardChain: PlacedDomino[],
  leftOpenPip: number | null,
  rightOpenPip: number | null
): boolean {
  if (boardChain.length === 0) return hand.length > 0;
  return hand.some((tile) => getLegalMovesForTile(tile, boardChain, leftOpenPip, rightOpenPip).length > 0);
}

// Best bot move finder
export function getBestBotDominoMove(
  hand: DominoTile[],
  boardChain: PlacedDomino[],
  leftOpenPip: number | null,
  rightOpenPip: number | null
): { tile: DominoTile; side: 'left' | 'right' | 'start'; flip: boolean } | null {
  const validMoves: { tile: DominoTile; side: 'left' | 'right' | 'start'; flip: boolean; weight: number }[] = [];

  for (const tile of hand) {
    const legal = getLegalMovesForTile(tile, boardChain, leftOpenPip, rightOpenPip);
    for (const move of legal) {
      // Heuristic: doubles and high-value tiles are prioritized to shed pips
      let weight = getTilePipSum(tile);
      if (tile.left === tile.right) weight += 10;
      validMoves.push({ tile, side: move.side, flip: move.flip, weight });
    }
  }

  if (validMoves.length === 0) return null;
  validMoves.sort((a, b) => b.weight - a.weight);
  return validMoves[0];
}

export function initDominoRound(playerIds: string[], targetScore: number = 100): DominoGameState {
  const fullSet = generateDoubleSixSet();
  const playerHands: Record<string, DominoTile[]> = {};
  
  const tilesPerPlayer = playerIds.length === 2 ? 7 : 6;
  playerIds.forEach((pid, index) => {
    playerHands[pid] = fullSet.slice(index * tilesPerPlayer, (index + 1) * tilesPerPlayer);
  });

  const boneyard = fullSet.slice(playerIds.length * tilesPerPlayer);

  // Find who has highest double or highest tile to start
  let startingPlayerId = playerIds[0];
  let highestDouble = -1;
  let highestPipSum = -1;

  playerIds.forEach((pid) => {
    const hand = playerHands[pid] || [];
    hand.forEach((t) => {
      if (t.left === t.right && t.left > highestDouble) {
        highestDouble = t.left;
        startingPlayerId = pid;
      }
      const sum = getTilePipSum(t);
      if (highestDouble === -1 && sum > highestPipSum) {
        highestPipSum = sum;
        startingPlayerId = pid;
      }
    });
  });

  const scores: Record<string, number> = {};
  playerIds.forEach((pid) => (scores[pid] = 0));

  return {
    boneyard,
    playerHands,
    boardChain: [],
    leftOpenPip: null,
    rightOpenPip: null,
    currentTurnPlayerId: startingPlayerId,
    turnTimeLeft: 30,
    roundNumber: 1,
    targetScore,
    scores,
    consecutivePasses: 0,
    roundWinnerId: null,
    matchWinnerId: null,
    logs: [`Round 1 started. Player dealt ${tilesPerPlayer} tiles each. First turn to open.`],
  };
}
