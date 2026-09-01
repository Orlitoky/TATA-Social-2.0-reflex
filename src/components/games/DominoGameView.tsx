import React, { useState } from 'react';
import { useGames } from '../../context/GamesContext';
import { DominoTile, PlacedDomino } from '../../types/games';
import { getLegalMovesForTile, getTilePipSum } from '../../utils/dominoEngine';
import { GameChatTray } from './GameChatTray';
import {
  ArrowLeft,
  Trophy,
  Sparkles,
  RefreshCw,
  Clock,
  Layers,
  HelpCircle,
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
} from 'lucide-react';

// Helper to render authentic domino pip dots
export const DominoFace: React.FC<{
  left: number;
  right: number;
  orientation?: 'horizontal' | 'vertical';
  isFlipped?: boolean;
  isClickable?: boolean;
  isLegal?: boolean;
  onClick?: () => void;
}> = ({ left, right, orientation = 'vertical', isFlipped = false, isClickable = false, isLegal = false, onClick }) => {
  const pipCoords: Record<number, number[][]> = {
    0: [],
    1: [[50, 50]],
    2: [[25, 25], [75, 75]],
    3: [[25, 25], [50, 50], [75, 75]],
    4: [[25, 25], [75, 25], [25, 75], [75, 75]],
    5: [[25, 25], [75, 25], [50, 50], [25, 75], [75, 75]],
    6: [[25, 20], [75, 20], [25, 50], [75, 50], [25, 80], [75, 80]],
  };

  const topVal = isFlipped ? right : left;
  const botVal = isFlipped ? left : right;

  const renderHalf = (count: number) => (
    <div className="relative size-full flex items-center justify-center p-0.5">
      {pipCoords[count]?.map(([x, y], idx) => (
        <span
          key={idx}
          className="absolute size-1.5 sm:size-2 rounded-full bg-[#0D1420] shadow-xs"
          style={{ left: `${x}%`, top: `${y}%`, transform: 'translate(-50%, -50%)' }}
        />
      ))}
    </div>
  );

  return (
    <div
      onClick={isClickable ? onClick : undefined}
      className={`relative select-none rounded-xl border border-slate-300 bg-linear-to-b from-white via-amber-50/20 to-slate-100 shadow-md transition-all ${
        orientation === 'vertical' ? 'w-9 sm:w-11 h-18 sm:h-22' : 'w-18 sm:w-22 h-9 sm:h-11'
      } ${
        isLegal
          ? 'ring-3 ring-emerald-400 shadow-emerald-200 cursor-pointer scale-105 hover:scale-110'
          : isClickable
          ? 'cursor-pointer hover:scale-105'
          : ''
      }`}
    >
      <div className={`flex size-full ${orientation === 'vertical' ? 'flex-col' : 'flex-row'}`}>
        <div className="flex-1 flex items-center justify-center">{renderHalf(topVal)}</div>
        <div className={`bg-slate-300 shrink-0 ${orientation === 'vertical' ? 'h-0.5 w-full' : 'w-0.5 h-full'}`} />
        <div className="flex-1 flex items-center justify-center">{renderHalf(botVal)}</div>
      </div>
    </div>
  );
};

export const DominoGameView: React.FC = () => {
  const { dominoState, currentRoom, leaveRoom, rematch, playDominoTile, drawDominoBoneyard, passDominoTurn, activeDemoUser } = useGames();
  const [selectedTile, setSelectedTile] = useState<DominoTile | null>(null);

  if (!dominoState || !currentRoom) return null;

  const isMyTurn = dominoState.currentTurnPlayerId === activeDemoUser.id;
  const myHand = dominoState.playerHands[activeDemoUser.id] || [];
  const opponentPlayers = currentRoom.players.filter((p) => p.id !== activeDemoUser.id);
  const currentTurnPlayer = currentRoom.players.find((p) => p.id === dominoState.currentTurnPlayerId);

  // Check legal moves for my hand
  const myHandMoves = myHand.map((t) => ({
    tile: t,
    moves: getLegalMovesForTile(t, dominoState.boardChain, dominoState.leftOpenPip, dominoState.rightOpenPip),
  }));

  const hasAnyMove = myHandMoves.some((m) => m.moves.length > 0);

  const handleTileClick = (tile: DominoTile) => {
    if (!isMyTurn) return;
    const moves = getLegalMovesForTile(tile, dominoState.boardChain, dominoState.leftOpenPip, dominoState.rightOpenPip);
    if (moves.length === 0) return;

    if (moves.length === 1 || dominoState.boardChain.length === 0) {
      playDominoTile(tile.id, moves[0].side);
      setSelectedTile(null);
    } else {
      // Tile fits on both left and right sides! Open selector
      setSelectedTile(tile);
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Top Controls Header */}
      <div className="flex items-center justify-between bg-white rounded-2xl border border-slate-200 p-3 shadow-xs">
        <button
          onClick={leaveRoom}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
        >
          <ArrowLeft className="size-3.5" />
          <span>Leave Match</span>
        </button>

        {/* Turn Status Pill */}
        <div className="flex items-center gap-2">
          {currentTurnPlayer && (
            <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl">
              <img
                src={currentTurnPlayer.avatarUrl}
                alt={currentTurnPlayer.displayName}
                className={`size-6 rounded-full object-cover ${isMyTurn ? 'ring-2 ring-emerald-500' : ''}`}
              />
              <span className="text-xs font-bold text-[#0D1420]">
                {isMyTurn ? 'Your Turn to Play' : `${currentTurnPlayer.displayName}'s Turn`}
              </span>
              <span className="inline-block size-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>
          )}
        </div>

        {/* Target Score Pill */}
        <div className="flex items-center gap-2 text-xs font-bold">
          <span className="text-slate-400">Target:</span>
          <span className="bg-sky-50 text-[#1E9EF5] px-2.5 py-1 rounded-lg border border-sky-100">
            {dominoState.targetScore} Pts
          </span>
        </div>
      </div>

      {/* Main Grid: Domino Board vs Chat/Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 Cols: The Domino Arena Table */}
        <div className="lg:col-span-2 space-y-4">
          <div className="relative flex flex-col rounded-3xl bg-linear-to-b from-slate-900 via-[#0D1420] to-slate-900 border border-slate-800 p-4 sm:p-5 shadow-2xl min-h-[480px] overflow-hidden">
            {/* Opponent Rack at Top */}
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-2">
              <div className="flex items-center gap-3">
                {opponentPlayers.map((opp) => {
                  const oppHand = dominoState.playerHands[opp.id] || [];
                  return (
                    <div key={opp.id} className="flex items-center gap-2 bg-slate-800/60 p-1.5 px-2.5 rounded-xl border border-slate-700">
                      <img src={opp.avatarUrl} alt={opp.displayName} className="size-6 rounded-full object-cover" />
                      <div>
                        <span className="text-xs font-bold text-slate-200 block leading-tight">{opp.displayName}</span>
                        <span className="text-[10px] text-amber-400 font-bold">{dominoState.scores[opp.id] || 0} pts</span>
                      </div>
                      {/* Face down tiles icons */}
                      <div className="flex items-center gap-0.5 ml-2">
                        {oppHand.map((_, i) => (
                          <div key={i} className="w-2.5 h-4.5 bg-amber-800/80 border border-amber-600/50 rounded-xs" />
                        ))}
                        <span className="text-[10px] text-slate-400 ml-1 font-mono font-bold">({oppHand.length})</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Boneyard Info */}
              <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700 text-xs text-slate-300">
                <Layers className="size-4 text-amber-400" />
                <span>Boneyard: <strong className="text-white">{dominoState.boneyard.length}</strong></span>
              </div>
            </div>

            {/* Central Board Felt Chain Area */}
            <div className="flex-1 flex flex-col items-center justify-center my-3 min-h-[220px] rounded-2xl bg-radial from-slate-800/40 via-transparent to-transparent p-2">
              {dominoState.boardChain.length === 0 ? (
                <div className="text-center p-6 bg-slate-800/40 rounded-2xl border border-dashed border-slate-700 max-w-sm">
                  <span className="text-2xl mb-1 block">🀄</span>
                  <p className="text-xs font-bold text-slate-300">Board is open</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    {isMyTurn ? 'Click any tile in your hand to start the round.' : 'Waiting for first tile...'}
                  </p>
                </div>
              ) : (
                <div className="w-full flex flex-col items-center gap-2">
                  {/* Open ends badges */}
                  <div className="flex items-center justify-between w-full max-w-md px-2 text-[11px] font-bold text-[#22D3EE]">
                    <span>Left End: [{dominoState.leftOpenPip}]</span>
                    <span>Right End: [{dominoState.rightOpenPip}]</span>
                  </div>

                  {/* Horizontal Scrollable Domino Chain */}
                  <div className="w-full overflow-x-auto p-4 flex items-center justify-center gap-1.5 sm:gap-2">
                    {dominoState.boardChain.map((placed, idx) => (
                      <DominoFace
                        key={idx}
                        left={placed.renderLeft}
                        right={placed.renderRight}
                        orientation={placed.orientation}
                        isFlipped={placed.flipped}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Two-Side Choice Popup Modal (When tile matches both ends) */}
            {selectedTile && (
              <div className="absolute inset-0 z-20 bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
                <div className="bg-slate-900 border border-slate-700 rounded-3xl p-5 text-center max-w-xs w-full shadow-2xl">
                  <h4 className="text-sm font-bold text-white mb-1">Play on which end?</h4>
                  <p className="text-xs text-slate-400 mb-4">
                    Tile [{selectedTile.left}|{selectedTile.right}] can connect to either end of the chain.
                  </p>
                  <div className="flex items-center justify-center gap-3">
                    <button
                      onClick={() => {
                        playDominoTile(selectedTile.id, 'left');
                        setSelectedTile(null);
                      }}
                      className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold transition-all"
                    >
                      <ChevronLeft className="size-4" />
                      <span>Left Side</span>
                    </button>
                    <button
                      onClick={() => {
                        playDominoTile(selectedTile.id, 'right');
                        setSelectedTile(null);
                      }}
                      className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-[#1E9EF5] hover:bg-sky-500 text-white text-xs font-bold transition-all"
                    >
                      <span>Right Side</span>
                      <ChevronRight className="size-4" />
                    </button>
                  </div>
                  <button
                    onClick={() => setSelectedTile(null)}
                    className="mt-3 text-xs text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Bottom Player's Rack */}
            <div className="mt-auto border-t border-slate-800 pt-3">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-200">Your Hand ({myHand.length} tiles)</span>
                  <span className="text-[10px] text-amber-400 font-bold bg-amber-950/60 px-2 py-0.5 rounded-md border border-amber-800/60">
                    Score: {dominoState.scores[activeDemoUser.id] || 0} pts
                  </span>
                </div>

                {/* Actions: Draw or Pass */}
                {isMyTurn && (
                  <div className="flex items-center gap-2">
                    {dominoState.boneyard.length > 0 ? (
                      <button
                        onClick={drawDominoBoneyard}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold shadow-xs transition-all"
                      >
                        <Layers className="size-3.5" />
                        <span>Draw Tile ({dominoState.boneyard.length})</span>
                      </button>
                    ) : !hasAnyMove ? (
                      <button
                        onClick={passDominoTurn}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold shadow-xs transition-all"
                      >
                        <span>Pass Turn</span>
                      </button>
                    ) : null}
                  </div>
                )}
              </div>

              {/* Hand Tiles Carousel */}
              <div className="flex items-center justify-center gap-2 p-2 bg-slate-800/50 rounded-2xl border border-slate-700/60 overflow-x-auto min-h-[95px]">
                {myHand.length === 0 ? (
                  <p className="text-xs text-emerald-400 font-bold">You emptied your hand! 🎉</p>
                ) : (
                  myHand.map((tile) => {
                    const legalMoves = getLegalMovesForTile(
                      tile,
                      dominoState.boardChain,
                      dominoState.leftOpenPip,
                      dominoState.rightOpenPip
                    );
                    const isLegal = isMyTurn && legalMoves.length > 0;

                    return (
                      <DominoFace
                        key={tile.id}
                        left={tile.left}
                        right={tile.right}
                        orientation="vertical"
                        isClickable={isMyTurn && isLegal}
                        isLegal={isLegal}
                        onClick={() => handleTileClick(tile)}
                      />
                    );
                  })
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Scorecard & In-Game Chat */}
        <div className="lg:col-span-1 space-y-4">
          {/* Scoreboard Card */}
          <div className="bg-white rounded-3xl border border-slate-200 p-4 shadow-xs">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100 mb-3">
              <div className="flex items-center gap-1.5 text-xs font-extrabold text-[#0D1420]">
                <Trophy className="size-4 text-amber-500" />
                <span>Domino Leaderboard</span>
              </div>
              <span className="text-[10px] text-slate-400 font-bold uppercase">Target: {dominoState.targetScore}</span>
            </div>

            <div className="space-y-2">
              {currentRoom.players.map((p) => {
                const score = dominoState.scores[p.id] || 0;
                const percent = Math.min(100, Math.round((score / dominoState.targetScore) * 100));
                return (
                  <div key={p.id} className="p-2.5 rounded-2xl bg-slate-50 border border-slate-100">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <img src={p.avatarUrl} alt={p.displayName} className="size-6 rounded-full object-cover" />
                        <span className="text-xs font-bold text-[#0D1420]">{p.displayName}</span>
                      </div>
                      <span className="text-xs font-black text-[#1E9EF5]">{score} pts</span>
                    </div>
                    {/* Progress Bar */}
                    <div className="w-full h-1.5 rounded-full bg-slate-200 overflow-hidden">
                      <div
                        className="h-full bg-linear-to-r from-sky-400 to-[#1E9EF5] transition-all duration-300"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <GameChatTray />
        </div>
      </div>

      {/* Round / Match Win Modal */}
      {(dominoState.roundWinnerId || dominoState.matchWinnerId) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 p-4 backdrop-blur-xs">
          <div className="w-full max-w-sm rounded-3xl bg-white p-6 text-center shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-150">
            <div className="inline-flex size-14 items-center justify-center rounded-2xl bg-amber-100 text-amber-600 mb-3 shadow-sm">
              <Trophy className="size-8" />
            </div>

            <h3 className="text-xl font-extrabold text-[#0D1420]">
              {dominoState.matchWinnerId ? '🏆 GRAND MATCH VICTORY!' : '🎉 Round Completed!'}
            </h3>

            <p className="text-xs text-slate-500 mt-1 mb-4">{dominoState.roundSummary}</p>

            {/* Scoreboard table */}
            <div className="rounded-2xl bg-slate-50 p-3 mb-5 border border-slate-100 space-y-2">
              {currentRoom.players.map((p) => (
                <div key={p.id} className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#0D1420]">{p.displayName}</span>
                  <span className="font-bold text-[#1E9EF5]">{dominoState.scores[p.id] || 0} pts</span>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={leaveRoom}
                className="flex-1 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
              >
                Exit to Lobby
              </button>
              <button
                onClick={rematch}
                className="flex-1 py-2.5 rounded-xl bg-[#1E9EF5] hover:bg-sky-600 text-white text-xs font-bold shadow-xs transition-colors"
              >
                Next Round
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
