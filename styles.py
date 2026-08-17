"""Premium e-commerce storefront theme for SmartBuyer.

Glassmorphism cards, animated ambient glow, floating gradient orbs,
rich micro-interactions, and a dark luxury shopping aesthetic.
"""

import gradio as gr

THEME = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#F0FDF9", c100="#CCFBEF", c200="#99F6DB", c300="#5CEFC4",
        c400="#2DE4AD", c500="#00D4AA", c600="#00B894", c700="#009B7D",
        c800="#007D64", c900="#00604C", c950="#003D30",
    ),
    neutral_hue=gr.themes.Color(
        c50="#F8FAFC", c100="#F1F5F9", c200="#E2E8F0", c300="#CBD5E1",
        c400="#94A3B8", c500="#64748B", c600="#475569", c700="#334155",
        c800="#1E293B", c900="#0F172A", c950="#020617",
    ),
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    font_mono=["JetBrains Mono", "ui-monospace", "monospace"],
)

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ═══════════════════════════════════════════
   AMBIENT BACKGROUND — animated gradient mesh
   ═══════════════════════════════════════════ */
.gradio-container {
    background: #08090D !important;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}
.gradio-container::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
        radial-gradient(ellipse 600px 500px at 15% 20%, rgba(0, 212, 170, 0.08), transparent),
        radial-gradient(ellipse 500px 400px at 80% 10%, rgba(255, 107, 53, 0.07), transparent),
        radial-gradient(ellipse 400px 350px at 50% 80%, rgba(139, 92, 246, 0.06), transparent),
        radial-gradient(ellipse 300px 300px at 90% 70%, rgba(251, 191, 36, 0.05), transparent);
    animation: ambientShift 20s ease-in-out infinite alternate;
    pointer-events: none;
}
@keyframes ambientShift {
    0%   { transform: scale(1) translate(0, 0); }
    33%  { transform: scale(1.05) translate(-15px, 10px); }
    66%  { transform: scale(0.97) translate(10px, -8px); }
    100% { transform: scale(1.02) translate(-5px, 5px); }
}

/* Floating glow orbs */
.gradio-container::after {
    content: "";
    position: fixed;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 212, 170, 0.12) 0%, transparent 70%);
    top: 60%;
    left: 5%;
    z-index: 0;
    animation: floatOrb 12s ease-in-out infinite;
    pointer-events: none;
}
@keyframes floatOrb {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.6; }
    50%      { transform: translate(40px, -30px) scale(1.2); opacity: 1; }
}

/* Make all content sit above the ambient bg */
.gradio-container > * {
    position: relative;
    z-index: 1;
}

/* ═══════════════════════════════════════════
   HEADER — luxury storefront banner
   ═══════════════════════════════════════════ */
#header {
    padding: 28px 8px 18px;
    text-align: left;
}
#header .badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(0, 212, 170, 0.12), rgba(0, 212, 170, 0.04));
    border: 1px solid rgba(0, 212, 170, 0.2);
    color: #00D4AA;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
#header .badge .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #00D4AA;
    animation: livePulse 2s ease-in-out infinite;
}
@keyframes livePulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 4px #00D4AA; }
    50%      { opacity: 0.4; box-shadow: 0 0 8px #00D4AA; }
}
#header h1 {
    font-weight: 900;
    font-size: 42px;
    margin: 4px 0 10px;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
#header h1 .smart {
    background: linear-gradient(135deg, #00D4AA 0%, #00B894 50%, #5CEFC4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
#header h1 .buyer {
    color: #F0F0F5;
}
#header .brand-bar {
    height: 3px;
    width: 160px;
    border-radius: 3px;
    background: linear-gradient(90deg, #00D4AA 0%, #FF6B35 40%, #FBBF24 70%, #8B5CF6 100%);
    margin-bottom: 8px;
}
#header .tagline {
    color: #6B7280;
    font-size: 14px;
    font-weight: 400;
    letter-spacing: 0.01em;
}
#header .tagline strong {
    color: #9CA3AF;
    font-weight: 600;
}

/* ═══════════════════════════════════════════
   GLASSMORPHISM CARDS — chat, plan, input
   ═══════════════════════════════════════════ */
#chat, #plan-panel, #ask-panel {
    background: rgba(22, 25, 35, 0.65) !important;
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 16px !important;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.04);
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
#chat:hover, #plan-panel:hover {
    border-color: rgba(0, 212, 170, 0.12) !important;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.35),
        0 0 20px rgba(0, 212, 170, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

/* ── Chat messages ── */
#chat .message {
    font-size: 14px;
    color: #E5E7EB;
    line-height: 1.65;
}
#chat span.svelte-1gfkn0 {
    color: #00D4AA !important;
    font-weight: 700;
}
#chat .chatbot-label, #chat label, #chat .label-wrap span {
    color: #E5E7EB !important;
}
#chat .user {
    background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 184, 148, 0.05)) !important;
    border: 1px solid rgba(0, 212, 170, 0.12) !important;
    border-radius: 14px 14px 4px 14px !important;
}
#chat .bot {
    background: rgba(255, 255, 255, 0.025) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 14px 14px 14px 4px !important;
}

/* ═══════════════════════════════════════════
   RESEARCH PLAN PANEL — live status tracker
   ═══════════════════════════════════════════ */
#plan-panel {
    padding: 20px 22px;
    min-height: 200px;
}
#plan-panel h3 {
    color: #00D4AA;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin: 0 0 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    align-items: center;
    gap: 8px;
}
#plan-panel h3::before {
    content: "📋";
    font-size: 14px;
}
#plan-panel .placeholder {
    color: #6B7280;
    font-size: 13px;
    font-style: italic;
    padding: 16px 0;
}
#plan-panel ul { list-style: none; padding: 0; margin: 0; }
#plan-panel li {
    color: #E5E7EB;
    font-size: 13px;
    line-height: 1.5;
    margin: 4px 0;
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding: 8px 10px;
    border-radius: 10px;
    transition: all 0.25s ease;
    border: 1px solid transparent;
}
#plan-panel li:hover {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.04);
}
#plan-panel .mark {
    flex: none;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    position: relative;
    top: 2px;
    transition: all 0.3s ease;
}
#plan-panel li.pending .mark {
    border: 2px solid #374151;
    background: transparent;
}
#plan-panel li.in_progress .mark {
    border: 2px solid #FF6B35;
    background: rgba(255, 107, 53, 0.5);
    box-shadow: 0 0 8px rgba(255, 107, 53, 0.6);
    animation: pulseActive 1.8s ease-in-out infinite;
}
#plan-panel li.in_progress {
    background: rgba(255, 107, 53, 0.04);
    border-color: rgba(255, 107, 53, 0.08);
}
#plan-panel li.completed .mark {
    border: 2px solid #00D4AA;
    background: #00D4AA;
    box-shadow: 0 0 6px rgba(0, 212, 170, 0.4);
}
#plan-panel li.completed {
    color: #6B7280;
}
@keyframes pulseActive {
    0%, 100% { box-shadow: 0 0 4px rgba(255, 107, 53, 0.3); transform: scale(1); }
    50%      { box-shadow: 0 0 12px rgba(255, 107, 53, 0.8); transform: scale(1.15); }
}

/* ═══════════════════════════════════════════
   INPUT AREA
   ═══════════════════════════════════════════ */
#ask-panel {
    padding: 6px;
}
#ask-panel textarea {
    color: #F0F0F5 !important;
    font-size: 14px;
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease;
}
#ask-panel textarea::placeholder {
    color: #6B7280;
}
#ask-panel textarea:focus {
    border-color: rgba(0, 212, 170, 0.4) !important;
    box-shadow:
        0 0 0 3px rgba(0, 212, 170, 0.08),
        0 0 20px rgba(0, 212, 170, 0.06) !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

/* ═══════════════════════════════════════════
   BUTTONS — premium CTA with depth & glow
   ═══════════════════════════════════════════ */
#go-button {
    background: linear-gradient(135deg, #FF6B35 0%, #FF8F5E 50%, #FF6B35 100%) !important;
    background-size: 200% 200% !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 800;
    font-size: 14px;
    padding: 12px 28px !important;
    border-radius: 12px !important;
    box-shadow:
        0 4px 14px rgba(255, 107, 53, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
    letter-spacing: 0.03em;
    text-transform: none;
    animation: shimmerCTA 3s ease-in-out infinite;
}
@keyframes shimmerCTA {
    0%, 100% { background-position: 0% 50%; }
    50%      { background-position: 100% 50%; }
}
#go-button:hover {
    background: linear-gradient(135deg, #E85D2C, #FF6B35) !important;
    box-shadow:
        0 8px 25px rgba(255, 107, 53, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.25);
    transform: translateY(-2px);
}
#go-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
}

#approve-button {
    background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%) !important;
    color: #0F1117 !important;
    border: none !important;
    font-weight: 800;
    font-size: 14px;
    border-radius: 12px !important;
    box-shadow:
        0 4px 14px rgba(251, 191, 36, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
#approve-button::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
    transform: translateX(-100%);
    animation: approveSheen 2.5s ease-in-out infinite;
}
@keyframes approveSheen {
    0%   { transform: translateX(-100%); }
    60%  { transform: translateX(100%); }
    100% { transform: translateX(100%); }
}
#approve-button:hover {
    background: linear-gradient(135deg, #F59E0B, #D97706) !important;
    box-shadow: 0 8px 25px rgba(251, 191, 36, 0.45);
    transform: translateY(-2px);
}

#reset-button {
    background: transparent !important;
    color: #EF4444 !important;
    border: 1px solid rgba(239, 68, 68, 0.25) !important;
    font-weight: 600;
    border-radius: 12px !important;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
#reset-button::before {
    content: "";
    position: absolute;
    inset: 0;
    background: rgba(239, 68, 68, 0.06);
    opacity: 0;
    transition: opacity 0.3s ease;
}
#reset-button:hover {
    border-color: rgba(239, 68, 68, 0.5) !important;
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.08);
}
#reset-button:hover::before { opacity: 1; }

/* ═══════════════════════════════════════════
   SCROLLBAR — minimal sleek
   ═══════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.14); }

/* ═══════════════════════════════════════════
   GRADIO GLOBAL OVERRIDES
   ═══════════════════════════════════════════ */
.dark .gradio-container, .gradio-container {
    --body-background-fill: #08090D !important;
    --block-background-fill: rgba(22, 25, 35, 0.65) !important;
    --block-border-color: rgba(255, 255, 255, 0.06) !important;
    --body-text-color: #E5E7EB !important;
    --input-background-fill: rgba(255, 255, 255, 0.03) !important;
    --block-label-text-color: #9CA3AF !important;
    --block-title-text-color: #E5E7EB !important;
}
footer { display: none !important; }
"""

JS = """
<script>
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.replace(url.href);
    }
</script>
"""
