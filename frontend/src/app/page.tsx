"use client";

import React, { useState, useMemo, useEffect, useRef } from "react";
import {
  Building2,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Search,
  Globe,
  Filter,
  CheckCircle2,
  XCircle,
  Copy,
  Download,
  Sliders,
  ExternalLink,
  MessageSquare,
  Bot,
  Zap,
  PhoneCall,
  Sparkles,
  RefreshCw,
  Trash2,
  FileSpreadsheet,
  Check,
  FileText,
  UserCheck,
  Plus,
  Upload,
  X,
  Mail,
  Phone,
} from "lucide-react";
import { BusinessLead, ScoringWeights, SuppressionEntry, ContactChannel, WebsiteAnalysis } from "@/types";
import {
  INITIAL_LEADS,
  INITIAL_SUPPRESSION,
  DEFAULT_WEIGHTS,
} from "@/lib/data";
import {
  recalculateLeadScore,
  isLeadSuppressed,
  generateLeadDraft,
  exportLeadsToCSV,
  SERVICE_TEMPLATES,
} from "@/lib/lead-engine";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "database" | "analyzer" | "discovery" | "scoring" | "outreach" | "suppression" | "export"
  >("overview");

  // Hydration state for localStorage
  const [isHydrated, setIsHydrated] = useState(false);

  // Main State
  const [leads, setLeads] = useState<BusinessLead[]>(INITIAL_LEADS);
  const [suppressionList, setSuppressionList] = useState<SuppressionEntry[]>(INITIAL_SUPPRESSION);
  const [weights, setWeights] = useState<ScoringWeights>(DEFAULT_WEIGHTS);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("All");
  const [selectedPriority, setSelectedPriority] = useState("All");

  // Selected Lead for Detail / Drawer
  const [selectedLeadId, setSelectedLeadId] = useState<number>(1);
  const selectedLead = useMemo(() => leads.find((l) => l.id === selectedLeadId) || leads[0], [leads, selectedLeadId]);

  // Live Analyzer State
  const [analyzeUrl, setAnalyzeUrl] = useState("https://austindentalspa.com");
  const [analyzeCategory, setAnalyzeCategory] = useState("Dentist & Dental Clinic");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  // Lead Auditing State (specific lead)
  const [auditingLeadId, setAuditingLeadId] = useState<number | null>(null);

  // Discovery State
  const [discoverCity, setDiscoverCity] = useState("Austin");
  const [discoverCountry, setDiscoverCountry] = useState("United States");
  const [discoverCategory, setDiscoverCategory] = useState("Healthcare & Medical");
  const [discoverLimit, setDiscoverLimit] = useState(15);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [discoverySuccess, setDiscoverySuccess] = useState("");

  // Outreach Studio State
  const [outreachService, setOutreachService] = useState("AI Chatbots & Customer Support Agents");
  const [copiedDraftId, setCopiedDraftId] = useState<string | null>(null);

  // Suppression Form State
  const [newSupType, setNewSupType] = useState<SuppressionEntry["type"]>("DOMAIN");
  const [newSupValue, setNewSupValue] = useState("");
  const [newSupReason, setNewSupReason] = useState("OPT_OUT");

  // Add Manual Lead Modal
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newLeadForm, setNewLeadForm] = useState({
    name: "",
    category: "Commercial Business",
    city: "",
    country: "United States",
    websiteUrl: "",
    email: "",
    phone: "",
  });

  // Toast feedback
  const [toastMessage, setToastMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const savedLeads = localStorage.getItem("xenith_leads_store");
      if (savedLeads) {
        const parsed = JSON.parse(savedLeads);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setLeads(parsed);
          setSelectedLeadId(parsed[0].id);
        }
      }
      const savedSup = localStorage.getItem("xenith_suppression_store");
      if (savedSup) {
        const parsed = JSON.parse(savedSup);
        if (Array.isArray(parsed)) setSuppressionList(parsed);
      }
      const savedWeights = localStorage.getItem("xenith_weights_store");
      if (savedWeights) {
        const parsed = JSON.parse(savedWeights);
        if (parsed.maxLegitimacy) setWeights(parsed);
      }
    } catch (e) {
      console.error("Failed to load state from localStorage", e);
    } finally {
      setIsHydrated(true);
    }
  }, []);

  // Save to localStorage when state changes
  useEffect(() => {
    if (!isHydrated) return;
    try {
      localStorage.setItem("xenith_leads_store", JSON.stringify(leads));
    } catch (e) {
      console.error("Failed to save leads to localStorage", e);
    }
  }, [leads, isHydrated]);

  useEffect(() => {
    if (!isHydrated) return;
    try {
      localStorage.setItem("xenith_suppression_store", JSON.stringify(suppressionList));
    } catch (e) {
      console.error("Failed to save suppression to localStorage", e);
    }
  }, [suppressionList, isHydrated]);

  useEffect(() => {
    if (!isHydrated) return;
    try {
      localStorage.setItem("xenith_weights_store", JSON.stringify(weights));
    } catch (e) {
      console.error("Failed to save weights to localStorage", e);
    }
  }, [weights, isHydrated]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 4500);
  };

  // Filtered Leads
  const filteredLeads = useMemo(() => {
    return leads.filter((l) => {
      const matchesSearch =
        l.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        l.city.toLowerCase().includes(searchQuery.toLowerCase()) ||
        l.category.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCountry = selectedCountry === "All" || l.country === selectedCountry;
      const matchesPriority = selectedPriority === "All" || l.score.priority === selectedPriority;
      return matchesSearch && matchesCountry && matchesPriority;
    });
  }, [leads, searchQuery, selectedCountry, selectedPriority]);

  // Dynamic Metrics
  const metrics = useMemo(() => {
    const total = leads.length;
    const verified = leads.filter((l) => l.verificationStatus === "VERIFIED").length;
    const highPriority = leads.filter((l) => l.score.priority === "HIGH_PRIORITY").length;
    const opportunities = leads.reduce((acc, l) => acc + l.analyses.length, 0);
    const approvedDrafts = leads.reduce(
      (acc, l) => acc + l.outreachDrafts.filter((d) => d.status === "APPROVED").length,
      0
    );
    return { total, verified, highPriority, opportunities, approvedDrafts };
  }, [leads]);

  // Recalculate all scores when weights change
  const handleRecalculateScores = (newWeights: ScoringWeights) => {
    setWeights(newWeights);
    setLeads((prev) =>
      prev.map((l) => ({
        ...l,
        score: recalculateLeadScore(l, newWeights),
      }))
    );
    showToast("Scoring weights updated & all lead scores recalculated.");
  };

  // Reset to default sample leads
  const handleResetToDefaults = () => {
    if (confirm("Reset leads and suppression lists to default XENITH verified data?")) {
      setLeads(INITIAL_LEADS);
      setSuppressionList(INITIAL_SUPPRESSION);
      setWeights(DEFAULT_WEIGHTS);
      setSelectedLeadId(INITIAL_LEADS[0].id);
      localStorage.removeItem("xenith_leads_store");
      localStorage.removeItem("xenith_suppression_store");
      localStorage.removeItem("xenith_weights_store");
      showToast("Reset completed successfully.");
    }
  };

  // Run live opportunity scan in analyzer tab
  const handleRunScan = async () => {
    if (!analyzeUrl) return;
    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: analyzeUrl,
          category: analyzeCategory,
          companyName: "Analyzed Business",
        }),
      });
      const data = await res.json();
      setAnalysisResult(data);
      showToast("Live URL opportunity scan completed!");
    } catch (e: any) {
      setAnalysisResult({ success: false, error: e.message });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Run lead discovery via API
  const handleRunDiscovery = async () => {
    if (!discoverCity.trim()) {
      alert("Please enter a target city name.");
      return;
    }

    setIsDiscovering(true);
    setDiscoverySuccess("");

    try {
      const res = await fetch("/api/discover", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          city: discoverCity,
          country: discoverCountry,
          category: discoverCategory,
          limit: discoverLimit,
        }),
      });

      const data = await res.json();
      if (data.success && Array.isArray(data.leads) && data.leads.length > 0) {
        setLeads((prev) => {
          const existingNames = new Set(prev.map((l) => l.name.toLowerCase()));
          const newUnique = data.leads.filter((l: BusinessLead) => !existingNames.has(l.name.toLowerCase()));
          return [...newUnique, ...prev];
        });

        const successText = `Discovered ${data.leads.length} qualified leads in ${discoverCity} (${data.fallbackUsed ? "Regional Prospector" : "Live OpenStreetMap Engine"})!`;
        setDiscoverySuccess(successText);
        showToast(successText);
        setSelectedLeadId(data.leads[0].id);
      } else {
        const errText = data.error || "No new leads returned. Try expanding search parameters.";
        setDiscoverySuccess(errText);
      }
    } catch (err: any) {
      setDiscoverySuccess(`Discovery error: ${err.message}`);
    } finally {
      setIsDiscovering(false);
    }
  };

  // Audit a single lead's live website
  const handleAuditLeadWebsite = async (lead: BusinessLead) => {
    if (!lead.websiteUrl) {
      alert("This prospect does not have a registered website URL to scan.");
      return;
    }

    setAuditingLeadId(lead.id);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: lead.websiteUrl,
          category: lead.category,
          companyName: lead.name,
        }),
      });

      const data = await res.json();
      if (data.success) {
        setLeads((prev) =>
          prev.map((l) => {
            if (l.id !== lead.id) return l;
            const updated: BusinessLead = {
              ...l,
              httpStatus: data.httpStatus,
              isReachable: data.isReachable,
              hasSsl: data.hasSsl,
              pageTitle: data.pageTitle || l.pageTitle,
              analyses: data.analyses && data.analyses.length > 0 ? data.analyses : l.analyses,
              verificationStatus: "VERIFIED",
            };
            updated.score = recalculateLeadScore(updated, weights);
            return updated;
          })
        );
        showToast(`Audit complete for ${lead.name}! Tech gaps & score updated.`);
      } else {
        alert(`Audit failed: ${data.error || "Could not reach website."}`);
      }
    } catch (err: any) {
      alert(`Error auditing website: ${err.message}`);
    } finally {
      setAuditingLeadId(null);
    }
  };

  // Add suppression entry
  const handleAddSuppression = () => {
    if (!newSupValue.trim()) return;
    const entry: SuppressionEntry = {
      id: `sup-${Date.now()}`,
      type: newSupType,
      value: newSupValue.trim(),
      reason: newSupReason,
      addedAt: new Date().toISOString().split("T")[0],
    };
    setSuppressionList((prev) => [entry, ...prev]);
    setNewSupValue("");
    showToast(`Suppression rule added: ${entry.value}`);
  };

  // Delete lead (Right to be forgotten)
  const handlePurgeLead = (id: number) => {
    if (confirm("Are you sure you want to purge this business from the database?")) {
      setLeads((prev) => prev.filter((l) => l.id !== id));
      showToast("Prospect removed permanently.");
    }
  };

  // Create Manual Lead
  const handleCreateManualLead = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newLeadForm.name.trim()) return;

    const contacts: ContactChannel[] = [];
    if (newLeadForm.email.trim()) {
      contacts.push({ type: "EMAIL", value: newLeadForm.email.trim(), verified: true });
    }
    if (newLeadForm.phone.trim()) {
      contacts.push({ type: "PHONE", value: newLeadForm.phone.trim(), verified: true });
    }

    let cleanUrl = newLeadForm.websiteUrl.trim();
    if (cleanUrl && !cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
      cleanUrl = `https://${cleanUrl}`;
    }
    if (cleanUrl) {
      contacts.push({ type: "CONTACT_FORM", value: `${cleanUrl}/contact`, verified: false });
    }

    const leadId = Date.now();
    const newLead: BusinessLead = {
      id: leadId,
      name: newLeadForm.name.trim(),
      category: newLeadForm.category || "Commercial Business",
      city: newLeadForm.city.trim() || "Unspecified",
      country: newLeadForm.country || "United States",
      websiteUrl: cleanUrl,
      httpStatus: cleanUrl ? 200 : undefined,
      isReachable: !!cleanUrl,
      hasSsl: cleanUrl.startsWith("https://"),
      verificationStatus: "VERIFIED",
      sourceName: "Team Manual Ingestion",
      createdAt: new Date().toISOString().split("T")[0],
      contacts,
      analyses: cleanUrl
        ? [
            {
              id: `an-${leadId}-1`,
              category: "AI_CHATBOT",
              shortExplanation: "Website has no active 24/7 client conversational agent.",
              evidenceUrl: cleanUrl,
              confidence: "HIGH",
              recommendedService: "AI Chatbots & Customer Support Agents",
            },
          ]
        : [],
      score: {
        total: 70,
        priority: "POTENTIAL_PROSPECT",
        legitimacy: 20,
        relevance: 15,
        opportunity: 15,
        contact: contacts.length > 0 ? 15 : 5,
        evidence: 5,
        breakdown: ["Manually qualified by sales team"],
      },
      outreachDrafts: [],
    };

    newLead.score = recalculateLeadScore(newLead, weights);

    setLeads((prev) => [newLead, ...prev]);
    setSelectedLeadId(newLead.id);
    setIsAddModalOpen(false);
    setNewLeadForm({
      name: "",
      category: "Commercial Business",
      city: "",
      country: "United States",
      websiteUrl: "",
      email: "",
      phone: "",
    });
    showToast(`Added new prospect: ${newLead.name}`);
  };

  // CSV File Import Handler
  const handleCSVUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target?.result as string;
      if (!text) return;
      const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
      if (lines.length <= 1) {
        alert("The uploaded CSV file is empty or has no data rows.");
        return;
      }

      const importedLeads: BusinessLead[] = [];
      const baseTime = Date.now();

      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(",").map((s) => s.replace(/^"(.*)"$/, "$1").trim());
        if (cols.length === 0 || !cols[0]) continue;

        const name = cols[0];
        const category = cols[1] || "Commercial Services";
        const city = cols[2] || "Unspecified";
        const country = cols[3] || "United States";
        let webUrl = cols[4] || "";
        if (webUrl && !webUrl.startsWith("http://") && !webUrl.startsWith("https://")) {
          webUrl = `https://${webUrl}`;
        }
        const email = cols[5] || "";
        const phone = cols[6] || "";

        const contacts: ContactChannel[] = [];
        if (email) contacts.push({ type: "EMAIL", value: email, verified: false });
        if (phone) contacts.push({ type: "PHONE", value: phone, verified: false });

        const itemLead: BusinessLead = {
          id: baseTime + i,
          name,
          category,
          city,
          country,
          websiteUrl: webUrl,
          isReachable: !!webUrl,
          verificationStatus: "UNVERIFIED",
          sourceName: "Batch CSV Ingestion",
          createdAt: new Date().toISOString().split("T")[0],
          contacts,
          analyses: [],
          score: {
            total: 60,
            priority: "POTENTIAL_PROSPECT",
            legitimacy: 15,
            relevance: 15,
            opportunity: 12,
            contact: contacts.length > 0 ? 12 : 5,
            evidence: 6,
            breakdown: ["Imported from external CSV roster"],
          },
          outreachDrafts: [],
        };

        itemLead.score = recalculateLeadScore(itemLead, weights);
        importedLeads.push(itemLead);
      }

      if (importedLeads.length > 0) {
        setLeads((prev) => [...importedLeads, ...prev]);
        setSelectedLeadId(importedLeads[0].id);
        showToast(`Successfully imported ${importedLeads.length} leads from CSV!`);
      }
    };

    reader.readAsText(file);
    e.target.value = "";
  };

  // Generate draft for selected lead
  const handleGenerateDraft = () => {
    if (!selectedLead) return;
    if (isLeadSuppressed(selectedLead, suppressionList)) {
      alert("Action blocked: This business or its domain/email is present on the Do-Not-Contact suppression list.");
      return;
    }
    const draft = generateLeadDraft(selectedLead, outreachService);
    setLeads((prev) =>
      prev.map((l) => (l.id === selectedLead.id ? { ...l, outreachDrafts: [draft, ...l.outreachDrafts] } : l))
    );
    showToast("Tailored outreach draft generated!");
  };

  // Update draft status
  const handleUpdateDraftStatus = (leadId: number, draftId: string, status: "APPROVED" | "REJECTED") => {
    setLeads((prev) =>
      prev.map((l) => {
        if (l.id !== leadId) return l;
        return {
          ...l,
          outreachDrafts: l.outreachDrafts.map((d) =>
            d.id === draftId
              ? {
                  ...d,
                  status,
                  reviewedBy: "XENITH Outreach Specialist",
                  reviewedAt: new Date().toLocaleString(),
                }
              : d
          ),
        };
      })
    );
    showToast(`Draft marked as ${status}.`);
  };

  // Copy draft to clipboard
  const handleCopyDraft = (draft: { id: string; subject: string; body: string }) => {
    navigator.clipboard.writeText(`Subject: ${draft.subject}\n\n${draft.body}`);
    setCopiedDraftId(draft.id);
    showToast("Email pitch copied to clipboard!");
    setTimeout(() => setCopiedDraftId(null), 2000);
  };

  // Export to CSV
  const handleDownloadCSV = () => {
    const csvContent = exportLeadsToCSV(filteredLeads);
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `xenith_leads_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast("CSV export downloaded successfully.");
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 border border-cyan-500/40 text-cyan-300 px-4 py-3 rounded-xl shadow-2xl flex items-center gap-3 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-cyan-400" />
          <span className="text-xs font-semibold">{toastMessage}</span>
        </div>
      )}

      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-[#0c1220]/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-400 bg-clip-text text-transparent">
                  XENITH Solutions
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  Lead Gen Engine
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                B2B Live Discovery • Observable Tech Gaps • Compliant Cold Outreach
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
              <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
              <span className="font-medium text-slate-400">Database:</span>
              <span className="font-semibold text-emerald-400">Local Sync Active</span>
            </div>

            <button
              onClick={() => setIsAddModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-cyan-500/20 transition-all"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Lead</span>
            </button>

            <button
              onClick={handleResetToDefaults}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700/60"
              title="Reset Sample Data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-6">
        {/* KPI Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-5 border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider">Total Prospects</span>
              <Building2 className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-3xl font-extrabold text-white tracking-tight">{metrics.total}</div>
            <div className="mt-2 text-xs text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{metrics.verified} Verified in Database</span>
            </div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-5 border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider">High Priority</span>
              <TrendingUp className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-extrabold text-amber-300 tracking-tight">{metrics.highPriority}</div>
            <div className="mt-2 text-xs text-slate-400">Score &gt;= {weights.highPriorityMin} threshold</div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-5 border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider">Tech Gap Signals</span>
              <Zap className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-3xl font-extrabold text-indigo-300 tracking-tight">{metrics.opportunities}</div>
            <div className="mt-2 text-xs text-slate-400">Concrete Pitch Angles</div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-5 border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider">Approved Outreach</span>
              <MessageSquare className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-3xl font-extrabold text-emerald-400 tracking-tight">{metrics.approvedDrafts}</div>
            <div className="mt-2 text-xs text-slate-400">Ready to Send</div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto border-b border-slate-800/80 pb-2 scrollbar-none text-sm font-medium">
          {[
            { id: "overview", label: "Overview", icon: TrendingUp },
            { id: "database", label: "Lead Database", icon: Building2 },
            { id: "discovery", label: "Live Lead Finder", icon: Globe },
            { id: "analyzer", label: "Live Tech Analyzer", icon: Zap },
            { id: "outreach", label: "Outreach Studio", icon: MessageSquare },
            { id: "scoring", label: "Scoring Weights", icon: Sliders },
            { id: "suppression", label: "DNC & Suppression", icon: ShieldCheck },
            { id: "export", label: "Import / Export", icon: Download },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 whitespace-nowrap ${
                  isActive
                    ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-lg text-white">Target Market Geo Distribution</h3>
                  <p className="text-xs text-slate-400">Prospect distribution across international target territories</p>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                  {leads.length} Total Registered
                </span>
              </div>

              <div className="space-y-4">
                {[
                  { country: "United States", color: "bg-cyan-500" },
                  { country: "Canada", color: "bg-indigo-500" },
                  { country: "Australia", color: "bg-purple-500" },
                  { country: "United Arab Emirates", color: "bg-amber-500" },
                  { country: "United Kingdom", color: "bg-emerald-500" },
                ].map((item) => {
                  const count = leads.filter((l) => l.country === item.country).length;
                  const pct = leads.length > 0 ? Math.round((count / leads.length) * 100) : 0;
                  return (
                    <div key={item.country} className="space-y-1.5">
                      <div className="flex justify-between text-xs font-semibold text-slate-300">
                        <span>{item.country}</span>
                        <span>{count} Leads ({pct}%)</span>
                      </div>
                      <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${item.color} rounded-full transition-all duration-500`}
                          style={{ width: `${pct}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="border-t border-slate-800/80 pt-6">
                <h4 className="text-sm font-semibold text-slate-200 mb-3">Service Pitch Angle Breakdown</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div className="bg-slate-950/70 p-3.5 rounded-lg border border-slate-800">
                    <div className="text-2xl font-bold text-cyan-400">
                      {leads.filter((l) => l.analyses.some((a) => a.category === "AI_CHATBOT")).length}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">24/7 AI Chatbot</div>
                  </div>
                  <div className="bg-slate-950/70 p-3.5 rounded-lg border border-slate-800">
                    <div className="text-2xl font-bold text-indigo-400">
                      {leads.filter((l) => l.analyses.some((a) => a.category === "BOOKING_AUTOMATION")).length}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Booking Automation</div>
                  </div>
                  <div className="bg-slate-950/70 p-3.5 rounded-lg border border-slate-800">
                    <div className="text-2xl font-bold text-purple-400">
                      {leads.filter((l) => l.analyses.some((a) => a.category === "WEBSITE_DEVELOPMENT")).length}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Web Redesign</div>
                  </div>
                  <div className="bg-slate-950/70 p-3.5 rounded-lg border border-slate-800">
                    <div className="text-2xl font-bold text-amber-400">
                      {leads.filter((l) => l.analyses.some((a) => a.category === "AI_CALLING_AGENT")).length}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Voice Agent Ops</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions Panel */}
            <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-5">
              <h3 className="font-bold text-base text-white">Team Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => setActiveTab("discovery")}
                  className="w-full py-3 px-4 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 rounded-xl text-xs font-semibold text-white flex items-center justify-between shadow-lg shadow-cyan-500/20 transition-all"
                >
                  <span className="flex items-center gap-2">
                    <Globe className="w-4 h-4" />
                    <span>Discover New Leads Worldwide</span>
                  </span>
                  <span>&rarr;</span>
                </button>

                <button
                  onClick={() => setIsAddModalOpen(true)}
                  className="w-full py-3 px-4 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-semibold text-slate-200 flex items-center justify-between border border-slate-700 transition-all"
                >
                  <span className="flex items-center gap-2">
                    <Plus className="w-4 h-4 text-cyan-400" />
                    <span>Add Lead Manually</span>
                  </span>
                  <span>&rarr;</span>
                </button>

                <button
                  onClick={() => setActiveTab("analyzer")}
                  className="w-full py-3 px-4 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-semibold text-slate-200 flex items-center justify-between border border-slate-700 transition-all"
                >
                  <span className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-indigo-400" />
                    <span>Audit Any Live Website</span>
                  </span>
                  <span>&rarr;</span>
                </button>

                <button
                  onClick={() => setActiveTab("export")}
                  className="w-full py-3 px-4 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-semibold text-slate-200 flex items-center justify-between border border-slate-700 transition-all"
                >
                  <span className="flex items-center gap-2">
                    <Download className="w-4 h-4 text-emerald-400" />
                    <span>Export Leads to CSV</span>
                  </span>
                  <span>&rarr;</span>
                </button>
              </div>

              <div className="p-3.5 bg-slate-950/80 rounded-xl border border-slate-800 text-xs space-y-1.5">
                <div className="font-semibold text-cyan-300 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  <span>Full Cold Outreach Compliance</span>
                </div>
                <p className="text-slate-400 leading-relaxed text-[11px]">
                  All generated pitches contain explicit physical company identification, legitimate observable business rationale, and automated 1-click opt-out suppression.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: LEAD DATABASE */}
        {activeTab === "database" && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-3 items-center justify-between bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
              <div className="relative w-full sm:w-80">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  placeholder="Search company, city, or vertical..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                <select
                  value={selectedCountry}
                  onChange={(e) => setSelectedCountry(e.target.value)}
                  className="px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="All">All Countries</option>
                  <option value="United States">United States</option>
                  <option value="Canada">Canada</option>
                  <option value="Australia">Australia</option>
                  <option value="United Arab Emirates">United Arab Emirates</option>
                  <option value="United Kingdom">United Kingdom</option>
                </select>

                <select
                  value={selectedPriority}
                  onChange={(e) => setSelectedPriority(e.target.value)}
                  className="px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="All">All Priorities</option>
                  <option value="HIGH_PRIORITY">High Priority (&gt;=80)</option>
                  <option value="POTENTIAL_PROSPECT">Potential (60-79)</option>
                  <option value="NEEDS_RESEARCH">Needs Research (&lt;60)</option>
                </select>

                <button
                  onClick={() => setIsAddModalOpen(true)}
                  className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-300 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors border border-slate-700"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Lead</span>
                </button>

                <button
                  onClick={handleDownloadCSV}
                  className="px-3 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export CSV</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Table List */}
              <div className="lg:col-span-2 bg-slate-900/60 backdrop-blur-md rounded-xl border border-slate-800/80 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold border-b border-slate-800">
                      <tr>
                        <th className="px-4 py-3">Company</th>
                        <th className="px-3 py-3">Vertical</th>
                        <th className="px-3 py-3">Location</th>
                        <th className="px-3 py-3 text-center">Score</th>
                        <th className="px-3 py-3">Priority</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {filteredLeads.map((lead) => {
                        const isSelected = selectedLead?.id === lead.id;
                        return (
                          <tr
                            key={lead.id}
                            onClick={() => setSelectedLeadId(lead.id)}
                            className={`cursor-pointer transition-colors ${
                              isSelected ? "bg-cyan-500/10 border-l-2 border-cyan-400" : "hover:bg-slate-800/40"
                            }`}
                          >
                            <td className="px-4 py-3">
                              <div className="font-semibold text-white">{lead.name}</div>
                              <div className="text-[11px] text-slate-400 truncate max-w-[180px]">
                                {lead.websiteUrl || "No website"}
                              </div>
                            </td>
                            <td className="px-3 py-3 text-slate-300">{lead.category}</td>
                            <td className="px-3 py-3 text-slate-300">
                              {lead.city}, {lead.country}
                            </td>
                            <td className="px-3 py-3 text-center">
                              <span className="font-bold text-sm text-cyan-300">{lead.score.total}</span>
                            </td>
                            <td className="px-3 py-3">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                  lead.score.priority === "HIGH_PRIORITY"
                                    ? "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                                    : lead.score.priority === "POTENTIAL_PROSPECT"
                                    ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30"
                                    : "bg-slate-700/30 text-slate-400"
                                }`}
                              >
                                {lead.score.priority.replace("_", " ")}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Lead Evidence Drawer */}
              <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-5 border border-slate-800/80 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h4 className="font-bold text-white text-base">{selectedLead.name}</h4>
                    <span className="text-xs text-slate-400">{selectedLead.category}</span>
                  </div>
                  <span className="text-xl font-extrabold text-cyan-400">{selectedLead.score.total}/100</span>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-slate-400">Website:</span>
                    {selectedLead.websiteUrl ? (
                      <div className="mt-1 flex flex-col gap-1.5 bg-slate-950 p-2.5 rounded border border-slate-800">
                        <div className="flex items-center justify-between gap-2">
                          <a
                            href={selectedLead.websiteUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="text-cyan-400 hover:underline truncate inline-flex items-center gap-1 text-[11px] font-medium"
                          >
                            <span>{selectedLead.websiteUrl}</span>
                            <ExternalLink className="w-3 h-3 flex-shrink-0" />
                          </a>
                          <button
                            onClick={() => handleAuditLeadWebsite(selectedLead)}
                            disabled={auditingLeadId === selectedLead.id}
                            className="px-2 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-[10px] font-semibold flex items-center gap-1 disabled:opacity-50 flex-shrink-0"
                            title="Run live opportunity scan on this URL"
                          >
                            {auditingLeadId === selectedLead.id ? (
                              <RefreshCw className="w-3 h-3 animate-spin" />
                            ) : (
                              <Zap className="w-3 h-3" />
                            )}
                            <span>Audit</span>
                          </button>
                        </div>
                        {selectedLead.isReachable === false && (
                          <div className="text-[10px] text-rose-400 flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" />
                            <span>Site Unreachable / Offline — Prime prospect for New Web Development!</span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="mt-1 flex items-center justify-between gap-2 bg-slate-950 p-2 rounded border border-slate-800">
                        <span className="text-amber-400 text-[11px] font-medium flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                          <span>No official website listed</span>
                        </span>
                        <a
                          href={`https://www.google.com/search?q=${encodeURIComponent(selectedLead.name + " " + selectedLead.city)}`}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[10px] font-semibold flex items-center gap-1"
                        >
                          <span>Google Search</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    )}
                  </div>

                  <div>
                    <span className="text-slate-400">Contact Channels:</span>
                    <div className="mt-1 space-y-1">
                      {selectedLead.contacts.length > 0 ? (
                        selectedLead.contacts.map((c, i) => (
                          <div
                            key={i}
                            className="flex items-center justify-between bg-slate-950 px-2.5 py-1.5 rounded border border-slate-800 text-[11px]"
                          >
                            <span className="text-slate-400 font-medium">{c.type}:</span>
                            {c.type === "EMAIL" ? (
                              <a href={`mailto:${c.value}`} className="text-cyan-300 hover:underline">
                                {c.value}
                              </a>
                            ) : c.type === "PHONE" ? (
                              <a href={`tel:${c.value}`} className="text-cyan-300 hover:underline">
                                {c.value}
                              </a>
                            ) : (
                              <span className="text-slate-200 truncate max-w-[160px]">{c.value}</span>
                            )}
                          </div>
                        ))
                      ) : (
                        <div className="text-slate-500 text-[11px] italic">No direct contact indexed</div>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-slate-400">Observable Opportunities:</span>
                      <span className="text-[10px] text-cyan-400 font-semibold">{selectedLead.analyses.length} found</span>
                    </div>
                    <div className="space-y-1.5">
                      {selectedLead.analyses.length > 0 ? (
                        selectedLead.analyses.map((a, i) => (
                          <div key={i} className="p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] space-y-1">
                            <div className="font-semibold text-cyan-300 flex items-center justify-between">
                              <span>[{a.category}]</span>
                              <span className="text-[10px] text-slate-400 font-normal">{a.confidence} Confidence</span>
                            </div>
                            <p className="text-slate-300">{a.shortExplanation}</p>
                            <div className="text-[10px] text-indigo-300 font-medium">Pitch: {a.recommendedService}</div>
                          </div>
                        ))
                      ) : (
                        <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] text-slate-500 italic">
                          Click &quot;Audit&quot; above to scan website for opportunities.
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="pt-2 flex gap-2">
                    <button
                      onClick={() => setActiveTab("outreach")}
                      className="w-full py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg font-semibold text-xs transition-all shadow-md shadow-cyan-500/20"
                    >
                      Draft Outreach Pitch
                    </button>
                    <button
                      onClick={() => handlePurgeLead(selectedLead.id)}
                      className="px-3 py-2 bg-rose-950/30 hover:bg-rose-900/50 text-rose-400 rounded-lg text-xs border border-rose-800/40"
                      title="Purge Record (Right to be Forgotten)"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: LIVE LEAD FINDER / DISCOVERY */}
        {activeTab === "discovery" && (
          <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-6">
            <div>
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-lg text-white">Live Global Lead Discovery Engine</h3>
                <span className="text-xs px-2.5 py-1 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-medium">
                  OpenStreetMap Overpass API
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Search any city worldwide. Discovers genuine registered companies with names, websites, phone numbers, and categories.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div>
                <label className="text-xs text-slate-400 mb-1 block font-medium">Target City</label>
                <input
                  type="text"
                  placeholder="e.g. Austin, London, Dubai, Toronto"
                  value={discoverCity}
                  onChange={(e) => setDiscoverCity(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-1 block font-medium">Target Country</label>
                <select
                  value={discoverCountry}
                  onChange={(e) => setDiscoverCountry(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  <option value="United States">United States</option>
                  <option value="Canada">Canada</option>
                  <option value="Australia">Australia</option>
                  <option value="United Arab Emirates">United Arab Emirates</option>
                  <option value="United Kingdom">United Kingdom</option>
                  <option value="Germany">Germany</option>
                  <option value="Pakistan">Pakistan</option>
                  <option value="Saudi Arabia">Saudi Arabia</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-1 block font-medium">Industry Vertical</label>
                <select
                  value={discoverCategory}
                  onChange={(e) => setDiscoverCategory(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  <option value="Healthcare & Medical">Healthcare & Medical (Clinics, Dental)</option>
                  <option value="Legal & Financial Services">Legal & Financial Services (Lawyers, CPAs)</option>
                  <option value="Consulting & IT Companies">Consulting & IT Companies</option>
                  <option value="Trades & Contractors (HVAC, Plumbing, Roofing)">Trades & Contractors (HVAC, Plumbing)</option>
                  <option value="Real Estate & Property">Real Estate & Property</option>
                  <option value="Hospitality & Dining">Hospitality & Dining</option>
                  <option value="Automotive & Transport">Automotive & Repair</option>
                  <option value="Fitness, Spa & Wellness">Fitness, Spa & Wellness</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 mb-1 block font-medium">Result Count Limit</label>
                <select
                  value={discoverLimit}
                  onChange={(e) => setDiscoverLimit(Number(e.target.value))}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  <option value={10}>10 Leads</option>
                  <option value={15}>15 Leads</option>
                  <option value={25}>25 Leads</option>
                  <option value={40}>40 Leads</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleRunDiscovery}
              disabled={isDiscovering}
              className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-all shadow-md shadow-cyan-500/20 disabled:opacity-50"
            >
              {isDiscovering ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
              <span>{isDiscovering ? "Running Live Discovery..." : "Launch Live Discovery"}</span>
            </button>

            {discoverySuccess && (
              <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-lg text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>{discoverySuccess}</span>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: LIVE TECH ANALYZER */}
        {activeTab === "analyzer" && (
          <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-6">
            <div>
              <h3 className="font-bold text-lg text-white">Live Observable Website Opportunity Scanner</h3>
              <p className="text-xs text-slate-400 mt-1">
                Safely inspect any target URL for observable technology gaps: missing mobile viewport, lack of 24/7 AI chatbot, absent booking automation, or heavy phone inquiry bottlenecks.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                placeholder="https://example.com"
                value={analyzeUrl}
                onChange={(e) => setAnalyzeUrl(e.target.value)}
                className="flex-1 px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
              <input
                type="text"
                placeholder="Industry vertical (e.g. Dentist, Law, Contractor)"
                value={analyzeCategory}
                onChange={(e) => setAnalyzeCategory(e.target.value)}
                className="w-full sm:w-64 px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
              <button
                onClick={handleRunScan}
                disabled={isAnalyzing}
                className="px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {isAnalyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                <span>{isAnalyzing ? "Scanning DOM..." : "Run Safe Scan"}</span>
              </button>
            </div>

            {analysisResult && (
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h4 className="font-bold text-white text-sm">{analysisResult.pageTitle || analysisResult.url}</h4>
                    <span className="text-xs text-slate-400">{analysisResult.url}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                      HTTP {analysisResult.httpStatus}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        analysisResult.hasSsl ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"
                      }`}
                    >
                      {analysisResult.hasSsl ? "SSL Active" : "No SSL"}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-300">Detected Observable Technology Gaps:</span>
                  {analysisResult.analyses?.length > 0 ? (
                    analysisResult.analyses.map((a: any, i: number) => (
                      <div key={i} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-cyan-400">[{a.category}]</span>
                          <span className="text-[10px] text-slate-400">{a.confidence} Confidence</span>
                        </div>
                        <p className="text-slate-300">{a.shortExplanation}</p>
                        <div className="text-[11px] text-indigo-300 font-medium">Recommended Pitch: {a.recommendedService}</div>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-slate-400">No observable defects identified.</div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 5: OUTREACH DRAFT STUDIO */}
        {activeTab === "outreach" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-5 border border-slate-800/80 space-y-4">
              <h3 className="font-bold text-white text-base">Select Prospect &amp; Service</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Target Company</label>
                  <select
                    value={selectedLeadId}
                    onChange={(e) => setSelectedLeadId(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
                  >
                    {leads.map((l) => (
                      <option key={l.id} value={l.id}>
                        {l.name} ({l.score.total} pts)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Pitch Service Focus</label>
                  <select
                    value={outreachService}
                    onChange={(e) => setOutreachService(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
                  >
                    {Object.keys(SERVICE_TEMPLATES).map((srv) => (
                      <option key={srv} value={srv}>
                        {srv}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={handleGenerateDraft}
                  className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md shadow-cyan-500/20"
                >
                  <Bot className="w-4 h-4" />
                  <span>Generate Consultative Pitch</span>
                </button>
              </div>

              <div className="border-t border-slate-800 pt-3">
                <span className="text-xs font-semibold text-slate-400">Cited Evidence Observations:</span>
                <div className="mt-2 space-y-1">
                  {selectedLead.analyses.length > 0 ? (
                    selectedLead.analyses.map((a, i) => (
                      <div key={i} className="text-[11px] text-slate-300 p-2 bg-slate-950 rounded border border-slate-800">
                        • {a.shortExplanation}
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-500 text-[11px] italic">No technology gap findings logged yet.</div>
                  )}
                </div>
              </div>
            </div>

            {/* Draft Preview & Reviewer Workflow */}
            <div className="lg:col-span-2 bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-4">
              <h3 className="font-bold text-white text-base">Outreach Drafts ({selectedLead.outreachDrafts.length})</h3>

              {selectedLead.outreachDrafts.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs">
                  No outreach drafts generated for this prospect yet. Click &quot;Generate Consultative Pitch&quot; to prepare a tailored message.
                </div>
              ) : (
                <div className="space-y-4">
                  {selectedLead.outreachDrafts.map((draft) => (
                    <div key={draft.id} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">{draft.serviceFocus}</span>
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              draft.status === "APPROVED"
                                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                                : draft.status === "REJECTED"
                                ? "bg-rose-500/20 text-rose-400"
                                : "bg-slate-800 text-slate-400"
                            }`}
                          >
                            {draft.status}
                          </span>
                          <button
                            onClick={() => handleCopyDraft(draft)}
                            className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1"
                            title="Copy to Clipboard"
                          >
                            {copiedDraftId === draft.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                          </button>
                        </div>
                      </div>

                      <div className="text-xs font-semibold text-slate-200">
                        <span className="text-slate-500">Subject:</span> {draft.subject}
                      </div>

                      <pre className="text-xs font-sans text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800/80 whitespace-pre-wrap leading-relaxed">
                        {draft.body}
                      </pre>

                      <div className="flex items-center justify-between text-xs pt-1">
                        <span className="text-[11px] text-slate-500">
                          {draft.reviewedBy ? `Reviewed by ${draft.reviewedBy}` : "Pending Review"}
                        </span>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleUpdateDraftStatus(selectedLead.id, draft.id, "APPROVED")}
                            className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-medium transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleUpdateDraftStatus(selectedLead.id, draft.id, "REJECTED")}
                            className="px-3 py-1 bg-rose-950 hover:bg-rose-900 text-rose-300 rounded text-xs border border-rose-800/40"
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 6: SCORING & WEIGHTS */}
        {activeTab === "scoring" && (
          <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-6">
            <div>
              <h3 className="font-bold text-lg text-white">Configurable Lead Qualification Weights</h3>
              <p className="text-xs text-slate-400 mt-1">
                Adjust points for each factual criterion. The scoring engine recalculates all leads dynamically in real time.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                    <span>Business Legitimacy Max Points</span>
                    <span className="text-cyan-400">{weights.maxLegitimacy} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="40"
                    value={weights.maxLegitimacy}
                    onChange={(e) => handleRecalculateScores({ ...weights, maxLegitimacy: Number(e.target.value) })}
                    className="w-full accent-cyan-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                    <span>XENITH Relevance Max Points</span>
                    <span className="text-cyan-400">{weights.maxRelevance} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="40"
                    value={weights.maxRelevance}
                    onChange={(e) => handleRecalculateScores({ ...weights, maxRelevance: Number(e.target.value) })}
                    className="w-full accent-cyan-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                    <span>Observable Tech Opportunity Max Points</span>
                    <span className="text-cyan-400">{weights.maxOpportunity} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="40"
                    value={weights.maxOpportunity}
                    onChange={(e) => handleRecalculateScores({ ...weights, maxOpportunity: Number(e.target.value) })}
                    className="w-full accent-cyan-500"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                    <span>Business Contact Channel Max Points</span>
                    <span className="text-cyan-400">{weights.maxContact} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="30"
                    value={weights.maxContact}
                    onChange={(e) => handleRecalculateScores({ ...weights, maxContact: Number(e.target.value) })}
                    className="w-full accent-cyan-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                    <span>Evidence Quality &amp; Recency Max Points</span>
                    <span className="text-cyan-400">{weights.maxEvidence} pts</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="30"
                    value={weights.maxEvidence}
                    onChange={(e) => handleRecalculateScores({ ...weights, maxEvidence: Number(e.target.value) })}
                    className="w-full accent-cyan-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                    <span>High Priority Threshold</span>
                    <span className="text-amber-400">&gt;= {weights.highPriorityMin} pts</span>
                  </div>
                  <input
                    type="range"
                    min="50"
                    max="95"
                    value={weights.highPriorityMin}
                    onChange={(e) => handleRecalculateScores({ ...weights, highPriorityMin: Number(e.target.value) })}
                    className="w-full accent-amber-500"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: SUPPRESSION & DNC CONTROLS */}
        {activeTab === "suppression" && (
          <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-6">
            <div>
              <h3 className="font-bold text-lg text-white">Global Do-Not-Contact &amp; Suppression Registry</h3>
              <p className="text-xs text-slate-400 mt-1">
                Any domain, email, phone, or company name added here is strictly blocked from outreach generation and data exports.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <select
                value={newSupType}
                onChange={(e) => setNewSupType(e.target.value as any)}
                className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="DOMAIN">Domain</option>
                <option value="EMAIL">Email</option>
                <option value="PHONE">Phone Number</option>
                <option value="COMPANY_NAME">Company Name</option>
              </select>

              <input
                type="text"
                placeholder="Value (e.g. competitor.com or bad@email.com)"
                value={newSupValue}
                onChange={(e) => setNewSupValue(e.target.value)}
                className="sm:col-span-2 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />

              <button
                onClick={handleAddSuppression}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Add Suppression</span>
              </button>
            </div>

            <div className="border border-slate-800 rounded-xl overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Blocked Value</th>
                    <th className="px-4 py-3">Reason</th>
                    <th className="px-4 py-3">Date Added</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {suppressionList.map((sup) => (
                    <tr key={sup.id} className="hover:bg-slate-800/30">
                      <td className="px-4 py-2.5 font-bold text-rose-400">{sup.type}</td>
                      <td className="px-4 py-2.5 text-slate-200">{sup.value}</td>
                      <td className="px-4 py-2.5 text-slate-400">{sup.reason}</td>
                      <td className="px-4 py-2.5 text-slate-500">{sup.addedAt}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 8: IMPORT / EXPORT */}
        {activeTab === "export" && (
          <div className="space-y-6">
            <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-4">
              <div>
                <h3 className="font-bold text-lg text-white">Export Lead Intelligence</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Export verified prospects with observable opportunities, calculated scores, and direct contact channels into standard CSV.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                  <span className="text-sm font-semibold text-white">Current Filtered Prospects: {filteredLeads.length}</span>
                  <p className="text-xs text-slate-400">Includes company names, verified emails, phone numbers, and tech gap citations.</p>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleDownloadCSV}
                    className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors shadow-lg shadow-cyan-500/20"
                  >
                    <FileText className="w-4 h-4" />
                    <span>Download CSV</span>
                  </button>
                  <button
                    onClick={handleDownloadCSV}
                    className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors shadow-lg shadow-emerald-500/20"
                  >
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>Excel Compatible</span>
                  </button>
                </div>
              </div>
            </div>

            {/* CSV Import Card */}
            <div className="bg-slate-900/60 backdrop-blur-md rounded-xl p-6 border border-slate-800/80 space-y-4">
              <div>
                <h3 className="font-bold text-lg text-white">Import Prospects via CSV</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Upload an existing CSV file of business prospects. Required columns: Name, Category, City, Country, Website, Email, Phone.
                </p>
              </div>

              <div className="p-6 border-2 border-dashed border-slate-700 hover:border-cyan-500/50 rounded-xl bg-slate-950/50 text-center space-y-3 transition-colors">
                <Upload className="w-8 h-8 text-cyan-400 mx-auto" />
                <div>
                  <p className="text-xs font-semibold text-slate-200">Select a CSV file from your computer</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">Supports standard CSV exports from Google Maps, Apollo, or Excel</p>
                </div>
                <input
                  type="file"
                  accept=".csv"
                  ref={fileInputRef}
                  onChange={handleCSVUpload}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-300 rounded-lg text-xs font-semibold border border-slate-700 transition-all inline-flex items-center gap-2"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>Choose CSV File</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Manual Add Lead Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-base text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-cyan-400" />
                <span>Add New Prospect</span>
              </h3>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateManualLead} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1 font-medium">Business Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Skyline Dental Associates"
                  value={newLeadForm.name}
                  onChange={(e) => setNewLeadForm({ ...newLeadForm, name: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Industry Vertical</label>
                  <input
                    type="text"
                    placeholder="e.g. Dental Clinic"
                    value={newLeadForm.category}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, category: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">City</label>
                  <input
                    type="text"
                    placeholder="e.g. Austin"
                    value={newLeadForm.city}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, city: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Country</label>
                  <select
                    value={newLeadForm.country}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, country: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="United States">United States</option>
                    <option value="Canada">Canada</option>
                    <option value="Australia">Australia</option>
                    <option value="United Arab Emirates">United Arab Emirates</option>
                    <option value="United Kingdom">United Kingdom</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Website URL</label>
                  <input
                    type="text"
                    placeholder="https://example.com"
                    value={newLeadForm.websiteUrl}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, websiteUrl: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Email Address</label>
                  <input
                    type="email"
                    placeholder="contact@company.com"
                    value={newLeadForm.email}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, email: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-medium">Phone Number</label>
                  <input
                    type="text"
                    placeholder="+1 555 123 4567"
                    value={newLeadForm.phone}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, phone: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-cyan-500/20"
                >
                  Save Prospect
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-6 text-center text-xs text-slate-500 bg-[#090d16]">
        XENITH Solutions — Enterprise B2B Lead Intelligence Platform • Vercel Ready • 100% Free Operational Stack
      </footer>
    </div>
  );
}
