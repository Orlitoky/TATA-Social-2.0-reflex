import React, { useState } from 'react';
import { AdminSystemStats, GameHistoryEntry, GameRoomDetailed, GameType } from '../types';
import {
  ShieldAlert,
  Users,
  Gamepad2,
  Coins,
  Activity,
  Trash2,
  CheckCircle,
  XCircle,
  RefreshCw,
  Eye,
  Sliders,
  Sparkles,
  ArrowLeft,
} from 'lucide-react';

interface AdminDashboardProps {
  stats: AdminSystemStats;
  rooms: GameRoomDetailed[];
  history: GameHistoryEntry[];
  onClose: () => void;
  onForceCloseRoom: (roomId: string) => void;
  onGrantCoins: (amount: number) => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({
  stats,
  rooms,
  history,
  onClose,
  onForceCloseRoom,
  onGrantCoins,
}) => {
  const [activeTab, setActiveTab] = useState<'rooms' | 'players' | 'ledger' | 'config'>('rooms');
  const [coinGrantAmount, setCoinGrantAmount] = useState(5000);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs animate-fadeIn">
      <div className="flex flex-col w-full max-w-4xl max-h-[90vh] rounded-3xl border border-slate-200 bg-white shadow-2xl overflow-hidden">
        {/* Admin Header */}
        <div className="flex items-center justify-between border-b border-slate-100 bg-[#0D1420] p-4 text-white">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-2xl bg-cyan-500/20 text-cyan-400 border border-cyan-400/30">
              <ShieldAlert className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-black">TATA Games Hub Admin & Arbiter</h2>
                <span className="rounded-full bg-cyan-400/20 px-2 py-0.5 text-[10px] font-extrabold text-cyan-300 border border-cyan-400/30">
                  SYSTEM SUPERVISOR
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Server-authoritative state monitoring, live match arbitration, and coin ledger audit.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-xl bg-white/10 hover:bg-white/20 p-2 text-white transition-colors"
          >
            <ArrowLeft className="size-4.5" />
          </button>
        </div>

        {/* System KPI Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-50/70 border-b border-slate-100">
          <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-2xs">
            <div className="flex items-center gap-2 text-sky-600 mb-1">
              <Gamepad2 className="size-4" />
              <span className="text-[10px] font-bold uppercase tracking-wider">Active Rooms</span>
            </div>
            <p className="text-xl font-black text-[#0D1420]">{rooms.length}</p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-2xs">
            <div className="flex items-center gap-2 text-emerald-600 mb-1">
              <Users className="size-4" />
              <span className="text-[10px] font-bold uppercase tracking-wider">Connected Players</span>
            </div>
            <p className="text-xl font-black text-[#0D1420]">
              {rooms.reduce((sum, r) => sum + r.players.length, 0)}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-2xs">
            <div className="flex items-center gap-2 text-amber-600 mb-1">
              <Coins className="size-4" />
              <span className="text-[10px] font-bold uppercase tracking-wider">Matches Recorded</span>
            </div>
            <p className="text-xl font-black text-[#0D1420]">{history.length}</p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-2xs">
            <div className="flex items-center gap-2 text-purple-600 mb-1">
              <Activity className="size-4" />
              <span className="text-[10px] font-bold uppercase tracking-wider">Total Virtual Coins</span>
            </div>
            <p className="text-xl font-black text-[#0D1420]">
              {history.reduce((sum, h) => sum + h.prizePool, 0).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 px-4 pt-3 border-b border-slate-100">
          {[
            { id: 'rooms', label: 'Active Rooms', icon: Gamepad2 },
            { id: 'players', label: 'Player Economy & Demo Coins', icon: Coins },
            { id: 'ledger', label: 'Match History & Audit', icon: Activity },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 border-b-2 px-3 py-2 text-xs font-bold transition-all ${
                  isActive
                    ? 'border-[#1E9EF5] text-[#1E9EF5]'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <Icon className="size-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {activeTab === 'rooms' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Live Game Arenas
                </h3>
                <span className="text-xs text-slate-500 font-medium">{rooms.length} active</span>
              </div>

              {rooms.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-200 p-8 text-center text-xs text-slate-400">
                  No active multiplayer rooms running at the moment.
                </div>
              ) : (
                <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200 bg-white">
                  {rooms.map((room) => (
                    <div
                      key={room.id}
                      className="flex flex-wrap items-center justify-between gap-3 p-3.5 hover:bg-slate-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="rounded-lg bg-sky-100 px-2 py-1 text-xs font-black text-[#1E9EF5] uppercase">
                          {room.gameType}
                        </span>
                        <div>
                          <p className="text-xs font-bold text-[#0D1420]">{room.title}</p>
                          <p className="text-[11px] text-slate-400">
                            Code: <strong>{room.code}</strong> • Status: {room.status} • {room.players.length} players
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => onForceCloseRoom(room.id)}
                          className="flex items-center gap-1 rounded-xl bg-rose-50 hover:bg-rose-100 px-3 py-1.5 text-xs font-bold text-rose-600 transition-colors"
                        >
                          <Trash2 className="size-3.5" />
                          <span>Force Close</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'players' && (
            <div className="space-y-4">
              <div className="rounded-2xl border border-sky-100 bg-sky-50/70 p-4">
                <h4 className="text-xs font-black uppercase text-sky-900 mb-1">
                  Test Mint Virtual TATA Coins
                </h4>
                <p className="text-xs text-sky-700 mb-3">
                  Inject demo virtual currency directly into test accounts for rapid gameplay simulation.
                </p>

                <div className="flex items-center gap-2 max-w-sm">
                  <input
                    type="number"
                    value={coinGrantAmount}
                    onChange={(e) => setCoinGrantAmount(Number(e.target.value))}
                    className="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-[#0D1420]"
                  />
                  <button
                    onClick={() => onGrantCoins(coinGrantAmount)}
                    className="rounded-xl bg-[#1E9EF5] hover:bg-sky-600 text-white px-4 py-2 text-xs font-black transition-colors"
                  >
                    Grant Coins
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'ledger' && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Match Result Ledger & Audit Log
              </h3>

              {history.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-200 p-8 text-center text-xs text-slate-400">
                  No completed matches recorded in this session yet.
                </div>
              ) : (
                <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200 bg-white">
                  {history.map((h) => (
                    <div
                      key={h.id}
                      className="flex items-center justify-between p-3.5 hover:bg-slate-50 text-xs"
                    >
                      <div className="flex items-center gap-3">
                        <span className="rounded-lg bg-emerald-100 px-2 py-0.5 text-[10px] font-black text-emerald-800 uppercase">
                          {h.gameType}
                        </span>
                        <div>
                          <p className="font-bold text-[#0D1420]">
                            Winner: <strong className="text-emerald-600">{h.winnerName}</strong>
                          </p>
                          <p className="text-[10px] text-slate-400">
                            Room {h.roomCode} • Played at {h.playedAt} • Duration {h.durationSeconds}s
                          </p>
                        </div>
                      </div>

                      <span className="font-black text-amber-600">+{h.prizePool} coins</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
