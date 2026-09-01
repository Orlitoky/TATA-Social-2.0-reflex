import { LudoGameState, LudoPiece } from '../types';

export const LUDO_COLORS = ['#EF4444', '#10B981', '#F59E0B', '#3B82F6']; // Red, Green, Yellow, Blue
export const LUDO_COLOR_NAMES = ['Red', 'Green', 'Yellow', 'Blue'];

// Offsets on the 52-square global track for the 4 player seats
export const PLAYER_START_OFFSETS = [0, 13, 26, 39];

// Safe zones on the global 52-step track (cannot be captured here)
export const SAFE_TRACK_SQUARES = [0, 8, 13, 21, 26, 34, 39, 47];

export const TOTAL_STEPS_TO_FINISH = 56; // 0..50 on global track (51 steps) + 5 steps home corridor (51..55) + 56 = home

export function initializeLudoGame(playerIds: string[], piecesPerPlayer: 2 | 4 = 4): LudoGameState {
  const pieces: Record<string, LudoPiece[]> = {};

  playerIds.forEach((pid) => {
    pieces[pid] = Array.from({ length: piecesPerPlayer }, (_, i) => ({
      id: i,
      playerId: pid,
      stepIndex: -1, // -1 means in base yard
      isFinished: false,
    }));
  });

  return {
    pieces,
    currentTurnPlayerId: playerIds[0],
    currentDiceValue: null,
    canRoll: true,
    mustMovePieceIds: [],
    consecutiveSixes: 0,
    turnDeadline: Date.now() + 20000,
    rankings: [],
    matchWinnerId: null,
    lastActionSummary: 'Match started! Roll the dice to begin.',
  };
}

// Convert player relative step (-1, 0..56) to global track index (0..51) or special identifier
export function getGlobalTrackPosition(seatIndex: number, relativeStep: number): { type: 'yard' | 'track' | 'corridor' | 'home'; index: number } {
  if (relativeStep < 0) {
    return { type: 'yard', index: -1 };
  }
  if (relativeStep < 51) {
    const offset = PLAYER_START_OFFSETS[seatIndex] || 0;
    const globalIdx = (offset + relativeStep) % 52;
    return { type: 'track', index: globalIdx };
  }
  if (relativeStep < 56) {
    return { type: 'corridor', index: relativeStep - 51 }; // 0..4
  }
  return { type: 'home', index: 56 };
}

export function rollLudoDice(
  state: LudoGameState,
  playerId: string,
  playerIds: string[],
  forcedVal?: number
): LudoGameState {
  if (state.currentTurnPlayerId !== playerId || !state.canRoll || state.matchWinnerId) {
    return state;
  }

  const dice = forcedVal ?? Math.floor(Math.random() * 6) + 1;
  const isSix = dice === 6;
  const newConsecutiveSixes = isSix ? state.consecutiveSixes + 1 : 0;

  // Penalty rule: 3 sixes in a row loses turn
  if (newConsecutiveSixes >= 3) {
    const nextPlayerId = getNextPlayerId(playerIds, playerId, state.rankings);
    return {
      ...state,
      currentDiceValue: 6,
      canRoll: true,
      consecutiveSixes: 0,
      mustMovePieceIds: [],
      currentTurnPlayerId: nextPlayerId,
      turnDeadline: Date.now() + 20000,
      lastActionSummary: 'Rolled three 6s in a row! Turn skipped.',
    };
  }

  // Find movable pieces
  const playerPieces = state.pieces[playerId] || [];
  const movablePieceIds: number[] = [];

  playerPieces.forEach((piece) => {
    if (piece.isFinished) return;
    if (piece.stepIndex === -1) {
      if (isSix) movablePieceIds.push(piece.id);
    } else {
      if (piece.stepIndex + dice <= TOTAL_STEPS_TO_FINISH) {
        movablePieceIds.push(piece.id);
      }
    }
  });

  // If no pieces can move, pass turn (unless rolled 6, but if no movable pieces even with 6, pass)
  if (movablePieceIds.length === 0) {
    const nextPlayerId = isSix ? playerId : getNextPlayerId(playerIds, playerId, state.rankings);
    return {
      ...state,
      currentDiceValue: dice,
      canRoll: isSix,
      consecutiveSixes: newConsecutiveSixes,
      mustMovePieceIds: [],
      currentTurnPlayerId: nextPlayerId,
      turnDeadline: Date.now() + 20000,
      lastActionSummary: `Rolled ${dice}. No legal moves available.`,
    };
  }

  // If only 1 piece can move, auto-flag or let player tap
  return {
    ...state,
    currentDiceValue: dice,
    canRoll: false,
    consecutiveSixes: newConsecutiveSixes,
    mustMovePieceIds: movablePieceIds,
    turnDeadline: Date.now() + 20000,
    lastActionSummary: `Rolled ${dice}! Choose a piece to move.`,
  };
}

export function moveLudoPiece(
  state: LudoGameState,
  playerId: string,
  pieceId: number,
  playerIds: string[]
): LudoGameState {
  if (
    state.currentTurnPlayerId !== playerId ||
    state.canRoll ||
    !state.currentDiceValue ||
    !state.mustMovePieceIds.includes(pieceId)
  ) {
    return state;
  }

  const dice = state.currentDiceValue;
  const playerPieces = [...(state.pieces[playerId] || [])];
  const targetPieceIndex = playerPieces.findIndex((p) => p.id === pieceId);
  if (targetPieceIndex === -1) return state;

  const piece = { ...playerPieces[targetPieceIndex] };
  const seatIdx = playerIds.indexOf(playerId);

  let newStepIndex = piece.stepIndex;
  if (piece.stepIndex === -1 && dice === 6) {
    newStepIndex = 0; // enter starting square
  } else {
    newStepIndex += dice;
  }

  const isFinished = newStepIndex >= TOTAL_STEPS_TO_FINISH;
  piece.stepIndex = newStepIndex;
  piece.isFinished = isFinished;
  playerPieces[targetPieceIndex] = piece;

  const newPieces = { ...state.pieces, [playerId]: playerPieces };

  // Check captures on track (if landing on global track)
  let capturedOpponent = false;
  let captureSummary = '';

  if (newStepIndex >= 0 && newStepIndex < 51) {
    const myPos = getGlobalTrackPosition(seatIdx, newStepIndex);
    const isSafe = SAFE_TRACK_SQUARES.includes(myPos.index);

    if (!isSafe) {
      // Check if any opponent piece is on this exact track square
      playerIds.forEach((otherPid, otherSeatIdx) => {
        if (otherPid === playerId) return;
        const otherPieces = newPieces[otherPid] ? [...newPieces[otherPid]] : [];
        let modified = false;

        otherPieces.forEach((op, opIdx) => {
          if (!op.isFinished && op.stepIndex >= 0 && op.stepIndex < 51) {
            const opPos = getGlobalTrackPosition(otherSeatIdx, op.stepIndex);
            if (opPos.index === myPos.index) {
              // Captured! Send back to yard
              otherPieces[opIdx] = { ...op, stepIndex: -1 };
              modified = true;
              capturedOpponent = true;
              captureSummary = `Captured an opponent piece! Bonus turn awarded!`;
            }
          }
        });

        if (modified) {
          newPieces[otherPid] = otherPieces;
        }
      });
    }
  }

  // Check if current player finished all pieces
  const allFinished = playerPieces.every((p) => p.isFinished);
  let newRankings = [...state.rankings];
  let matchWinnerId = state.matchWinnerId;

  if (allFinished && !newRankings.includes(playerId)) {
    newRankings.push(playerId);
    if (!matchWinnerId) {
      matchWinnerId = playerId;
    }
  }

  // Extra turn if rolled 6, reached home, or captured opponent
  const getsBonusRoll = (dice === 6 || isFinished || capturedOpponent) && !allFinished;
  const nextPlayerId = getsBonusRoll ? playerId : getNextPlayerId(playerIds, playerId, newRankings);

  return {
    ...state,
    pieces: newPieces,
    currentDiceValue: null,
    canRoll: true,
    mustMovePieceIds: [],
    currentTurnPlayerId: nextPlayerId,
    turnDeadline: Date.now() + 20000,
    rankings: newRankings,
    matchWinnerId,
    lastActionSummary: isFinished
      ? `Piece entered HOME! 🏆 ${getsBonusRoll ? 'Bonus turn!' : ''}`
      : captureSummary || `Piece moved ${dice} spaces.`,
  };
}

function getNextPlayerId(playerIds: string[], currentPid: string, rankings: string[]): string {
  const remaining = playerIds.filter((pid) => !rankings.includes(pid));
  if (remaining.length === 0) return currentPid;

  const currentIdx = playerIds.indexOf(currentPid);
  for (let i = 1; i <= playerIds.length; i++) {
    const nextPid = playerIds[(currentIdx + i) % playerIds.length];
    if (remaining.includes(nextPid)) {
      return nextPid;
    }
  }
  return remaining[0];
}

// Bot Decision Logic for Ludo
export function getLudoBotAction(
  state: LudoGameState,
  botPlayerId: string,
  playerIds: string[]
): { action: 'roll' | 'move'; pieceId?: number } {
  if (state.canRoll) {
    return { action: 'roll' };
  }

  if (state.mustMovePieceIds.length === 0) {
    return { action: 'roll' };
  }

  const seatIdx = playerIds.indexOf(botPlayerId);
  const pieces = state.pieces[botPlayerId] || [];
  const dice = state.currentDiceValue || 1;

  // Score candidate moves to pick smartest option
  let bestPieceId = state.mustMovePieceIds[0];
  let bestScore = -9999;

  for (const pid of state.mustMovePieceIds) {
    const p = pieces.find((x) => x.id === pid);
    if (!p) continue;

    let score = 0;

    // High priority: Enter track from yard if rolled 6
    if (p.stepIndex === -1 && dice === 6) {
      score += 500;
    }

    // High priority: Reach finish
    if (p.stepIndex + dice === TOTAL_STEPS_TO_FINISH) {
      score += 1000;
    }

    // High priority: Capture opponent piece
    const futureStep = p.stepIndex + dice;
    if (futureStep >= 0 && futureStep < 51) {
      const futurePos = getGlobalTrackPosition(seatIdx, futureStep);
      const isSafe = SAFE_TRACK_SQUARES.includes(futurePos.index);

      if (!isSafe) {
        let wouldCapture = false;
        playerIds.forEach((otherPid, otherSeat) => {
          if (otherPid === botPlayerId) return;
          (state.pieces[otherPid] || []).forEach((op) => {
            if (!op.isFinished && op.stepIndex >= 0 && op.stepIndex < 51) {
              const opPos = getGlobalTrackPosition(otherSeat, op.stepIndex);
              if (opPos.index === futurePos.index) {
                wouldCapture = true;
              }
            }
          });
        });
        if (wouldCapture) score += 800;
      }
    }

    // Medium priority: Move into safe zone
    if (futureStep >= 0 && futureStep < 51) {
      const futurePos = getGlobalTrackPosition(seatIdx, futureStep);
      if (SAFE_TRACK_SQUARES.includes(futurePos.index)) {
        score += 200;
      }
    }

    // Base advancement priority
    score += p.stepIndex;

    if (score > bestScore) {
      bestScore = score;
      bestPieceId = pid;
    }
  }

  return {
    action: 'move',
    pieceId: bestPieceId,
  };
}
