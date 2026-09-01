import React, { useState } from 'react';
import {
  FaritanyGameState,
  FaritanyPhase,
  GamePlayer,
  GameRoomDetailed,
  Territory,
} from '../types';
import { GameHeader } from '../components/GameHeader';
import { InGameChat } from '../components/InGameChat';
import { GameResultsModal } from '../components/GameResultsModal';
import {
  Shield,
  Swords,
  Coins,
  ArrowRight,
  MapPin,
  CheckCircle,
  Flag,
  Award,
  Sparkles,
  Flame,
} from 'lucide-react';

interface FaritanyGameProps {
  room: GameRoomDetailed;
  currentPlayerId: string;
  onNextPhase: () => void;
  onReinforce: (territoryId: string, count: number) => void;
  onAttack: (fromId: string, toId: string) => void;
  onLeave: () => void;
  onRematch: () => void;
  onSendMessage: (text: string) => void;
}

export const FaritanyGame: React.FC<FaritanyGameProps> = ({
  room,
  currentPlayerId,
  onNextPhase,
  onReinforce,
  onAttack,
  onLeave,
  onRematch,
  onSendMessage,
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedFromId, setSelectedFromId] = useState<string | null>(null);
  const [selectedToId, setSelectedToId] = useState<string | null>(null);

  const state = room.faritanyState;
  if (!state) return null;

  const playerIds = room.players.map((p) => p.id);
  const isMyTurn = state.currentTurnPlayerId === currentPlayerId && !state.matchWinnerId;
  const currentPlayer = room.players.find((p) => p.id === currentPlayerId) || room.players[0];
  const myResources = state.playerResources[currentPlayerId] || {
    gold: 0,
    energy: 0,
    reinforcedThisTurn: 0,
  };

  const totalTerritories = Object.keys(state.territories).length;
  const myTerritories = Object.values(state.territories).filter(
    (t) => t.ownerId === currentPlayerId
  );
  const myControlPct = Math.round((myTerritories.length / totalTerritories) * 100);

  const getPlayerColor = (ownerId: string | null): string => {
    if (!ownerId) return '#94A3B8'; // Slate neutral
    const player = room.players.find((p) => p.id === ownerId);
    return player ? player.color : '#1E9EF5';
  };

  const handleTerritoryClick = (t: Territory) => {
    if (!isMyTurn) return;

    if (state.currentPhase === 'reinforce') {
      if (t.ownerId === currentPlayerId && myResources.reinforcedThisTurn > 0) {
        onReinforce(t.id, 1);
      }
    } else if (state.currentPhase === 'attack') {
      if (t.ownerId === currentPlayerId && t.troops > 1) {
        setSelectedFromId(t.id);
        setSelectedToId(null);
      } else if (selectedFromId && t.ownerId !== currentPlayerId) {
        const fromT = state.territories[selectedFromId];
        if (fromT && fromT.adjacentIds.includes(t.id)) {
          setSelectedToId(t.id);
          onAttack(selectedFromId, t.id);
        }
      }
    }
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

        {/* Action Status Bar & Turn Phase Stepper */}
        <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-2xs space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider text-[#0D1420]">
                Faritany Realm War
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-xs font-bold text-slate-500">Turn {state.turnNumber}/25</span>
            </div>
            <div className="flex items-center gap-1 text-xs font-bold text-emerald-600">
              <Flag className="size-3.5" />
              <span>Control: {myControlPct}% (Goal: 65%)</span>
            </div>
          </div>

          {/* Phase Stepper */}
          <div className="grid grid-cols-4 gap-1.5 text-center text-[11px] font-extrabold">
            {(['harvest', 'reinforce', 'attack', 'fortify'] as FaritanyPhase[]).map((phase) => {
              const isCurrent = state.currentPhase === phase;
              return (
                <div
                  key={phase}
                  className={`rounded-xl py-1.5 uppercase transition-all ${
                    isCurrent
                      ? 'bg-[#1E9EF5] text-white shadow-xs font-black ring-2 ring-sky-200'
                      : 'bg-slate-100 text-slate-400 font-semibold'
                  }`}
                >
                  {phase}
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-between border-t border-slate-100 pt-2">
            <p className="text-xs text-slate-600 font-medium truncate">{state.lastActionSummary}</p>
            {isMyTurn && (
              <button
                onClick={onNextPhase}
                className="rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-1.5 text-xs font-bold shadow-xs active:scale-95 transition-all"
              >
                {state.currentPhase === 'fortify' ? 'End Turn →' : 'Next Phase →'}
              </button>
            )}
          </div>
        </div>

        {/* Center SVG Province Strategy Map */}
        <div className="relative mx-auto max-w-xl aspect-[4/5] w-full rounded-3xl border border-slate-800/40 bg-gradient-to-b from-[#091528] via-[#0d1f3d] to-[#081224] p-3 sm:p-4 shadow-2xl flex flex-col justify-center select-none overflow-hidden">
          {/* Subtle ocean ripple lines */}
          <div className="absolute inset-0 opacity-10 pointer-events-none bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px]" />

          <svg className="size-full" viewBox="0 0 380 680">
            {/* Territory Polygons */}
            {Object.values(state.territories).map((t) => {
              const isOwner = t.ownerId === currentPlayerId;
              const isSelected = selectedFromId === t.id;
              const isTarget = selectedToId === t.id;
              const color = getPlayerColor(t.ownerId);
              const [cx, cy] = t.center;

              return (
                <g key={t.id} onClick={() => handleTerritoryClick(t)} className="cursor-pointer">
                  {/* Territory Shape */}
                  <path
                    d={t.polygon}
                    fill={color}
                    fillOpacity={t.ownerId ? 0.85 : 0.4}
                    stroke={isSelected ? '#F59E0B' : isTarget ? '#EF4444' : 'white'}
                    strokeWidth={isSelected || isTarget ? '4' : '1.5'}
                    className="transition-all hover:fill-opacity-95"
                  />

                  {/* Troop Badge on Center */}
                  <circle
                    cx={cx}
                    cy={cy}
                    r="16"
                    fill="#0D1420"
                    stroke={color}
                    strokeWidth="3"
                    filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.5))"
                  />
                  <text
                    x={cx}
                    y={cy + 5}
                    textAnchor="middle"
                    fill="white"
                    fontSize="13"
                    fontWeight="900"
                  >
                    {t.troops}
                  </text>

                  {/* Territory Code Label */}
                  <text
                    x={cx}
                    y={cy - 20}
                    textAnchor="middle"
                    fill="white"
                    fontSize="10"
                    fontWeight="bold"
                    opacity="0.9"
                  >
                    {t.code}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Reinforcement & Tactical Resource Tray */}
        <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Coins className="size-5 text-amber-500" />
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase">Treasury Gold</p>
                <p className="text-sm font-black text-[#0D1420]">{myResources.gold} G</p>
              </div>
            </div>

            <div className="flex items-center gap-2 border-l border-slate-100 pl-4">
              <Shield className="size-5 text-emerald-500" />
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase">Available Recruits</p>
                <p className="text-sm font-black text-emerald-600">
                  +{myResources.reinforcedThisTurn} Troops
                </p>
              </div>
            </div>
          </div>

          {/* Quick Reinforce Hint */}
          {state.currentPhase === 'reinforce' && myResources.reinforcedThisTurn > 0 && isMyTurn && (
            <span className="rounded-xl bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700 border border-emerald-200 animate-pulse">
              Click any owned territory on map to deploy recruits!
            </span>
          )}

          {state.currentPhase === 'attack' && isMyTurn && (
            <span className="rounded-xl bg-rose-50 px-3 py-1.5 text-xs font-bold text-rose-700 border border-rose-200">
              Select your territory, then click an adjacent enemy to strike!
            </span>
          )}
        </div>

        {/* Recent Tactical Battle Logs */}
        {state.battleLog.length > 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-2xs space-y-2">
            <h4 className="text-xs font-bold text-[#0D1420]">Recent Battle Skirmishes</h4>
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {state.battleLog.slice(0, 3).map((log) => (
                <div
                  key={log.id}
                  className="flex items-center justify-between rounded-xl bg-slate-50 p-2 text-xs"
                >
                  <div className="flex items-center gap-2">
                    <Swords className="size-3.5 text-rose-500" />
                    <span>
                      <strong>{log.fromTerritory}</strong> struck <strong>{log.toTerritory}</strong>
                    </span>
                  </div>
                  <span
                    className={`font-bold ${log.conquered ? 'text-emerald-600' : 'text-slate-500'}`}
                  >
                    {log.conquered ? 'Territory Conquered!' : 'Defended'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
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
