import { create } from "zustand";

export type CeremonyPhase =
  | "draft"
  | "scheduled"
  | "collect"
  | "cluster"
  | "vote"
  | "discuss"
  | "action"
  | "review"
  | "completed"
  | "cancelled";

export interface CeremonyState {
  ceremonyId: string | null;
  currentPhase: CeremonyPhase;
  isFacilitator: boolean;
  anonymityConfig: {
    collect: "anonymous" | "named";
    vote: "anonymous" | "named";
    discuss: "anonymous" | "named";
    action: "named";
    quietMode: boolean;
    delayedReveal: boolean;
  };
  timerSeconds: number | null;
  timerRunning: boolean;
  participantCount: number;
  userNotesCount: number;
  userVotesRemaining: number;

  // Actions
  setCeremony: (id: string, isFacilitator: boolean) => void;
  setPhase: (phase: CeremonyPhase) => void;
  setAnonymity: (config: CeremonyState["anonymityConfig"]) => void;
  startTimer: (seconds: number) => void;
  stopTimer: () => void;
  decrementVotes: () => void;
  incrementNotes: () => void;
  setParticipantCount: (count: number) => void;
  reset: () => void;
}

const defaultAnonymity = {
  collect: "anonymous" as const,
  vote: "anonymous" as const,
  discuss: "named" as const,
  action: "named" as const,
  quietMode: false,
  delayedReveal: false,
};

export const useCeremonyStore = create<CeremonyState>((set) => ({
  ceremonyId: null,
  currentPhase: "draft",
  isFacilitator: false,
  anonymityConfig: defaultAnonymity,
  timerSeconds: null,
  timerRunning: false,
  participantCount: 0,
  userNotesCount: 0,
  userVotesRemaining: 3,

  setCeremony: (id, isFacilitator) =>
    set({ ceremonyId: id, isFacilitator }),

  setPhase: (phase) => set({ currentPhase:phase }),

  setAnonymity: (config) => set({ anonymityConfig: config }),

  startTimer: (seconds) =>
    set({ timerSeconds: seconds, timerRunning: true }),

  stopTimer: () => set({ timerRunning: false }),

  decrementVotes: set((state) => ({
    userVotesRemaining: Math.max(0, state.userVotesRemaining - 1),
  })),

  incrementNotes: set((state) => ({
    userNotesCount: state.userNotesCount + 1,
  })),

  setParticipantCount: (count) => set({ participantCount: count }),

  reset: set({
    ceremonyId: null,
    currentPhase: "draft",
    isFacilitator: false,
    anonymityConfig: defaultAnonymity,
    timerSeconds: null,
    timerRunning: false,
    participantCount: 0,
    userNotesCount: 0,
    userVotesRemaining: 3,
  }),
}));
