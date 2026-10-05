import { BusinessLead, LeadScore, OutreachDraft, ScoringWeights, SuppressionEntry } from "@/types";

export const SERVICE_TEMPLATES: Record<string, { subject: string; bodyTemplate: (biz: BusinessLead, obs: string) => string }> = {
  "AI Chatbots & Customer Support Agents": {
    subject: "24/7 client response solution for {company}",
    bodyTemplate: (biz, obs) => `Hello ${biz.name} Team,

I hope your week is going well. I was reviewing your website (${biz.websiteUrl}) and noted your comprehensive ${biz.category} services.

An observable detail stood out: ${obs || "No interactive 24/7 AI customer service agent detected on homepage to answer preliminary client inquiries"}. Many prospective clients searching after standard business hours often leave without getting their preliminary questions answered.

At XENITH Solutions, we build tailored AI customer-support agents trained strictly on your business documentation. They answer customer inquiries instantly 24/7, qualify prospect needs, and route high-intent leads directly to your team.

Could we schedule a short demonstration to show how an intelligent assistant could save your team hours of repetitive inquiries?

Best regards,
Outreach Specialist — XENITH Solutions
https://xenithsolutions.ai

---
Opt-out: Reply 'Unsubscribe' to be removed from all future correspondence.`,
  },

  "AI Workflow & Process Automation": {
    subject: "Automating scheduling & intake workflows at {company}",
    bodyTemplate: (biz, obs) => `Hi ${biz.name} Team,

I noticed ${biz.name}'s established presence in ${biz.city || "your region"}, ${biz.country}.

While exploring your website (${biz.websiteUrl}), I noticed: ${obs || "Client inquiries require manual email or phone calls rather than automated real-time booking"}.

Manual intake and back-and-forth scheduling frequently introduce friction for clients looking to book quickly. At XENITH Solutions, we design custom workflow automation systems that synchronize web inquiries directly into your calendar, CRM, and internal notifications—eliminating repetitive administrative overhead.

Would you be open to discussing how automated client workflows could help your team save time?

Warm regards,
Automation Lead — XENITH Solutions
https://xenithsolutions.ai

---
Opt-out: Reply 'Unsubscribe' to immediately opt out.`,
  },

  "Website Design & Development": {
    subject: "Quick observation regarding {company}'s web presence",
    bodyTemplate: (biz, obs) => `Hi ${biz.name} Team,

I came across ${biz.name} while researching ${biz.category} providers in ${biz.city}, ${biz.country}.

While reviewing your homepage (${biz.websiteUrl}), I noticed an observable technical opportunity: ${obs || "Website layout could benefit from modernized responsive performance and interactive conversion elements"}.

At XENITH Solutions, we help growing businesses modernize their digital storefronts into fast, responsive, high-converting platforms that reflect the real quality of your work.

Would you be open to a brief 10-minute introductory conversation next week to see how a streamlined design could improve your visitor conversions?

Best regards,
Outreach Team — XENITH Solutions
https://xenithsolutions.ai

---
Opt-out: Reply 'Unsubscribe' to be placed on our Do-Not-Contact registry.`,
  },

  "AI Calling Agents & Voice Bots": {
    subject: "After-hours call handling and voice automation for {company}",
    bodyTemplate: (biz, obs) => `Hello ${biz.name} Team,

I noticed that ${biz.name} handles significant customer inquiries by phone in ${biz.city}, ${biz.country}.

An observable characteristic from your web presence (${biz.websiteUrl}) is: ${obs || "Direct phone-first inquiry routing without 24/7 automated scheduling"}.

For high-demand service businesses, missed calls during peak hours or after closing represent missed revenue. At XENITH Solutions, we build natural-sounding AI voice calling agents that answer incoming phone inquiries, schedule appointments, and qualify callers 24/7 without delays or hold times.

If improving phone response coverage is a priority this quarter, would you be open to hearing a short audio demonstration?

Best regards,
Voice AI Specialist — XENITH Solutions
https://xenithsolutions.ai

---
Opt-out: Reply 'Unsubscribe' to be placed on our Do-Not-Contact registry.`,
  },
};

export function recalculateLeadScore(biz: BusinessLead, weights: ScoringWeights): LeadScore {
  const breakdown: string[] = [];

  // 1. Legitimacy
  let leg = 0;
  if (biz.name && biz.name.length > 2) {
    leg += 5;
    breakdown.push("+5: Valid registered company entity");
  }
  if (biz.category) {
    leg += 5;
    breakdown.push(`+5: Identified industry sector (${biz.category})`);
  }
  if (biz.city && biz.country) {
    leg += 3;
    breakdown.push(`+3: Verified municipal location (${biz.city}, ${biz.country})`);
  }
  if (biz.isReachable) {
    leg += 7;
    breakdown.push("+7: Verified operational HTTP website");
  }
  leg = Math.min(leg, weights.maxLegitimacy);

  // 2. Relevance
  let rel = 0;
  const highFitKeywords = ["dental", "clinic", "health", "law", "legal", "hvac", "plumb", "roof", "realty", "cpa", "advisory", "transport"];
  const catLower = (biz.category || "").toLowerCase();
  if (highFitKeywords.some((k) => catLower.includes(k))) {
    rel += 20;
    breakdown.push("+20: Prime target vertical for XENITH AI/web solutions");
  } else {
    rel += 10;
    breakdown.push("+10: Commercial business category");
  }
  rel = Math.min(rel, weights.maxRelevance);

  // 3. Opportunity
  let opp = 0;
  const oppCount = biz.analyses.length;
  if (oppCount >= 2) {
    opp += 18;
    breakdown.push(`+18: ${oppCount} corroborated observable technology opportunities`);
  } else if (oppCount === 1) {
    opp += 12;
    breakdown.push("+12: Verified observable technology gap");
  } else if (!biz.websiteUrl) {
    opp += 15;
    breakdown.push("+15: No website present (candidate for new web build)");
  }
  opp = Math.min(opp, weights.maxOpportunity);

  // 4. Contact
  let con = 0;
  const hasEmail = biz.contacts.some((c) => c.type === "EMAIL");
  const hasPhone = biz.contacts.some((c) => c.type === "PHONE");
  const hasForm = biz.contacts.some((c) => c.type === "CONTACT_FORM");
  if (hasEmail) {
    con += 8;
    breakdown.push("+8: Verified official business email");
  }
  if (hasPhone) {
    con += 5;
    breakdown.push("+5: Official business telephone");
  }
  if (hasForm) {
    con += 2;
    breakdown.push("+2: Verified contact intake form");
  }
  con = Math.min(con, weights.maxContact);

  // 5. Evidence
  let evi = 0;
  if (biz.httpStatus === 200) {
    evi += 12;
    breakdown.push("+12: Live verified HTTP 200 inspect completed");
  }
  if (oppCount > 0) {
    evi += 8;
    breakdown.push("+8: Timestamped DOM inspection findings logged");
  }
  evi = Math.min(evi, weights.maxEvidence);

  const total = Math.max(0, Math.min(100, leg + rel + opp + con + evi));

  let priority: LeadScore["priority"] = "NEEDS_RESEARCH";
  if (total >= weights.highPriorityMin) {
    priority = "HIGH_PRIORITY";
  } else if (total >= weights.potentialProspectMin) {
    priority = "POTENTIAL_PROSPECT";
  }

  return {
    total,
    priority,
    legitimacy: leg,
    relevance: rel,
    opportunity: opp,
    contact: con,
    evidence: evi,
    breakdown,
  };
}

export function isLeadSuppressed(biz: BusinessLead, suppressionList: SuppressionEntry[]): boolean {
  for (const sup of suppressionList) {
    if (sup.type === "COMPANY_NAME" && biz.name.toLowerCase().includes(sup.value.toLowerCase())) {
      return true;
    }
    if (sup.type === "DOMAIN" && biz.websiteUrl && biz.websiteUrl.toLowerCase().includes(sup.value.toLowerCase())) {
      return true;
    }
    if (sup.type === "EMAIL") {
      const email = biz.contacts.find((c) => c.type === "EMAIL")?.value.toLowerCase();
      if (email && email === sup.value.toLowerCase()) return true;
    }
    if (sup.type === "PHONE") {
      const phoneDigits = biz.contacts.find((c) => c.type === "PHONE")?.value.replace(/\D/g, "");
      const supDigits = sup.value.replace(/\D/g, "");
      if (phoneDigits && phoneDigits === supDigits) return true;
    }
  }
  return false;
}

export function generateLeadDraft(biz: BusinessLead, preferredService: string): OutreachDraft {
  const serviceKey = SERVICE_TEMPLATES[preferredService] ? preferredService : "AI Chatbots & Customer Support Agents";
  const template = SERVICE_TEMPLATES[serviceKey];
  const matchingObs = biz.analyses.find((a) => a.recommendedService === serviceKey)?.shortExplanation || (biz.analyses[0]?.shortExplanation ?? "");

  const subject = template.subject.replace("{company}", biz.name);
  const body = template.bodyTemplate(biz, matchingObs);

  return {
    id: `draft-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
    businessId: biz.id,
    serviceFocus: serviceKey,
    subject,
    body,
    status: "DRAFT",
  };
}

export function exportLeadsToCSV(leads: BusinessLead[]): string {
  const headers = [
    "Business ID",
    "Business Name",
    "Category",
    "City",
    "State",
    "Country",
    "Website",
    "Score",
    "Priority",
    "Emails",
    "Phones",
    "Observable Opportunities",
    "Recommended Services",
    "Verification Status",
  ];

  const rows = leads.map((l) => [
    l.id,
    `"${l.name.replace(/"/g, '""')}"`,
    `"${l.category || ""}"`,
    `"${l.city || ""}"`,
    `"${l.state || ""}"`,
    `"${l.country || ""}"`,
    `"${l.websiteUrl || ""}"`,
    l.score.total,
    l.score.priority,
    `"${l.contacts.filter((c) => c.type === "EMAIL").map((c) => c.value).join("; ")}"`,
    `"${l.contacts.filter((c) => c.type === "PHONE").map((c) => c.value).join("; ")}"`,
    `"${l.analyses.map((a) => a.category).join("; ")}"`,
    `"${l.analyses.map((a) => a.recommendedService).join("; ")}"`,
    l.verificationStatus,
  ]);

  return [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
}
