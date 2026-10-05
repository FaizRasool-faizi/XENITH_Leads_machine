export type PriorityLabel = "HIGH_PRIORITY" | "POTENTIAL_PROSPECT" | "NEEDS_RESEARCH";

export type FindingCategory =
  | "WEBSITE_DEVELOPMENT"
  | "AI_CHATBOT"
  | "BOOKING_AUTOMATION"
  | "AI_CALLING_AGENT"
  | "WORKFLOW_AUTOMATION";

export interface ContactChannel {
  type: "EMAIL" | "PHONE" | "CONTACT_FORM" | "LINKEDIN";
  value: string;
  verified: boolean;
  sourceUrl?: string;
}

export interface WebsiteAnalysis {
  id: string;
  category: FindingCategory;
  shortExplanation: string;
  evidenceUrl: string;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  recommendedService: string;
}

export interface LeadScore {
  total: number;
  priority: PriorityLabel;
  legitimacy: number;
  relevance: number;
  opportunity: number;
  contact: number;
  evidence: number;
  breakdown: string[];
  isOverridden?: boolean;
  overrideReason?: string;
}

export interface OutreachDraft {
  id: string;
  businessId: number;
  serviceFocus: string;
  subject: string;
  body: string;
  status: "DRAFT" | "APPROVED" | "REJECTED";
  reviewedBy?: string;
  reviewedAt?: string;
}

export interface BusinessLead {
  id: number;
  name: string;
  category: string;
  city: string;
  state?: string;
  country: string;
  websiteUrl: string;
  httpStatus?: number;
  isReachable?: boolean;
  pageTitle?: string;
  metaDescription?: string;
  hasSsl?: boolean;
  contacts: ContactChannel[];
  analyses: WebsiteAnalysis[];
  score: LeadScore;
  outreachDrafts: OutreachDraft[];
  verificationStatus: "VERIFIED" | "UNVERIFIED";
  sourceName: string;
  createdAt: string;
}

export interface ScoringWeights {
  maxLegitimacy: number;
  maxRelevance: number;
  maxOpportunity: number;
  maxContact: number;
  maxEvidence: number;
  highPriorityMin: number;
  potentialProspectMin: number;
}

export interface SuppressionEntry {
  id: string;
  type: "DOMAIN" | "EMAIL" | "PHONE" | "COMPANY_NAME";
  value: string;
  reason: string;
  addedAt: string;
}
