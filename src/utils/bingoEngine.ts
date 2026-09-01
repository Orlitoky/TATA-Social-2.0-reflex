import { BingoCard, BingoPattern, LotoGameState } from '../types/games';
import { shuffleArray } from './dominoEngine';

// Generate a valid 5x5 BINGO card (B: 1-15, I: 16-30, N: 31-45, G: 46-60, O: 61-75)
export function generateBingoCard(playerId: string, cardIndex: number = 0): BingoCard {
  const columnRanges = [
    { min: 1, max: 15 },
    { min: 16, max: 30 },
    { min: 31, max: 45 },
    { min: 46, max: 60 },
    { min: 61, max: 75 },
  ];

  const columns: number[][] = [];
  columnRanges.forEach(({ min, max }) => {
    const nums: number[] = [];
    for (let i = min; i <= max; i++) nums.push(i);
    const shuffled = shuffleArray(nums);
    columns.push(shuffled.slice(0, 5));
  });

  const numbers: (number | null)[][] = [];
  const daubed: boolean[][] = [];

  for (let r = 0; r < 5; r++) {
    const rowNums: (number | null)[] = [];
    const rowDaubed: boolean[] = [];

    for (let c = 0; c < 5; c++) {
      if (r === 2 && c === 2) {
        // Free Center Space
        rowNums.push(0);
        rowDaubed.push(true);
      } else {
        rowNums.push(columns[c][r]);
        rowDaubed.push(false);
      }
    }
    numbers.push(rowNums);
    daubed.push(rowDaubed);
  }

  return {
    id: `card_${playerId}_${cardIndex}_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
    playerId,
    numbers,
    daubed,
  };
}

export function initLotoGame(
  playerIds: string[],
  cardsPerPlayer: Record<string, number> = {},
  autoDaub: boolean = true
): LotoGameState {
  const cards: BingoCard[] = [];

  playerIds.forEach((pid) => {
    const count = cardsPerPlayer[pid] || 2;
    for (let i = 0; i < count; i++) {
      cards.push(generateBingoCard(pid, i));
    }
  });

  return {
    cards,
    calledNumbers: [],
    currentBall: null,
    isDrawing: false,
    drawSpeedSeconds: 3.5,
    autoDaub,
    roundHistory: [],
    claims: [],
    isGameOver: false,
    winnerIds: [],
    logs: ['Loto / Bingo room started! Numbers will be called from drum 1–75.'],
  };
}

// Check if a card satisfies a specific winning pattern
export function checkBingoPattern(
  card: BingoCard,
  pattern: BingoPattern
): { satisfied: boolean; winningCoords: [number, number][] } {
  const d = card.daubed;

  if (pattern === 'full_house') {
    const coords: [number, number][] = [];
    for (let r = 0; r < 5; r++) {
      for (let c = 0; c < 5; c++) {
        if (!d[r][c]) return { satisfied: false, winningCoords: [] };
        coords.push([r, c]);
      }
    }
    return { satisfied: true, winningCoords: coords };
  }

  if (pattern === 'corners') {
    if (d[0][0] && d[0][4] && d[4][0] && d[4][4]) {
      return {
        satisfied: true,
        winningCoords: [
          [0, 0],
          [0, 4],
          [4, 0],
          [4, 4],
        ],
      };
    }
  }

  if (pattern === 'line') {
    // Check 5 horizontal rows
    for (let r = 0; r < 5; r++) {
      if (d[r][0] && d[r][1] && d[r][2] && d[r][3] && d[r][4]) {
        return {
          satisfied: true,
          winningCoords: [
            [r, 0],
            [r, 1],
            [r, 2],
            [r, 3],
            [r, 4],
          ],
        };
      }
    }

    // Check 5 vertical columns
    for (let c = 0; c < 5; c++) {
      if (d[0][c] && d[1][c] && d[2][c] && d[3][c] && d[4][c]) {
        return {
          satisfied: true,
          winningCoords: [
            [0, c],
            [1, c],
            [2, c],
            [3, c],
            [4, c],
          ],
        };
      }
    }

    // Check 2 diagonals
    if (d[0][0] && d[1][1] && d[2][2] && d[3][3] && d[4][4]) {
      return {
        satisfied: true,
        winningCoords: [
          [0, 0],
          [1, 1],
          [2, 2],
          [3, 3],
          [4, 4],
        ],
      };
    }
    if (d[0][4] && d[1][3] && d[2][2] && d[3][1] && d[4][0]) {
      return {
        satisfied: true,
        winningCoords: [
          [0, 4],
          [1, 3],
          [2, 2],
          [3, 1],
          [4, 0],
        ],
      };
    }
  }

  return { satisfied: false, winningCoords: [] };
}
