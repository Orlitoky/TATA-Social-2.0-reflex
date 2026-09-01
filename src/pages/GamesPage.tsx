import React, { useState, useEffect } from 'react';
import { GamePlayer, GameRoomDetailed, GameType, RoomSettings } from '../games/types';
import { DEMO_TEST_PLAYERS, gameManager } from '../games/roomStore';
import { DemoPlayerSwitcher } from '../games/components/DemoPlayerSwitcher';
import { RoomLobby } from '../games/components/RoomLobby';
import { DominoGame } from '../games/domino/DominoGame';
import { LudoGame } from '../games/ludo/LudoGame';
import { BingoGame } from '../games/bingo/BingoGame';
import { FaritanyGame } from '../games/faritany/FaritanyGame';
import { AdminDashboard } from '../games/components/AdminDashboard';
import { useAuth } from '../context/AuthContext';
import { sounds } from '../games/audio';
import {
  Gamepad2,
  Trophy,
  Users,
  Play,
  PlusCircle,
  LogIn,
  Coins,
  Shield,
  Layers,
  Dices,
  Sparkles,
  Search,
  BookOpen,
  Info,
  Radio,
  Flame,
  ArrowRight,
  ShieldAlert,
  X,
  Zap,
} from 'lucide-react';

interface GameInfoCard {
  type: GameType;
  title: string;
  tagline: string;
  description: string;
  icon: React.ElementType;
  color: string;
  badge: string;
  onlineCount: number;
  playersText: string;
  bgGradient: string;
}

const GAME_CARDS: GameInfoCard[] = [
  {
    type: 'domino',
    title: 'DOMINO',
    tagline: 'Classic Double-Six Dominoes',
    description:
      'Strategic tile placement matching open ends. Play down to 0 tiles to declare Domino or lock the board with lowest pips!',
    icon: Layers,
    color: '#1E9EF5',
    badge: 'POPULAR',
    onlineCount: 1420,
    playersText: '2 Players',
    bgGradient: 'from-sky-500/10 via-sky-500/5 to-transparent',
  },
  {
    type: 'ludo',
    title: 'LUDO',
    tagline: '4-Player Board Championship',
    description:
      'Roll 6 to launch tokens from base yard. Navigate the 52-step track, capture opponent tokens for bonus turns, and race to center home!',
    icon: Dices,
    color: '#EF4444',
    badge: 'TRENDING',
    onlineCount: 2850,
    playersText: '2-4 Players',
    bgGradient: 'from-rose-500/10 via-rose-500/5 to-transparent',
  },
  {
    type: 'bingo',
    title: 'LOTO / BINGO',
    tagline: '75-Ball Live Hopper & Cards',
    description:
      'Fast-paced numbers game. Complete 5-number horizontal, vertical or diagonal lines, or complete full card for the grand BINGO pot!',
    icon: Sparkles,
    color: '#F59E0B',
    badge: 'JACKPOT',
    onlineCount: 3110,
    playersText: '2-4 Players',
    bgGradient: 'from-amber-500/10 via-amber-500/5 to-transparent',
  },
  {
    type: 'faritany',
    title: 'FARITANY',
    tagline: 'Original Province Territory Strategy',
    description:
      'Command regional provinces, harvest treasury gold, deploy tactical reinforcements, and launch dice-backed invasions to control 65% of the island!',
    icon: Shield,
    color: '#10B981',
    badge: 'ORIGINAL STRATEGY',
    onlineCount: 980,
    playersText: '2-4 Players',
    bgGradient: 'from-emerald-500/10 via-emerald-500/5 to-transparent',
  },
];

export const GamesPage: React.FC = () => {
  const { currentUser, addCoins } = useAuth();
  const [activeRoom, setActiveRoom] = useState<GameRoomDetailed | null>(gameManager.getActiveRoom());
  const [currentActivePlayerId, setCurrentActivePlayerId] = useState<string>(
    gameManager.getCurrentActivePlayerId()
  );
  const [rooms, setRooms] = useState<GameRoomDetailed[]>(gameManager.getAllRooms());
  const [history, setHistory] = useState(gameManager.getGameHistory());

  // Modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [rulesModalGame, setRulesModalGame] = useState<GameType | null>(null);

  // Form states for Create Room
  const [createGameType, setCreateGameType] = useState<GameType>('domino');
  const [createTitle, setCreateTitle] = useState('');
  const [createMaxPlayers, setCreateMaxPlayers] = useState(2);
  const [createEntryFee, setCreateEntryFee] = useState(100);
  const [createTargetScore, setCreateTargetScore] = useState<50 | 100 | 120 | 150>(100);

  // Form state for Join Room
  const [joinCodeInput, setJoinCodeInput] = useState('');
  const [joinError, setJoinError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = gameManager.subscribe(() => {
      setActiveRoom(gameManager.getActiveRoom());
      setCurrentActivePlayerId(gameManager.getCurrentActivePlayerId());
      setRooms(gameManager.getAllRooms());
      setHistory(gameManager.getGameHistory());
    });
    return () => unsubscribe();
  }, []);

  const handleSelectDemoPlayer = (pid: string) => {
    gameManager.setCurrentActivePlayerId(pid);
    sounds.playClick();
  };

  const handleQuickPlay = (gameType: GameType) => {
    sounds.playClick();
    gameManager.startQuickPlay(gameType, true);
  };

  const handleCreateRoomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const hostPlayer =
      DEMO_TEST_PLAYERS.find((p) => p.id === currentActivePlayerId) || DEMO_TEST_PLAYERS[0];
    gameManager.createRoom(
      createGameType,
      createTitle || `${createGameType.toUpperCase()} Room`,
      {
        maxPlayers: createMaxPlayers,
        entryFee: createEntryFee,
        targetScore: createTargetScore,
      } as any,
      hostPlayer
    );
    setIsCreateModalOpen(false);
    sounds.playClick();
  };

  const handleJoinSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setJoinError(null);
    const player =
      DEMO_TEST_PLAYERS.find((p) => p.id === currentActivePlayerId) || DEMO_TEST_PLAYERS[1];
    const ok = gameManager.joinRoomByCode(joinCodeInput, player);
    if (ok) {
      setIsJoinModalOpen(false);
      setJoinCodeInput('');
    } else {
      setJoinError('Invalid room code or room is already full!');
      sounds.playError();
    }
  };

  // Active game actions
  const handleLeaveRoom = () => {
    if (activeRoom) {
      gameManager.removePlayer(activeRoom.id, currentActivePlayerId);
      gameManager.setActiveRoom(null);
    }
  };

  const handleStartGame = () => {
    if (activeRoom) {
      gameManager.startGame(activeRoom.id);
    }
  };

  const handleAddBot = () => {
    if (activeRoom) {
      gameManager.addBotToRoom(activeRoom.id);
    }
  };

  const handleToggleReady = () => {
    if (activeRoom) {
      gameManager.toggleReady(activeRoom.id, currentActivePlayerId);
    }
  };

  const handleRemovePlayer = (pid: string) => {
    if (activeRoom) {
      gameManager.removePlayer(activeRoom.id, pid);
    }
  };

  const handleSendMessage = (text: string) => {
    if (activeRoom) {
      const sender =
        DEMO_TEST_PLAYERS.find((p) => p.id === currentActivePlayerId) || DEMO_TEST_PLAYERS[0];
      gameManager.sendChatMessage(activeRoom.id, text, sender);
    }
  };

  const handleRematch = () => {
    if (activeRoom) {
      gameManager.voteRematch(activeRoom.id, currentActivePlayerId);
    }
  };

  // IF ACTIVE ROOM IS LOADED, RENDER APPROPRIATE VIEW
  if (activeRoom) {
    if (activeRoom.status === 'waiting') {
      return (
        <div className="space-y-4">
          <DemoPlayerSwitcher
            currentActivePlayerId={currentActivePlayerId}
            onSelectPlayer={handleSelectDemoPlayer}
            onQuickReset={() => gameManager.resetMatch(activeRoom.id)}
            onOpenAdmin={() => setIsAdminOpen(true)}
          />
          <RoomLobby
            room={activeRoom}
            currentPlayerId={currentActivePlayerId}
            onToggleReady={handleToggleReady}
            onStartGame={handleStartGame}
            onAddBot={handleAddBot}
            onRemovePlayer={handleRemovePlayer}
            onLeave={handleLeaveRoom}
          />
          {isAdminOpen && (
            <AdminDashboard
              stats={gameManager.getAdminStats()}
              rooms={rooms}
              history={history}
              onClose={() => setIsAdminOpen(false)}
              onForceCloseRoom={(id) => gameManager.removePlayer(id, activeRoom.hostId)}
              onGrantCoins={(amt) => addCoins(amt, 'Admin demo grant')}
            />
          )}
        </div>
      );
    }

    if (activeRoom.gameType === 'domino') {
      return (
        <div className="space-y-4">
          <DemoPlayerSwitcher
            currentActivePlayerId={currentActivePlayerId}
            onSelectPlayer={handleSelectDemoPlayer}
            onQuickReset={() => gameManager.resetMatch(activeRoom.id)}
            onOpenAdmin={() => setIsAdminOpen(true)}
          />
          <DominoGame
            room={activeRoom}
            currentPlayerId={currentActivePlayerId}
            onPlayTile={(idx, side) =>
              gameManager.dominoPlayTile(activeRoom.id, currentActivePlayerId, idx, side)
            }
            onDraw={() => gameManager.dominoDraw(activeRoom.id, currentActivePlayerId)}
            onPass={() => gameManager.dominoPass(activeRoom.id, currentActivePlayerId)}
            onNextRound={() => gameManager.dominoNextRound(activeRoom.id)}
            onLeave={handleLeaveRoom}
            onRematch={handleRematch}
            onSendMessage={handleSendMessage}
          />
          {isAdminOpen && (
            <AdminDashboard
              stats={gameManager.getAdminStats()}
              rooms={rooms}
              history={history}
              onClose={() => setIsAdminOpen(false)}
              onForceCloseRoom={(id) => gameManager.removePlayer(id, activeRoom.hostId)}
              onGrantCoins={(amt) => addCoins(amt, 'Admin demo grant')}
            />
          )}
        </div>
      );
    }

    if (activeRoom.gameType === 'ludo') {
      return (
        <div className="space-y-4">
          <DemoPlayerSwitcher
            currentActivePlayerId={currentActivePlayerId}
            onSelectPlayer={handleSelectDemoPlayer}
            onQuickReset={() => gameManager.resetMatch(activeRoom.id)}
            onOpenAdmin={() => setIsAdminOpen(true)}
          />
          <LudoGame
            room={activeRoom}
            currentPlayerId={currentActivePlayerId}
            onRoll={() => gameManager.ludoRoll(activeRoom.id, currentActivePlayerId)}
            onMovePiece={(pid) => gameManager.ludoMove(activeRoom.id, currentActivePlayerId, pid)}
            onLeave={handleLeaveRoom}
            onRematch={handleRematch}
            onSendMessage={handleSendMessage}
          />
          {isAdminOpen && (
            <AdminDashboard
              stats={gameManager.getAdminStats()}
              rooms={rooms}
              history={history}
              onClose={() => setIsAdminOpen(false)}
              onForceCloseRoom={(id) => gameManager.removePlayer(id, activeRoom.hostId)}
              onGrantCoins={(amt) => addCoins(amt, 'Admin demo grant')}
            />
          )}
        </div>
      );
    }

    if (activeRoom.gameType === 'bingo') {
      return (
        <div className="space-y-4">
          <DemoPlayerSwitcher
            currentActivePlayerId={currentActivePlayerId}
            onSelectPlayer={handleSelectDemoPlayer}
            onQuickReset={() => gameManager.resetMatch(activeRoom.id)}
            onOpenAdmin={() => setIsAdminOpen(true)}
          />
          <BingoGame
            room={activeRoom}
            currentPlayerId={currentActivePlayerId}
            onDrawNumber={() => gameManager.bingoDrawNumber(activeRoom.id)}
            onDaub={(cardId, r, c) => gameManager.bingoDaub(activeRoom.id, cardId, r, c)}
            onLeave={handleLeaveRoom}
            onRematch={handleRematch}
            onSendMessage={handleSendMessage}
          />
          {isAdminOpen && (
            <AdminDashboard
              stats={gameManager.getAdminStats()}
              rooms={rooms}
              history={history}
              onClose={() => setIsAdminOpen(false)}
              onForceCloseRoom={(id) => gameManager.removePlayer(id, activeRoom.hostId)}
              onGrantCoins={(amt) => addCoins(amt, 'Admin demo grant')}
            />
          )}
        </div>
      );
    }

    if (activeRoom.gameType === 'faritany') {
      return (
        <div className="space-y-4">
          <DemoPlayerSwitcher
            currentActivePlayerId={currentActivePlayerId}
            onSelectPlayer={handleSelectDemoPlayer}
            onQuickReset={() => gameManager.resetMatch(activeRoom.id)}
            onOpenAdmin={() => setIsAdminOpen(true)}
          />
          <FaritanyGame
            room={activeRoom}
            currentPlayerId={currentActivePlayerId}
            onNextPhase={() => gameManager.faritanyNextPhase(activeRoom.id, currentActivePlayerId)}
            onReinforce={(tid, count) =>
              gameManager.faritanyReinforce(activeRoom.id, currentActivePlayerId, tid, count)
            }
            onAttack={(from, to) =>
              gameManager.faritanyAttack(activeRoom.id, currentActivePlayerId, from, to)
            }
            onLeave={handleLeaveRoom}
            onRematch={handleRematch}
            onSendMessage={handleSendMessage}
          />
          {isAdminOpen && (
            <AdminDashboard
              stats={gameManager.getAdminStats()}
              rooms={rooms}
              history={history}
              onClose={() => setIsAdminOpen(false)}
              onForceCloseRoom={(id) => gameManager.removePlayer(id, activeRoom.hostId)}
              onGrantCoins={(amt) => addCoins(amt, 'Admin demo grant')}
            />
          )}
        </div>
      );
    }
  }

  // ==================== DEFAULT GAMES HUB OVERVIEW ====================
  return (
    <div className="space-y-6">
      {/* Permanent Top Test Bar */}
      <DemoPlayerSwitcher
        currentActivePlayerId={currentActivePlayerId}
        onSelectPlayer={handleSelectDemoPlayer}
        onOpenAdmin={() => setIsAdminOpen(true)}
      />

      {/* Hero Games Hub Banner */}
      <div className="relative rounded-3xl border border-slate-200 bg-gradient-to-br from-[#0D1420] via-slate-900 to-[#10243E] p-6 sm:p-8 text-white shadow-xl overflow-hidden">
        <div className="absolute -top-12 -right-12 size-60 rounded-full bg-[#1E9EF5]/20 blur-3xl" />
        <div className="absolute -bottom-12 -left-12 size-60 rounded-full bg-cyan-400/15 blur-3xl" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-[#1E9EF5]/30 border border-[#1E9EF5]/50 px-3 py-0.5 text-xs font-black text-cyan-300 uppercase tracking-wider">
                TATA — CONNECT • LIVE • PLAY
              </span>
              <span className="flex items-center gap-1 text-xs font-bold text-emerald-400">
                <Radio className="size-3 animate-pulse" /> 8,360 Online
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
              Multiplayer Games Hub
            </h1>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Real-time multiplayer board and strategy arenas. Play instantly vs friends or smart AI bots, enter public/private rooms, and compete for virtual TATA coin pots.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 z-10">
            <button
              onClick={() => {
                setCreateGameType('domino');
                setIsCreateModalOpen(true);
                sounds.playClick();
              }}
              className="flex items-center gap-2 rounded-2xl bg-[#1E9EF5] hover:bg-sky-500 px-5 py-3 text-xs font-black text-white shadow-lg shadow-sky-500/30 transition-all active:scale-95"
            >
              <PlusCircle className="size-4" />
              <span>Create Room</span>
            </button>

            <button
              onClick={() => {
                setIsJoinModalOpen(true);
                sounds.playClick();
              }}
              className="flex items-center gap-2 rounded-2xl border border-white/20 bg-white/10 hover:bg-white/20 px-5 py-3 text-xs font-black text-white backdrop-blur-md transition-all active:scale-95"
            >
              <LogIn className="size-4" />
              <span>Join with Code</span>
            </button>
          </div>
        </div>
      </div>

      {/* 4 Games Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {GAME_CARDS.map((game) => {
          const Icon = game.icon;

          return (
            <div
              key={game.type}
              className={`rounded-3xl border border-slate-200 bg-gradient-to-br ${game.bgGradient} bg-white p-5 sm:p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-3">
                    <div
                      className="flex size-12 items-center justify-center rounded-2xl text-white shadow-sm"
                      style={{ backgroundColor: game.color }}
                    >
                      <Icon className="size-6" />
                    </div>
                    <div>
                      <h3 className="text-lg font-black text-[#0D1420]">{game.title}</h3>
                      <p className="text-xs font-bold text-slate-400">{game.tagline}</p>
                    </div>
                  </div>

                  <span
                    className="rounded-full px-2.5 py-0.5 text-[10px] font-black uppercase tracking-wider text-white"
                    style={{ backgroundColor: game.color }}
                  >
                    {game.badge}
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed mb-4">{game.description}</p>

                <div className="flex items-center gap-4 text-xs text-slate-400 font-semibold mb-4 border-y border-slate-100 py-2.5">
                  <div className="flex items-center gap-1.5">
                    <Users className="size-3.5 text-slate-500" />
                    <span>{game.playersText}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Radio className="size-3.5 text-emerald-500" />
                    <span className="text-emerald-600 font-bold">
                      {game.onlineCount.toLocaleString()} Players Online
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => handleQuickPlay(game.type)}
                  className="col-span-1 flex items-center justify-center gap-1.5 rounded-xl bg-[#1E9EF5] hover:bg-sky-600 text-white py-2.5 text-xs font-black shadow-xs transition-all active:scale-95"
                >
                  <Zap className="size-3.5 fill-white" />
                  <span>Play</span>
                </button>

                <button
                  onClick={() => {
                    setCreateGameType(game.type);
                    setIsCreateModalOpen(true);
                  }}
                  className="col-span-1 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 py-2.5 text-xs font-bold transition-colors"
                >
                  Create
                </button>

                <button
                  onClick={() => {
                    setRulesModalGame(game.type);
                    sounds.playClick();
                  }}
                  className="col-span-1 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 py-2.5 text-xs font-bold transition-colors"
                >
                  Rules
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Live Public Lobbies & Recent Match History */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Rooms */}
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gamepad2 className="size-4 text-[#1E9EF5]" />
              <h3 className="text-sm font-bold text-[#0D1420]">Live Room Lobbies</h3>
            </div>
            <span className="text-xs text-slate-400 font-medium">{rooms.length} rooms</span>
          </div>

          {rooms.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-200 p-6 text-center text-xs text-slate-400">
              No live rooms currently open. Create a room or launch Quick Play!
            </div>
          ) : (
            <div className="space-y-2">
              {rooms.map((room) => (
                <div
                  key={room.id}
                  className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/70 p-3 hover:bg-sky-50/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="rounded-lg bg-sky-100 px-2 py-1 text-xs font-black text-[#1E9EF5] uppercase">
                      {room.gameType}
                    </span>
                    <div>
                      <p className="text-xs font-bold text-[#0D1420]">{room.title}</p>
                      <p className="text-[10px] text-slate-400">
                        Code: <strong>{room.code}</strong> • {room.players.length}/
                        {room.settings.maxPlayers} players
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      gameManager.setActiveRoom(room.id);
                      sounds.playClick();
                    }}
                    className="rounded-xl bg-[#1E9EF5] hover:bg-sky-600 text-white px-3.5 py-1.5 text-xs font-bold transition-all shadow-2xs"
                  >
                    Enter
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Match Records */}
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy className="size-4 text-amber-500" />
              <h3 className="text-sm font-bold text-[#0D1420]">Recent Champion Matches</h3>
            </div>
            <span className="text-xs text-slate-400 font-medium">{history.length} completed</span>
          </div>

          {history.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-200 p-6 text-center text-xs text-slate-400">
              Play your first match to record scores on the champion leaderboard!
            </div>
          ) : (
            <div className="space-y-2">
              {history.slice(0, 4).map((h) => (
                <div
                  key={h.id}
                  className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/70 p-3 text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="rounded-lg bg-amber-100 px-2 py-0.5 text-[10px] font-black text-amber-800 uppercase">
                      {h.gameType}
                    </span>
                    <div>
                      <p className="font-bold text-[#0D1420]">
                        {h.winnerName} <span className="text-slate-400 font-normal">won match</span>
                      </p>
                      <p className="text-[10px] text-slate-400">{h.playedAt}</p>
                    </div>
                  </div>

                  <span className="font-black text-emerald-600">+{h.prizePool} coins</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* CREATE ROOM MODAL */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs animate-fadeIn">
          <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <PlusCircle className="size-5 text-[#1E9EF5]" />
                <h3 className="text-base font-black text-[#0D1420]">Create Multiplayer Room</h3>
              </div>
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="size-5" />
              </button>
            </div>

            <form onSubmit={handleCreateRoomSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Select Game</label>
                <div className="grid grid-cols-2 gap-2">
                  {GAME_CARDS.map((g) => (
                    <button
                      key={g.type}
                      type="button"
                      onClick={() => setCreateGameType(g.type)}
                      className={`rounded-xl border p-2.5 text-left text-xs font-bold transition-all ${
                        createGameType === g.type
                          ? 'border-[#1E9EF5] bg-sky-50 text-[#1E9EF5] ring-2 ring-sky-200'
                          : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      {g.title}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Room Title</label>
                <input
                  type="text"
                  value={createTitle}
                  onChange={(e) => setCreateTitle(e.target.value)}
                  placeholder={`My ${createGameType.toUpperCase()} Match`}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-[#0D1420] focus:bg-white focus:border-[#1E9EF5] outline-hidden"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Max Players</label>
                  <select
                    value={createMaxPlayers}
                    onChange={(e) => setCreateMaxPlayers(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold text-[#0D1420] outline-hidden"
                  >
                    <option value={2}>2 Players</option>
                    <option value={3}>3 Players</option>
                    <option value={4}>4 Players</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Entry Fee</label>
                  <select
                    value={createEntryFee}
                    onChange={(e) => setCreateEntryFee(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold text-[#0D1420] outline-hidden"
                  >
                    <option value={50}>50 Coins</option>
                    <option value={100}>100 Coins</option>
                    <option value={250}>250 Coins</option>
                    <option value={500}>500 Coins</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full rounded-2xl bg-[#1E9EF5] hover:bg-sky-600 text-white py-3 text-xs font-black shadow-md transition-all active:scale-95"
              >
                Create Room & Enter Lobby
              </button>
            </form>
          </div>
        </div>
      )}

      {/* JOIN ROOM MODAL */}
      {isJoinModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs animate-fadeIn">
          <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <LogIn className="size-5 text-[#1E9EF5]" />
                <h3 className="text-base font-black text-[#0D1420]">Join Room by Code</h3>
              </div>
              <button
                onClick={() => setIsJoinModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="size-5" />
              </button>
            </div>

            <form onSubmit={handleJoinSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Enter 8-digit Room Code
                </label>
                <input
                  type="text"
                  value={joinCodeInput}
                  onChange={(e) => setJoinCodeInput(e.target.value.toUpperCase())}
                  placeholder="e.g. TATA-DOM-123"
                  className="w-full uppercase tracking-wider text-center font-mono rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm font-bold text-[#0D1420] focus:bg-white focus:border-[#1E9EF5] outline-hidden"
                />
                {joinError && <p className="text-xs text-rose-500 font-bold mt-1.5">{joinError}</p>}
              </div>

              <button
                type="submit"
                className="w-full rounded-2xl bg-[#1E9EF5] hover:bg-sky-600 text-white py-3 text-xs font-black shadow-md transition-all active:scale-95"
              >
                Join Room
              </button>
            </form>
          </div>
        </div>
      )}

      {/* GAME RULES MODAL */}
      {rulesModalGame && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs animate-fadeIn">
          <div className="w-full max-w-lg rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl relative max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <BookOpen className="size-5 text-[#1E9EF5]" />
                <h3 className="text-base font-black text-[#0D1420] uppercase">
                  {rulesModalGame} Rules & Mechanics
                </h3>
              </div>
              <button
                onClick={() => setRulesModalGame(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="size-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
              {rulesModalGame === 'domino' && (
                <>
                  <p className="font-bold text-[#0D1420]">Double-Six 28 Tiles:</p>
                  <p>
                    Each player is dealt 7 tiles. The player with the highest double leads. Players match either the Left End or Right End of the open chain. If you have no matching tile, draw from the Boneyard. If the boneyard is empty, pass turn.
                  </p>
                  <p className="font-bold text-[#0D1420]">Winning the Round:</p>
                  <p>
                    First player to place all tiles declares Domino and wins all opponent remaining pips. If the table locks, the player with the lowest total pip count wins the hand!
                  </p>
                </>
              )}

              {rulesModalGame === 'ludo' && (
                <>
                  <p className="font-bold text-[#0D1420]">Objective & Pieces:</p>
                  <p>
                    Each player controls 4 colored tokens. Roll a 6 on the dice to exit your base yard onto the starting square.
                  </p>
                  <p className="font-bold text-[#0D1420]">Captures & Safe Zones:</p>
                  <p>
                    Landing on an opponent's token outside safe zones captures it, sends it back to their yard, and grants you an immediate bonus turn!
                  </p>
                </>
              )}

              {rulesModalGame === 'bingo' && (
                <>
                  <p className="font-bold text-[#0D1420]">75-Ball Live Hopper:</p>
                  <p>
                    Numbers are drawn from 1 to 75 (B: 1-15, I: 16-30, N: 31-45, G: 46-60, O: 61-75). The center square is FREE.
                  </p>
                  <p className="font-bold text-[#0D1420]">Prizes:</p>
                  <p>
                    First player to complete any 5-number line wins 30% of the pot. The first player to mark their entire card wins the Grand BINGO Jackpot!
                  </p>
                </>
              )}

              {rulesModalGame === 'faritany' && (
                <>
                  <p className="font-bold text-[#0D1420]">Province Strategy Conquest:</p>
                  <p>
                    Turn phases proceed sequentially: Harvest income from owned lands → Deploy recruits to borders → Attack neighboring territories with tactical dice → Fortify and end turn.
                  </p>
                  <p className="font-bold text-[#0D1420]">Victory Condition:</p>
                  <p>
                    Control 65% or more of the 15 island provinces to claim total territorial dominion!
                  </p>
                </>
              )}
            </div>

            <button
              onClick={() => setRulesModalGame(null)}
              className="mt-6 w-full rounded-2xl bg-[#1E9EF5] hover:bg-sky-600 text-white py-2.5 text-xs font-bold transition-colors"
            >
              Got it, let's play!
            </button>
          </div>
        </div>
      )}

      {/* ADMIN DASHBOARD MODAL */}
      {isAdminOpen && (
        <AdminDashboard
          stats={gameManager.getAdminStats()}
          rooms={rooms}
          history={history}
          onClose={() => setIsAdminOpen(false)}
          onForceCloseRoom={(id) => gameManager.removePlayer(id, 'usr_me')}
          onGrantCoins={(amt) => addCoins(amt, 'Admin demo grant')}
        />
      )}
    </div>
  );
};
