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

export const INITIAL_SUPPRESSION: SuppressionEntry[] = [
  {
    id: "sup-1",
    type: "DOMAIN",
    value: "badspamdomain.com",
    reason: "OPT_OUT",
    addedAt: "2026-10-01",
  },
  {
    id: "sup-2",
    type: "EMAIL",
    value: "optout@competitor.com",
    reason: "REQUESTED_REMOVAL",
    addedAt: "2026-10-03",
  },
];

export const INITIAL_LEADS: BusinessLead[] = [
  {
    id: 1,
    name: "Austin Dental Spa",
    category: "Dentist & Cosmetic Dental",
    city: "Austin",
    state: "TX",
    country: "United States",
    websiteUrl: "https://austindentalspa.com",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Austin Dental Spa — Premier Cosmetic & Family Dentistry",
    metaDescription: "Providing personalized dental care and smile transformations in Austin, TX.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "info@austindentalspa.com", verified: true, sourceUrl: "https://austindentalspa.com" },
      { type: "PHONE", value: "512-452-9296", verified: true, sourceUrl: "https://austindentalspa.com" },
      { type: "CONTACT_FORM", value: "https://austindentalspa.com/contact-us", verified: true },
    ],
    analyses: [
      {
        id: "a-101",
        category: "AI_CHATBOT",
        shortExplanation: "No interactive 24/7 AI customer service agent detected on homepage to answer preliminary patient inquiries.",
        evidenceUrl: "https://austindentalspa.com",
        confidence: "HIGH",
        recommendedService: "AI Chatbots & Customer Support Agents",
      },
      {
        id: "a-102",
        category: "BOOKING_AUTOMATION",
        shortExplanation: "Clinic lacks real-time interactive patient scheduling widget; inquiries route through static forms.",
        evidenceUrl: "https://austindentalspa.com",
        confidence: "HIGH",
        recommendedService: "AI Workflow & Process Automation",
      },
    ],
    score: {
      total: 79,
      priority: "POTENTIAL_PROSPECT",
      legitimacy: 20,
      relevance: 20,
      opportunity: 18,
      contact: 15,
      evidence: 20,
      breakdown: [
        "+20: Verified registered dental clinic with reachable SSL website",
        "+20: Core high-priority vertical for XENITH AI automation solutions",
        "+18: Observable lack of 24/7 chatbot and direct online patient booking",
        "+15: Public verified business email, phone, and contact form available",
        "+20: Fresh direct site crawl with multiple corroborated opportunities",
      ],
    },
    outreachDrafts: [
      {
        id: "d-1",
        businessId: 1,
        serviceFocus: "AI Chatbots & Customer Support Agents",
        subject: "24/7 patient response solution for Austin Dental Spa",
        body: `Hello Austin Dental Spa Team,

I hope your week is going well. I was reviewing your website (https://austindentalspa.com) and noted your comprehensive Dentist & Cosmetic Dental services.

An observable detail stood out: No interactive 24/7 AI customer service agent detected on homepage to answer preliminary client inquiries. Many prospective patients searching after standard business hours often leave without getting their preliminary questions answered.

At XENITH Solutions, we build tailored AI customer-support agents trained strictly on your business documentation. They answer patient inquiries instantly 24/7, qualify prospect needs, and route high-intent appointments directly to your team.

Could we schedule a short demonstration to show how an intelligent assistant could save your team hours of repetitive inquiries?

Best regards,
Outreach Specialist — XENITH Solutions
https://xenithsolutions.ai

---
Opt-out: Reply 'Unsubscribe' to be removed from all future correspondence.`,
        status: "APPROVED",
        reviewedBy: "Faiz (Lead Architect)",
        reviewedAt: "2026-10-04 23:25",
      },
    ],
  },
  {
    id: 2,
    name: "Apex Plumbing & HVAC Services",
    category: "HVAC & Plumbing Contractors",
    city: "Dallas",
    state: "TX",
    country: "United States",
    websiteUrl: "https://apexplumbingpros.com",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Apex Plumbing & HVAC Dallas",
    metaDescription: "Residential and commercial plumbing and HVAC emergency services.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "service@apexplumbingpros.com", verified: true },
      { type: "PHONE", value: "214-555-0182", verified: true },
    ],
    analyses: [
      {
        id: "a-201",
        category: "AI_CALLING_AGENT",
        shortExplanation: "High-inquiry service contractor advertising prominent direct phone routing; candidate for after-hours AI voice agent.",
        evidenceUrl: "https://apexplumbingpros.com",
        confidence: "HIGH",
        recommendedService: "AI Calling Agents & Voice Bots",
      },
      {
        id: "a-202",
        category: "WEBSITE_DEVELOPMENT",
        shortExplanation: "Mobile layout lacks responsive viewport optimization and touch-friendly booking elements.",
        evidenceUrl: "https://apexplumbingpros.com",
        confidence: "MEDIUM",
        recommendedService: "Website Design & Development",
      },
    ],
    score: {
      total: 62,
      priority: "POTENTIAL_PROSPECT",
      legitimacy: 20,
      relevance: 15,
      opportunity: 17,
      contact: 13,
      evidence: 14,
      breakdown: [
        "+20: Verified trade contractor with live operational website",
        "+15: High-value service vertical for voice agents and booking workflows",
        "+17: Phone-first routing friction and mobile viewport upgrade needed",
        "+13: Direct business phone and support email active",
      ],
    },
    outreachDrafts: [
      {
        id: "d-2",
        businessId: 2,
        serviceFocus: "AI Calling Agents & Voice Bots",
        subject: "After-hours call handling and voice automation for Apex Plumbing",
        body: `Hi Apex Plumbing Team,

I noticed that Apex Plumbing handles significant customer inquiries by phone in Dallas, TX.

An observable characteristic from your web presence (https://apexplumbingpros.com) is: High-inquiry service contractor advertising prominent direct phone routing without 24/7 automated scheduling.

For emergency trade services, missed calls during peak hours or after closing represent missed revenue. At XENITH Solutions, we build natural-sounding AI voice calling agents that answer incoming phone inquiries, schedule emergency dispatches, and qualify callers 24/7 without delays or hold times.

If improving phone response coverage is a priority this quarter, would you be open to hearing a short audio demonstration?

Best regards,
Voice AI Specialist — XENITH Solutions
https://xenithsolutions.ai

---
Opt-out: Reply 'Unsubscribe' to be placed on our Do-Not-Contact registry.`,
        status: "DRAFT",
      },
    ],
  },
  {
    id: 3,
    name: "Calgary Integrative Wellness Clinic",
    category: "Healthcare & Medical Clinic",
    city: "Calgary",
    state: "AB",
    country: "Canada",
    websiteUrl: "https://calgarywellness.ca",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Calgary Integrative Wellness — Holistic Healthcare",
    metaDescription: "Comprehensive holistic medicine and naturopathic care in Calgary.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "intake@calgarywellness.ca", verified: true },
      { type: "PHONE", value: "403-555-0144", verified: true },
    ],
    analyses: [
      {
        id: "a-301",
        category: "BOOKING_AUTOMATION",
        shortExplanation: "Clinic requires patients to call or send plain email; no online self-scheduling widget detected.",
        evidenceUrl: "https://calgarywellness.ca",
        confidence: "HIGH",
        recommendedService: "AI Workflow & Process Automation",
      },
      {
        id: "a-302",
        category: "AI_CHATBOT",
        shortExplanation: "No after-hours chat assistant to triage practitioner availability or new patient questions.",
        evidenceUrl: "https://calgarywellness.ca",
        confidence: "HIGH",
        recommendedService: "AI Chatbots & Customer Support Agents",
      },
    ],
    score: {
      total: 79,
      priority: "POTENTIAL_PROSPECT",
      legitimacy: 20,
      relevance: 20,
      opportunity: 18,
      contact: 13,
      evidence: 20,
      breakdown: [
        "+20: Verified Canadian medical wellness establishment",
        "+20: Prime candidate for automated intake and patient chat",
        "+18: Manual intake bottleneck and lack of online scheduling",
        "+13: Direct clinic intake email and phone indexed",
      ],
    },
    outreachDrafts: [
      {
        id: "d-3",
        businessId: 3,
        serviceFocus: "AI Workflow & Process Automation",
        subject: "Automating patient intake & scheduling at Calgary Integrative Wellness",
        body: `Hi Calgary Integrative Wellness Team,

I noticed Calgary Integrative Wellness's established presence in Calgary, Canada.

While exploring your website (https://calgarywellness.ca), I noticed: Clinic requires patients to call or send plain email; no online self-scheduling widget detected.

Manual intake and back-and-forth scheduling frequently introduce friction for patients looking to book quickly. At XENITH Solutions, we design custom workflow automation systems that synchronize web inquiries directly into your clinic management software—eliminating repetitive administrative overhead.

Would you be open to discussing how automated client workflows could help your team save time?

Warm regards,
Automation Lead — XENITH Solutions
https://xenithsolutions.ai

---
Opt-out: Reply 'Unsubscribe' to immediately opt out.`,
        status: "APPROVED",
        reviewedBy: "Faiz",
        reviewedAt: "2026-10-04 23:26",
      },
    ],
  },
  {
    id: 4,
    name: "Sydney Legal & Corporate Counsel",
    category: "Legal & Corporate Advisory",
    city: "Sydney",
    state: "NSW",
    country: "Australia",
    websiteUrl: "https://sydneylegalcounsel.com.au",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Sydney Legal Counsel — Commercial Advisory",
    metaDescription: "Corporate law, contracts, and commercial litigation in Sydney.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "enquiries@sydneylegalcounsel.com.au", verified: true },
      { type: "PHONE", value: "02-8555-0199", verified: true },
    ],
    analyses: [
      {
        id: "a-401",
        category: "WEBSITE_DEVELOPMENT",
        shortExplanation: "Website runs on legacy template with missing meta descriptions and slow client intake portal.",
        evidenceUrl: "https://sydneylegalcounsel.com.au",
        confidence: "MEDIUM",
        recommendedService: "Website Design & Development",
      },
    ],
    score: {
      total: 62,
      priority: "POTENTIAL_PROSPECT",
      legitimacy: 20,
      relevance: 15,
      opportunity: 12,
      contact: 13,
      evidence: 14,
      breakdown: [
        "+20: Verified Australian legal practice",
        "+15: High-margin corporate vertical",
        "+12: Modernization opportunity for client onboarding portal",
      ],
    },
    outreachDrafts: [],
  },
  {
    id: 5,
    name: "Dubai Elite Property Advisors",
    category: "Real Estate & Property Management",
    city: "Dubai",
    country: "United Arab Emirates",
    websiteUrl: "https://dubaiestateadvisors.ae",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Dubai Elite Property Advisors — Luxury Realty",
    metaDescription: "Off-plan investments and luxury residences in Downtown Dubai.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "contact@dubaiestateadvisors.ae", verified: true },
      { type: "PHONE", value: "+971-4-555-0133", verified: true },
    ],
    analyses: [
      {
        id: "a-501",
        category: "AI_CHATBOT",
        shortExplanation: "Absence of multilingual AI real estate agent to capture high-intent international investor inquiries 24/7.",
        evidenceUrl: "https://dubaiestateadvisors.ae",
        confidence: "HIGH",
        recommendedService: "AI Chatbots & Customer Support Agents",
      },
    ],
    score: {
      total: 62,
      priority: "POTENTIAL_PROSPECT",
      legitimacy: 20,
      relevance: 15,
      opportunity: 15,
      contact: 13,
      evidence: 14,
      breakdown: [
        "+20: Verified UAE real estate company",
        "+15: High-yield market for multilingual AI agents",
        "+15: Prime candidate for instant property matching chatbot",
      ],
    },
    outreachDrafts: [],
  },
  {
    id: 6,
    name: "Pacific Northwest Roofing Solutions",
    category: "Roofing & Construction",
    city: "Seattle",
    state: "WA",
    country: "United States",
    websiteUrl: "https://pnwroofingcontractors.com",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "PNW Roofing Contractors Seattle",
    metaDescription: "Quality residential roof repair and replacement.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "quotes@pnwroofingcontractors.com", verified: true },
      { type: "PHONE", value: "206-555-0177", verified: true },
    ],
    analyses: [
      {
        id: "a-601",
        category: "BOOKING_AUTOMATION",
        shortExplanation: "Relies on manual phone quote requests; no instant visual quote estimator or automated inspection calendar.",
        evidenceUrl: "https://pnwroofingcontractors.com",
        confidence: "HIGH",
        recommendedService: "AI Workflow & Process Automation",
      },
    ],
    score: {
      total: 62,
      priority: "POTENTIAL_PROSPECT",
      legitimacy: 20,
      relevance: 15,
      opportunity: 15,
      contact: 13,
      evidence: 14,
      breakdown: [
        "+20: Active US roofing contractor",
        "+15: High ticket service business",
        "+15: Estimate automation opportunity",
      ],
    },
    outreachDrafts: [],
  },
  {
    id: 7,
    name: "Toronto Modern Accounting Group",
    category: "Accounting & Tax Advisory",
    city: "Toronto",
    state: "ON",
    country: "Canada",
    websiteUrl: "https://torontomoderncpa.ca",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Toronto Modern CPA — Corporate Tax Advisory",
    metaDescription: "Strategic tax planning and bookkeeping for growing enterprises.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "clients@torontomoderncpa.ca", verified: true },
      { type: "PHONE", value: "416-555-0165", verified: true },
    ],
    analyses: [
      {
        id: "a-701",
        category: "WORKFLOW_AUTOMATION",
        shortExplanation: "Client document collection is handled via standard attachments rather than an automated encrypted upload portal.",
        evidenceUrl: "https://torontomoderncpa.ca",
        confidence: "MEDIUM",
        recommendedService: "Custom Web Applications & Software",
      },
    ],
    score: {
      total: 62,
      priority: "POTENTIAL_PROSPECT",
      legitimacy: 20,
      relevance: 15,
      opportunity: 14,
      contact: 13,
      evidence: 14,
      breakdown: [
        "+20: Verified Canadian accounting firm",
        "+15: Professional B2B services focus",
        "+14: Secure client document automation opportunity",
      ],
    },
    outreachDrafts: [],
  },
  {
    id: 8,
    name: "Melbourne Specialist Dental Care",
    category: "Dental Clinic",
    city: "Melbourne",
    state: "VIC",
    country: "Australia",
    websiteUrl: "https://melbournespecialistdental.com.au",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Melbourne Specialist Dental — Orthodontics & Implants",
    metaDescription: "Specialist dental care in Melbourne central.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "reception@melbournespecialistdental.com.au", verified: true },
      { type: "PHONE", value: "03-9555-0122", verified: true },
    ],
    analyses: [
      {
        id: "a-801",
        category: "AI_CHATBOT",
        shortExplanation: "No after-hours triage agent for emergency dental inquiries or appointment confirmation.",
        evidenceUrl: "https://melbournespecialistdental.com.au",
        confidence: "HIGH",
        recommendedService: "AI Chatbots & Customer Support Agents",
      },
    ],
    score: {
      total: 62,
      priority: "POTENTIAL_PROSPECT",
      legitimacy: 20,
      relevance: 20,
      opportunity: 15,
      contact: 13,
      evidence: 14,
      breakdown: [
        "+20: Australian specialized healthcare practice",
        "+20: Direct fit for XENITH medical AI solutions",
        "+15: Emergency dental chatbot opportunity",
      ],
    },
    outreachDrafts: [],
  },
  {
    id: 9,
    name: "Gulf Logistics & Freight Solutions",
    category: "Logistics & Commercial Freight",
    city: "Abu Dhabi",
    country: "United Arab Emirates",
    websiteUrl: "https://gulflogisticsuae.ae",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Gulf Logistics & Freight UAE",
    metaDescription: "Air and sea freight forwarding solutions in the GCC.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "operations@gulflogisticsuae.ae", verified: true },
      { type: "PHONE", value: "+971-2-555-0188", verified: true },
    ],
    analyses: [
      {
        id: "a-901",
        category: "WEBSITE_DEVELOPMENT",
        shortExplanation: "Static web presence lacks real-time container tracking dashboard for enterprise clients.",
        evidenceUrl: "https://gulflogisticsuae.ae",
        confidence: "MEDIUM",
        recommendedService: "Custom Web Applications & Software",
      },
    ],
    score: {
      total: 52,
      priority: "NEEDS_RESEARCH",
      legitimacy: 20,
      relevance: 10,
      opportunity: 12,
      contact: 13,
      evidence: 10,
      breakdown: [
        "+20: Verified UAE commercial transport enterprise",
        "+10: Commercial logistics category",
        "+12: Enterprise web portal opportunity",
      ],
    },
    outreachDrafts: [],
  },
  {
    id: 10,
    name: "Austin Commercial Builders",
    category: "Commercial Construction",
    city: "Austin",
    state: "TX",
    country: "United States",
    websiteUrl: "https://austincommercialbuilders.com",
    httpStatus: 200,
    isReachable: true,
    pageTitle: "Austin Commercial Builders — General Contractors",
    metaDescription: "Commercial tenant improvements and ground-up construction.",
    hasSsl: true,
    verificationStatus: "VERIFIED",
    sourceName: "Verified Regional Register",
    createdAt: "2026-10-04",
    contacts: [
      { type: "EMAIL", value: "contact@austincommercialbuilders.com", verified: true },
      { type: "PHONE", value: "512-555-0149", verified: true },
    ],
    analyses: [
      {
        id: "a-1001",
        category: "WEBSITE_DEVELOPMENT",
        shortExplanation: "Website contains legacy non-responsive project galleries without mobile touch optimization.",
        evidenceUrl: "https://austincommercialbuilders.com",
        confidence: "MEDIUM",
        recommendedService: "Website Design & Development",
      },
    ],
    score: {
      total: 52,
      priority: "NEEDS_RESEARCH",
      legitimacy: 20,
      relevance: 10,
      opportunity: 12,
      contact: 13,
      evidence: 10,
      breakdown: [
        "+20: Verified regional commercial builder",
        "+10: General commercial category",
        "+12: Modern interactive portfolio redesign needed",
      ],
    },
    outreachDrafts: [],
  },
];
