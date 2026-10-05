import { BusinessLead, ScoringWeights, SuppressionEntry } from "@/types";

export const DEFAULT_WEIGHTS: ScoringWeights = {
  maxLegitimacy: 20,
  maxRelevance: 20,
  maxOpportunity: 25,
  maxContact: 15,
  maxEvidence: 20,
  highPriorityMin: 80,
  potentialProspectMin: 60,
};

export const INITIAL_SUPPRESSION: SuppressionEntry[] = [];

// Clean initial state — team will populate genuine leads through Live Discovery or manual ingestion
export const INITIAL_LEADS: BusinessLead[] = [];
