import React, { useState } from 'react';
import { Radio, Sparkles, Lock, Mail, User as UserIcon, Coins, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const AuthPage: React.FC = () => {
  const { login, signup, isLoading, error } = useAuth();
  const [isLogin, setIsLogin] = useState(true);

  // Form fields
  const [identifier, setIdentifier] = useState('alex_tata');
  const [password, setPassword] = useState('password123');
  const [displayName, setDisplayName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLogin) {
      await login(identifier, password);
    } else {
      await signup(displayName, username, email, password);
    }
  };

  const handleQuickDemo = async () => {
    await login('alex_tata', 'password123');
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12">
      <div className="w-full max-w-md">
        {/* Brand Card Header */}
        <div className="mb-6 text-center">
          <div className="mx-auto flex size-14 items-center justify-center rounded-3xl bg-[#1E9EF5] text-white shadow-lg shadow-sky-200">
            <Radio className="size-7 animate-pulse" />
          </div>
          <h1 className="mt-4 text-2xl font-black tracking-tight text-[#0D1420]">
            TATA Social<span className="text-[#1E9EF5]"> 2.0</span>
          </h1>
          <p className="mt-1 text-xs sm:text-sm font-medium text-slate-500">
            Connect, share stories, message friends & earn TATA coins.
          </p>
        </div>

        {/* Auth Box */}
        <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xl">
          {/* Toggle Tab */}
          <div className="flex rounded-2xl bg-slate-100 p-1 mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 rounded-xl py-2 text-xs font-bold transition-all ${
                isLogin ? 'bg-white text-[#1E9EF5] shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 rounded-xl py-2 text-xs font-bold transition-all ${
                !isLogin ? 'bg-white text-[#1E9EF5] shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div className="mb-4 rounded-xl bg-rose-50 p-3 text-xs font-semibold text-rose-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            {isLogin ? (
              <>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                    Username or Email
                  </label>
                  <div className="relative mt-1">
                    <UserIcon className="absolute left-3.5 top-3 size-4 text-slate-400" />
                    <input
                      type="text"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      placeholder="alex_tata or alex@tata.social"
                      className="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-3 text-xs sm:text-sm font-medium text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                    Password
                  </label>
                  <div className="relative mt-1">
                    <Lock className="absolute left-3.5 top-3 size-4 text-slate-400" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-3 text-xs sm:text-sm font-medium text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
                      required
                    />
                  </div>
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                    Full Display Name
                  </label>
                  <input
                    type="text"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="Jordan Lee"
                    className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs sm:text-sm font-medium text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                    Username handle
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="jordan_lee"
                    className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs sm:text-sm font-medium text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="jordan@example.com"
                    className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs sm:text-sm font-medium text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Create a strong password"
                    className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs sm:text-sm font-medium text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden"
                    required
                  />
                </div>

                <div className="rounded-xl bg-sky-50 p-2.5 text-xs text-sky-800 flex items-center gap-2">
                  <Coins className="size-4 text-[#1E9EF5] shrink-0" />
                  <span>Includes <strong>+500 TATA Coins</strong> instant welcome grant!</span>
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-2xl bg-[#1E9EF5] py-3 text-xs sm:text-sm font-bold text-white shadow-md shadow-sky-200 hover:bg-sky-600 active:scale-[0.98] disabled:opacity-50 transition-all"
            >
              <span>{isLoading ? 'Authenticating...' : isLogin ? 'Sign In to TATA' : 'Join TATA Social'}</span>
              <ArrowRight className="size-4" />
            </button>
          </form>

          {/* Quick Demo Access Button */}
          <div className="mt-5 border-t border-slate-100 pt-4">
            <button
              onClick={handleQuickDemo}
              type="button"
              className="flex w-full items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <Sparkles className="size-3.5 text-[#1E9EF5]" />
              <span>Instant Demo Account (Alex Rivers)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
