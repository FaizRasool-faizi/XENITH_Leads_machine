import { NextResponse } from "next/server";
import { FindingCategory, WebsiteAnalysis } from "@/types";

export async function POST(req: Request) {
  try {
    const { url, category, companyName } = await req.json();

    if (!url) {
      return NextResponse.json({ success: false, error: "URL is required" }, { status: 400 });
    }

    let cleanUrl = url.trim();
    if (!cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
      cleanUrl = `https://${cleanUrl}`;
    }

    // SSRF Safety Check
    const parsed = new URL(cleanUrl);
    const host = parsed.hostname.toLowerCase();
    if (
      host === "localhost" ||
      host === "127.0.0.1" ||
      host === "::1" ||
      host.startsWith("192.168.") ||
      host.startsWith("10.") ||
      host.startsWith("172.16.") ||
      host === "169.254.169.254"
    ) {
      return NextResponse.json(
        { success: false, error: "SSRF Protection: Access to private/loopback/cloud metadata IP is strictly prohibited." },
        { status: 403 }
      );
    }

    let isReachable = false;
    let httpStatus = 0;
    let pageTitle = "";
    let html = "";
    let hasViewport = false;
    let hasSsl = cleanUrl.startsWith("https://");

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 8000);

      const res = await fetch(cleanUrl, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) XENITH-Prospector/1.0 (+https://xenithsolutions.ai)",
          Accept: "text/html,application/xhtml+xml",
        },
        signal: controller.signal,
        redirect: "follow",
      });
      clearTimeout(timeout);

      httpStatus = res.status;
      isReachable = res.ok;
      if (res.ok) {
        html = await res.text();
        const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
        if (titleMatch) pageTitle = titleMatch[1].trim();
        hasViewport = html.toLowerCase().includes('name="viewport"');
      }
    } catch (e: any) {
      isReachable = false;
      httpStatus = 502;
    }

    const analyses: WebsiteAnalysis[] = [];
    const htmlLower = html.toLowerCase();
    const catLower = (category || "").toLowerCase();

    // 1. Mobile viewport gap
    if (!hasViewport && isReachable) {
      analyses.push({
        id: `an-${Date.now()}-1`,
        category: "WEBSITE_DEVELOPMENT",
        shortExplanation: "Missing viewport meta tag, resulting in non-responsive rendering on mobile devices.",
        evidenceUrl: cleanUrl,
        confidence: "HIGH",
        recommendedService: "Website Design & Development",
      });
    }

    // 2. Chatbot widget check
    const chatSignals = ["intercom", "drift", "crisp.chat", "tidio", "zendesk", "livechat", "tawk.to", "botpress"];
    const hasChat = chatSignals.some((sig) => htmlLower.includes(sig));
    if (!hasChat) {
      analyses.push({
        id: `an-${Date.now()}-2`,
        category: "AI_CHATBOT",
        shortExplanation: "No interactive 24/7 AI customer service agent detected on homepage to answer preliminary inquiries.",
        evidenceUrl: cleanUrl,
        confidence: "HIGH",
        recommendedService: "AI Chatbots & Customer Support Agents",
      });
    }

    // 3. Online booking automation check
    const bookingSignals = ["calendly", "acuity", "fresha", "booksy", "jane.app", "appointlet", "hubspot.com/meetings"];
    const hasBooking = bookingSignals.some((sig) => htmlLower.includes(sig));
    const serviceOriented = ["clinic", "dental", "doctor", "lawyer", "legal", "plumb", "hvac", "roof", "cpa", "consult"].some((k) =>
      catLower.includes(k)
    );

    if (!hasBooking && serviceOriented) {
      analyses.push({
        id: `an-${Date.now()}-3`,
        category: "BOOKING_AUTOMATION",
        shortExplanation: `Service business (${category || "services"}) relies on manual telephone/contact forms without automated self-scheduling.`,
        evidenceUrl: cleanUrl,
        confidence: "HIGH",
        recommendedService: "AI Workflow & Process Automation",
      });
    }

    // 4. AI Calling Agent candidate
    const phoneCta = ["call us today", "call now", "call for quote", "call for appointment"].some((k) => htmlLower.includes(k));
    if (phoneCta && !hasBooking) {
      analyses.push({
        id: `an-${Date.now()}-4`,
        category: "AI_CALLING_AGENT",
        shortExplanation: "Business prominently routes new inquiries to telephone calls; prime candidate for after-hours AI voice agent.",
        evidenceUrl: cleanUrl,
        confidence: "MEDIUM",
        recommendedService: "AI Calling Agents & Voice Bots",
      });
    }

    // 5. Unreachable or error fallback
    if (!isReachable) {
      analyses.push({
        id: `an-${Date.now()}-0`,
        category: "WEBSITE_DEVELOPMENT",
        shortExplanation: `Website is offline or returned HTTP ${httpStatus}, preventing prospective clients from reaching the business.`,
        evidenceUrl: cleanUrl,
        confidence: "HIGH",
        recommendedService: "Website Design & Development",
      });
    }

    return NextResponse.json({
      success: true,
      url: cleanUrl,
      httpStatus,
      isReachable,
      hasSsl,
      pageTitle: pageTitle || `${companyName || "Company"} Official Site`,
      analyses,
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
