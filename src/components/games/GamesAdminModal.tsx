import React, { useState, useEffect } from 'react';
import { useGames, TEST_PROFILES } from '../../context/GamesContext';
import {
  Shield,
  X,
  Coins,
  Activity,
  Layers,
  Settings,
  Trash2,
  CheckCircle,
  PlusCircle,
  Sparkles,
  RefreshCw,
} from 'lucide-react';

interface GamesAdminModalProps {
  onClose: () => void;
}

export const GamesAdminModal: React.FC<GamesAdminModalProps> = ({ onClose }) => {
  const { publicRooms, adminGrantCoins, adminCloseRoom, activeDemoUser } = useGames();
  const [activeTab, setActiveTab] = useState<'rooms' | 'ledger' | 'settings'>('rooms');
  const [selectedUser, setSelectedUser] = useState(activeDemoUser.id);
  const [grantAmount, setGrantAmount] = useState(500);
  const [grantSuccess, setGrantSuccess] = useState(false);
  const [ledgerLogs, setLedgerLogs] = useState<any[]>([]);

  const fetchAdminData = async () => {
    try {
      const res = await fetch('/api/admin/overview');
      if (res.ok) {
        const data = await res.json();
        if (data.ledger) {
          setLedgerLogs(data.ledger);
        }
      }
    } catch {
      // Fallback
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleGrant = async () => {
    await adminGrantCoins(selectedUser, grantAmount, 'Admin Test Grant');
    setGrantSuccess(true);
    fetchAdminData();
    setTimeout(() => setGrantSuccess(false), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 p-3 sm:p-4 backdrop-blur-xs">
      <div className="w-full max-w-2xl rounded-3xl bg-white p-5 sm:p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 duration-150 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="flex size-9 items-center justify-center rounded-2xl bg-gradient-to-tr from-sky-600 to-[#1E9EF5] text-white shadow-xs">
              <Shield className="size-5" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-[#0D1420]">TATA Games Hub Admin Panel</h3>
              <p className="text-xs text-slate-400">Manage active rooms, player ledger, and game configurations</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex size-8 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100"
          >
            <X className="size-4" />
          </button>
        </div>

        {/* Tab switcher */}
        <div className="flex items-center gap-2 mt-4 border-b border-slate-100 pb-2">
          <button
            onClick={() => setActiveTab('rooms')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors ${
              activeTab === 'rooms'
                ? 'bg-sky-50 text-[#1E9EF5]'
                : 'text-slate-500 hover:bg-slate-50'
            }`}
          >
            <Activity className="size-3.5" />
            <span>Active Rooms ({publicRooms.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('ledger')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors ${
              activeTab === 'ledger'
                ? 'bg-sky-50 text-[#1E9EF5]'
                : 'text-slate-500 hover:bg-slate-50'
            }`}
          >
            <Coins className="size-3.5" />
            <span>Virtual Coins Faucet</span>
          </button>

          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors ${
              activeTab === 'settings'
                ? 'bg-sky-50 text-[#1E9EF5]'
                : 'text-slate-500 hover:bg-slate-50'
            }`}
          >
            <Settings className="size-3.5" />
            <span>Game Rules</span>
          </button>
        </div>

        {/* Body content */}
        <div className="flex-1 overflow-y-auto py-4">
          {activeTab === 'rooms' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase">Live Server Rooms</span>
                <button
                  onClick={fetchAdminData}
                  className="flex items-center gap-1 text-xs text-[#1E9EF5] font-semibold hover:underline"
                >
                  <RefreshCw className="size-3" /> Refresh
                </button>
              </div>

              {publicRooms.length === 0 ? (
                <p className="text-center text-xs text-slate-400 py-6">No active rooms at this time.</p>
              ) : (
                publicRooms.map((room) => (
                  <div
                    key={room.id}
                    className="flex items-center justify-between p-3 rounded-2xl border border-slate-200 bg-slate-50/60"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-[#0D1420]">{room.title}</span>
                        <span className="font-mono text-[10px] bg-slate-200 px-1.5 py-0.5 rounded-md font-bold">
                          {room.code}
                        </span>
                        <span className="text-[10px] uppercase font-bold text-[#1E9EF5] bg-sky-50 px-2 py-0.5 rounded-md">
                          {room.gameType}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Players: {room.players.length}/{room.maxPlayers} • Status: {room.status} • Prize: {room.prizePool} coins
                      </p>
                    </div>

                    <button
                      onClick={() => adminCloseRoom(room.id)}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-rose-50 text-rose-600 hover:bg-rose-100 text-xs font-bold transition-colors"
                    >
                      <Trash2 className="size-3.5" />
                      <span>Terminate</span>
                    </button>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'ledger' && (
            <div className="space-y-4">
              {/* Grant Faucet */}
              <div className="rounded-2xl border border-sky-100 bg-gradient-to-r from-sky-50 to-cyan-50 p-4">
                <div className="flex items-center gap-2 text-[#1E9EF5] font-bold text-xs mb-3">
                  <Coins className="size-4" />
                  <span>Test Coin Faucet (Instant Sandbox Grant)</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="text-[11px] font-bold text-slate-600 block mb-1">Select Profile</label>
                    <select
                      value={selectedUser}
                      onChange={(e) => setSelectedUser(e.target.value)}
                      className="w-full rounded-xl bg-white border border-slate-200 p-2 text-xs font-medium text-[#0D1420] focus:outline-hidden focus:border-[#1E9EF5]"
                    >
                      {TEST_PROFILES.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.displayName} (@{p.username})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-slate-600 block mb-1">Amount (Virtual Coins)</label>
                    <select
                      value={grantAmount}
                      onChange={(e) => setGrantAmount(Number(e.target.value))}
                      className="w-full rounded-xl bg-white border border-slate-200 p-2 text-xs font-medium text-[#0D1420] focus:outline-hidden focus:border-[#1E9EF5]"
                    >
                      <option value={200}>+200 Coins</option>
                      <option value={500}>+500 Coins</option>
                      <option value={1000}>+1,000 Coins</option>
                      <option value={5000}>+5,000 Coins</option>
                    </select>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between">
                  {grantSuccess ? (
                    <span className="flex items-center gap-1 text-xs font-bold text-emerald-600">
                      <CheckCircle className="size-4" /> Coins granted successfully!
                    </span>
                  ) : <span />}

                  <button
                    onClick={handleGrant}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#1E9EF5] text-white text-xs font-bold hover:bg-sky-600 transition-colors shadow-xs"
                  >
                    <PlusCircle className="size-3.5" />
                    <span>Grant Virtual Coins</span>
                  </button>
                </div>
              </div>

              {/* Recent Ledger Audit Logs */}
              <div>
                <span className="text-xs font-bold text-slate-500 uppercase block mb-2">Ledger Audit Logs</span>
                <div className="rounded-2xl border border-slate-200 divide-y divide-slate-100 max-h-48 overflow-y-auto">
                  {ledgerLogs.length === 0 ? (
                    <p className="p-3 text-center text-xs text-slate-400">No transactions recorded yet.</p>
                  ) : (
                    ledgerLogs.map((tx) => (
                      <div key={tx.id} className="flex items-center justify-between p-2.5 text-xs">
                        <div>
                          <p className="font-semibold text-[#0D1420]">{tx.description}</p>
                          <p className="text-[10px] text-slate-400">{tx.userId} • {tx.timestamp}</p>
                        </div>
                        <span className="font-extrabold text-emerald-600">+{tx.amount} coins</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-2xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                <div>
                  <p className="font-bold text-[#0D1420]">DOMINO Engine</p>
                  <p className="text-[11px] text-slate-400">Double-six 28-tile matching and blocked score resolution</p>
                </div>
                <span className="px-2 py-1 rounded-lg bg-emerald-100 text-emerald-700 font-bold text-[10px]">
                  ACTIVE / READY
                </span>
              </div>

              <div className="p-3 rounded-2xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                <div>
                  <p className="font-bold text-[#0D1420]">LUDO 4-Player Engine</p>
                  <p className="text-[11px] text-slate-400">15x15 board circuit, yard deployment on 6, and safe zones</p>
                </div>
                <span className="px-2 py-1 rounded-lg bg-emerald-100 text-emerald-700 font-bold text-[10px]">
                  ACTIVE / READY
                </span>
              </div>

              <div className="p-3 rounded-2xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                <div>
                  <p className="font-bold text-[#0D1420]">LOTO / BINGO Drum Caller</p>
                  <p className="text-[11px] text-slate-400">75-ball drawing pool, auto-dauber, and Line/Bingo payouts</p>
                </div>
                <span className="px-2 py-1 rounded-lg bg-emerald-100 text-emerald-700 font-bold text-[10px]">
                  ACTIVE / READY
                </span>
              </div>

              <div className="p-3 rounded-2xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                <div>
                  <p className="font-bold text-[#0D1420]">FARITANY Strategic War Engine</p>
                  <p className="text-[11px] text-slate-400">14 territory tactical map, dice combat, reinforcement formulas</p>
                </div>
                <span className="px-2 py-1 rounded-lg bg-emerald-100 text-emerald-700 font-bold text-[10px]">
                  ACTIVE / READY
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors"
          >
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
};
