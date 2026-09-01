import {
  FaritanyBattleLog,
  FaritanyGameState,
  FaritanyPhase,
  Territory,
} from '../types';

export const INITIAL_TERRITORIES: Record<string, Territory> = {
  diana: {
    id: 'diana',
    name: 'Diana Cape',
    code: 'DIA',
    region: 'North',
    polygon: 'M 180,30 L 250,20 L 280,70 L 210,95 Z',
    center: [230, 55],
    adjacentIds: ['sava', 'sofia'],
    ownerId: null,
    troops: 2,
    goldProduction: 120,
    defenseBonus: 1,
  },
  sava: {
    id: 'sava',
    name: 'Sava Coast',
    code: 'SAV',
    region: 'North',
    polygon: 'M 280,70 L 340,110 L 310,180 L 240,140 Z',
    center: [290, 125],
    adjacentIds: ['diana', 'sofia', 'atsinanana'],
    ownerId: null,
    troops: 2,
    goldProduction: 140,
    defenseBonus: 1,
  },
  sofia: {
    id: 'sofia',
    name: 'Sofia Basin',
    code: 'SOF',
    region: 'North-West',
    polygon: 'M 160,90 L 240,140 L 220,220 L 130,170 Z',
    center: [185, 155],
    adjacentIds: ['diana', 'sava', 'boeny', 'betsiboka'],
    ownerId: null,
    troops: 2,
    goldProduction: 110,
    defenseBonus: 0,
  },
  boeny: {
    id: 'boeny',
    name: 'Boeny Gulf',
    code: 'BOE',
    region: 'West',
    polygon: 'M 90,160 L 160,190 L 140,280 L 70,240 Z',
    center: [115, 215],
    adjacentIds: ['sofia', 'betsiboka', 'melaky'],
    ownerId: null,
    troops: 2,
    goldProduction: 130,
    defenseBonus: 1,
  },
  betsiboka: {
    id: 'betsiboka',
    name: 'Betsiboka Plateau',
    code: 'BET',
    region: 'Central-North',
    polygon: 'M 160,190 L 240,210 L 220,290 L 140,280 Z',
    center: [190, 245],
    adjacentIds: ['sofia', 'boeny', 'analamanga', 'atsinanana'],
    ownerId: null,
    troops: 3,
    goldProduction: 100,
    defenseBonus: 0,
  },
  analamanga: {
    id: 'analamanga',
    name: 'Analamanga Citadel',
    code: 'ANA',
    region: 'Central',
    polygon: 'M 180,290 L 260,290 L 250,370 L 170,360 Z',
    center: [215, 330],
    adjacentIds: ['betsiboka', 'atsinanana', 'menabe', 'matsiatra'],
    ownerId: null,
    troops: 4,
    goldProduction: 200,
    defenseBonus: 2,
  },
  atsinanana: {
    id: 'atsinanana',
    name: 'Atsinanana Port',
    code: 'ATS',
    region: 'East',
    polygon: 'M 240,200 L 330,220 L 300,340 L 250,320 Z',
    center: [280, 270],
    adjacentIds: ['sava', 'betsiboka', 'analamanga', 'vatovavy'],
    ownerId: null,
    troops: 2,
    goldProduction: 160,
    defenseBonus: 1,
  },
  melaky: {
    id: 'melaky',
    name: 'Melaky Wilds',
    code: 'MEL',
    region: 'West',
    polygon: 'M 50,250 L 140,280 L 120,380 L 40,340 Z',
    center: [85, 310],
    adjacentIds: ['boeny', 'menabe'],
    ownerId: null,
    troops: 2,
    goldProduction: 90,
    defenseBonus: 0,
  },
  menabe: {
    id: 'menabe',
    name: 'Menabe Plains',
    code: 'MEN',
    region: 'South-West',
    polygon: 'M 70,360 L 170,360 L 150,470 L 60,450 Z',
    center: [110, 410],
    adjacentIds: ['melaky', 'analamanga', 'matsiatra', 'atsimo'],
    ownerId: null,
    troops: 3,
    goldProduction: 120,
    defenseBonus: 0,
  },
  matsiatra: {
    id: 'matsiatra',
    name: 'Matsiatra Highlands',
    code: 'MAT',
    region: 'Central-South',
    polygon: 'M 170,370 L 250,370 L 230,470 L 160,460 Z',
    center: [205, 420],
    adjacentIds: ['analamanga', 'menabe', 'vatovavy', 'ihorombe'],
    ownerId: null,
    troops: 3,
    goldProduction: 140,
    defenseBonus: 1,
  },
  vatovavy: {
    id: 'vatovavy',
    name: 'Vatovavy Rainforest',
    code: 'VAT',
    region: 'East',
    polygon: 'M 250,330 L 310,340 L 280,460 L 230,450 Z',
    center: [270, 395],
    adjacentIds: ['atsinanana', 'analamanga', 'matsiatra', 'fitovinany'],
    ownerId: null,
    troops: 2,
    goldProduction: 110,
    defenseBonus: 1,
  },
  ihorombe: {
    id: 'ihorombe',
    name: 'Ihorombe Steppe',
    code: 'IHO',
    region: 'South',
    polygon: 'M 150,470 L 240,470 L 220,560 L 130,540 Z',
    center: [185, 510],
    adjacentIds: ['menabe', 'matsiatra', 'fitovinany', 'androy'],
    ownerId: null,
    troops: 2,
    goldProduction: 90,
    defenseBonus: 0,
  },
  fitovinany: {
    id: 'fitovinany',
    name: 'Fitovinany Shore',
    code: 'FIT',
    region: 'South-East',
    polygon: 'M 230,460 L 290,470 L 260,560 L 210,550 Z',
    center: [250, 510],
    adjacentIds: ['vatovavy', 'matsiatra', 'ihorombe', 'anosy'],
    ownerId: null,
    troops: 2,
    goldProduction: 130,
    defenseBonus: 1,
  },
  androy: {
    id: 'androy',
    name: 'Androy Red Desert',
    code: 'AND',
    region: 'Deep-South',
    polygon: 'M 120,550 L 200,560 L 180,640 L 100,610 Z',
    center: [150, 595],
    adjacentIds: ['ihorombe', 'anosy'],
    ownerId: null,
    troops: 2,
    goldProduction: 80,
    defenseBonus: 2,
  },
  anosy: {
    id: 'anosy',
    name: 'Anosy Haven',
    code: 'ANO',
    region: 'Deep-South',
    polygon: 'M 190,560 L 270,560 L 240,640 L 170,630 Z',
    center: [220, 600],
    adjacentIds: ['fitovinany', 'ihorombe', 'androy'],
    ownerId: null,
    troops: 3,
    goldProduction: 150,
    defenseBonus: 1,
  },
};

export function initializeFaritanyGame(playerIds: string[]): FaritanyGameState {
  const territories = JSON.parse(JSON.stringify(INITIAL_TERRITORIES)) as Record<string, Territory>;
  const territoryKeys = Object.keys(territories);

  // Shuffle starting territories among players
  const shuffledKeys = [...territoryKeys].sort(() => Math.random() - 0.5);
  const playerResources: Record<string, { gold: number; energy: number; reinforcedThisTurn: number }> = {};

  playerIds.forEach((pid, idx) => {
    playerResources[pid] = {
      gold: 300,
      energy: 5,
      reinforcedThisTurn: 0,
    };

    // Assign 2 starting core territories per player with strong garrisons
    const startKeys = shuffledKeys.splice(0, 2);
    startKeys.forEach((key) => {
      territories[key].ownerId = pid;
      territories[key].troops = 5;
    });
  });

  return {
    territories,
    playerResources,
    currentTurnPlayerId: playerIds[0],
    currentPhase: 'harvest',
    turnNumber: 1,
    maxTurns: 25,
    selectedTerritoryId: null,
    targetTerritoryId: null,
    battleLog: [],
    turnDeadline: Date.now() + 35000,
    matchWinnerId: null,
    lastActionSummary: 'Faritany territory war declared! Harvest your regional income.',
  };
}

export function advanceFaritanyPhase(
  state: FaritanyGameState,
  playerId: string,
  playerIds: string[]
): FaritanyGameState {
  if (state.currentTurnPlayerId !== playerId || state.matchWinnerId) {
    return state;
  }

  const phases: FaritanyPhase[] = ['harvest', 'reinforce', 'attack', 'fortify'];
  const curIdx = phases.indexOf(state.currentPhase);

  if (curIdx < phases.length - 1) {
    const nextPhase = phases[curIdx + 1];
    let summary = `Entered ${nextPhase.toUpperCase()} phase.`;

    if (nextPhase === 'reinforce') {
      // Calculate recruit income
      const owned = Object.values(state.territories).filter((t) => t.ownerId === playerId);
      const income = owned.reduce((sum, t) => sum + t.goldProduction, 0);
      const freeTroops = Math.max(3, Math.floor(owned.length / 2));

      const updatedResources = {
        ...state.playerResources,
        [playerId]: {
          ...state.playerResources[playerId],
          gold: (state.playerResources[playerId]?.gold || 0) + income,
          reinforcedThisTurn: freeTroops,
        },
      };

      summary = `Collected +${income} Gold and +${freeTroops} Reinforcements!`;

      return {
        ...state,
        currentPhase: nextPhase,
        playerResources: updatedResources,
        selectedTerritoryId: null,
        targetTerritoryId: null,
        turnDeadline: Date.now() + 35000,
        lastActionSummary: summary,
      };
    }

    return {
      ...state,
      currentPhase: nextPhase,
      selectedTerritoryId: null,
      targetTerritoryId: null,
      turnDeadline: Date.now() + 35000,
      lastActionSummary: summary,
    };
  }

  // End turn: advance to next player
  const currentIdx = playerIds.indexOf(playerId);
  const nextPlayerId = playerIds[(currentIdx + 1) % playerIds.length];
  const newTurnNumber = nextPlayerId === playerIds[0] ? state.turnNumber + 1 : state.turnNumber;

  // Check victory: territory control ratio
  const totalTerritories = Object.keys(state.territories).length;
  let matchWinnerId: string | null = null;

  for (const pid of playerIds) {
    const count = Object.values(state.territories).filter((t) => t.ownerId === pid).length;
    if (count / totalTerritories >= 0.65) {
      matchWinnerId = pid;
      break;
    }
  }

  return {
    ...state,
    currentPhase: 'harvest',
    currentTurnPlayerId: nextPlayerId,
    turnNumber: newTurnNumber,
    selectedTerritoryId: null,
    targetTerritoryId: null,
    turnDeadline: Date.now() + 35000,
    matchWinnerId,
    lastActionSummary: matchWinnerId
      ? '🎉 Strategic VICTORY! Territory dominance achieved!'
      : `Turn ended. Player ${nextPlayerId}'s turn to harvest.`,
  };
}

export function deployFaritanyTroops(
  state: FaritanyGameState,
  playerId: string,
  territoryId: string,
  count: number = 1
): FaritanyGameState {
  const territory = state.territories[territoryId];
  if (!territory || territory.ownerId !== playerId || state.currentPhase !== 'reinforce') {
    return state;
  }

  const res = state.playerResources[playerId];
  if (!res || res.reinforcedThisTurn < count) {
    return state;
  }

  const updatedTerritories = {
    ...state.territories,
    [territoryId]: {
      ...territory,
      troops: territory.troops + count,
    },
  };

  const updatedResources = {
    ...state.playerResources,
    [playerId]: {
      ...res,
      reinforcedThisTurn: res.reinforcedThisTurn - count,
    },
  };

  return {
    ...state,
    territories: updatedTerritories,
    playerResources: updatedResources,
    lastActionSummary: `Deployed +${count} troops to ${territory.name}.`,
  };
}

export function executeFaritanyAttack(
  state: FaritanyGameState,
  playerId: string,
  fromId: string,
  toId: string
): FaritanyGameState {
  const from = state.territories[fromId];
  const to = state.territories[toId];

  if (
    !from ||
    !to ||
    from.ownerId !== playerId ||
    to.ownerId === playerId ||
    from.troops <= 1 ||
    !from.adjacentIds.includes(toId) ||
    state.currentPhase !== 'attack'
  ) {
    return state;
  }

  // Tactical Dice Battle
  // Attacker rolls up to 3 dice (based on troops - 1)
  const attackerDiceCount = Math.min(3, from.troops - 1);
  const defenderDiceCount = Math.min(2, to.troops);

  const attackerDice = Array.from({ length: attackerDiceCount }, () => Math.floor(Math.random() * 6) + 1).sort(
    (a, b) => b - a
  );
  const defenderDice = Array.from({ length: defenderDiceCount }, () => Math.floor(Math.random() * 6) + 1).sort(
    (a, b) => b - a
  );

  let attackerLosses = 0;
  let defenderLosses = 0;

  const comparisons = Math.min(attackerDice.length, defenderDice.length);
  for (let i = 0; i < comparisons; i++) {
    // Defender wins ties and defense bonuses
    if (attackerDice[i] > defenderDice[i] + (to.defenseBonus > 0 && i === 0 ? 1 : 0)) {
      defenderLosses++;
    } else {
      attackerLosses++;
    }
  }

  const newAttackerTroops = Math.max(1, from.troops - attackerLosses);
  const newDefenderTroops = Math.max(0, to.troops - defenderLosses);

  const isConquered = newDefenderTroops === 0;
  const invadingTroops = isConquered ? Math.max(1, newAttackerTroops - 1) : 0;

  const updatedTerritories = {
    ...state.territories,
    [fromId]: {
      ...from,
      troops: isConquered ? 1 : newAttackerTroops,
    },
    [toId]: {
      ...to,
      ownerId: isConquered ? playerId : to.ownerId,
      troops: isConquered ? invadingTroops : newDefenderTroops,
    },
  };

  const battleLog: FaritanyBattleLog = {
    id: `btl_${Date.now()}`,
    attackerId: playerId,
    defenderId: to.ownerId,
    fromTerritory: from.name,
    toTerritory: to.name,
    attackerDice,
    defenderDice,
    attackerLosses,
    defenderLosses,
    conquered: isConquered,
  };

  return {
    ...state,
    territories: updatedTerritories,
    battleLog: [battleLog, ...state.battleLog.slice(0, 8)],
    selectedTerritoryId: isConquered ? toId : fromId,
    targetTerritoryId: null,
    lastActionSummary: isConquered
      ? `VICTORY! Conquered ${to.name} with ${invadingTroops} troops!`
      : `Battle at ${to.name}: Attacker lost ${attackerLosses}, Defender lost ${defenderLosses}.`,
  };
}

// Bot Decision Logic for Faritany
export function getFaritanyBotAction(
  state: FaritanyGameState,
  botPlayerId: string,
  playerIds: string[]
): {
  type: 'phase' | 'reinforce' | 'attack';
  fromId?: string;
  toId?: string;
  territoryId?: string;
  count?: number;
} {
  const owned = Object.values(state.territories).filter((t) => t.ownerId === botPlayerId);
  const res = state.playerResources[botPlayerId];

  if (state.currentPhase === 'harvest') {
    return { type: 'phase' };
  }

  if (state.currentPhase === 'reinforce') {
    if (res && res.reinforcedThisTurn > 0 && owned.length > 0) {
      // Find the border territory with fewest troops
      owned.sort((a, b) => a.troops - b.troops);
      return {
        type: 'reinforce',
        territoryId: owned[0].id,
        count: res.reinforcedThisTurn,
      };
    }
    return { type: 'phase' };
  }

  if (state.currentPhase === 'attack') {
    // Look for an attack with strong odds (troops >= enemy troops + 2)
    for (const myTerritory of owned) {
      if (myTerritory.troops > 2) {
        for (const adjId of myTerritory.adjacentIds) {
          const adj = state.territories[adjId];
          if (adj && adj.ownerId !== botPlayerId && myTerritory.troops >= adj.troops + 1) {
            return {
              type: 'attack',
              fromId: myTerritory.id,
              toId: adj.id,
            };
          }
        }
      }
    }
    return { type: 'phase' }; // No more good attacks, proceed to next phase
  }

  // Fortify phase: end turn
  return { type: 'phase' };
}
