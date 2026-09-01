import { BingoCard, BingoGameState, BingoGrid } from '../types';

export const BINGO_LETTERS = ['B', 'I', 'N', 'G', 'O'] as const;

export function generateBingoCard(playerId: string): BingoCard {
  const grid: BingoGrid = [];
  const ranges = [
    [1, 15],
    [16, 30],
    [31, 45],
    [46, 60],
    [61, 75],
  ];

  // Pick 5 unique numbers for each column
  const cols: number[][] = [];
  for (let c = 0; c < 5; c++) {
    const [min, max] = ranges[c];
    const pool: number[] = [];
    for (let n = min; n <= max; n++) pool.push(n);
    // Shuffle pool
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    cols.push(pool.slice(0, 5));
  }

  // Construct 5x5 rows
  const marked: boolean[][] = [];
  for (let r = 0; r < 5; r++) {
    const row: (number | null)[] = [];
    const markRow: boolean[] = [];
    for (let c = 0; c < 5; c++) {
      if (r === 2 && c === 2) {
        row.push(null); // FREE center space
        markRow.push(true); // Pre-marked free space
      } else {
        row.push(cols[c][r]);
        markRow.push(false);
      }
    }
    grid.push(row);
    marked.push(markRow);
  }

  return {
    id: `card_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
    playerId,
    grid,
    marked,
    hasCompletedLine: false,
    hasBingo: false,
  };
}

export function initializeBingoGame(
  playerIds: string[],
  cardsPerPlayer: number = 2,
  cardCost: number = 50
): BingoGameState {
  const cards: BingoCard[] = [];
  const autoDaub: Record<string, boolean> = {};

  playerIds.forEach((pid) => {
    autoDaub[pid] = true;
    for (let i = 0; i < cardsPerPlayer; i++) {
      cards.push(generateBingoCard(pid));
    }
  });

  const prizePool = cards.length * cardCost;
  const linePrize = Math.floor(prizePool * 0.3);
  const bingoPrize = prizePool - linePrize;

  return {
    drawnNumbers: [],
    currentDrawnNumber: null,
    isDrawing: true,
    cards,
    winningLinePlayerIds: [],
    bingoWinnerId: null,
    prizePool,
    linePrize,
    bingoPrize,
    turnDeadline: Date.now() + 3500,
    autoDaub,
    lastActionSummary: 'LOTO / Bingo Cage initialized. Numbers are rolling!',
  };
}

export function getLetterForNumber(num: number): string {
  if (num <= 15) return 'B';
  if (num <= 30) return 'I';
  if (num <= 45) return 'N';
  if (num <= 60) return 'G';
  return 'O';
}

export function drawNextBingoNumber(state: BingoGameState): BingoGameState {
  if (state.bingoWinnerId || state.drawnNumbers.length >= 75) {
    return { ...state, isDrawing: false };
  }

  // Pick random unused number 1..75
  const used = new Set(state.drawnNumbers);
  const remaining: number[] = [];
  for (let i = 1; i <= 75; i++) {
    if (!used.has(i)) remaining.push(i);
  }

  if (remaining.length === 0) {
    return { ...state, isDrawing: false };
  }

  const drawn = remaining[Math.floor(Math.random() * remaining.length)];
  const letter = getLetterForNumber(drawn);
  const newDrawn = [...state.drawnNumbers, drawn];

  // Auto-mark cards for all players who have auto-daub enabled
  const updatedCards = state.cards.map((card) => {
    const isAuto = state.autoDaub[card.playerId] ?? true;
    let cardModified = false;
    const newMarked = card.marked.map((row, r) =>
      row.map((m, c) => {
        if (m) return true;
        if (isAuto && card.grid[r][c] === drawn) {
          cardModified = true;
          return true;
        }
        return false;
      })
    );

    if (!cardModified && !isAuto) return card;

    const lineCheck = checkCardLine(newMarked);
    const bingoCheck = checkCardBingo(newMarked);

    return {
      ...card,
      marked: newMarked,
      hasCompletedLine: lineCheck,
      hasBingo: bingoCheck,
    };
  });

  // Evaluate winners
  let winningLinePlayerIds = [...state.winningLinePlayerIds];
  let bingoWinnerId = state.bingoWinnerId;
  let summary = `Drawn: ${letter}-${drawn}!`;

  updatedCards.forEach((card) => {
    if (card.hasCompletedLine && !winningLinePlayerIds.includes(card.playerId)) {
      winningLinePlayerIds.push(card.playerId);
      summary = `Player achieved LINE pattern! (+${state.linePrize} coins)`;
    }
    if (card.hasBingo && !bingoWinnerId) {
      bingoWinnerId = card.playerId;
      summary = `🎉 BINGO! FULL CARD WINNER! (+${state.bingoPrize} coins)`;
    }
  });

  return {
    ...state,
    drawnNumbers: newDrawn,
    currentDrawnNumber: drawn,
    cards: updatedCards,
    winningLinePlayerIds,
    bingoWinnerId,
    isDrawing: !bingoWinnerId && newDrawn.length < 75,
    turnDeadline: Date.now() + 3500,
    lastActionSummary: summary,
  };
}

export function daubCardCell(
  state: BingoGameState,
  cardId: string,
  rowIndex: number,
  colIndex: number
): BingoGameState {
  const cardIndex = state.cards.findIndex((c) => c.id === cardId);
  if (cardIndex === -1) return state;

  const card = state.cards[cardIndex];
  const targetVal = card.grid[rowIndex][colIndex];

  // Can only mark if it's the free space or number was actually drawn
  if (targetVal !== null && !state.drawnNumbers.includes(targetVal)) {
    return state;
  }

  const newMarked = card.marked.map((r, rIdx) =>
    r.map((c, cIdx) => (rIdx === rowIndex && cIdx === colIndex ? true : c))
  );

  const lineCheck = checkCardLine(newMarked);
  const bingoCheck = checkCardBingo(newMarked);

  const updatedCard = {
    ...card,
    marked: newMarked,
    hasCompletedLine: lineCheck,
    hasBingo: bingoCheck,
  };

  const newCards = [...state.cards];
  newCards[cardIndex] = updatedCard;

  let winningLinePlayerIds = [...state.winningLinePlayerIds];
  let bingoWinnerId = state.bingoWinnerId;

  if (lineCheck && !winningLinePlayerIds.includes(card.playerId)) {
    winningLinePlayerIds.push(card.playerId);
  }
  if (bingoCheck && !bingoWinnerId) {
    bingoWinnerId = card.playerId;
  }

  return {
    ...state,
    cards: newCards,
    winningLinePlayerIds,
    bingoWinnerId,
    isDrawing: !bingoWinnerId,
    lastActionSummary: bingoCheck ? '🎉 BINGO DECLARED & VALIDATED!' : state.lastActionSummary,
  };
}

export function checkCardLine(marked: boolean[][]): boolean {
  // Check 5 rows
  for (let r = 0; r < 5; r++) {
    if (marked[r].every((val) => val)) return true;
  }
  // Check 5 cols
  for (let c = 0; c < 5; c++) {
    let colFull = true;
    for (let r = 0; r < 5; r++) {
      if (!marked[r][c]) {
        colFull = false;
        break;
      }
    }
    if (colFull) return true;
  }
  // Check diagonals
  const diag1 = marked[0][0] && marked[1][1] && marked[2][2] && marked[3][3] && marked[4][4];
  const diag2 = marked[0][4] && marked[1][3] && marked[2][2] && marked[3][1] && marked[4][0];
  return diag1 || diag2;
}

export function checkCardBingo(marked: boolean[][]): boolean {
  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 5; c++) {
      if (!marked[r][c]) return false;
    }
  }
  return true;
}
