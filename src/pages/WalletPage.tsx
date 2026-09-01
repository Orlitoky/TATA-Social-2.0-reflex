import React, { useState } from 'react';
import {
  Coins,
  Gift,
  ArrowUpRight,
  ArrowDownLeft,
  Sparkles,
  Send,
  History,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSocial } from '../context/SocialContext';
import confetti from 'canvas-confetti';

export const WalletPage: React.FC = () => {
  const { currentUser, coinTransactions, addCoins, claimDailyReward, hasClaimedDaily } = useAuth();
  const { users } = useSocial();

  const [recipientUsername, setRecipientUsername] = useState('');
  const [tipAmount, setTipAmount] = useState('50');
  const [tipNote, setTipNote] = useState('');

  if (!currentUser) return null;

  const handleSendTip = (e: React.FormEvent) => {
    e.preventDefault();
    const amount = parseInt(tipAmount, 10);
    if (isNaN(amount) || amount <= 0) return;

    if (currentUser.coinBalance < amount) {
      alert('Insufficient coin balance.');
      return;
    }

    const targetUser = users.find(
      (u) =>
        u.username.toLowerCase() === recipientUsername.toLowerCase().replace('@', '') ||
        u.displayName.toLowerCase() === recipientUsername.toLowerCase()
    );

    const recipientName = targetUser ? targetUser.displayName : recipientUsername;

    addCoins(-amount, `Sent ${amount} coins tip to ${recipientName}${tipNote ? ` ("${tipNote}")` : ''}`, 'gift_sent');
    alert(`Successfully transferred ${amount} TATA Coins to ${recipientName}!`);
    setRecipientUsername('');
    setTipNote('');
    confetti({ particleCount: 50, spread: 60 });
  };

  return (
    <div className="flex flex-col gap-5">
      {/* Wallet Balance Card */}
      <div className="relative overflow-hidden rounded-3xl border border-sky-100 bg-gradient-to-br from-[#1E9EF5] to-blue-700 p-6 sm:p-8 text-white shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-1.5">
              <span className="rounded-full bg-white/20 px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-white">
                Virtual Ledger
              </span>
            </div>
            <span className="mt-2 block text-xs font-semibold text-white/80">Total TATA Coins Balance</span>
            <div className="flex items-baseline gap-2">
              <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white">
                {currentUser.coinBalance.toLocaleString()}
              </h1>
              <span className="text-sm font-bold text-sky-200">coins</span>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <button
              onClick={claimDailyReward}
              disabled={hasClaimedDaily}
              className={`flex items-center justify-center gap-2 rounded-2xl px-5 py-3 text-xs font-bold transition-all shadow-md ${
                hasClaimedDaily
                  ? 'bg-white/20 text-white/60 cursor-not-allowed'
                  : 'bg-white text-[#1E9EF5] hover:bg-sky-50 active:scale-95'
              }`}
            >
              <Gift className="size-4" />
              <span>{hasClaimedDaily ? 'Daily Bonus Claimed' : 'Claim Daily +100 Coins'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Send Coins / Tip Form & Quick Ways to Earn */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Tip Friend Form */}
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Send className="size-5 text-[#1E9EF5]" />
            <h2 className="text-base font-bold text-[#0D1420]">Tip or Transfer Coins</h2>
          </div>

          <form onSubmit={handleSendTip} className="mt-4 space-y-3">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                Recipient (Username or Name)
              </label>
              <input
                type="text"
                value={recipientUsername}
                onChange={(e) => setRecipientUsername(e.target.value)}
                placeholder="e.g. sophia.chen or Marcus Vance"
                className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2 text-xs font-medium text-[#0D1420] focus:border-[#1E9EF5] outline-hidden"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                  Amount
                </label>
                <input
                  type="number"
                  value={tipAmount}
                  onChange={(e) => setTipAmount(e.target.value)}
                  min="10"
                  max={currentUser.coinBalance}
                  className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2 text-xs font-medium text-[#0D1420] focus:border-[#1E9EF5] outline-hidden"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                  Quick Amount
                </label>
                <div className="mt-1 flex gap-1">
                  {['25', '50', '100'].map((val) => (
                    <button
                      key={val}
                      type="button"
                      onClick={() => setTipAmount(val)}
                      className="flex-1 rounded-xl border border-slate-200 bg-slate-50 py-1.5 text-xs font-bold text-slate-600 hover:bg-sky-50 hover:text-[#1E9EF5]"
                    >
                      {val}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                Optional Message
              </label>
              <input
                type="text"
                value={tipNote}
                onChange={(e) => setTipNote(e.target.value)}
                placeholder="Thanks for the great post!"
                className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2 text-xs font-medium text-[#0D1420] focus:border-[#1E9EF5] outline-hidden"
              />
            </div>

            <button
              type="submit"
              disabled={!recipientUsername.trim()}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#1E9EF5] py-2.5 text-xs font-bold text-white shadow-xs hover:bg-sky-600 active:scale-98 disabled:opacity-50"
            >
              <Send className="size-3.5" />
              <span>Send Tip</span>
            </button>
          </form>
        </div>

        {/* Ways to Earn Card */}
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Sparkles className="size-5 text-[#1E9EF5]" />
            <h2 className="text-base font-bold text-[#0D1420]">How to Earn TATA Coins</h2>
          </div>

          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between rounded-2xl bg-sky-50/70 p-3">
              <div>
                <p className="text-xs font-bold text-[#0D1420]">Daily Login Streak</p>
                <p className="text-[11px] text-slate-500">Visit daily to claim rewards</p>
              </div>
              <span className="rounded-full bg-white px-2.5 py-1 text-xs font-extrabold text-[#1E9EF5] shadow-xs">
                +100 Coins
              </span>
            </div>

            <div className="flex items-center justify-between rounded-2xl bg-sky-50/70 p-3">
              <div>
                <p className="text-xs font-bold text-[#0D1420]">Publish Community Posts</p>
                <p className="text-[11px] text-slate-500">Share updates and photos</p>
              </div>
              <span className="rounded-full bg-white px-2.5 py-1 text-xs font-extrabold text-[#1E9EF5] shadow-xs">
                +10 Coins / Post
              </span>
            </div>

            <div className="flex items-center justify-between rounded-2xl bg-sky-50/70 p-3">
              <div>
                <p className="text-xs font-bold text-[#0D1420]">Share a 24h Story</p>
                <p className="text-[11px] text-slate-500">Post quick visual moments</p>
              </div>
              <span className="rounded-full bg-white px-2.5 py-1 text-xs font-extrabold text-[#1E9EF5] shadow-xs">
                +15 Coins / Story
              </span>
            </div>

            <div className="flex items-center justify-between rounded-2xl bg-sky-50/70 p-3">
              <div>
                <p className="text-xs font-bold text-[#0D1420]">Play Arcade Mini-Games</p>
                <p className="text-[11px] text-slate-500">Trivia Blitz, Dice Duel, Coin Flip</p>
              </div>
              <span className="rounded-full bg-white px-2.5 py-1 text-xs font-extrabold text-emerald-600 shadow-xs">
                Up to +150 Coins
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Transaction History Ledger */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <History className="size-5 text-[#1E9EF5]" />
            <h2 className="text-base font-bold text-[#0D1420]">Transaction History</h2>
          </div>
          <span className="text-xs font-semibold text-slate-400">
            {coinTransactions.length} recorded events
          </span>
        </div>

        <div className="mt-3 divide-y divide-slate-100">
          {coinTransactions.map((tx) => {
            const isPositive = tx.amount > 0;
            return (
              <div key={tx.id} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex size-9 items-center justify-center rounded-2xl ${
                      isPositive ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'
                    }`}
                  >
                    {isPositive ? (
                      <ArrowDownLeft className="size-4" />
                    ) : (
                      <ArrowUpRight className="size-4" />
                    )}
                  </div>
                  <div>
                    <p className="text-xs sm:text-sm font-bold text-[#0D1420]">{tx.description}</p>
                    <span className="text-[11px] text-slate-400">{tx.timestamp}</span>
                  </div>
                </div>

                <div
                  className={`text-xs sm:text-sm font-black ${
                    isPositive ? 'text-emerald-600' : 'text-slate-700'
                  }`}
                >
                  {isPositive ? `+${tx.amount}` : tx.amount} coins
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
