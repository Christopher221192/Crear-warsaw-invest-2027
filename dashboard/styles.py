def get_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* ─────────────────────────────────────────────────────────────────────
           BASE
        ───────────────────────────────────────────────────────────────────── */
        .stApp {
            background-color: #030308;
            color: #e8e8f0;
        }

        /* Subtle grid texture overlay */
        .stApp::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }

        /* ─────────────────────────────────────────────────────────────────────
           TYPOGRAPHY
        ───────────────────────────────────────────────────────────────────── */
        h1, h2, h3, h4 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            letter-spacing: -0.03em;
            color: #f0f0fa;
        }

        .premium-id {
            color: rgba(255,255,255,0.28);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }

        .section-label {
            color: rgba(255,255,255,0.55);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            margin: 0 0 16px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding-bottom: 6px;
        }

        /* ─────────────────────────────────────────────────────────────────────
           CARDS — Glassmorphism
        ───────────────────────────────────────────────────────────────────── */
        .bento-card {
            background: linear-gradient(
                135deg,
                rgba(25,25,35,0.6) 0%,
                rgba(15,15,22,0.4) 100%
            );
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 20px;
            padding: 24px 28px;
            margin-bottom: 16px;
            transition: border-color 0.25s ease, box-shadow 0.25s ease;
            position: relative;
            overflow: hidden;
        }

        .bento-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
        }

        .bento-card:hover {
            border-color: rgba(255,255,255,0.13);
            box-shadow: 0 24px 48px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,215,0,0.04);
        }

        /* ─────────────────────────────────────────────────────────────────────
           METRICS ROW
        ───────────────────────────────────────────────────────────────────── */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 14px;
            padding: 16px 18px;
        }

        [data-testid="stMetricLabel"] > div {
            color: rgba(255,255,255,0.35) !important;
            font-size: 0.72rem !important;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-family: 'Inter', sans-serif !important;
        }

        [data-testid="stMetricValue"] > div {
            color: #f0f0fa !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }

        /* ─────────────────────────────────────────────────────────────────────
           DATA TABLE
        ───────────────────────────────────────────────────────────────────── */
        [data-testid="stDataEditor"] > div {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.07) !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }

        /* ─────────────────────────────────────────────────────────────────────
           DETAIL — HERO
        ───────────────────────────────────────────────────────────────────── */
        .detail-hero {
            padding: 4px 0 16px 0;
        }

        .detail-title {
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 2rem;
            color: #f0f0fa;
            margin: 0 0 4px 0;
            letter-spacing: -0.045em;
            line-height: 1.1;
        }

        .detail-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            color: rgba(255,255,255,0.28);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 14px;
        }

        .price-display {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.4rem;
            font-weight: 700;
            color: #FFD700;
            letter-spacing: -0.02em;
            line-height: 1;
            margin: 10px 0 4px 0;
            text-shadow: 0 0 40px rgba(255,215,0,0.25);
        }

        .price-sqm {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
            color: rgba(255,255,255,0.38);
        }

        /* ─────────────────────────────────────────────────────────────────────
           TABS
        ───────────────────────────────────────────────────────────────────── */
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 1px solid rgba(255,255,255,0.07) !important;
            gap: 0 !important;
        }

        [data-testid="stTabs"] [data-baseweb="tab"] {
            background: transparent !important;
            color: rgba(255,255,255,0.38) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.84rem !important;
            font-weight: 500 !important;
            padding: 10px 20px !important;
            border-radius: 0 !important;
            border-bottom: 2px solid transparent !important;
            transition: color 0.2s, border-color 0.2s !important;
        }

        [data-testid="stTabs"] [data-baseweb="tab"]:hover {
            color: rgba(255,255,255,0.75) !important;
            background: rgba(255,255,255,0.03) !important;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            color: #FFD700 !important;
            border-bottom-color: #FFD700 !important;
            background: transparent !important;
        }

        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            display: none !important;
        }

        /* ─────────────────────────────────────────────────────────────────────
           SPEC GRID
        ───────────────────────────────────────────────────────────────────── */
        .spec-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px 28px;
            margin-top: 8px;
        }

        .spec-item {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        .spec-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.66rem;
            color: rgba(255,255,255,0.28);
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }

        .spec-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: rgba(255,255,255,0.85);
            font-weight: 500;
        }

        .spec-value.gold {
            color: #FFD700;
            font-size: 1.05rem;
        }

        /* ─────────────────────────────────────────────────────────────────────
           FEATURE LIST
        ───────────────────────────────────────────────────────────────────── */
        .feature-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 9px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: rgba(255,255,255,0.75);
            line-height: 1.4;
        }

        .feature-item:last-child { border-bottom: none; }

        /* ─────────────────────────────────────────────────────────────────────
           MORTGAGE
        ───────────────────────────────────────────────────────────────────── */
        .mortgage-summary { margin-top: 8px; }

        .mort-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .mort-row:last-child { border-bottom: none; }

        .mort-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.82rem;
            color: rgba(255,255,255,0.38);
        }

        .mort-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.88rem;
            color: rgba(255,255,255,0.85);
            font-weight: 500;
        }

        .mort-value.gold  { color: #FFD700; font-size: 0.98rem; }
        .mort-value.green { color: #4ADE80; }
        .mort-value.red   { color: #F87171; }

        /* ─────────────────────────────────────────────────────────────────────
           MAP PLACEHOLDER
        ───────────────────────────────────────────────────────────────────── */
        .map-placeholder {
            height: 360px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255,255,255,0.2);
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            background: rgba(255,255,255,0.02);
            border-radius: 16px;
            border: 1px dashed rgba(255,255,255,0.07);
        }

        /* ─────────────────────────────────────────────────────────────────────
           AI ANALYSIS COMPONENTS
        ───────────────────────────────────────────────────────────────────── */
        .ai-intro {
            background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05));
            border: 1px solid rgba(139,92,246,0.18);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 20px;
        }

        .ai-intro-title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 1.05rem;
            color: rgba(255,255,255,0.9);
            margin: 0 0 8px 0;
            letter-spacing: -0.02em;
        }

        .ai-intro-desc {
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: rgba(255,255,255,0.45);
            margin: 0;
            line-height: 1.6;
        }

        .ai-metric-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }

        .ai-metric-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.68rem;
            color: rgba(255,255,255,0.55);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            margin: 0 0 6px 0;
            font-weight: 600;
        }

        .ai-metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.05rem;
            font-weight: 600;
            color: rgba(255,255,255,0.9);
            margin: 0;
        }

        .ai-summary-card {
            background: linear-gradient(135deg, rgba(255,215,0,0.04), rgba(255,165,0,0.02));
            border: 1px solid rgba(255,215,0,0.12);
            border-radius: 14px;
            padding: 20px 24px;
            margin-bottom: 16px;
        }

        .ai-summary-text {
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            color: rgba(255,255,255,0.7);
            line-height: 1.7;
            margin: 0;
        }

        .ai-pro-item {
            padding: 8px 0;
            border-bottom: 1px solid rgba(74,222,128,0.08);
            font-family: 'Inter', sans-serif;
            font-size: 0.84rem;
            color: #4ADE80;
            line-height: 1.4;
        }

        .ai-pro-item:last-of-type { border-bottom: none; }

        .ai-con-item {
            padding: 8px 0;
            border-bottom: 1px solid rgba(248,113,113,0.08);
            font-family: 'Inter', sans-serif;
            font-size: 0.84rem;
            color: #F87171;
            line-height: 1.4;
        }

        .ai-con-item:last-of-type { border-bottom: none; }

        .ai-detail-text {
            font-family: 'Inter', sans-serif;
            font-size: 0.84rem;
            color: rgba(255,255,255,0.62);
            line-height: 1.7;
            margin: 0 0 4px 0;
        }

        /* ─────────────────────────────────────────────────────────────────────
           SIDEBAR
        ───────────────────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: rgba(6,6,16,0.98) !important;
            border-right: 1px solid rgba(255,255,255,0.06) !important;
        }

        [data-testid="stSidebar"] .stMarkdown h2 {
            font-size: 0.95rem !important;
            color: rgba(255,255,255,0.6) !important;
            letter-spacing: -0.01em;
        }

        /* ─────────────────────────────────────────────────────────────────────
           BUTTONS
        ───────────────────────────────────────────────────────────────────── */
        .stButton > button {
            border-radius: 10px;
            background: rgba(255,255,255,0.06);
            color: rgba(255,255,255,0.75);
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 0.84rem;
            border: 1px solid rgba(255,255,255,0.1);
            padding: 0.5rem 1.4rem;
            transition: all 0.18s cubic-bezier(0.4,0,0.2,1);
        }

        .stButton > button:hover {
            background: rgba(255,255,255,0.1);
            color: #ffffff;
            border-color: rgba(255,255,255,0.18);
            transform: translateY(-1px);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, rgba(99,102,241,0.8), rgba(139,92,246,0.8));
            border-color: rgba(139,92,246,0.4);
            color: #ffffff;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, rgba(99,102,241,1), rgba(139,92,246,1));
            box-shadow: 0 4px 20px rgba(139,92,246,0.35);
            transform: translateY(-1px);
        }

        /* Link button */
        .stLinkButton a {
            border-radius: 10px !important;
            background: linear-gradient(135deg, rgba(255,215,0,0.12), rgba(255,165,0,0.08)) !important;
            border: 1px solid rgba(255,215,0,0.25) !important;
            color: #FFD700 !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.06em !important;
            transition: all 0.18s ease !important;
        }

        .stLinkButton a:hover {
            background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,165,0,0.15)) !important;
            border-color: rgba(255,215,0,0.4) !important;
            box-shadow: 0 4px 16px rgba(255,215,0,0.15) !important;
        }

        /* ─────────────────────────────────────────────────────────────────────
           SLIDER — gold accent
        ───────────────────────────────────────────────────────────────────── */
        [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
            background-color: #FFD700 !important;
            box-shadow: 0 0 0 4px rgba(255,215,0,0.2) !important;
        }

        [data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
            color: rgba(255,255,255,0.5) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.75rem !important;
        }

        /* ─────────────────────────────────────────────────────────────────────
           DIVIDER
        ───────────────────────────────────────────────────────────────────── */
        hr {
            border-color: rgba(255,255,255,0.06) !important;
            margin: 20px 0 !important;
        }

        /* ─────────────────────────────────────────────────────────────────────
           SCORE BADGE
        ───────────────────────────────────────────────────────────────────── */
        .score-badge {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #000;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 50px;
            font-size: 0.9rem;
            display: inline-block;
            box-shadow: 0 4px 16px rgba(255,215,0,0.28);
        }

        /* ─────────────────────────────────────────────────────────────────────
           MISC LAYOUT
        ───────────────────────────────────────────────────────────────────── */
        [data-testid="stHorizontalBlock"] {
            gap: 1.2rem;
        }

        /* Spinner */
        [data-testid="stSpinner"] p {
            color: rgba(255,255,255,0.45) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.84rem !important;
        }

        /* Number input */
        [data-testid="stNumberInput"] input {
            background: rgba(255,255,255,0.04) !important;
            border-color: rgba(255,255,255,0.1) !important;
            color: rgba(255,255,255,0.85) !important;
            font-family: 'JetBrains Mono', monospace !important;
            border-radius: 8px !important;
        }

        /* Alerts */
        [data-testid="stAlert"] {
            border-radius: 12px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
        }
    </style>
    """
