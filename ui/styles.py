"""Custom CSS and aesthetic themes for XENITH Lead Generator."""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Top banner branding */
    .xenith-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0369a1 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .xenith-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .xenith-header p {
        margin: 6px 0 0 0;
        font-size: 14px;
        color: #94a3b8;
    }

    /* KPI Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 18px 20px;
        border: 1px solid #334155;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    .metric-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    
    .metric-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-top: 8px;
    }
    
    .badge-cyan { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
    .badge-green { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .badge-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; }

    /* Evidence pill */
    .evidence-pill {
        background: #0f172a;
        border: 1px solid #38bdf8;
        border-radius: 6px;
        padding: 6px 12px;
        margin: 4px 0;
        font-size: 13px;
        color: #e2e8f0;
    }

    /* Status Badges */
    .status-verified {
        color: #22c55e;
        font-weight: 600;
    }
    .status-unverified {
        color: #94a3b8;
        font-weight: 500;
    }
    .status-high {
        color: #ef4444;
        font-weight: 700;
    }
    .status-potential {
        color: #3b82f6;
        font-weight: 600;
    }
</style>
"""


def render_xenith_header():
    """Render branded top header."""
    return """
    <div class="xenith-header">
        <h1>XENITH Solutions — B2B Lead Generator</h1>
        <p>Evidence-Backed Lead Discovery • Conservative Web Intelligence • Opportunity Scoring • Compliant Outreach</p>
    </div>
    """
