import React, { useState } from 'react';
import { GamePlayer, GameRoomDetailed, LudoGameState, LudoPiece } from '../types';
import {
  getGlobalTrackPosition,
  LUDO_COLORS,
  LUDO_COLOR_NAMES,
  SAFE_TRACK_SQUARES,
  TOTAL_STEPS_TO_FINISH,
} from './ludoEngine';
import { GameHeader } from '../components/GameHeader';
import { InGameChat } from '../components/InGameChat';
import { GameResultsModal } from '../components/GameResultsModal';
import { Dices, Trophy, Sparkles, Shield, RefreshCw } from 'lucide-react';

interface LudoGameProps {
  room: GameRoomDetailed;
  currentPlayerId: string;
  onRoll: () => void;
  onMovePiece: (pieceId: number) => void;
  onLeave: () => void;
  onRematch: () => void;
  onSendMessage: (text: string) => void;
}

// Global 52 Track grid coordinates on a 15x15 board (0..14)
export const TRACK_GRID_COORDS: [number, number][] = [
  // Red Start & Top-Left Stretch (0..4)
  [1, 6], [2, 6], [3, 6], [4, 6], [5, 6],
  // North Arm (5..10)
  [6, 5], [6, 4], [6, 3], [6, 2], [6, 1], [6, 0],
  [7, 0], [8, 0],
  // North-East Drop (13..17) -> 13 is Green Start
  [8, 1], [8, 2], [8, 3], [8, 4], [8, 5],
  // East Arm (18..23)
  [9, 6], [10, 6], [11, 6], [12, 6], [13, 6], [14, 6],
  [14, 7], [14, 8],
  // South-East Stretch (26..30) -> 26 is Yellow Start
  [13, 8], [12, 8], [11, 8], [10, 8], [9, 8],
  // South Arm (31..36)
  [8, 9], [8, 10], [8, 11], [8, 12], [8, 13], [8, 14],
  [7, 14], [6, 14],
  // South-West Rise (39..43) -> 39 is Blue Start
  [6, 13], [6, 12], [6, 11], [6, 10], [6, 9],
  // West Arm (44..49)
  [5, 8], [4, 8], [3, 8], [2, 8], [1, 8], [0, 8],
  [0, 7], [0, 6],
];

export const LudoGame: React.FC<LudoGameProps> = ({
  room,
  currentPlayerId,
  onRoll,
  onMovePiece,
  onLeave,
  onRematch,
  onSendMessage,
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  const state = room.ludoState;
  if (!state) return null;

  const playerIds = room.players.map((p) => p.id);
  const mySeatIdx = playerIds.indexOf(currentPlayerId);
  const isMyTurn = state.currentTurnPlayerId === currentPlayerId && !state.matchWinnerId;
  const myPieces = state.pieces[currentPlayerId] || [];
  const currentPlayer = room.players.find((p) => p.id === currentPlayerId) || room.players[0];

  const renderDiceFace = (val: number | null) => {
    if (!val) return <Dices className="size-8 text-slate-400" />;

    const dotMatrix: Record<number, number[][]> = {
      1: [[50, 50]],
      2: [
        [25, 25],
        [75, 75],
      ],
      3: [
        [25, 25],
        [50, 50],
        [75, 75],
      ],
      4: [
        [25, 25],
        [75, 25],
        [25, 75],
        [75, 75],
      ],
      5: [
        [25, 25],
        [75, 25],
        [50, 50],
        [25, 75],
        [75, 75],
      ],
      6: [
        [25, 25],
        [25, 50],
        [25, 75],
        [75, 25],
        [75, 50],
        [75, 75],
      ],
    };

    const dots = dotMatrix[val] || [];

    return (
      <svg className="size-10" viewBox="0 0 100 100">
        <rect width="100" height="100" rx="20" fill="#1E9EF5" />
        {dots.map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r="9" fill="white" />
        ))}
      </svg>
    );
  };

  return (
    <div className="flex flex-col lg:flex-row gap-4 items-start w-full">
      <div className="flex-1 w-full space-y-4">
        {/* Game Header with Timer & Controls */}
        <GameHeader
          room={room}
          currentTurnPlayerId={state.currentTurnPlayerId}
          turnDeadline={state.turnDeadline}
          onLeave={onLeave}
          onToggleChat={() => setIsChatOpen(!isChatOpen)}
          chatUnreadCount={room.chatMessages.length}
        />

        {/* Action Status Bar */}
        <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-2.5 shadow-2xs">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-[#0D1420]">LUDO ARENA</span>
            <span className="text-slate-300">•</span>
            <p className="text-xs text-slate-500 font-medium truncate">{state.lastActionSummary}</p>
          </div>
          <div className="flex items-center gap-2 text-xs font-bold">
            <span className="text-slate-400">Players:</span>
            <span className="text-emerald-600 font-black">{room.players.length}</span>
          </div>
        </div>

        {/* Center Ludo Board Arena */}
        <div className="relative mx-auto max-w-xl aspect-square w-full rounded-3xl border-4 border-slate-800 bg-white p-2 sm:p-3 shadow-2xl flex flex-col justify-center select-none">
          {/* SVG Ludo Board 15x15 Grid */}
          <svg className="size-full" viewBox="0 0 1500 1500">
            {/* Grid background */}
            <rect width="1500" height="1500" fill="#f8fafc" />

            {/* Corner Base 1: RED (Top-Left 0..5, 0..5) */}
            <rect x="0" y="0" width="600" height="600" fill="#FEE2E2" stroke="#EF4444" strokeWidth="6" />
            <rect x="100" y="100" width="400" height="400" rx="30" fill="white" stroke="#EF4444" strokeWidth="4" />
            <text x="300" y="70" textAnchor="middle" fill="#EF4444" fontSize="36" fontWeight="bold">
              RED YARD
            </text>

            {/* Corner Base 2: GREEN (Top-Right 9..14, 0..5) */}
            <rect x="900" y="0" width="600" height="600" fill="#DCFCE7" stroke="#10B981" strokeWidth="6" />
            <rect x="1000" y="100" width="400" height="400" rx="30" fill="white" stroke="#10B981" strokeWidth="4" />
            <text x="1200" y="70" textAnchor="middle" fill="#10B981" fontSize="36" fontWeight="bold">
              GREEN YARD
            </text>

            {/* Corner Base 3: YELLOW (Bottom-Right 9..14, 9..14) */}
            <rect x="900" y="900" width="600" height="600" fill="#FEF3C7" stroke="#F59E0B" strokeWidth="6" />
            <rect x="1000" y="1000" width="400" height="400" rx="30" fill="white" stroke="#F59E0B" strokeWidth="4" />
            <text x="1200" y="1450" textAnchor="middle" fill="#F59E0B" fontSize="36" fontWeight="bold">
              YELLOW YARD
            </text>

            {/* Corner Base 4: BLUE (Bottom-Left 0..5, 9..14) */}
            <rect x="0" y="900" width="600" height="600" fill="#DBEAFE" stroke="#3B82F6" strokeWidth="6" />
            <rect x="100" y="1000" width="400" height="400" rx="30" fill="white" stroke="#3B82F6" strokeWidth="4" />
            <text x="300" y="1450" textAnchor="middle" fill="#3B82F6" fontSize="36" fontWeight="bold">
              BLUE YARD
            </text>

            {/* Center Victory Home Triangles (600..900, 600..900) */}
            <polygon points="600,600 750,750 600,900" fill="#EF4444" />
            <polygon points="600,600 750,750 900,600" fill="#10B981" />
            <polygon points="900,600 750,750 900,900" fill="#F59E0B" />
            <polygon points="600,900 750,750 900,900" fill="#3B82F6" />
            <circle cx="750" cy="750" r="45" fill="white" stroke="#0D1420" strokeWidth="3" />
            <text x="750" y="762" textAnchor="middle" fontSize="36" fontWeight="900" fill="#0D1420">
              🏆
            </text>

            {/* Home Stretch Corridors */}
            {/* Red Home Stretch (rows 1..5, col 7) */}
            {[1, 2, 3, 4, 5].map((c) => (
              <rect
                key={`r_home_${c}`}
                x={c * 100}
                y="700"
                width="100"
                height="100"
                fill="#F87171"
                stroke="#slate-300"
                strokeWidth="2"
              />
            ))}
            {/* Green Home Stretch (row 7, cols 1..5) */}
            {[1, 2, 3, 4, 5].map((r) => (
              <rect
                key={`g_home_${r}`}
                x="700"
                y={r * 100}
                width="100"
                height="100"
                fill="#34D399"
                stroke="#slate-300"
                strokeWidth="2"
              />
            ))}
            {/* Yellow Home Stretch */}
            {[9, 10, 11, 12, 13].map((c) => (
              <rect
                key={`y_home_${c}`}
                x={c * 100}
                y="700"
                width="100"
                height="100"
                fill="#FBBF24"
                stroke="#slate-300"
                strokeWidth="2"
              />
            ))}
            {/* Blue Home Stretch */}
            {[9, 10, 11, 12, 13].map((r) => (
              <rect
                key={`b_home_${r}`}
                x="700"
                y={r * 100}
                width="100"
                height="100"
                fill="#60A5FA"
                stroke="#slate-300"
                strokeWidth="2"
              />
            ))}

            {/* 52 Global Track Squares */}
            {TRACK_GRID_COORDS.map(([gx, gy], trackIdx) => {
              const isStartRed = trackIdx === 0;
              const isStartGreen = trackIdx === 13;
              const isStartYellow = trackIdx === 26;
              const isStartBlue = trackIdx === 39;
              const isSafe = SAFE_TRACK_SQUARES.includes(trackIdx);

              let fillColor = 'white';
              if (isStartRed) fillColor = '#EF4444';
              else if (isStartGreen) fillColor = '#10B981';
              else if (isStartYellow) fillColor = '#F59E0B';
              else if (isStartBlue) fillColor = '#3B82F6';

              return (
                <g key={`track_${trackIdx}`}>
                  <rect
                    x={gx * 100}
                    y={gy * 100}
                    width="100"
                    height="100"
                    fill={fillColor}
                    stroke="#CBD5E1"
                    strokeWidth="2"
                  />
                  {isSafe && !isStartRed && !isStartGreen && !isStartYellow && !isStartBlue && (
                    <text
                      x={gx * 100 + 50}
                      y={gy * 100 + 65}
                      textAnchor="middle"
                      fill="#64748B"
                      fontSize="44"
                      fontWeight="bold"
                    >
                      ★
                    </text>
                  )}
                </g>
              );
            })}

            {/* Render All Active Pieces on Board */}
            {room.players.map((player, seatIdx) => {
              const pieces = state.pieces[player.id] || [];
              const color = LUDO_COLORS[seatIdx % 4];

              // Base Yard Piece Circle Positions (2x2 grid in yard)
              const yardBases: [number, number][] = [
                [200, 200], // Red
                [1100, 200], // Green
                [1100, 1100], // Yellow
                [200, 1100], // Blue
              ];
              const [baseX, baseY] = yardBases[seatIdx % 4];
              const yardOffsets: [number, number][] = [
                [-60, -60],
                [60, -60],
                [-60, 60],
                [60, 60],
              ];

              return pieces.map((piece) => {
                let px = 0;
                let py = 0;

                if (piece.stepIndex === -1) {
                  // In Yard
                  const [ox, oy] = yardOffsets[piece.id];
                  px = baseX + ox;
                  py = baseY + oy;
                } else if (piece.isFinished) {
                  // In Center Home
                  px = 750 + (piece.id - 1.5) * 20;
                  py = 750;
                } else if (piece.stepIndex >= 51) {
                  // In Home Corridor
                  const corridorStep = piece.stepIndex - 51; // 0..4
                  if (seatIdx === 0) {
                    // Red -> rightwards
                    px = (corridorStep + 1) * 100 + 50;
                    py = 750;
                  } else if (seatIdx === 1) {
                    // Green -> downwards
                    px = 750;
                    py = (corridorStep + 1) * 100 + 50;
                  } else if (seatIdx === 2) {
                    // Yellow -> leftwards
                    px = (13 - corridorStep) * 100 + 50;
                    py = 750;
                  } else {
                    // Blue -> upwards
                    px = 750;
                    py = (13 - corridorStep) * 100 + 50;
                  }
                } else {
                  // On Track
                  const pos = getGlobalTrackPosition(seatIdx, piece.stepIndex);
                  const [gx, gy] = TRACK_GRID_COORDS[pos.index];
                  px = gx * 100 + 50 + (piece.id - 1.5) * 8;
                  py = gy * 100 + 50 + (piece.id - 1.5) * 8;
                }

                const isMovable =
                  isMyTurn &&
                  player.id === currentPlayerId &&
                  state.mustMovePieceIds.includes(piece.id);

                return (
                  <g
                    key={`piece_${player.id}_${piece.id}`}
                    onClick={() => isMovable && onMovePiece(piece.id)}
                    className={isMovable ? 'cursor-pointer' : ''}
                  >
                    {isMovable && (
                      <circle
                        cx={px}
                        cy={py}
                        r="38"
                        fill="none"
                        stroke="#F59E0B"
                        strokeWidth="6"
                        className="animate-ping"
                      />
                    )}
                    <circle
                      cx={px}
                      cy={py}
                      r="28"
                      fill={color}
                      stroke="white"
                      strokeWidth="5"
                      filter="drop-shadow(0px 6px 6px rgba(0,0,0,0.35))"
                    />
                    <circle cx={px} cy={py} r="12" fill="white" opacity="0.9" />
                  </g>
                );
              });
            })}
          </svg>
        </div>

        {/* Dice Rolling & Turn Tray */}
        <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex size-14 items-center justify-center rounded-2xl bg-slate-100 border border-slate-200 shadow-inner">
              {renderDiceFace(state.currentDiceValue)}
            </div>
            <div>
              <p className="text-xs font-bold text-[#0D1420]">
                {state.currentDiceValue ? `Rolled ${state.currentDiceValue}` : 'Roll to start'}
              </p>
              <p className="text-[11px] text-slate-400 font-medium">
                {isMyTurn
                  ? state.canRoll
                    ? 'Your turn! Tap Roll Dice.'
                    : 'Choose an illuminated piece on board.'
                  : `Waiting for ${room.players.find((p) => p.id === state.currentTurnPlayerId)?.name}...`}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {isMyTurn && state.canRoll && (
              <button
                onClick={onRoll}
                className="flex items-center gap-2 rounded-2xl bg-[#1E9EF5] hover:bg-sky-600 text-white px-6 py-3 text-sm font-black shadow-lg active:scale-95 transition-all"
              >
                <Dices className="size-5" />
                <span>ROLL DICE</span>
              </button>
            )}

            {isMyTurn && !state.canRoll && state.mustMovePieceIds.length > 0 && (
              <div className="flex items-center gap-1.5">
                {state.mustMovePieceIds.map((pid) => (
                  <button
                    key={pid}
                    onClick={() => onMovePiece(pid)}
                    className="rounded-xl bg-amber-400 hover:bg-amber-500 text-amber-950 px-3 py-2 text-xs font-extrabold shadow-sm active:scale-95"
                  >
                    Move Piece #{pid + 1}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Side Chat Drawer */}
      {isChatOpen && (
        <div className="w-full lg:w-80 shrink-0">
          <InGameChat
            messages={room.chatMessages}
            currentPlayer={currentPlayer}
            onSendMessage={onSendMessage}
            onClose={() => setIsChatOpen(false)}
          />
        </div>
      )}

      {/* Match Completed Results Modal */}
      {state.matchWinnerId && (
        <GameResultsModal
          room={room}
          winnerId={state.matchWinnerId}
          currentPlayerId={currentPlayerId}
          onRematch={onRematch}
          onLeave={onLeave}
        />
      )}
    </div>
  );
};
