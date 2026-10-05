import { NextResponse } from "next/server";
import { INITIAL_LEADS } from "@/lib/data";

// In-memory persistent cache for serverless invocation
let leadsStore = [...INITIAL_LEADS];

export async function GET() {
  return NextResponse.json({
    success: true,
    total: leadsStore.length,
    leads: leadsStore,
  });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    if (!body.name) {
      return NextResponse.json({ success: false, error: "Business name is required" }, { status: 400 });
    }

    const newLead = {
      id: Date.now(),
      name: body.name,
      category: body.category || "Commercial Business",
      city: body.city || "Unspecified",
      state: body.state || "",
      country: body.country || "United States",
      websiteUrl: body.websiteUrl || "",
      httpStatus: 200,
      isReachable: !!body.websiteUrl,
      verificationStatus: "VERIFIED" as const,
      sourceName: body.sourceName || "Manual Dashboard Ingestion",
      createdAt: new Date().toISOString().split("T")[0],
      contacts: body.contacts || [],
      analyses: body.analyses || [],
      score: body.score || {
        total: 65,
        priority: "POTENTIAL_PROSPECT",
        legitimacy: 20,
        relevance: 15,
        opportunity: 15,
        contact: 15,
        evidence: 0,
        breakdown: ["+65: Ingested through active dashboard session"],
      },
      outreachDrafts: [],
    };

    leadsStore.unshift(newLead);

    return NextResponse.json({
      success: true,
      lead: newLead,
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
