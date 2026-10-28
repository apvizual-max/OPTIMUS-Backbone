<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Alex Popescu × Client | B2B UX Architecture Proposal</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&family=Nunito:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
theme: {
extend: {
fontFamily: {
sans: ['Roboto', 'sans-serif'],
display: ['Nunito', 'sans-serif'],
},
colors: {
midnight: { DEFAULT: '#002060', dark: '#001540', light: '#003080' },
indian: { DEFAULT: '#d04a2f', dark: '#a83820', light: '#e8634a' },
smoke: '#f2f2f2',
steel: '#202b3a',
}
}
}
}
</script>
<style>
:root {
--color-midnight-blue: #002060;
--color-indian-red: #d04a2f;
--color-white-smoke: #f2f2f2;
--color-dark-gray: #202b3a;
}
html { scroll-behavior: smooth; }
body {
font-family: 'Roboto', sans-serif;
background: #ffffff;
color: var(--color-dark-gray);
}
h1, h2, h3, h4, h5, .font-display { font-family: 'Nunito', sans-serif; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--color-white-smoke); }
::-webkit-scrollbar-thumb { background: var(--color-midnight-blue); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--color-indian-red); }
.nav-link {
position: relative;
padding: 0.5rem 0.875rem;
font-weight: 600;
font-size: 0.8125rem;
letter-spacing: 0.03em;
color: #4a5568;
transition: color 0.2s;
white-space: nowrap;
cursor: pointer;
border-radius: 4px;
}
.nav-link:hover { color: var(--color-midnight-blue); background: rgba(0,32,96,0.05); }
.nav-link.active {
color: var(--color-midnight-blue);
background: rgba(0,32,96,0.08);
}
.nav-link.active::after {
content: '';
position: absolute;
bottom: -2px;
left: 50%;
transform: translateX(-50%);
width: 24px;
height: 3px;
background: var(--color-indian-red);
border-radius: 2px;
}
.tab-content { display: none; }
.tab-content.active { display: block; }
.info-card {
background: #ffffff;
border: 1px solid #e2e8f0;
border-radius: 8px;
padding: 1.25rem;
transition: all 0.25s ease;
cursor: pointer;
position: relative;
overflow: hidden;
}
.info-card:hover {
border-color: var(--color-indian-red);
box-shadow: 0 10px 25px -5px rgba(0,32,96,0.15);
transform: translateY(-2px);
}
.info-card::before {
content: '';
position: absolute;
top: 0; left: 0;
width: 4px; height: 100%;
background: var(--color-midnight-blue);
transform: scaleY(0);
transform-origin: top;
transition: transform 0.25s ease;
}
.info-card:hover::before { transform: scaleY(1); }
.info-card .click-hint { opacity: 0; transition: opacity 0.2s; }
.info-card:hover .click-hint { opacity: 1; }
.section-label {
display: inline-flex;
align-items: center;
gap: 0.5rem;
padding: 0.375rem 0.875rem;
background: rgba(0,32,96,0.06);
color: var(--color-midnight-blue);
font-size: 0.75rem;
font-weight: 700;
letter-spacing: 0.1em;
text-transform: uppercase;
border-radius: 4px;
border-left: 3px solid var(--color-indian-red);
}
.progress-track { height: 8px; background: #edf2f7; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--color-midnight-blue), var(--color-indian-red)); border-radius: 4px; }
.pill {
display: inline-flex;
align-items: center;
padding: 0.25rem 0.75rem;
font-size: 0.6875rem;
font-weight: 700;
letter-spacing: 0.05em;
text-transform: uppercase;
border-radius: 999px;
}
.pill-midnight { background: rgba(0,32,96,0.08); color: var(--color-midnight-blue); }
.pill-indian { background: rgba(208,74,47,0.1); color: var(--color-indian-red); }
.pill-steel { background: rgba(32,43,58,0.08); color: var(--color-dark-gray); }
.modal-overlay {
position: fixed;
inset: 0;
background: rgba(0,21,64,0.75);
backdrop-filter: blur(6px);
z-index: 100;
display: none;
align-items: center;
justify-content: center;
padding: 1rem;
}
.modal-overlay.active { display: flex; }
.modal-content {
background: #ffffff;
border-radius: 12px;
max-width: 760px;
width: 100%;
max-height: 85vh;
overflow-y: auto;
position: relative;
box-shadow: 0 25px 50px -12px rgba(0,0,0,0.4);
border-top: 6px solid var(--color-indian-red);
}
.modal-close {
position: sticky;
top: 12px;
float: right;
margin: 12px 12px 0 0;
width: 36px;
height: 36px;
background: var(--color-white-smoke);
border-radius: 50%;
display: flex;
align-items: center;
justify-content: center;
cursor: pointer;
color: var(--color-dark-gray);
font-weight: 700;
z-index: 10;
transition: all 0.2s;
}
.modal-close:hover { background: var(--color-indian-red); color: #fff; }
.modal-header { padding: 1.75rem 2rem 1rem; border-bottom: 1px solid #edf2f7; }
.modal-body { padding: 1.5rem 2rem 2rem; }
.hero-grid {
background-image:
linear-gradient(rgba(0,32,96,0.04) 1px, transparent 1px),
linear-gradient(90deg, rgba(0,32,96,0.04) 1px, transparent 1px);
background-size: 40px 40px;
}
.stat-card {
background: linear-gradient(135deg, #fff 0%, var(--color-white-smoke) 100%);
border: 1px solid #e2e8f0;
border-radius: 8px;
padding: 1.25rem;
text-align: center;
}
.stat-value {
font-family: 'Nunito', sans-serif;
font-size: 2rem;
font-weight: 800;
color: var(--color-midnight-blue);
line-height: 1;
}
.section-divider {
display: flex;
align-items: center;
gap: 1rem;
margin: 3rem 0 2rem;
}
.section-divider::before,
.section-divider::after {
content: '';
flex: 1;
height: 1px;
background: linear-gradient(90deg, transparent, #cbd5e0, transparent);
}
.sub-nav {
display: flex;
flex-wrap: wrap;
gap: 0.5rem;
padding: 1rem;
background: var(--color-white-smoke);
border-radius: 8px;
margin-bottom: 2rem;
}
.sub-nav a {
padding: 0.375rem 0.875rem;
font-size: 0.75rem;
font-weight: 600;
color: var(--color-dark-gray);
background: #fff;
border: 1px solid #e2e8f0;
border-radius: 4px;
text-decoration: none;
transition: all 0.2s;
}
.sub-nav a:hover {
background: var(--color-midnight-blue);
color: #fff;
border-color: var(--color-midnight-blue);
}
.quote-block {
border-left: 4px solid var(--color-indian-red);
padding: 1rem 1.25rem;
background: rgba(208,74,47,0.04);
font-style: italic;
color: #4a5568;
border-radius: 0 8px 8px 0;
}
.data-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.data-table th {
text-align: left;
padding: 0.75rem 1rem;
background: var(--color-midnight-blue);
color: #fff;
font-weight: 600;
font-size: 0.75rem;
letter-spacing: 0.05em;
text-transform: uppercase;
}
.data-table td { padding: 0.875rem 1rem; border-bottom: 1px solid #edf2f7; vertical-align: top; }
.data-table tr:hover td { background: #f7fafc; }
[id] { scroll-margin-top: 90px; }
@media (max-width: 768px) {
.nav-scroll { overflow-x: auto; scrollbar-width: none; }
.nav-scroll::-webkit-scrollbar { display: none; }
}
/* ===========================
WOW ANIMATION - Client GRID
=========================== */
.Client-wow-wrap {
position: relative;
width: 100%;
margin: 2rem 0 1rem;
border-radius: 16px;
overflow: hidden;
background: radial-gradient(ellipse at center, #00102e 0%, #000818 70%, #000410 100%);
border: 1px solid rgba(208,74,47,0.35);
box-shadow:
0 0 40px rgba(0,32,96,0.4),
inset 0 0 60px rgba(0,32,96,0.3);
}
.Client-wow-svg { display: block; width: 100%; height: auto; }
.Client-grid-bg {
stroke: rgba(0,120,255,0.18);
stroke-width: 0.5;
}
.Client-grid-bg-strong {
stroke: rgba(208,74,47,0.25);
stroke-width: 0.8;
}
.energy-flow {
fill: none;
stroke-linecap: round;
stroke-dasharray: 8 14;
animation: flowDash 2.4s linear infinite;
}
.energy-flow-fast { animation-duration: 1.4s; }
.energy-flow-slow { animation-duration: 4s; }
@keyframes flowDash {
from { stroke-dashoffset: 0; }
to { stroke-dashoffset: -220; }
}
.node-core {
transform-origin: center;
transform-box: fill-box;
animation: nodePulse 2.8s ease-in-out infinite;
}
@keyframes nodePulse {
0%, 100% { transform: scale(1); opacity: 1; }
50% { transform: scale(1.25); opacity: 0.7; }
}
.node-halo {
transform-origin: center;
transform-box: fill-box;
animation: haloExpand 2.8s ease-out infinite;
}
@keyframes haloExpand {
0% { transform: scale(0.6); opacity: 0.9; }
100% { transform: scale(2.4); opacity: 0; }
}
.bolt {
fill: #fff;
filter: drop-shadow(0 0 6px rgba(208,74,47,0.9)) drop-shadow(0 0 12px rgba(208,74,47,0.5));
animation: boltFlash 3.2s ease-in-out infinite;
}
.bolt-b { animation-delay: 1.1s; }
.bolt-c { animation-delay: 2.3s; }
@keyframes boltFlash {
0%, 90%, 100% { opacity: 0; transform: scale(0.85); }
92%, 96% { opacity: 1; transform: scale(1.05); }
94% { opacity: 0.6; transform: scale(0.95); }
}
.ring-rotate {
transform-origin: center;
transform-box: fill-box;
animation: ringRotate 30s linear infinite;
}
.ring-rotate-rev {
transform-origin: center;
transform-box: fill-box;
animation: ringRotateRev 22s linear infinite;
}
@keyframes ringRotate { to { transform: rotate(360deg); } }
@keyframes ringRotateRev { to { transform: rotate(-360deg); } }
.scanline {
animation: scanMove 4s linear infinite;
}
@keyframes scanMove {
0% { transform: translateY(-100%); opacity: 0; }
10% { opacity: 0.7; }
90% { opacity: 0.7; }
100% { transform: translateY(300%); opacity: 0; }
}
.hud-text {
font-family: 'Roboto', monospace;
letter-spacing: 0.15em;
animation: hudFlicker 4s ease-in-out infinite;
}
@keyframes hudFlicker {
0%, 100% { opacity: 1; }
50% { opacity: 0.55; }
52% { opacity: 1; }
54% { opacity: 0.7; }
56% { opacity: 1; }
}
/* ===========================
UI SIMULATION SHOWCASE
=========================== */
.ui-sim-wrap {
background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
border: 1px solid #d8dee9;
border-radius: 14px;
padding: 1.5rem;
box-shadow: 0 4px 20px rgba(0,32,96,0.08);
}
.ui-sim-chrome {
background: #fff;
border: 1px solid #e2e8f0;
border-radius: 10px;
overflow: hidden;
box-shadow: 0 2px 12px rgba(0,32,96,0.06);
}
.ui-sim-topbar {
background: var(--color-midnight-blue);
color: #fff;
padding: 0.625rem 1rem;
display: flex;
align-items: center;
justify-content: space-between;
gap: 0.75rem;
font-size: 0.75rem;
}
.ui-sim-topbar .dots { display: flex; gap: 6px; }
.ui-sim-topbar .dot { width: 10px; height: 10px; border-radius: 50%; }
.ui-sim-topbar .dot-r { background: #ff5f57; }
.ui-sim-topbar .dot-y { background: #febc2e; }
.ui-sim-topbar .dot-g { background: #28c840; }
.ui-sim-body {
display: grid;
grid-template-columns: 200px 1fr;
min-height: 440px;
}
@media (max-width: 768px) {
.ui-sim-body { grid-template-columns: 1fr; }
.ui-sim-sidebar { display: none; }
}
.ui-sim-sidebar {
background: #0a1535;
color: #cbd5e0;
padding: 1rem 0.75rem;
font-size: 0.75rem;
border-right: 1px solid rgba(255,255,255,0.06);
}
.ui-sim-nav-item {
display: flex;
align-items: center;
gap: 0.5rem;
padding: 0.5rem 0.625rem;
border-radius: 5px;
margin-bottom: 2px;
cursor: pointer;
transition: all 0.15s;
}
.ui-sim-nav-item:hover { background: rgba(255,255,255,0.05); color: #fff; }
.ui-sim-nav-item.active {
background: rgba(208,74,47,0.15);
color: #fff;
border-left: 2px solid var(--color-indian-red);
padding-left: calc(0.625rem - 2px);
}
.ui-sim-main { padding: 1rem 1.25rem; overflow-x: auto; }
.ui-sim-metrics {
display: grid;
grid-template-columns: repeat(4, 1fr);
gap: 0.75rem;
margin-bottom: 1rem;
}
@media (max-width: 640px) {
.ui-sim-metrics { grid-template-columns: repeat(2, 1fr); }
}
.ui-sim-metric {
background: #fff;
border: 1px solid #e2e8f0;
border-radius: 6px;
padding: 0.75rem;
position: relative;
}
.ui-sim-metric-label { font-size: 0.65rem; color: #718096; text-transform: uppercase; letter-spacing: 0.08em; }
.ui-sim-metric-value { font-size: 1.25rem; font-weight: 800; color: var(--color-midnight-blue); margin-top: 0.125rem; font-family: 'Nunito', sans-serif; }
.ui-sim-metric-delta { font-size: 0.65rem; font-weight: 700; margin-top: 0.125rem; }
.ui-sim-metric-delta.up { color: #10b981; }
.ui-sim-metric-delta.down { color: var(--color-indian-red); }
.ui-sim-spark { margin-top: 0.5rem; height: 22px; }
.ui-sim-grid {
background: #fff;
border: 1px solid #e2e8f0;
border-radius: 6px;
overflow: hidden;
}
.ui-sim-grid-head {
background: #0a1535;
color: #fff;
padding: 0.5rem 0.75rem;
display: flex;
justify-content: space-between;
align-items: center;
font-size: 0.75rem;
}
.ui-sim-grid-head .title { font-weight: 700; letter-spacing: 0.05em; }
.ui-sim-grid-head .badge {
background: rgba(208,74,47,0.2);
color: #fff;
padding: 0.125rem 0.5rem;
border-radius: 999px;
font-size: 0.625rem;
display: inline-flex;
align-items: center;
gap: 4px;
}
.ui-sim-grid-head .badge .pulse-dot {
width: 6px; height: 6px; border-radius: 50%; background: #10b981;
animation: liveDot 1.2s ease-in-out infinite;
}
@keyframes liveDot {
0%, 100% { opacity: 1; transform: scale(1); }
50% { opacity: 0.5; transform: scale(1.3); }
}
.ui-sim-grid table {
width: 100%;
border-collapse: collapse;
font-size: 0.72rem;
}
.ui-sim-grid th {
text-align: left;
padding: 0.5rem 0.625rem;
background: #f8fafc;
color: #475569;
font-weight: 600;
font-size: 0.625rem;
text-transform: uppercase;
letter-spacing: 0.06em;
border-bottom: 1px solid #e2e8f0;
white-space: nowrap;
}
.ui-sim-grid td {
padding: 0.5rem 0.625rem;
border-bottom: 1px solid #f1f5f9;
white-space: nowrap;
}
.ui-sim-grid tr { transition: background 0.15s; }
.ui-sim-grid tr:hover { background: #f8fafc; }
.ui-sim-grid tr:focus-within {
outline: 2px solid var(--color-indian-red);
outline-offset: -2px;
background: rgba(208,74,47,0.05);
}
.ui-sim-grid .row-tick-up {
animation: tickUp 2s ease-out;
}
.ui-sim-grid .row-tick-down {
animation: tickDown 2s ease-out;
}
@keyframes tickUp {
0% { background: rgba(16,185,129,0.3); }
100% { background: transparent; }
}
@keyframes tickDown {
0% { background: rgba(208,74,47,0.3); }
100% { background: transparent; }
}
.ui-sim-grid .price { font-weight: 700; font-variant-numeric: tabular-nums; }
.ui-sim-grid .price-up { color: #10b981; }
.ui-sim-grid .price-down { color: var(--color-indian-red); }
.ui-sim-grid .status-pill {
display: inline-flex;
align-items: center;
gap: 4px;
padding: 0.125rem 0.5rem;
border-radius: 999px;
font-size: 0.6rem;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 0.05em;
}
.ui-sim-grid .status-active { background: rgba(16,185,129,0.12); color: #10b981; }
.ui-sim-grid .status-pending { background: rgba(251,191,36,0.12); color: #d97706; }
.ui-sim-grid .status-cleared { background: rgba(0,32,96,0.08); color: var(--color-midnight-blue); }
.ui-sim-grid .chevron {
display: inline-block;
font-size: 0.7rem;
margin-left: 2px;
}
/* best-practice annotations */
.bp-badge {
position: absolute;
background: var(--color-midnight-blue);
color: #fff;
padding: 0.25rem 0.625rem;
border-radius: 4px;
font-size: 0.6rem;
font-weight: 700;
letter-spacing: 0.08em;
text-transform: uppercase;
box-shadow: 0 2px 8px rgba(0,32,96,0.3);
display: inline-flex;
align-items: center;
gap: 4px;
z-index: 5;
pointer-events: none;
}
.bp-badge::before {
content: '✓';
color: #10b981;
font-weight: 900;
}
.bp-badge.red { background: var(--color-indian-red); }
.bp-badge.red::before { color: #fff; }
.bp-line {
position: absolute;
border: 1px dashed var(--color-indian-red);
pointer-events: none;
z-index: 4;
}
.ui-sim-footer {
padding: 0.625rem 1rem;
background: #f8fafc;
border-top: 1px solid #e2e8f0;
display: flex;
justify-content: space-between;
align-items: center;
font-size: 0.65rem;
color: #64748b;
flex-wrap: wrap;
gap: 0.5rem;
}
.ui-sim-footer .kb-hint {
display: inline-flex;
align-items: center;
gap: 6px;
}
.kbd {
display: inline-block;
padding: 0.125rem 0.375rem;
background: #fff;
border: 1px solid #cbd5e0;
border-bottom-width: 2px;
border-radius: 3px;
font-family: 'Roboto', monospace;
font-size: 0.6rem;
font-weight: 600;
color: var(--color-midnight-blue);
}
.ui-sim-legend {
display: flex;
flex-wrap: wrap;
gap: 1rem;
padding: 0.75rem 1rem;
background: rgba(0,32,96,0.04);
border-radius: 8px;
margin-top: 1rem;
font-size: 0.7rem;
color: #475569;
}
.ui-sim-legend-item { display: flex; align-items: center; gap: 6px; }
.ui-sim-legend-item .swatch {
width: 12px; height: 12px; border-radius: 3px;
}
</style>
</head>
<body>
<nav class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm">
<div class="max-w-7xl mx-auto px-4 md:px-6">
<div class="flex items-center justify-between h-16">
<div class="flex items-center gap-3 shrink-0 cursor-pointer" onclick="switchTab('home')">
<div class="w-9 h-9 rounded-md flex items-center justify-center" style="background: var(--color-midnight-blue);">
<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/>
</svg>
</div>
<div class="hidden sm:block">
<div class="font-display font-bold text-sm leading-none" style="color: var(--color-midnight-blue);">AP-ID × Client</div>
<div class="text-[10px] text-gray-500 tracking-wider mt-0.5">B2B UX ARCHITECTURE</div>
</div>
</div>
<div class="nav-scroll flex items-center gap-1">
<div class="nav-link active" data-target="home" onclick="switchTab('home')">ALEX</div>
<div class="nav-link" data-target="Clientui" onclick="switchTab('Clientui')">Client UI</div>
<div class="nav-link" data-target="Clientint" onclick="switchTab('Clientint')">Client INT.</div>
<div class="nav-link" data-target="interview" onclick="switchTab('interview')">AI INTERVIEW</div>
<div class="nav-link" data-target="b2b" onclick="switchTab('b2b')">B2B RATE</div>
<div class="nav-link" data-target="aiui" onclick="switchTab('aiui')">AI UI</div>
</div>
<a href="mailto:apvizual@gmail.com" class="hidden md:flex items-center gap-2 px-3 py-2 rounded-md text-xs font-bold text-white shrink-0" style="background: var(--color-indian-red);">
<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
CONTACT
</a>
</div>
</div>
</nav>
<main class="max-w-7xl mx-auto px-4 md:px-6 py-8">
<!-- ============================================= -->
<!-- TAB 1: ALEX - VALUE PROPOSITION -->
<!-- ============================================= -->
<section id="home" class="tab-content active">
<!-- HERO -->
<div class="hero-grid rounded-xl p-8 md:p-12 mb-8 border border-gray-200" style="background-color: #fafbfc;">
<div class="max-w-4xl">
<div class="section-label mb-6">01 / VALUE PROPOSITION</div>
<h1 class="font-display text-4xl md:text-6xl font-extrabold leading-tight mb-6" style="color: var(--color-midnight-blue);">
The <span style="color: var(--color-indian-red);">INTJ-A Architect</span><br>
for Enterprise UX
</h1>
<p class="text-base md:text-lg text-gray-700 leading-relaxed mb-2 max-w-3xl font-semibold">
Mapping the candidate profile to Client's Senior UI/UX position.
</p>
<p class="text-sm md:text-base text-gray-600 leading-relaxed mb-8 max-w-3xl">
8 research pillars covering <span class="font-semibold" style="color: var(--color-midnight-blue);">psychology</span>, <span class="font-semibold" style="color: var(--color-midnight-blue);">portfolio</span>, <span class="font-semibold" style="color: var(--color-midnight-blue);">stack</span>, <span class="font-semibold" style="color: var(--color-midnight-blue);">gaps</span>, <span class="font-semibold" style="color: var(--color-midnight-blue);">validation</span>, <span class="font-semibold" style="color: var(--color-midnight-blue);">positioning</span>, and <span class="font-semibold" style="color: var(--color-midnight-blue);">reference documentation</span>.
</p>
<!-- ========== WOW ANIMATION: Client ENERGY GRID (FIXED) ========== -->
<div class="Client-wow-wrap">
<svg class="Client-wow-svg" viewBox="0 0 1200 380" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Client branded energy grid visualization with animated electricity flows">
<defs>
<linearGradient id="ClientGrad" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#d04a2f;stop-opacity:1" />
<stop offset="50%" style="stop-color:#ff7043;stop-opacity:1" />
<stop offset="100%" style="stop-color:#d04a2f;stop-opacity:1" />
</linearGradient>
<linearGradient id="flowBlue" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" style="stop-color:#003080;stop-opacity:0.3" />
<stop offset="50%" style="stop-color:#4d9fff;stop-opacity:1" />
<stop offset="100%" style="stop-color:#003080;stop-opacity:0.3" />
</linearGradient>
<linearGradient id="flowRed" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" style="stop-color:#d04a2f;stop-opacity:0.4" />
<stop offset="50%" style="stop-color:#ff8a6b;stop-opacity:1" />
<stop offset="100%" style="stop-color:#d04a2f;stop-opacity:0.4" />
</linearGradient>
<radialGradient id="nodeGlow" cx="50%" cy="50%" r="50%">
<stop offset="0%" style="stop-color:#4d9fff;stop-opacity:1" />
<stop offset="60%" style="stop-color:#003080;stop-opacity:0.8" />
<stop offset="100%" style="stop-color:#00102e;stop-opacity:0" />
</radialGradient>
<radialGradient id="nodeGlowRed" cx="50%" cy="50%" r="50%">
<stop offset="0%" style="stop-color:#ff8a6b;stop-opacity:1" />
<stop offset="60%" style="stop-color:#d04a2f;stop-opacity:0.8" />
<stop offset="100%" style="stop-color:#4a0f05;stop-opacity:0" />
</radialGradient>
<filter id="softGlow">
<feGaussianBlur stdDeviation="2.5" result="blur"/>
<feMerge>
<feMergeNode in="blur"/>
<feMergeNode in="SourceGraphic"/>
</feMerge>
</filter>
</defs>
<!-- background grid -->
<g opacity="0.9">
<g class="Client-grid-bg">
<line x1="0" y1="40" x2="1200" y2="40"/>
<line x1="0" y1="80" x2="1200" y2="80"/>
<line x1="0" y1="120" x2="1200" y2="120"/>
<line x1="0" y1="160" x2="1200" y2="160"/>
<line x1="0" y1="200" x2="1200" y2="200"/>
<line x1="0" y1="240" x2="1200" y2="240"/>
<line x1="0" y1="280" x2="1200" y2="280"/>
<line x1="0" y1="320" x2="1200" y2="320"/>
<line x1="0" y1="360" x2="1200" y2="360"/>
</g>
<g class="Client-grid-bg">
<line x1="60" y1="0" x2="60" y2="380"/>
<line x1="180" y1="0" x2="180" y2="380"/>
<line x1="300" y1="0" x2="300" y2="380"/>
<line x1="420" y1="0" x2="420" y2="380"/>
<line x1="540" y1="0" x2="540" y2="380"/>
<line x1="660" y1="0" x2="660" y2="380"/>
<line x1="780" y1="0" x2="780" y2="380"/>
<line x1="900" y1="0" x2="900" y2="380"/>
<line x1="1020" y1="0" x2="1020" y2="380"/>
<line x1="1140" y1="0" x2="1140" y2="380"/>
</g>
<g class="Client-grid-bg-strong">
<line x1="600" y1="0" x2="600" y2="380"/>
<line x1="0" y1="190" x2="1200" y2="190"/>
</g>
</g>
<!-- scanline effect -->
<g class="scanline">
<rect x="0" y="0" width="1200" height="2" fill="rgba(77,159,255,0.4)"/>
<rect x="0" y="2" width="1200" height="40" fill="url(#nodeGlow)" opacity="0.15"/>
</g>
<!-- energy flow paths -->
<g filter="url(#softGlow)">
<path class="energy-flow" d="M 0 100 Q 300 80, 600 100 T 1200 100" stroke="url(#flowBlue)" stroke-width="2"/>
<path class="energy-flow energy-flow-slow" d="M 0 280 Q 400 300, 800 280 T 1200 280" stroke="url(#flowBlue)" stroke-width="1.5" opacity="0.7"/>
<path class="energy-flow energy-flow-fast" d="M 100 40 L 300 40 L 420 160 L 600 160 L 780 40 L 1100 40" stroke="url(#flowRed)" stroke-width="2"/>
<path class="energy-flow" d="M 60 340 L 240 340 L 360 220 L 540 220 L 720 340 L 900 340 L 1080 220 L 1200 220" stroke="url(#flowRed)" stroke-width="1.5" opacity="0.8"/>
<path class="energy-flow energy-flow-slow" d="M 0 200 Q 300 100, 600 190 Q 900 280, 1200 190" stroke="url(#flowBlue)" stroke-width="1.2" opacity="0.6"/>
</g>
<!-- node cluster LEFT (generation) -->
<g>
<circle class="node-halo" cx="120" cy="100" r="14" fill="none" stroke="#4d9fff" stroke-width="1.5"/>
<circle class="node-core" cx="120" cy="100" r="6" fill="url(#nodeGlow)"/>
<text x="120" y="128" text-anchor="middle" fill="#4d9fff" font-size="8" font-family="Roboto" class="hud-text">GEN-01</text>
</g>
<g>
<circle class="node-halo" cx="240" cy="280" r="14" fill="none" stroke="#4d9fff" stroke-width="1.5"/>
<circle class="node-core" cx="240" cy="280" r="6" fill="url(#nodeGlow)"/>
<text x="240" y="308" text-anchor="middle" fill="#4d9fff" font-size="8" font-family="Roboto" class="hud-text">SOLAR-A</text>
</g>
<g>
<circle class="node-halo" cx="180" cy="200" r="12" fill="none" stroke="#4d9fff" stroke-width="1.2"/>
<circle class="node-core" cx="180" cy="200" r="5" fill="url(#nodeGlow)"/>
<text x="180" y="225" text-anchor="middle" fill="#4d9fff" font-size="7" font-family="Roboto" class="hud-text">WIND-7</text>
</g>
<!-- node cluster RIGHT (consumption/trading) -->
<g>
<circle class="node-halo" cx="1080" cy="100" r="14" fill="none" stroke="#ff8a6b" stroke-width="1.5"/>
<circle class="node-core" cx="1080" cy="100" r="6" fill="url(#nodeGlowRed)"/>
<text x="1080" y="128" text-anchor="middle" fill="#ff8a6b" font-size="8" font-family="Roboto" class="hud-text">MARKET</text>
</g>
<g>
<circle class="node-halo" cx="960" cy="280" r="14" fill="none" stroke="#ff8a6b" stroke-width="1.5"/>
<circle class="node-core" cx="960" cy="280" r="6" fill="url(#nodeGlowRed)"/>
<text x="960" y="308" text-anchor="middle" fill="#ff8a6b" font-size="8" font-family="Roboto" class="hud-text">GRID-EU</text>
</g>
<g>
<circle class="node-halo" cx="1020" cy="200" r="12" fill="none" stroke="#ff8a6b" stroke-width="1.2"/>
<circle class="node-core" cx="1020" cy="200" r="5" fill="url(#nodeGlowRed)"/>
<text x="1020" y="225" text-anchor="middle" fill="#ff8a6b" font-size="7" font-family="Roboto" class="hud-text">AUCTION</text>
</g>
<!-- ========== central Client hub (FIXED: silhouette removed, Client text centered) ========== -->
<g transform="translate(600,190)">
<!-- outer rotating ring -->
<g class="ring-rotate">
<circle r="80" fill="none" stroke="rgba(208,74,47,0.4)" stroke-width="1" stroke-dasharray="4 6"/>
</g>
<g class="ring-rotate-rev">
<circle r="68" fill="none" stroke="rgba(77,159,255,0.5)" stroke-width="1" stroke-dasharray="2 4"/>
</g>
<!-- mid filled circle with orange stroke -->
<circle r="56" fill="rgba(0,32,96,0.5)" stroke="#d04a2f" stroke-width="1.5"/>
<circle r="56" fill="none" stroke="#4d9fff" stroke-width="0.8" stroke-dasharray="3 5" opacity="0.6"/>
<!-- Client text centered perfectly in the middle of the orange stroked circle -->
<text y="5" text-anchor="middle" dominant-baseline="middle" fill="#fff" font-family="Nunito" font-size="16" font-weight="800" letter-spacing="4">Client</text>
</g>
<!-- lightning bolts -->
<g>
<polygon class="bolt" points="420,150 425,165 418,165 423,180 413,160 420,160 415,150"/>
<polygon class="bolt bolt-b" points="780,150 785,165 778,165 783,180 773,160 780,160 775,150"/>
<polygon class="bolt bolt-c" points="600,60 605,75 598,75 603,90 593,70 600,70 595,60"/>
</g>
<!-- HUD text overlays -->
<g class="hud-text" fill="#4d9fff" font-size="9">
<text x="20" y="24">GRID-OPS :: LIVE</text>
<text x="20" y="372">FREQ 50.02Hz ▸ STABLE</text>
<text x="1060" y="24" text-anchor="end">LATENCY &lt; 12ms</text>
<text x="1060" y="372" text-anchor="end">NODES: 2,847 ACTIVE</text>
</g>
<g class="hud-text" fill="#ff8a6b" font-size="9">
<text x="600" y="24" text-anchor="middle">⚡ Client :: ENERGY INTELLIGENCE LAYER ⚡</text>
</g>
<!-- data packets moving along paths -->
<g>
<circle r="3" fill="#fff" filter="url(#softGlow)">
<animateMotion dur="3s" repeatCount="indefinite" path="M 0 100 Q 300 80, 600 100 T 1200 100"/>
</circle>
<circle r="3" fill="#ff8a6b" filter="url(#softGlow)">
<animateMotion dur="2.2s" repeatCount="indefinite" path="M 100 40 L 300 40 L 420 160 L 600 160 L 780 40 L 1100 40"/>
</circle>
<circle r="2.5" fill="#4d9fff" filter="url(#softGlow)">
<animateMotion dur="4s" repeatCount="indefinite" path="M 0 280 Q 400 300, 800 280 T 1200 280"/>
</circle>
<circle r="2.5" fill="#fff" filter="url(#softGlow)">
<animateMotion dur="5s" repeatCount="indefinite" path="M 60 340 L 240 340 L 360 220 L 540 220 L 720 340 L 900 340 L 1080 220 L 1200 220"/>
</circle>
</g>
</svg>
<!-- HUD bottom strip -->
<div class="absolute bottom-0 left-0 right-0 px-4 py-2 flex items-center justify-between text-[10px] text-white/80 bg-gradient-to-t from-black/60 to-transparent font-mono tracking-widest pointer-events-none" style="letter-spacing: 0.2em;">
<span class="flex items-center gap-2">
<span class="w-1.5 h-1.5 rounded-full" style="background: #10b981; box-shadow: 0 0 8px #10b981;"></span>
SYSTEM ONLINE
</span>
<span class="hidden md:inline">GRID 2.0 :: UI-UX ARCHITECTURE PROPOSAL</span>
<span class="flex items-center gap-2">
AP-ID
<span class="w-1.5 h-1.5 rounded-full" style="background: #d04a2f; box-shadow: 0 0 8px #d04a2f;"></span>
</span>
</div>
</div>
<!-- ========== END WOW ANIMATION ========== -->
<div class="flex flex-wrap gap-3 mt-6">
<span class="pill pill-midnight">20+ Years Market-Proven</span>
<span class="pill pill-indian">Microsoft Certified</span>
<span class="pill pill-steel">Yokogawa · Microsoft · Dacia</span>
</div>
</div>
</div>
<!-- KEY METRICS -->
<div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
<div class="stat-card" data-popup data-title="Yokogawa Tenure" data-content="Lead UI/UX Designer for nearly 3 years. Created cohesive visual aesthetics, complex GUI elements, and data dashboards across 12 European countries for CENTUM VP distributed control systems.">
<div class="stat-value">2y 9m</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">YOKOGAWA EU</div>
</div>
<div class="stat-card" data-popup data-title="Template Systems at Scale" data-content="200+ graphic templates designed for Yokogawa's 12-country European rollout. Ensured brand consistency, regulatory compliance, and cross-market adaptability.">
<div class="stat-value">200+</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">TEMPLATES</div>
</div>
<div class="stat-card" data-popup data-title="iGaming Platforms" data-content="100+ online casino and 100+ online bingo websites delivered in live market conditions. Mastered real-time data grids, multi-layer forms, and sub-100ms latency constraints — directly transferable to energy trading order books.">
<div class="stat-value">200+</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">LIVE PLATFORMS</div>
</div>
<div class="stat-card" data-popup data-title="WCAG Compliance" data-content="90%+ WCAG 2.1 AA/AAA compliance achieved at Microsoft PCoE via Shipley Associates. Passed rigorous Microsoft accessibility audits on multimillion-dollar global deal presentations.">
<div class="stat-value">90%+</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">WCAG PASS</div>
</div>
<div class="stat-card" data-popup data-title="Microsoft Certifications" data-content="8 Microsoft certifications earned February 2025: Accessibility Evaluation & Testing, Accessibility Fundamentals, Web Accessibility Principles, Create Accessible AI Experiences, Fundamental AI Concepts, Build Accessible SharePoint Sites, Create Accessible Content, Introduction to Accessibility.">
<div class="stat-value">8</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">MSFT CERTS</div>
</div>
</div>
<!-- 7 PILLARS -->
<div class="section-divider"><span class="font-display font-bold text-sm tracking-widest uppercase" style="color: var(--color-midnight-blue);">The 7 Strategic Pillars</span></div>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-12">
<div class="info-card" data-popup data-title="1. Cognitive & Psychological Alignment" data-content="MBTI: INTJ-A (The Architect). 95% Intuitive (systems thinking), 81% Thinking (objective logic), 67% Judging (structured execution), 61% Assertive (confident navigation of high-stakes corporate environments). Dominant Ni function identifies systemic flaws in legacy applications; auxiliary Te translates strategic vision into disciplined workflows.">
<div class="flex items-start justify-between mb-3">
<div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(0,32,96,0.1);">
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-midnight-blue);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
</div>
<span class="click-hint text-[10px] font-bold uppercase tracking-wider" style="color: var(--color-indian-red);">Click →</span>
</div>
<div class="pill pill-midnight mb-2">01 · PSYCHOLOGY</div>
<h3 class="font-display font-bold text-lg mb-2" style="color: var(--color-dark-gray);">INTJ-A Architect in Enterprise R&D</h3>
<p class="text-sm text-gray-600 leading-relaxed">Holistic information architecture. Structured flexibility for chaotic legacy workflows. Assertive SME pushback.</p>
</div>
<div class="info-card" data-popup data-title="2. Domain Expertise Transferability" data-content="Industrial automation (Yokogawa CENTUM VP HMI design, 12-country EU rollout, SCADA dashboards). iGaming ecosystem (100+ casino/bingo sites, real-time grids, multi-layer forms, sub-100ms latency). Microsoft/Shipley (multimillion-dollar B2B data visualization, WCAG-compliant infographics). Romexpo & Dacia (enterprise exhibitor portals, RBAC dashboards, 1,200+ concurrent user scaling, end-to-end dealer website & app).">
<div class="flex items-start justify-between mb-3">
<div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(208,74,47,0.1);">
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-indian-red);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
</div>
<span class="click-hint text-[10px] font-bold uppercase tracking-wider" style="color: var(--color-indian-red);">Click →</span>
</div>
<div class="pill pill-indian mb-2">02 · DOMAIN</div>
<h3 class="font-display font-bold text-lg mb-2" style="color: var(--color-dark-gray);">Industrial Automation & High-Stakes Data</h3>
<p class="text-sm text-gray-600 leading-relaxed">Yokogawa HMI · iGaming real-time grids · Microsoft B2B data viz · Dacia/Romexpo end-to-end funnels.</p>
</div>
<div class="info-card" data-popup data-title="3. Technical Stack Synergy" data-content="Figma mastery: component libraries, design tokens, Dev Mode handoff, Confluence/TFS documentation. ag-Grid Enterprise fluency: pivot tables, sparklines, server-side row models, delta-row updates, virtual scrolling, row buffering, sub-second refresh cycles. Angular ecosystem familiarity: conceptual mapping via React/Next.js/Node.js background, Ivy rendering, reactive forms, Angular Material theming, NgRx/RxJS state management, lazy-loaded module bundling. HTML/CSS constraint awareness for feasible, performant UIs.">
<div class="flex items-start justify-between mb-3">
<div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(32,43,58,0.1);">
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-dark-gray);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
</div>
<span class="click-hint text-[10px] font-bold uppercase tracking-wider" style="color: var(--color-indian-red);">Click →</span>
</div>
<div class="pill pill-steel mb-2">03 · STACK</div>
<h3 class="font-display font-bold text-lg mb-2" style="color: var(--color-dark-gray);">Immediate Productivity & Dev Alignment</h3>
<p class="text-sm text-gray-600 leading-relaxed">Figma · ag-Grid Enterprise · Angular ecosystem · HTML/CSS constraint literacy.</p>
</div>
<div class="info-card" data-popup data-title="4. Proactive Gap Resolution" data-content="Microsoft Certified AI Fundamentals (AI-900) for LLM & GenAI rapid prototyping. Generative AI workflows: Adobe Firefly, Midjourney, Claude, Python scripting — cutting prototyping time by 50%. Microsoft Certified Accessibility (Feb 2025) for WCAG 2.1 AA/AAA implementation & audit readiness. Risk mitigation: preventing costly enterprise compliance retrofits in regulated energy markets (EN 301 549 alignment, seizure-safe animation, automated auditing pipelines).">
<div class="flex items-start justify-between mb-3">
<div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(0,32,96,0.1);">
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-midnight-blue);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
</div>
<span class="click-hint text-[10px] font-bold uppercase tracking-wider" style="color: var(--color-indian-red);">Click →</span>
</div>
<div class="pill pill-midnight mb-2">04 · GAPS</div>
<h3 class="font-display font-bold text-lg mb-2" style="color: var(--color-dark-gray);">AI Augmentation & Regulatory Compliance</h3>
<p class="text-sm text-gray-600 leading-relaxed">AI-900 · Adobe Firefly · Claude · WCAG 2.1 AA/AAA · EN 301 549.</p>
</div>
<div class="info-card" data-popup data-title="5. Third-Party Validation" data-content="Bert Konings (VP Product Management, HMS Networks): 'he went from being all over the map to a smooth process where everyone knew what they could expect.' Kevin Donlan (VP Strategic Alliances, Shipley/Microsoft): 'world class graphic designer... ability to work directly with SMEs sets him apart.' Gaetano Micera (Director Life Science, Yokogawa): 'reliable and sharp, on time, exceeding expectations.' Maria Claus & Paul Holthuis (Yokogawa): 'transforms abstract ideas into concrete designs.' Plus EU Directors: Dominiek, Cynthia, Mailyn, Emma.">
<div class="flex items-start justify-between mb-3">
<div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(208,74,47,0.1);">
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-indian-red);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
</div>
<span class="click-hint text-[10px] font-bold uppercase tracking-wider" style="color: var(--color-indian-red);">Click →</span>
</div>
<div class="pill pill-indian mb-2">05 · PROOF</div>
<h3 class="font-display font-bold text-lg mb-2" style="color: var(--color-dark-gray);">Corporate Risk Mitigation via Testimonials</h3>
<p class="text-sm text-gray-600 leading-relaxed">VP & Director endorsements: structuring chaos, SME translation, reliability, global stakeholder management.</p>
</div>
<div class="info-card" data-popup data-title="6. Operational Execution" data-content="The Pressure Test: 200+ profit-generating logos and 200+ iGaming platforms delivered in live market conditions. Template Systems at Scale: 200+ graphic templates for Yokogawa's 12 EU markets. Educational Leadership: STEP IT Academy coaching — translating complex concepts to junior designers. The B2B Mindset: 15+ years of AP-ID.ro autonomy, client retention, and commercial viability.">
<div class="flex items-start justify-between mb-3">
<div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(32,43,58,0.1);">
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-dark-gray);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
</div>
<span class="click-hint text-[10px] font-bold uppercase tracking-wider" style="color: var(--color-indian-red);">Click →</span>
</div>
<div class="pill pill-steel mb-2">06 · EXECUTION</div>
<h3 class="font-display font-bold text-lg mb-2" style="color: var(--color-dark-gray);">High-Volume Delivery & Architectural Thinking</h3>
<p class="text-sm text-gray-600 leading-relaxed">200+ logos · 200+ live platforms · 12-country templates · STEP IT Academy coaching.</p>
</div>
<div class="info-card md:col-span-2 lg:col-span-3" data-popup data-title="7. Strategic B2B Partnership Framing" data-content="The 'Force Multiplier' Effect: AI & Accessibility certifications accelerate Client's R&D cycle while reducing compliance risk. Zero Ramp-Up Time: hitting the ground running with ag-Grid, Figma, and enterprise data patterns already mastered. The Perfect Balance: merging corporate industrial rigor (Yokogawa) with human-centric creativity — not a robot, not a full-on artist. Contractual Alignment: Romanian citizen, B2B entity (AP-ID), ready for 6-month extension model with transition path to SRL.">
<div class="flex items-start justify-between mb-3">
<div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: linear-gradient(135deg, var(--color-midnight-blue), var(--color-indian-red));">
<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
</div>
<span class="click-hint text-[10px] font-bold uppercase tracking-wider" style="color: var(--color-indian-red);">Click →</span>
</div>
<div class="pill pill-indian mb-2">07 · PARTNERSHIP</div>
<h3 class="font-display font-bold text-lg mb-2" style="color: var(--color-dark-gray);">B2B ROI & Force Multiplication</h3>
<p class="text-sm text-gray-600 leading-relaxed">AI + Accessibility certifications as R&D accelerators · Zero ramp-up with ag-Grid/Figma · Industrial rigor + human-centric creativity · Romanian B2B entity ready for 6-month extension.</p>
</div>
</div>
<!-- TESTIMONIALS PREVIEW -->
<div class="section-divider"><span class="font-display font-bold text-sm tracking-widest uppercase" style="color: var(--color-midnight-blue);">Social Proof Armor</span></div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-12">
<div class="info-card" data-popup data-title="Bert Konings — VP Product Management, HMS Networks" data-content="'Guiding teams in need through a creative process and building structure to what is needed... is what Alex does, and he does it well... he went from being all over the map to a smooth process where everyone knew what they could expect.' — Direct Match for Client's need to analyze and structure chaotic existing workflows. Proves ability to bring order and process to complexity.">
<div class="quote-block mb-3">"Guiding teams in need through a creative process and building structure to what is needed... is what Alex does, and he does it well."</div>
<div class="flex items-center gap-3">
<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold" style="background: var(--color-midnight-blue);">BK</div>
<div>
<div class="font-display font-bold text-sm">Bert Konings</div>
<div class="text-xs text-gray-500">VP Product Management · HMS Networks</div>
</div>
</div>
</div>
<div class="info-card" data-popup data-title="Kevin Donlan — VP Strategic Alliances, Shipley/Microsoft" data-content="'Alexandru is a world class graphic designer... his ability to work directly with subject matter experts to scope, tailor and customize presentations sets him apart.' — Collaboration proof: validates exceptional cross-functional skills crucial for bridging developers and domain experts in the energy trading domain.">
<div class="quote-block mb-3">"World class graphic designer... his ability to work directly with subject matter experts to scope, tailor and customize presentations sets him apart."</div>
<div class="flex items-center gap-3">
<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold" style="background: var(--color-indian-red);">KD</div>
<div>
<div class="font-display font-bold text-sm">Kevin Donlan</div>
<div class="text-xs text-gray-500">VP Strategic Alliances · Shipley/Microsoft</div>
</div>
</div>
</div>
<div class="info-card" data-popup data-title="Gaetano Micera — Director Life Science, Yokogawa" data-content="'He was reliable and sharp on his task assignment being on time and exceeding expectations on final product.' — Reliability & ROI assurance: confirms professionalism, timeliness, and commitment to delivering high-quality, valuable work under enterprise deadlines.">
<div class="quote-block mb-3">"Reliable and sharp on his task assignment being on time and exceeding expectations on final product."</div>
<div class="flex items-center gap-3">
<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold" style="background: var(--color-midnight-blue);">GM</div>
<div>
<div class="font-display font-bold text-sm">Gaetano Micera</div>
<div class="text-xs text-gray-500">Director Life Science · Yokogawa</div>
</div>
</div>
</div>
<div class="info-card" data-popup data-title="Maria Claus — Marketing Event Coordinator, Yokogawa" data-content="'He is capable of transforming abstract ideas into concrete designs, from concept to execution, implementation and simplification. There is nothing he can't do.' — Execution & Problem-Solving: demonstrates end-to-end project ownership and ability to simplify complex concepts, core requirement for Client's Senior UI/UX role.">
<div class="quote-block mb-3">"Capable of transforming abstract ideas into concrete designs, from concept to execution, implementation and simplification."</div>
<div class="flex items-center gap-3">
<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold" style="background: var(--color-indian-red);">MC</div>
<div>
<div class="font-display font-bold text-sm">Maria Claus</div>
<div class="text-xs text-gray-500">Marketing Event Coordinator · Yokogawa</div>
</div>
</div>
</div>
</div>
<!-- ============================================= -->
<!-- I. EXECUTIVE SUMMARY & STRATEGIC POSITIONING -->
<!-- ============================================= -->
<div class="section-divider"><span class="font-display font-bold text-sm tracking-widest uppercase" style="color: var(--color-midnight-blue);">I. Executive Summary & Strategic Positioning</span></div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
<div class="info-card" data-popup data-title="Core Value Proposition" data-content="The INTJ-A Architect as a Strategic R&D Asset for Client. Alex is not merely a UI/UX designer but a strategic systems thinker capable of driving meaningful innovation within Client's R&D team working on mission-critical software for electricity market operations and energy trading.">
<div class="pill pill-midnight mb-2">1.1</div>
<h3 class="font-display font-bold text-base mb-1">Core Value Proposition</h3>
<p class="text-sm text-gray-600">INTJ-A Architect as strategic R&D asset.</p>
</div>
<div class="info-card" data-popup data-title="Research Scope" data-content="Strategic capability matching, gap analysis, and competitive differentiation. Three-pillar approach: (1) Proven experience in high-stakes corporate/industrial environments, (2) Third-party validation via testimonials, (3) INTJ-A personality as cognitive advantage for complex problem-solving.">
<div class="pill pill-midnight mb-2">1.2</div>
<h3 class="font-display font-bold text-base mb-1">Research Scope & Methodology</h3>
<p class="text-sm text-gray-600">Capability matching · Gap analysis · Differentiation.</p>
</div>
<div class="info-card" data-popup data-title="Target Alignment" data-content="Client's Senior UI/UX Role Requirements vs. Alex Popescu's 20+ Year Market-Proven Track Record. JD emphasizes data-heavy interfaces, multi-layer forms, dashboards, grid-based screens — all directly addressed by Yokogawa HMI work, Microsoft data visualization, and 200+ iGaming platforms.">
<div class="pill pill-midnight mb-2">1.3</div>
<h3 class="font-display font-bold text-base mb-1">Target Alignment</h3>
<p class="text-sm text-gray-600">JD requirements ↔ 20+ year track record.</p>
</div>
<div class="info-card" data-popup data-title="B2B UX Architecture Proposal" data-content="Reframing the engagement from transactional hire to strategic partnership. Alex positions himself as a B2B UX Architecture Partner, emphasizing mutual growth and de-risked collaboration — directly addressing Robert's priorities of hands-on value with minimal ramp-up.">
<div class="pill pill-midnight mb-2">1.4</div>
<h3 class="font-display font-bold text-base mb-1">B2B UX Architecture Proposal</h3>
<p class="text-sm text-gray-600">Transactional hire → strategic partnership.</p>
</div>
</div>
<!-- ============================================= -->
<!-- UI INTERFACE SIMULATION SHOWCASE (FIXED)       -->
<!-- ============================================= -->
<div class="section-divider"><span class="font-display font-bold text-sm tracking-widest uppercase" style="color: var(--color-indian-red);">⚡ UI Interface Simulation — Energy Trading Console</span></div>
<div class="ui-sim-wrap mb-12">
<div class="flex flex-wrap items-start justify-between gap-4 mb-4">
<div>
<div class="pill pill-indian mb-2">FICTIVE PRODUCT · Client GRID OPS</div>
<h3 class="font-display text-2xl md:text-3xl font-extrabold" style="color: var(--color-midnight-blue);">
Real-Time Energy Trading Console
</h3>
<p class="text-sm text-gray-600 mt-2 max-w-2xl leading-relaxed">
A simulation of the kind of mission-critical interface I would architect for Client — showcasing <strong>ag-Grid best practices</strong>, <strong>WCAG 2.1 AA compliance</strong>, <strong>Angular reactive forms</strong>, and <strong>low-latency data visualization</strong> that engineering teams actually want to build.
</p>
</div>
<div class="flex flex-col items-end gap-1">
<span class="text-[10px] font-mono text-gray-500 tracking-widest">PROTOTYPE v0.4</span>
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold" style="background: rgba(16,185,129,0.12); color: #10b981;">
<span class="w-1.5 h-1.5 rounded-full" style="background:#10b981; box-shadow:0 0 6px #10b981;"></span>
LIVE SIMULATION
</span>
</div>
</div>
<!-- Best-practice badges floating (FIXED positions) -->
<div class="relative">
<!-- WCAG badge top-right (unchanged) -->
<div class="bp-badge" style="top: 12px; right: 12px;">WCAG AA · 7.1:1 contrast</div>
<!-- ARIA-LIVE badge moved LOWER to avoid overlap (was bottom: 95px, now bottom: 28px) -->
<div class="bp-badge" style="bottom: 28px; right: 12px;">ARIA-live polite</div>
<div class="ui-sim-chrome">
<!-- Top bar -->
<div class="ui-sim-topbar">
<div class="flex items-center gap-3">
<div class="dots">
<span class="dot dot-r"></span>
<span class="dot dot-y"></span>
<span class="dot dot-g"></span>
</div>
<span class="font-bold tracking-wider" style="letter-spacing: 0.15em;">⚡ Client GRID OPS</span>
<span class="hidden md:inline text-white/60">/ Energy Trading / Day-Ahead Market</span>
</div>
<div class="flex items-center gap-3 text-white/80">
<span class="hidden md:inline">Trader: <span class="font-bold text-white">A. POPESCU</span></span>
<span class="inline-flex items-center gap-1.5">
<span class="w-1.5 h-1.5 rounded-full" style="background:#10b981; animation: liveDot 1.2s ease-in-out infinite;"></span>
CONNECTED
</span>
</div>
</div>
<div class="ui-sim-body">
<!-- Sidebar -->
<aside class="ui-sim-sidebar">
<div class="text-[10px] uppercase tracking-widest text-white/40 px-2 mb-2">Trading</div>
<div class="ui-sim-nav-item active">
<span>⚡</span> <span>Day-Ahead</span>
</div>
<div class="ui-sim-nav-item">
<span>📊</span> <span>Intraday</span>
</div>
<div class="ui-sim-nav-item">
<span>🔁</span> <span>Balancing</span>
</div>
<div class="ui-sim-nav-item">
<span>📦</span> <span>Capacity</span>
</div>
<div class="text-[10px] uppercase tracking-widest text-white/40 px-2 mt-4 mb-2">Portfolio</div>
<div class="ui-sim-nav-item">
<span>📈</span> <span>Positions</span>
</div>
<div class="ui-sim-nav-item">
<span>🧾</span> <span>Settlement</span>
</div>
<div class="text-[10px] uppercase tracking-widest text-white/40 px-2 mt-4 mb-2">System</div>
<div class="ui-sim-nav-item">
<span>⚙️</span> <span>Settings</span>
</div>
<div class="ui-sim-nav-item">
<span>♿</span> <span>Accessibility</span>
</div>
</aside>
<!-- Main -->
<div class="ui-sim-main">
<!-- Breadcrumb + title + action row (FIXED: ag-Grid SSRM badge moved here as blue inline badge) -->
<div class="flex flex-wrap items-center justify-between gap-2 mb-3">
<div>
<div class="text-[10px] text-gray-500 tracking-wider">TRADING / DAY-AHEAD / ROM-OPCOM</div>
<h4 class="font-display text-lg font-bold" style="color: var(--color-midnight-blue);">Day-Ahead Market — Hourly Contracts</h4>
</div>
<div class="flex items-center gap-2">
<!-- FIX: ag-Grid SSRM badge — now inline, blue background, white text, next to buttons -->
<span class="inline-flex items-center gap-1 px-2 py-1 rounded text-[10px] font-bold text-white" style="background: var(--color-midnight-blue); letter-spacing: 0.05em;">
<span style="color: #4d9fff;">⚡</span> ag-Grid SSRM
</span>
<button class="px-3 py-1.5 text-xs font-bold text-white rounded" style="background: var(--color-indian-red);" aria-label="Place new order">+ NEW ORDER</button>
<button class="px-3 py-1.5 text-xs font-bold rounded border" style="color: var(--color-midnight-blue); border-color: var(--color-midnight-blue);" aria-label="Export data">EXPORT</button>
</div>
</div>
<!-- Metrics -->
<div class="ui-sim-metrics">
<div class="ui-sim-metric" data-popup data-title="KPI: Clearing Price" data-content="Weighted average clearing price across all 24 hourly contracts. Tabular-nums font for stable alignment during live updates (WCAG 1.3.1).">
<div class="ui-sim-metric-label">Avg Clearing Price</div>
<div class="ui-sim-metric-value">€87.42<span class="text-xs text-gray-500 font-normal">/MWh</span></div>
<div class="ui-sim-metric-delta up">▲ +2.3% vs DA-1</div>
<svg class="ui-sim-spark" viewBox="0 0 100 22" preserveAspectRatio="none">
<polyline fill="none" stroke="#002060" stroke-width="1.5" points="0,18 10,14 20,16 30,10 40,12 50,8 60,10 70,6 80,9 90,4 100,7"/>
</svg>
</div>
<div class="ui-sim-metric" data-popup data-title="KPI: Volume" data-content="Total traded volume in MWh for the current trading session. Uses delta-row updates (ag-Grid) to avoid full-table rerender.">
<div class="ui-sim-metric-label">Traded Volume</div>
<div class="ui-sim-metric-value">4,812<span class="text-xs text-gray-500 font-normal"> MWh</span></div>
<div class="ui-sim-metric-delta up">▲ +18.6%</div>
<svg class="ui-sim-spark" viewBox="0 0 100 22" preserveAspectRatio="none">
<polyline fill="none" stroke="#10b981" stroke-width="1.5" points="0,18 10,16 20,12 30,14 40,10 50,8 60,6 70,10 80,4 90,8 100,2"/>
</svg>
</div>
<div class="ui-sim-metric" data-popup data-title="KPI: Active Bids" data-content="Number of bids currently in the order book awaiting clearing. Live updates via ARIA-live 'polite' region — screen readers announce changes without interrupting users (WCAG 4.1.3).">
<div class="ui-sim-metric-label">Active Bids</div>
<div class="ui-sim-metric-value">1,247</div>
<div class="ui-sim-metric-delta down">▼ −42 last 5min</div>
<svg class="ui-sim-spark" viewBox="0 0 100 22" preserveAspectRatio="none">
<polyline fill="none" stroke="#d04a2f" stroke-width="1.5" points="0,4 10,8 20,6 30,12 40,10 50,14 60,12 70,16 80,14 90,18 100,16"/>
</svg>
</div>
<div class="ui-sim-metric" data-popup data-title="KPI: Grid Frequency" data-content="Real-time grid frequency. Sub-100ms updates via WebSocket; visual tick indicators (green/red flash) respect prefers-reduced-motion and seizure-safe animation (WCAG 2.3.1).">
<div class="ui-sim-metric-label">Grid Frequency</div>
<div class="ui-sim-metric-value">50.02<span class="text-xs text-gray-500 font-normal"> Hz</span></div>
<div class="ui-sim-metric-delta up">● STABLE</div>
<svg class="ui-sim-spark" viewBox="0 0 100 22" preserveAspectRatio="none">
<polyline fill="none" stroke="#002060" stroke-width="1.5" points="0,11 10,10 20,12 30,11 40,11 50,10 60,12 70,11 80,11 90,10 100,11"/>
</svg>
</div>
</div>
<!-- Grid -->
<div class="ui-sim-grid" role="grid" aria-label="Day-ahead market hourly contracts">
<div class="ui-sim-grid-head">
<div class="title">📋 HOURLY CONTRACTS · ag-Grid Enterprise</div>
<div class="flex items-center gap-2">
<span class="badge"><span class="pulse-dot"></span>LIVE · SSRM</span>
<span class="text-white/60 text-[10px]">24 rows · 8 cols</span>
</div>
</div>
<div style="overflow-x:auto;">
<table role="grid">
<thead>
<tr>
<th scope="col" style="width:80px;">Hour</th>
<th scope="col">Price (€/MWh)</th>
<th scope="col">Volume (MWh)</th>
<th scope="col">Bid/Ask</th>
<th scope="col">Delta</th>
<th scope="col">Status</th>
<th scope="col">Congestion</th>
<th scope="col" style="width:90px;">Action</th>
</tr>
</thead>
<tbody>
<tr class="row-tick-up" tabindex="0">
<td><strong>H-01</strong> <span class="text-[10px] text-gray-500">00:00</span></td>
<td class="price price-up">€72.18 <span class="chevron">▲</span></td>
<td>412</td>
<td>1.24</td>
<td class="price-up">+1.8%</td>
<td><span class="status-pill status-cleared">● Cleared</span></td>
<td>LOW</td>
<td><button class="text-[10px] font-bold px-2 py-1 rounded" style="background: rgba(0,32,96,0.08); color: var(--color-midnight-blue);">VIEW</button></td>
</tr>
<tr class="row-tick-down" tabindex="0">
<td><strong>H-02</strong> <span class="text-[10px] text-gray-500">01:00</span></td>
<td class="price price-down">€68.45 <span class="chevron">▼</span></td>
<td>388</td>
<td>0.96</td>
<td class="price-down">−0.6%</td>
<td><span class="status-pill status-cleared">● Cleared</span></td>
<td>LOW</td>
<td><button class="text-[10px] font-bold px-2 py-1 rounded" style="background: rgba(0,32,96,0.08); color: var(--color-midnight-blue);">VIEW</button></td>
</tr>
<tr tabindex="0">
<td><strong>H-03</strong> <span class="text-[10px] text-gray-500">02:00</span></td>
<td class="price">€64.92</td>
<td>356</td>
<td>0.88</td>
<td class="text-gray-500">0.0%</td>
<td><span class="status-pill status-cleared">● Cleared</span></td>
<td>LOW</td>
<td><button class="text-[10px] font-bold px-2 py-1 rounded" style="background: rgba(0,32,96,0.08); color: var(--color-midnight-blue);">VIEW</button></td>
</tr>
<tr class="row-tick-up" tabindex="0">
<td><strong>H-08</strong> <span class="text-[10px] text-gray-500">07:00</span></td>
<td class="price price-up">€94.73 <span class="chevron">▲</span></td>
<td>612</td>
<td>1.42</td>
<td class="price-up">+4.2%</td>
<td><span class="status-pill status-active">● Active</span></td>
<td><span class="font-bold" style="color: var(--color-indian-red);">HIGH</span></td>
<td><button class="text-[10px] font-bold px-2 py-1 rounded text-white" style="background: var(--color-indian-red);">TRADE</button></td>
</tr>
<tr tabindex="0">
<td><strong>H-12</strong> <span class="text-[10px] text-gray-500">11:00</span></td>
<td class="price">€102.31</td>
<td>724</td>
<td>1.58</td>
<td class="price-up">+2.1%</td>
<td><span class="status-pill status-pending">● Pending</span></td>
<td>MED</td>
<td><button class="text-[10px] font-bold px-2 py-1 rounded text-white" style="background: var(--color-indian-red);">TRADE</button></td>
</tr>
<tr class="row-tick-up" tabindex="0">
<td><strong>H-18</strong> <span class="text-[10px] text-gray-500">17:00</span></td>
<td class="price price-up">€118.56 <span class="chevron">▲</span></td>
<td>847</td>
<td>1.87</td>
<td class="price-up">+6.8%</td>
<td><span class="status-pill status-active">● Active</span></td>
<td><span class="font-bold" style="color: var(--color-indian-red);">HIGH</span></td>
<td><button class="text-[10px] font-bold px-2 py-1 rounded text-white" style="background: var(--color-indian-red);">TRADE</button></td>
</tr>
<tr class="row-tick-down" tabindex="0">
<td><strong>H-22</strong> <span class="text-[10px] text-gray-500">21:00</span></td>
<td class="price price-down">€82.14 <span class="chevron">▼</span></td>
<td>498</td>
<td>1.12</td>
<td class="price-down">−3.4%</td>
<td><span class="status-pill status-cleared">● Cleared</span></td>
<td>MED</td>
<td><button class="text-[10px] font-bold px-2 py-1 rounded" style="background: rgba(0,32,96,0.08); color: var(--color-midnight-blue);">VIEW</button></td>
</tr>
</tbody>
</table>
</div>
<div class="ui-sim-footer">
<div class="flex items-center gap-3 flex-wrap">
<span class="kb-hint"><span class="kbd">↑</span><span class="kbd">↓</span> Navigate rows</span>
<span class="kb-hint"><span class="kbd">Enter</span> Open detail</span>
<span class="kb-hint"><span class="kbd">/</span> Quick search</span>
<span class="kb-hint"><span class="kbd">Esc</span> Clear selection</span>
</div>
<div class="flex items-center gap-2">
<span>Rows <strong>1-7</strong> of <strong>24</strong></span>
<button class="kbd">‹</button>
<button class="kbd">›</button>
</div>
</div>
</div>
<!-- Legend -->
<div class="ui-sim-legend" role="note" aria-label="Best-practice legend">
<div class="ui-sim-legend-item">
<div class="swatch" style="background:#10b981;"></div>
<span><strong>Price up</strong> — color + chevron (not color alone, WCAG 1.4.1)</span>
</div>
<div class="ui-sim-legend-item">
<div class="swatch" style="background:var(--color-indian-red);"></div>
<span><strong>Price down / high congestion</strong></span>
</div>
<div class="ui-sim-legend-item">
<div class="swatch" style="background:var(--color-midnight-blue);"></div>
<span><strong>Focus ring</strong> — visible on Tab navigation</span>
</div>
<div class="ui-sim-legend-item">
<span>⚡</span>
<span><strong>Live ticks</strong> respect <code>prefers-reduced-motion</code></span>
</div>
</div>
</div>
</div>
</div>
<!-- Engineering concerns addressed -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mt-6">
<div class="info-card" data-popup data-title="ag-Grid Performance" data-content="Server-Side Row Model (SSRM) with delta-row updates. Only changed cells rerender — critical for sub-100ms latency in live energy feeds. Virtual scrolling enabled for datasets exceeding 10K rows. Custom cell renderers kept lightweight to avoid DOM virtualization collapse.">
<div class="text-xl mb-1">⚙️</div>
<div class="font-display font-bold text-sm mb-1" style="color: var(--color-midnight-blue);">ag-Grid Performance</div>
<p class="text-[11px] text-gray-600">SSRM · Delta updates · Virtual scroll · Lightweight cell renderers</p>
</div>
<div class="info-card" data-popup data-title="Angular Reactive Forms" data-content="FormGroups with typed FormControls, async validators for market-availability checks, and RxJS debounce on price inputs to prevent API spam. State managed via NgRx selectors — no prop drilling, predictable updates across sibling components.">
<div class="text-xl mb-1">🧩</div>
<div class="font-display font-bold text-sm mb-1" style="color: var(--color-midnight-blue);">Angular Reactive Forms</div>
<p class="text-[11px] text-gray-600">Typed FormControls · Async validators · NgRx selectors</p>
</div>
<div class="info-card" data-popup data-title="WCAG 2.1 AA Compliance" data-content="Keyboard-navigable grid (Tab + Arrow keys), visible focus indicators, ARIA-live regions for live data updates, 7:1 contrast ratios on all text, status conveyed via color + icon + text (WCAG 1.4.1), seizure-safe animations (WCAG 2.3.1), and respects prefers-reduced-motion.">
<div class="text-xl mb-1">♿</div>
<div class="font-display font-bold text-sm mb-1" style="color: var(--color-midnight-blue);">WCAG 2.1 AA</div>
<p class="text-[11px] text-gray-600">Keyboard nav · ARIA-live · 7:1 contrast · Seizure-safe</p>
</div>
<div class="info-card" data-popup data-title="Cognitive Load Management" data-content="Progressive disclosure: default view shows 6 critical columns, 2 additional columns revealed on demand. Color + chevron + text for status (never color alone). Sparklines embedded in KPI cards for at-a-glance trend recognition without switching contexts.">
<div class="text-xl mb-1">🧠</div>
<div class="font-display font-bold text-sm mb-1" style="color: var(--color-midnight-blue);">Cognitive Load</div>
<p class="text-[11px] text-gray-600">Progressive disclosure · Multi-channel status · Inline sparklines</p>
</div>
</div>
<!-- Engineer-friendly summary -->
<div class="mt-6 p-5 rounded-lg border-l-4" style="background: rgba(0,32,96,0.04); border-color: var(--color-midnight-blue);">
<div class="flex items-start gap-3">
<div class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" style="background: var(--color-midnight-blue);">
<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
</div>
<div>
<h4 class="font-display font-bold text-base mb-1" style="color: var(--color-midnight-blue);">Why engineers will want to build this</h4>
<p class="text-sm text-gray-700 leading-relaxed">
This isn't a "pretty mockup that's impossible to ship." Every element maps to a real Angular/ag-Grid primitive: typed reactive forms, SSRM with delta updates, NgRx selectors, and a Figma design-token file that exports directly to CSS variables. I design <em>with</em> the framework, not <em>despite</em> it — which is exactly what your VP of Engineering needs to hear.
</p>
</div>
</div>
</div>
</div>
<!-- ============================================= -->
<!-- END UI INTERFACE SIMULATION                   -->
<!-- ============================================= -->
</section>
<!-- ============================================= -->
<!-- TAB 2: Client UI - STRATEGIC CAPABILITY -->
<!-- ============================================= -->
<section id="Clientui" class="tab-content">
<div class="section-label mb-4">02 / STRATEGIC UI-UX ALIGNMENT</div>
<h1 class="font-display text-3xl md:text-5xl font-extrabold mb-4" style="color: var(--color-midnight-blue);">
Strategic UI-UX Capability Alignment<br>& Interview Intelligence
</h1>
<p class="text-gray-600 text-lg mb-8 max-w-3xl">
Mapping the candidate profile to Client's Senior UI/UX position. 8 research pillars covering psychology, portfolio, stack, gaps, validation, positioning, and reference documentation.
</p>
<div class="sub-nav">
<a href="#s1">I. Executive</a>
<a href="#s2">II. INTJ-A</a>
<a href="#s3">III. Portfolio</a>
<a href="#s4">IV. Stack</a>
<a href="#s5">V. Gaps</a>
<a href="#s6">VI. Validation</a>
<a href="#s7">VII. Positioning</a>
<a href="#s8">VIII. References</a>
</div>
<div id="s1" class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">I. Executive Summary & Strategic Positioning</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Core Value Proposition" data-content="The INTJ-A Architect as a Strategic R&D Asset for Client. Alex is not merely a UI/UX designer but a strategic systems thinker capable of driving meaningful innovation within Client's R&D team working on mission-critical software for electricity market operations and energy trading.">
<div class="pill pill-midnight mb-2">1.1</div>
<h3 class="font-display font-bold text-base mb-1">Core Value Proposition</h3>
<p class="text-sm text-gray-600">INTJ-A Architect as strategic R&D asset.</p>
</div>
<div class="info-card" data-popup data-title="Research Scope" data-content="Strategic capability matching, gap analysis, and competitive differentiation. Three-pillar approach: (1) Proven experience in high-stakes corporate/industrial environments, (2) Third-party validation via testimonials, (3) INTJ-A personality as cognitive advantage for complex problem-solving.">
<div class="pill pill-midnight mb-2">1.2</div>
<h3 class="font-display font-bold text-base mb-1">Research Scope & Methodology</h3>
<p class="text-sm text-gray-600">Capability matching · Gap analysis · Differentiation.</p>
</div>
<div class="info-card" data-popup data-title="Target Alignment" data-content="Client's Senior UI/UX Role Requirements vs. Alex Popescu's 20+ Year Market-Proven Track Record. JD emphasizes data-heavy interfaces, multi-layer forms, dashboards, grid-based screens — all directly addressed by Yokogawa HMI work, Microsoft data visualization, and 200+ iGaming platforms.">
<div class="pill pill-midnight mb-2">1.3</div>
<h3 class="font-display font-bold text-base mb-1">Target Alignment</h3>
<p class="text-sm text-gray-600">JD requirements ↔ 20+ year track record.</p>
</div>
<div class="info-card" data-popup data-title="B2B UX Architecture Proposal" data-content="Reframing the engagement from transactional hire to strategic partnership. Alex positions himself as a B2B UX Architecture Partner, emphasizing mutual growth and de-risked collaboration — directly addressing Robert's priorities of hands-on value with minimal ramp-up.">
<div class="pill pill-midnight mb-2">1.4</div>
<h3 class="font-display font-bold text-base mb-1">B2B UX Architecture Proposal</h3>
<p class="text-sm text-gray-600">Transactional hire → strategic partnership.</p>
</div>
</div>
</div>
<div id="s2" class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">II. Psychological & Cognitive Architecture</h2>
<div class="bg-white rounded-xl p-6 border border-gray-200 mb-6">
<h3 class="font-display font-bold text-lg mb-4">MBTI Framework Decoded</h3>
<div class="space-y-4">
<div>
<div class="flex justify-between text-sm mb-1"><span class="font-semibold">Introverted (I)</span><span class="font-mono text-xs">Deep focus</span></div>
<div class="progress-track"><div class="progress-fill" style="width: 53%;"></div></div>
</div>
<div>
<div class="flex justify-between text-sm mb-1"><span class="font-semibold">Intuitive (N) — Systems Thinking</span><span class="font-mono text-xs">95%</span></div>
<div class="progress-track"><div class="progress-fill" style="width: 95%;"></div></div>
</div>
<div>
<div class="flex justify-between text-sm mb-1"><span class="font-semibold">Thinking (T) — Objective Logic</span><span class="font-mono text-xs">81%</span></div>
<div class="progress-track"><div class="progress-fill" style="width: 81%;"></div></div>
</div>
<div>
<div class="flex justify-between text-sm mb-1"><span class="font-semibold">Judging (J) — Structured Flexibility</span><span class="font-mono text-xs">67%</span></div>
<div class="progress-track"><div class="progress-fill" style="width: 67%;"></div></div>
</div>
<div>
<div class="flex justify-between text-sm mb-1"><span class="font-semibold">Assertive (-A) — Confident Navigation</span><span class="font-mono text-xs">61%</span></div>
<div class="progress-track"><div class="progress-fill" style="width: 61%;"></div></div>
</div>
</div>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Dominant Ni — Introverted Intuition" data-content="Systems thinking, pattern recognition, holistic information architecture. Identifies underlying patterns, long-term implications, and systemic connections. Analyzes legacy applications as logical ecosystems — pinpoints root causes of inefficiency, proposes holistic architectural improvements rather than cosmetic fixes.">
<div class="pill pill-indian mb-2">2.2.1 · Ni</div>
<h3 class="font-display font-bold text-base mb-1">Dominant Introverted Intuition</h3>
<p class="text-sm text-gray-600">Systems thinking · Pattern recognition · Holistic architecture.</p>
</div>
<div class="info-card" data-popup data-title="Auxiliary Te — Extraverted Thinking" data-content="Structured workflows, objective decision-making, execution rigor. Highly organized, efficient, results-oriented. Translates strategic visions into disciplined, productive workflows. Values clear metrics, logical arguments, and measurable outcomes.">
<div class="pill pill-indian mb-2">2.2.2 · Te</div>
<h3 class="font-display font-bold text-base mb-1">Auxiliary Extraverted Thinking</h3>
<p class="text-sm text-gray-600">Structured workflows · Objective decisions · Execution rigor.</p>
</div>
<div class="info-card" data-popup data-title="Tertiary Fi — Introverted Feeling" data-content="Human-centered values, ethical design, user empathy scaffolding. Strong internal values and authenticity. Contributes to human-centric design philosophy — ensuring logical, system-focused solutions align with genuine end-user needs and well-being.">
<div class="pill pill-indian mb-2">2.2.3 · Fi</div>
<h3 class="font-display font-bold text-base mb-1">Tertiary Introverted Feeling</h3>
<p class="text-sm text-gray-600">Human-centered values · Ethical design · User empathy.</p>
</div>
<div class="info-card" data-popup data-title="Inferior Se — Extraverted Sensing" data-content="Practical reality-grounding, detail orientation, market-tested delivery. Meticulous attention to detail and practical realities to ground abstract theories. 200+ logos in real market conditions proves healthy integration — visionary ideas always tested against real-world application.">
<div class="pill pill-indian mb-2">2.2.4 · Se</div>
<h3 class="font-display font-bold text-base mb-1">Inferior Extraverted Sensing</h3>
<p class="text-sm text-gray-600">Reality-grounding · Detail orientation · Market-tested delivery.</p>
</div>
</div>
</div>
<div id="s3" class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">III. Enterprise UI/UX Portfolio & Domain Expertise</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Yokogawa Electric Corp." data-content="Lead UI/UX Designer tenure (~3 years), 12-country European rollout. CENTUM VP / DCS HMI dashboard design. Real-time telemetry visualization. Cognitive load reduction, alarm prioritization, operator workflow optimization. Cross-functional collaboration with engineering, Tokyo HQ, and regional SMEs. Co-Innovation Tour execution, modular expo stand systems, mobile skid demo UI simulations.">
<div class="pill pill-midnight mb-2">3.1 · INDUSTRIAL</div>
<h3 class="font-display font-bold text-base mb-1">Yokogawa Electric Corp.</h3>
<p class="text-sm text-gray-600">CENTUM VP · DCS HMI · 12-country EU rollout · SCADA.</p>
</div>
<div class="info-card" data-popup data-title="Microsoft / Shipley Associates" data-content="Multimillion-dollar global deal support. Strategic infographic architecture. Translating abstract financial/technical data into actionable, WCAG-compliant visual narratives. Enterprise presentation systems, stakeholder customization, sales enablement integration. 20+ global clients: H&M, La Roche, Erste Group, UAE Ministry of Education, HMS Networks, SITA Africa.">
<div class="pill pill-midnight mb-2">3.2 · B2B</div>
<h3 class="font-display font-bold text-base mb-1">Microsoft / Shipley Associates</h3>
<p class="text-sm text-gray-600">Global deal support · WCAG-compliant data viz · 20+ clients.</p>
</div>
<div class="info-card" data-popup data-title="iGaming Ecosystem" data-content="100+ casino + 100+ bingo platforms delivered in live market conditions. Real-time data grids, live odds synchronization, sub-100ms latency constraint management. Complex multi-layer forms, financial transaction flows, KYC/AML integration, user retention mechanics. Domain transferability: functional parallels between iGaming volatility and energy trading order books.">
<div class="pill pill-indian mb-2">3.3 · iGAMING</div>
<h3 class="font-display font-bold text-base mb-1">iGaming Ecosystem</h3>
<p class="text-sm text-gray-600">200+ live platforms · Real-time grids · KYC/AML flows.</p>
</div>
<div class="info-card" data-popup data-title="Dacia, Romexpo, Nikon" data-content="Dacia Romania: official dealer website & app full-funnel architecture, cross-platform consistency. Romexpo: enterprise exhibitor portals, real-time booth analytics, RBAC dashboards, 1,200+ concurrent user scaling. Nikon Romania: large-scale rebranding, templatized design systems, market-proven visual governance. 200+ profit-generating logos across diverse industrial & retail sectors.">
<div class="pill pill-indian mb-2">3.4 · BRAND</div>
<h3 class="font-display font-bold text-base mb-1">Dacia · Romexpo · Nikon</h3>
<p class="text-sm text-gray-600">End-to-end digital ecosystems · RBAC dashboards · 200+ logos.</p>
</div>
</div>
</div>
<div id="s4" class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">IV. Technical Proficiency & Stack Alignment</h2>
<div class="overflow-x-auto rounded-xl border border-gray-200">
<table class="data-table">
<thead>
<tr>
<th>Domain</th>
<th>Mastery Level</th>
<th>Key Capabilities</th>
</tr>
</thead>
<tbody>
<tr class="cursor-pointer" data-popup data-title="Figma Mastery" data-content="Component library governance, developer handoff protocols, Confluence/TFS documentation integration. Interactive prototyping, design token management, design-to-code translation pipelines.">
<td class="font-semibold">Figma</td>
<td><div class="progress-track w-24"><div class="progress-fill" style="width: 98%;"></div></div></td>
<td class="text-sm">Component libs · Design tokens · Dev Mode handoff</td>
</tr>
<tr class="cursor-pointer" data-popup data-title="ag-Grid Enterprise" data-content="Hands-on configuration: pivot tables, sparklines, server-side row models, delta-row update architectures. Performance optimization: virtual scrolling, row buffering, lazy loading, sub-second refresh cycles under load. Custom cell renderers, keyboard-navigable control hierarchies, low-latency fidelity for energy market operations.">
<td class="font-semibold">ag-Grid Enterprise</td>
<td><div class="progress-track w-24"><div class="progress-fill" style="width: 92%;"></div></div></td>
<td class="text-sm">SSRM · Delta updates · Pivot tables · Virtual scroll</td>
</tr>
<tr class="cursor-pointer" data-popup data-title="Angular Ecosystem" data-content="Angular 14-17 implementation evidence: Ivy rendering, reactive forms, Angular Material theming. State management architecture: NgRx, RxJS data stream orchestration, lazy-loaded module bundling. Cross-framework conceptual mapping via React/Next.js/Node.js background.">
<td class="font-semibold">Angular</td>
<td><div class="progress-track w-24"><div class="progress-fill" style="width: 85%;"></div></div></td>
<td class="text-sm">Ivy · Reactive Forms · NgRx · RxJS</td>
</tr>
<tr class="cursor-pointer" data-popup data-title="Front-End Constraints" data-content="Understanding HTML/CSS limitations to design feasible, performant UIs. Knowing what's technically achievable prevents over-designed mockups that engineering cannot implement efficiently.">
<td class="font-semibold">HTML/CSS</td>
<td><div class="progress-track w-24"><div class="progress-fill" style="width: 88%;"></div></div></td>
<td class="text-sm">Constraint literacy · Performance-aware design</td>
</tr>
</tbody>
</table>
</div>
</div>
<div id="s5" class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">V. Proactive Gap Resolution (AI & WCAG)</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="AI-900 & GenAI Workflows" data-content="Microsoft Certified AI Fundamentals (AI-900). Leveraging LLMs & GenAI for rapid prototyping. Generative AI workflows: Adobe Firefly, Midjourney, Claude & Python scripting for R&D velocity. Cutting prototyping time by 50%, accelerating R&D cycles, future-proofing Client's design operations.">
<div class="pill pill-midnight mb-2">5.1 · AI</div>
<h3 class="font-display font-bold text-base mb-1">Microsoft AI-900 Certified</h3>
<p class="text-sm text-gray-600">LLMs · GenAI · Firefly · Midjourney · Claude · Python.</p>
</div>
<div class="info-card" data-popup data-title="WCAG 2.1 AA/AAA" data-content="Microsoft Certified Accessibility (Feb 2025). Implementation & audit readiness. Industrial & iGaming implementation: keyboard navigation, ARIA-Live regions, focus management, dynamic contrast scaling. EN 301 549 / EU Procurement alignment, seizure-safe animation controls, automated accessibility auditing pipelines.">
<div class="pill pill-indian mb-2">5.2 · WCAG</div>
<h3 class="font-display font-bold text-base mb-1">WCAG 2.1 AA/AAA Compliance</h3>
<p class="text-sm text-gray-600">ARIA-Live · Focus mgmt · EN 301 549 · Seizure-safe.</p>
</div>
<div class="info-card md:col-span-2" data-popup data-title="Risk Mitigation" data-content="Preventing costly enterprise compliance retrofits in regulated energy markets. Strategic value: ensuring legal compliance, expanding inclusive enterprise user bases, reducing long-term maintenance costs. Alex builds accessibility into the design process from the outset — not as an afterthought or compliance checkbox.">
<div class="pill pill-steel mb-2">5.3 · RISK</div>
<h3 class="font-display font-bold text-base mb-1">Risk Mitigation: Compliance Retrofits Prevention</h3>
<p class="text-sm text-gray-600">Proactive WCAG prevents costly enterprise compliance retrofits in regulated energy markets.</p>
</div>
</div>
</div>
<div id="s6" class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">VI. Third-Party Validation & Corporate Viability</h2>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
<div class="info-card" data-popup data-title="Bert Konings — Structuring Chaos" data-content="VP Product Management, HMS Networks. Validates process predictability and creative workflow leadership. 'Went from being all over the map to a smooth process where everyone knew what they could expect.'">
<div class="font-display font-bold text-sm mb-1">Bert Konings</div>
<div class="text-xs text-gray-500 mb-2">VP Product Mgmt · HMS Networks</div>
<div class="pill pill-midnight">Structuring Chaos</div>
</div>
<div class="info-card" data-popup data-title="Kevin Donlan — SME Translation" data-content="VP Strategic Alliances, Shipley/Microsoft. Validates cross-functional collaboration and technical translation for global deals.">
<div class="font-display font-bold text-sm mb-1">Kevin Donlan</div>
<div class="text-xs text-gray-500 mb-2">VP Strategic Alliances · Microsoft</div>
<div class="pill pill-indian">SME Translation</div>
</div>
<div class="info-card" data-popup data-title="Gaetano Micera — Reliability" data-content="Director Life Science, Yokogawa. 'Reliable and sharp on task assignment, on time, exceeding expectations.'">
<div class="font-display font-bold text-sm mb-1">Gaetano Micera</div>
<div class="text-xs text-gray-500 mb-2">Director Life Science · Yokogawa</div>
<div class="pill pill-midnight">Reliability</div>
</div>
<div class="info-card" data-popup data-title="Maria Claus & Paul Holthuis" data-content="Yokogawa colleagues. 'Transforms abstract ideas into concrete designs, from concept to execution, implementation and simplification. There is nothing he can't do.' — Abstract-to-concrete simplification mastery.">
<div class="font-display font-bold text-sm mb-1">Maria Claus · Paul Holthuis</div>
<div class="text-xs text-gray-500 mb-2">Yokogawa</div>
<div class="pill pill-indian">Abstract → Concrete</div>
</div>
<div class="info-card" data-popup data-title="EU Directors — Global Stakeholder Mgmt" data-content="Dominiek Vanthuyse (MD Samson NV), Cynthia Doms (Marketing Yokogawa Belgium), Mailyn Schürmann (Digital Marketing/Life Science), Emma Bundy (Head of Marketing Yokogawa RAP). Validates cross-cultural stakeholder management across 12 EU markets.">
<div class="font-display font-bold text-sm mb-1">EU Directors (4)</div>
<div class="text-xs text-gray-500 mb-2">Dominiek · Cynthia · Mailyn · Emma</div>
<div class="pill pill-steel">Global Stakeholder Mgmt</div>
</div>
<div class="info-card" data-popup data-title="Social Proof Synthesis" data-content="Transforming qualitative endorsements into quantifiable hiring confidence & ROI assurance. Each testimonial addresses specific Client needs: process structure, SME collaboration, reliability, simplification, cross-cultural coordination.">
<div class="font-display font-bold text-sm mb-1">Social Proof Synthesis</div>
<div class="text-xs text-gray-500 mb-2">Qualitative → Quantifiable ROI</div>
<div class="pill pill-indian">Confidence Metric</div>
</div>
</div>
</div>
<div id="s7" class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">VII. Strategic Positioning & Pre-Interview Intelligence</h2>
<div class="bg-white rounded-xl p-6 border border-gray-200 mb-6">
<h3 class="font-display font-bold text-lg mb-3">Anticipated Objections & Counter-Responses</h3>
<div class="space-y-3">
<div class="info-card" data-popup data-title="Objection 1: No Direct Energy Sector Experience" data-content="PIVOT: Universal UX principles of high-stakes data, telemetry, and cognitive load management. EVIDENCE: Yokogawa CENTUM VP (industrial process control) + 100+ casino platforms (real-time financial grids). Both domains require identical core competencies: real-time data visualization, multi-layer forms, latency-constrained interactions.">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold shrink-0" style="background: var(--color-indian-red);">1</div>
<div>
<div class="font-display font-bold text-sm">"No direct energy trading sector experience"</div>
<div class="text-xs text-gray-500">→ Pivot: Universal UX principles · Evidence: Yokogawa + 100+ casinos</div>
</div>
</div>
</div>
<div class="info-card" data-popup data-title="Objection 2: Ramp-Up Speed" data-content="PIVOT: INTJ-A autonomy + immediate stack fluency (Figma, ag-Grid, Angular concepts). EVIDENCE: Structuring chaos testimonial (Bert Konings/HMS Networks) and legacy system mapping experience. Zero ramp-up time on the exact tools in Client's stack.">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold shrink-0" style="background: var(--color-indian-red);">2</div>
<div>
<div class="font-display font-bold text-sm">"Can you ramp up and add value quickly?"</div>
<div class="text-xs text-gray-500">→ INTJ-A autonomy · ag-Grid/Figma mastery · Legacy structuring</div>
</div>
</div>
</div>
<div class="info-card" data-popup data-title="Objection 3: Rate Justification" data-content="PIVOT: Shift from 'Hourly Resource' to 'Strategic Force Multiplier'. EVIDENCE: AI-accelerated prototyping (Adobe Firefly/Claude), preventing costly WCAG retrofits, architectural longevity. Alex delivers measurable efficiency gains and a higher-quality product — an investment, not a cost.">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold shrink-0" style="background: var(--color-indian-red);">3</div>
<div>
<div class="font-display font-bold text-sm">"How do you justify your B2B rate?"</div>
<div class="text-xs text-gray-500">→ Force Multiplier · Compliance risk reduction · Architectural longevity</div>
</div>
</div>
</div>
</div>
</div>
</div>
<div id="s8">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">VIII. Reference Index & Source Documentation</h2>
<div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
<div class="info-card" data-popup data-title="Primary Assets" data-content="ap-id.ro portfolio · LinkedIn /in/ap-id · CV · MBTI reports · WordPress/Salient documentation.">
<div class="font-display font-bold">Primary Assets</div>
<div class="text-xs text-gray-500 mt-1">ap-id.ro · LinkedIn · CV · MBTI</div>
</div>
<div class="info-card" data-popup data-title="Stack References" data-content="Angular 14-17 · ag-Grid Enterprise · WCAG 2.1/2.2 · AI-900 · Figma · Confluence/TFS.">
<div class="font-display font-bold">Stack References</div>
<div class="text-xs text-gray-500 mt-1">Angular · ag-Grid · WCAG · AI-900</div>
</div>
<div class="info-card" data-popup data-title="Client Archives" data-content="Yokogawa CENTUM VP · Microsoft/Shipley · Dacia Romania · Romexpo · 200+ iGaming platforms.">
<div class="font-display font-bold">Client Archives</div>
<div class="text-xs text-gray-500 mt-1">Yokogawa · Microsoft · Dacia · iGaming</div>
</div>
<div class="info-card" data-popup data-title="Research" data-content="HCI journals · NASA-TLX cognitive load studies · Latency/throughput trade-offs · Accessibility audits.">
<div class="font-display font-bold">Research</div>
<div class="text-xs text-gray-500 mt-1">HCI · NASA-TLX · Latency · WCAG audits</div>
</div>
<div class="info-card" data-popup data-title="URL Repo" data-content="Cross-referenced URL repository, verification logs, and scraped data provenance.">
<div class="font-display font-bold">URL Repo</div>
<div class="text-xs text-gray-500 mt-1">Verification logs · Scraped provenance</div>
</div>
<div class="info-card" data-popup data-title="Glossary" data-content="HMI · DCS · SCADA · RBAC · WCAG · AI-900 · ag-Grid · NgRx · RxJS · INTJ-A Cognitive Functions.">
<div class="font-display font-bold">Glossary</div>
<div class="text-xs text-gray-500 mt-1">HMI · DCS · SCADA · RBAC · WCAG</div>
</div>
</div>
</div>
</section>
<!-- ============================================= -->
<!-- TAB 3: Client INT - COMPANY INTELLIGENCE -->
<!-- ============================================= -->
<section id="Clientint" class="tab-content">
<div class="section-label mb-4">03 / COMPANY INTELLIGENCE</div>
<h1 class="font-display text-3xl md:text-5xl font-extrabold mb-4" style="color: var(--color-midnight-blue);">
Client & Multinational<br>Group Intelligence Dossier
</h1>
<p class="text-gray-600 text-lg mb-8 max-w-3xl">
Corporate architecture, market mission, technical constraints, and recruiter psychological/business priorities.
</p>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">1. Corporate Architecture & Entity Mapping</h2>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
<div class="info-card" data-popup data-title="Client Power (US Parent)" data-content="Clean energy innovator. Founded by Drew Baglino (ex-Tesla SVP). $140M Series B from Andreessen Horowitz and Breakthrough Energy. Flagship product: 'Client Link' solid-state transformers. Mission: debottleneck the grid for the AI & renewable era.">
<div class="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style="background: var(--color-midnight-blue);">
<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
</div>
<div class="font-display font-bold text-sm mb-1">Client Power (US)</div>
<div class="text-xs text-gray-500">Clean energy innovator · Parent co.</div>
</div>
<div class="info-card" data-popup data-title="Client (Romania)" data-content="B2B consultancy & R&D hub in Bucharest. Building the software layer for Grid 2.0. Hires B2B contractors for agility and scale. Robert (Business Partner) leading Romanian presence since Feb 2020.">
<div class="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style="background: var(--color-indian-red);">
<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
</div>
<div class="font-display font-bold text-sm mb-1">Client (RO)</div>
<div class="text-xs text-gray-500">B2B consultancy · R&D hub</div>
</div>
<div class="info-card" data-popup data-title="Client.net / Digital Ecosystem" data-content="Interconnected market presence across the group's digital properties.">
<div class="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style="background: var(--color-dark-gray);">
<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/></svg>
</div>
<div class="font-display font-bold text-sm mb-1">Client.net</div>
<div class="text-xs text-gray-500">Digital ecosystem</div>
</div>
<div class="info-card" data-popup data-title="Romanian Market Entry Strategy" data-content="Why Bucharest? Why B2B contractors? Access to senior engineering talent at competitive rates, timezone alignment with Western Europe, and agility to scale teams up/down per project needs. Initial 6-month contracts with extension potential.">
<div class="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style="background: rgba(0,32,96,0.1);">
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-midnight-blue);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"/></svg>
</div>
<div class="font-display font-bold text-sm mb-1">RO Entry Strategy</div>
<div class="text-xs text-gray-500">Bucharest · B2B agility</div>
</div>
</div>
</div>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">2. Client Power (US) Strategic Overview</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Core Mission" data-content="Debottleneck the grid for the AI & renewable era. The legacy US grid was not built to handle the dual pressures of electrification and the surge in power demand from AI data centers. Client Power's solution replaces bulky, outdated transformers with solid-state power electronics.">
<div class="pill pill-midnight mb-2">2.1 · MISSION</div>
<h3 class="font-display font-bold text-base mb-1">Debottleneck the Grid</h3>
<p class="text-sm text-gray-600">For the AI & renewable era.</p>
</div>
<div class="info-card" data-popup data-title="Client Link" data-content="Flagship solid-state transformer technology. Enables faster deployment of renewable energy sources like solar and battery storage. Direct connection of data centers and renewables to the grid.">
<div class="pill pill-midnight mb-2">2.2 · PRODUCT</div>
<h3 class="font-display font-bold text-base mb-1">'Client Link' Solid-State Transformers</h3>
<p class="text-sm text-gray-600">Flagship technology replacing legacy grid infrastructure.</p>
</div>
<div class="info-card" data-popup data-title="Leadership & Pedigree" data-content="Drew Baglino — former Tesla Senior Vice President of Powertrain and Energy Engineering. Deep expertise in scaling hardware companies and power electronics.">
<div class="pill pill-indian mb-2">2.3 · LEADERSHIP</div>
<h3 class="font-display font-bold text-base mb-1">Drew Baglino (Ex-Tesla SVP)</h3>
<p class="text-sm text-gray-600">Founder & visionary leadership.</p>
</div>
<div class="info-card" data-popup data-title="Financial Backing" data-content="$140M Series B financing co-led by Andreessen Horowitz and Breakthrough Energy (Bill Gates' climate investment fund). Signals strong investor confidence and runway for long-term R&D.">
<div class="pill pill-indian mb-2">2.4 · FUNDING</div>
<h3 class="font-display font-bold text-base mb-1">$140M Series B</h3>
<p class="text-sm text-gray-600">a16z · Breakthrough Energy.</p>
</div>
</div>
</div>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">4. Target Product Domain: Electricity Market Operations</h2>
<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
<div class="info-card text-center" data-popup data-title="Energy Trading" data-content="Real-time market price feeds, order book visualization, trade execution interfaces. Requires sub-100ms latency and high-density data presentation.">
<div class="text-2xl mb-2">⚡</div>
<div class="font-display font-bold text-sm">Energy Trading</div>
</div>
<div class="info-card text-center" data-popup data-title="Capacity Auctions" data-content="Complex bidding and scheduling interfaces with multi-layer forms, regulatory compliance tracking, and audit trails.">
<div class="text-2xl mb-2">📊</div>
<div class="font-display font-bold text-sm">Capacity Auctions</div>
</div>
<div class="info-card text-center" data-popup data-title="Grid Management" data-content="Settlement, balancing, reserve & congestion management dashboards. Real-time telemetry visualization for grid operators.">
<div class="text-2xl mb-2">🔌</div>
<div class="font-display font-bold text-sm">Grid Management</div>
</div>
<div class="info-card text-center" data-popup data-title="User Base" data-content="Traders, analysts, grid operators, and regulatory stakeholders. All require zero-error tolerance interfaces with high-stakes financial data.">
<div class="text-2xl mb-2">👥</div>
<div class="font-display font-bold text-sm">Traders · Analysts · Operators</div>
</div>
</div>
</div>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">5. Technical Stack & Design Infrastructure</h2>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
<div class="info-card" data-popup data-title="Angular" data-content="Component-based architecture, Reactive Forms, Ivy rendering, Angular Material theming. Primary front-end framework for Client's energy market applications.">
<div class="pill pill-midnight mb-2">5.1</div>
<h3 class="font-display font-bold text-base mb-1">Angular</h3>
<p class="text-sm text-gray-600">Component-based · Reactive Forms · Ivy.</p>
</div>
<div class="info-card" data-popup data-title="ag-Grid Enterprise" data-content="Enterprise Edition, Server-Side Row Models, Pivot Tables, Sparklines. Critical for displaying high-density energy market data with sub-second refresh cycles.">
<div class="pill pill-indian mb-2">5.2</div>
<h3 class="font-display font-bold text-base mb-1">ag-Grid Enterprise</h3>
<p class="text-sm text-gray-600">SSRM · Pivot · Sparklines.</p>
</div>
<div class="info-card" data-popup data-title="Figma" data-content="Prototyping, Design Systems, Developer Handoff. Primary design tool for collaborative UX workflows.">
<div class="pill pill-steel mb-2">5.3</div>
<h3 class="font-display font-bold text-base mb-1">Figma</h3>
<p class="text-sm text-gray-600">Prototyping · Design systems · Handoff.</p>
</div>
</div>
<div class="bg-white rounded-xl p-6 border border-gray-200" data-popup data-title="CSS & Design Tokens" data-content="Client's web architecture uses Roboto/Nunito typography pairing with Midnight Blue (#002060) as primary brand color and Indian Red (#d04a2f) as accent. Semantic type scale with .type-h1, .type-subheading, .type-large-body tokens.">
<h3 class="font-display font-bold text-base mb-4">CSS Architecture (Scraped)</h3>
<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
<div>
<div class="text-xs font-bold text-gray-500 mb-1">MIDNIGHT BLUE</div>
<div class="h-12 rounded-md mb-1" style="background: #002060;"></div>
<div class="text-xs font-mono">#002060</div>
</div>
<div>
<div class="text-xs font-bold text-gray-500 mb-1">INDIAN RED</div>
<div class="h-12 rounded-md mb-1" style="background: #d04a2f;"></div>
<div class="text-xs font-mono">#d04a2f</div>
</div>
<div>
<div class="text-xs font-bold text-gray-500 mb-1">ROBOTO</div>
<div class="h-12 rounded-md mb-1 bg-gray-100 flex items-center justify-center font-sans font-bold">Aa</div>
<div class="text-xs font-mono">Body / UI</div>
</div>
<div>
<div class="text-xs font-bold text-gray-500 mb-1">NUNITO</div>
<div class="h-12 rounded-md mb-1 bg-gray-100 flex items-center justify-center font-display font-bold">Aa</div>
<div class="text-xs font-mono">Display</div>
</div>
</div>
</div>
</div>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">6. Decision-Maker Intelligence: Robert</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Robert — Professional Profile" data-content="Business Partner at Client. Seasoned IT professional with strategy & sales focus. Building Client's Romanian presence since February 2020. 500+ LinkedIn connections.">
<div class="pill pill-midnight mb-2">6.1 · PROFILE</div>
<h3 class="font-display font-bold text-base mb-1">Business Partner · Strategy & Sales</h3>
<p class="text-sm text-gray-600">Seasoned IT professional · RO lead since Feb 2020.</p>
</div>
<div class="info-card" data-popup data-title="Hiring Philosophy" data-content="Prioritizes 'hands-on' value, minimal ramp-up, and B2B ROI. Looking for contractors who can deliver immediately without extensive onboarding. 6-month initial contracts with extension potential based on delivery results.">
<div class="pill pill-indian mb-2">6.2 · PHILOSOPHY</div>
<h3 class="font-display font-bold text-base mb-1">Hands-on Value · Minimal Ramp-Up</h3>
<p class="text-sm text-gray-600">B2B ROI · 6-month contracts · Delivery-driven extension.</p>
</div>
<div class="info-card" data-popup data-title="Current Talent Mandates" data-content="Hiring for: (1) Senior UI/UX Designers for energy trading software, (2) Senior AI Platform Engineers (Python/LLMs) for AI infrastructure. Signals a strategic push into both UX modernization and AI capability building.">
<div class="pill pill-steel mb-2">6.3 · MANDATES</div>
<h3 class="font-display font-bold text-base mb-1">UI/UX Designers + AI Platform Engineers</h3>
<p class="text-sm text-gray-600">Dual push: UX modernization + AI infrastructure.</p>
</div>
<div class="info-card" data-popup data-title="Communication Style" data-content="Direct, business-focused. Prefers concise B2B proposals with clear rate cards and deliverables. Available via LinkedIn DM, WhatsApp, and email. Values professionalism and responsiveness.">
<div class="pill pill-midnight mb-2">6.4 · STYLE</div>
<h3 class="font-display font-bold text-base mb-1">Direct · B2B-Focused · Responsive</h3>
<p class="text-sm text-gray-600">Clear rate cards · Deliverables · WhatsApp available.</p>
</div>
</div>
</div>
<div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">7. The Senior UI/UX Role: Explicit vs. Implicit Needs</h2>
<div class="overflow-x-auto rounded-xl border border-gray-200">
<table class="data-table">
<thead>
<tr>
<th>Category</th>
<th>Requirement</th>
<th>Alex Match</th>
</tr>
</thead>
<tbody>
<tr>
<td class="font-semibold text-sm" rowspan="4">Explicit JD</td>
<td class="text-sm">Figma mastery</td>
<td class="text-sm"><span class="pill pill-midnight">98%</span></td>
</tr>
<tr><td class="text-sm">Complex web apps, data-heavy UIs</td><td class="text-sm"><span class="pill pill-midnight">Yokogawa + iGaming</span></td></tr>
<tr><td class="text-sm">Multi-layer forms, dashboards, grids</td><td class="text-sm"><span class="pill pill-midnight">200+ platforms</span></td></tr>
<tr><td class="text-sm">Strong English (advanced)</td><td class="text-sm"><span class="pill pill-midnight">Full professional</span></td></tr>
<tr>
<td class="font-semibold text-sm" rowspan="3">Mandatory "Nice-to-Haves"</td>
<td class="text-sm">Angular / ag-Grid experience</td>
<td class="text-sm"><span class="pill pill-indian">Hands-on</span></td>
</tr>
<tr><td class="text-sm">Design systems experience</td><td class="text-sm"><span class="pill pill-indian">200+ Yokogawa templates</span></td></tr>
<tr><td class="text-sm">Energy/utilities domain</td><td class="text-sm"><span class="pill pill-indian">Adjacent: industrial automation</span></td></tr>
<tr>
<td class="font-semibold text-sm">Implicit Needs</td>
<td class="text-sm">Legacy system modernization & workflow structuring</td>
<td class="text-sm"><span class="pill pill-steel">Bert Konings testimonial</span></td>
</tr>
<tr>
<td class="font-semibold text-sm">Unspoken Gaps</td>
<td class="text-sm">AI integration + WCAG accessibility + enterprise compliance</td>
<td class="text-sm"><span class="pill pill-steel">AI-900 + 8 MSFT certs</span></td>
</tr>
</tbody>
</table>
</div>
</div>
</section>
<!-- ============================================= -->
<!-- TAB 4: AI INTERVIEW -->
<!-- ============================================= -->
<section id="interview" class="tab-content">
<div class="section-label mb-4">04 / INTERVIEW STRATEGY</div>
<h1 class="font-display text-3xl md:text-5xl font-extrabold mb-4" style="color: var(--color-midnight-blue);">
Client Interview<br>& Technical Alignment Strategy
</h1>
<p class="text-gray-600 text-lg mb-8 max-w-3xl">
Unified playbook for recruiter screening (Robert) and technical deep-dive (VP of Engineering / Angular-ag-Grid leads).
</p>
<div class="mb-12">
<div class="pill pill-midnight mb-3">PART I · BUSINESS ALIGNMENT (Robert)</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">The 3-Pillar Pitch</h2>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
<div class="info-card" data-popup data-title="Pillar 1: Complex Data Interfaces" data-content="Proven expertise in Yokogawa HMI (industrial automation dashboards, 12-country EU rollout, CENTUM VP DCS) and iGaming real-time grids (100+ casino/bingo platforms with sub-100ms latency constraints). Both domains directly parallel energy trading order books and capacity auction interfaces.">
<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold mb-3" style="background: var(--color-midnight-blue);">1</div>
<h3 class="font-display font-bold text-base mb-1">Complex Data Interfaces</h3>
<p class="text-sm text-gray-600">Yokogawa HMI · iGaming real-time grids.</p>
</div>
<div class="info-card" data-popup data-title="Pillar 2: Unstated Needs" data-content="Immediate value in WCAG compliance (Microsoft-certified, 90%+ pass rate at PCoE) and AI workflows (AI-900, Adobe Firefly, Claude). Addresses gaps the JD didn't mention but Client will need as they scale.">
<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold mb-3" style="background: var(--color-indian-red);">2</div>
<h3 class="font-display font-bold text-base mb-1">Unstated Needs</h3>
<p class="text-sm text-gray-600">WCAG compliance · AI workflows.</p>
</div>
<div class="info-card" data-popup data-title="Pillar 3: Corporate Viability" data-content="Validated via VP & Director testimonials: Bert Konings (HMS Networks), Kevin Donlan (Microsoft/Shipley), Gaetano Micera (Yokogawa), Maria Claus (Yokogawa). Social proof mitigates hiring risk for B2B contractors.">
<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold mb-3" style="background: var(--color-dark-gray);">3</div>
<h3 class="font-display font-bold text-base mb-1">Corporate Viability</h3>
<p class="text-sm text-gray-600">VP & Director testimonials.</p>
</div>
</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">B2B Partnership Framework</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="6-Month Contract Structure" data-content="Milestone-driven deliverables & prototype-first validation. Initial 6-month B2B engagement via DDA (Drepturi de Autor) with extension path to SRL micro-enterprise. Zero-overhead onboarding eliminates administrative friction.">
<div class="pill pill-midnight mb-2">4.1</div>
<h3 class="font-display font-bold text-base mb-1">6-Month Contract Structure</h3>
<p class="text-sm text-gray-600">Milestone-driven · Prototype-first validation.</p>
</div>
<div class="info-card" data-popup data-title="Rate Card" data-content="Official B2B Rate Card with value-based pricing anchors. €3,130 gross/month (≈€20/hour). Target €2,400 net take-home via DDA tax structure.">
<div class="pill pill-indian mb-2">4.2</div>
<h3 class="font-display font-bold text-base mb-1">Official B2B Rate Card</h3>
<p class="text-sm text-gray-600">Value-based pricing anchors.</p>
</div>
<div class="info-card" data-popup data-title="1-Page UX Architecture Summary" data-content="Executive summary for VP of Engineering: psychological alignment, stack fluency, and domain expertise in one page.">
<div class="pill pill-steel mb-2">4.3</div>
<h3 class="font-display font-bold text-base mb-1">1-Page UX Architecture Summary</h3>
<p class="text-sm text-gray-600">For VP of Engineering.</p>
</div>
<div class="info-card" data-popup data-title="Recruiter → Technical Transition" data-content="Handoff protocol from Robert's business screen to VP of Engineering's technical deep-dive. Pre-briefed talking points and evidence packages.">
<div class="pill pill-midnight mb-2">4.4</div>
<h3 class="font-display font-bold text-base mb-1">Recruiter → Technical Handoff</h3>
<p class="text-sm text-gray-600">Pre-briefed evidence packages.</p>
</div>
</div>
</div>
<div class="mb-12">
<div class="pill pill-indian mb-3">PART II · TECHNICAL ALIGNMENT (VP Eng / ag-Grid Leads)</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">The "Bridge" Persona</h2>
<div class="quote-block mb-6">
"Proving understanding of the 'physics' of the engine without pretending to write the TypeScript."
</div>
<h3 class="font-display text-xl font-bold mb-3" style="color: var(--color-midnight-blue);">6. Speaking the Stack's Language</h3>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
<div class="info-card" data-popup data-title="ag-Grid Realities" data-content="DOM virtualization & scroll performance. Avoiding heavy custom HTML in cell renderers. Designing slide-out drawers, master-detail rows, and modal overlays for density instead of cramming everything into grid cells.">
<div class="pill pill-midnight mb-2">6.1</div>
<h3 class="font-display font-bold text-base mb-1">ag-Grid Realities</h3>
<p class="text-sm text-gray-600">DOM virtualization · Slide-out drawers · Master-detail rows.</p>
</div>
<div class="info-card" data-popup data-title="Angular Realities" data-content="Designing for Reactive Forms (FormGroups, FormArrays, nested data). Mapping Figma variables to Angular Material / custom design tokens. Understanding NgRx and RxJS data stream orchestration.">
<div class="pill pill-indian mb-2">6.2</div>
<h3 class="font-display font-bold text-base mb-1">Angular Realities</h3>
<p class="text-sm text-gray-600">Reactive Forms · NgRx · RxJS orchestration.</p>
</div>
<div class="info-card" data-popup data-title="Real-Time Data (Sub-100ms)" data-content="Designing 'delta states' (visual feedback for price/data ticks). Preventing cognitive overload and seizure risks in live order books. Skeleton loaders, API failure states, empty state architecture.">
<div class="pill pill-steel mb-2">6.3</div>
<h3 class="font-display font-bold text-base mb-1">Real-Time Data Constraints</h3>
<p class="text-sm text-gray-600">Sub-100ms · Delta states · Seizure-safe animations.</p>
</div>
</div>
<h3 class="font-display text-xl font-bold mb-3" style="color: var(--color-midnight-blue);">8. Strategic Questions to Ask Engineering</h3>
<div class="space-y-3">
<div class="info-card" data-popup data-title="Q1: Technical Debt" data-content="'What is the biggest UX-related technical debt in the current Angular codebase?' — Signals awareness that legacy systems carry hidden costs and positions Alex as a problem-solver, not a screen-painter.">
<div class="font-mono text-xs font-bold mb-1" style="color: var(--color-indian-red);">Q1</div>
<div class="font-display font-semibold text-sm">"What is the biggest UX-related technical debt in the current Angular codebase?"</div>
</div>
<div class="info-card" data-popup data-title="Q2: Row Models" data-content="'Are we using Client-Side or Server-Side Row Models (SSRM) for the heavy market data?' — Demonstrates ag-Grid fluency at architecture level, not just UI level.">
<div class="font-mono text-xs font-bold mb-1" style="color: var(--color-indian-red);">Q2</div>
<div class="font-display font-semibold text-sm">"Are we using Client-Side or Server-Side Row Models (SSRM) for the heavy market data?"</div>
</div>
<div class="info-card" data-popup data-title="Q3: Unsaved Changes" data-content="'How is global state handling unsaved changes in complex, multi-layer capacity auction forms?' — Addresses real-world UX challenge in financial interfaces.">
<div class="font-mono text-xs font-bold mb-1" style="color: var(--color-indian-red);">Q3</div>
<div class="font-display font-semibold text-sm">"How is global state handling unsaved changes in complex, multi-layer capacity auction forms?"</div>
</div>
<div class="info-card" data-popup data-title="Q4: CI/CD Pipeline" data-content="'What is the current CI/CD pipeline for updating the Design System from Figma to Angular?' — Signals systems thinking and design-ops maturity.">
<div class="font-mono text-xs font-bold mb-1" style="color: var(--color-indian-red);">Q4</div>
<div class="font-display font-semibold text-sm">"What is the current CI/CD pipeline for updating the Design System from Figma to Angular?"</div>
</div>
</div>
</div>
<div>
<div class="pill pill-steel mb-3">PART III · SYNTHESIS</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">Uniting Business & Technical Narratives</h2>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
<div class="info-card" data-popup data-title="Technical Reality → Business Pitch" data-content="ag-Grid/Angular fluency directly validates the business pitch of zero ramp-up time. Alex can deliver from Day 1 on Client's exact stack.">
<div class="font-display font-bold text-sm mb-1">10.1</div>
<div class="text-xs text-gray-600">Technical reality validates ramp-up speed pitch.</div>
</div>
<div class="info-card" data-popup data-title="Business Reality → Technical Rigor" data-content="B2B ROI justifies the technical rigor of accessibility & AI integration — both reduce long-term costs and risk.">
<div class="font-display font-bold text-sm mb-1">10.2</div>
<div class="text-xs text-gray-600">B2B ROI justifies WCAG/AI rigor.</div>
</div>
<div class="info-card" data-popup data-title="Final Posture" data-content="Operating as a peer, a force multiplier, and a strategic partner for Client Power's Grid 2.0 mission — not a hired gun.">
<div class="font-display font-bold text-sm mb-1">10.3</div>
<div class="text-xs text-gray-600">Peer · Force multiplier · Strategic partner.</div>
</div>
</div>
</div>
</section>
<!-- ============================================= -->
<!-- TAB 5: B2B RATE -->
<!-- ============================================= -->
<section id="b2b" class="tab-content">
<div class="section-label mb-4">05 / COMMERCIAL PROPOSAL</div>
<h1 class="font-display text-3xl md:text-5xl font-extrabold mb-4" style="color: var(--color-midnight-blue);">
B2B UX Architecture Proposal<br>& Strategic Alignment
</h1>
<p class="text-gray-600 text-lg mb-8 max-w-3xl">
70% commercial focus, 30% technical validation. Pure financial offer, tax optimization, and measurable ROI for Client.
</p>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">1. Pure Financial Offer & Rate Card</h2>
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
<div class="stat-card">
<div class="stat-value">€3,130</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">GROSS / MONTH</div>
</div>
<div class="stat-card">
<div class="stat-value">€20</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">PER HOUR</div>
</div>
<div class="stat-card">
<div class="stat-value" style="color: var(--color-indian-red);">~€2,400</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">NET TAKE-HOME</div>
</div>
<div class="stat-card">
<div class="stat-value">160h</div>
<div class="text-xs text-gray-500 font-semibold mt-2 tracking-wide">MONTHLY BASE</div>
</div>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Currency & Payment Terms" data-content="EUR/USD parity · Net 30 payment terms · Wire/SWIFT transfer to Romanian multi-currency account. Flexible invoicing in either EUR or USD based on Client's preference.">
<div class="pill pill-midnight mb-2">1.3</div>
<h3 class="font-display font-bold text-base mb-1">Currency & Payment Terms</h3>
<p class="text-sm text-gray-600">EUR/USD · Net 30 · Wire/SWIFT · Multi-currency account.</p>
</div>
<div class="info-card" data-popup data-title="'All-In' Value Proposition" data-content="Base UX Architecture + AI Agentic Workflows + WCAG Audits included in single rate. Zero hidden fees. No separate line items for AI prototyping, accessibility reviews, or design system governance.">
<div class="pill pill-indian mb-2">1.4</div>
<h3 class="font-display font-bold text-base mb-1">"All-In" Value Proposition</h3>
<p class="text-sm text-gray-600">UX Architecture + AI Workflows + WCAG Audits · Zero hidden fees.</p>
</div>
</div>
</div>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">2. Contractual Framework & Romanian Tax Structure</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
<div class="info-card" data-popup data-title="DDA — Drepturi de Autor" data-content="Copyright Contract advantage for B2B collaborations. Client's Romanian entity withholds taxes at source (impozit + CAS + CASS). Alex receives clean net amount. 40% forfetary deduction significantly reduces taxable base.">
<div class="pill pill-midnight mb-2">2.1 · DDA</div>
<h3 class="font-display font-bold text-base mb-1">Drepturi de Autor (Copyright Contract)</h3>
<p class="text-sm text-gray-600">B2B advantage · 40% forfetary deduction · At-source withholding.</p>
</div>
<div class="info-card" data-popup data-title="Withholding at Source" data-content="Client RO entity responsibilities & ANAF compliance. They calculate, withhold, and pay impozit (10%), CAS, and CASS at source. Alex receives clean net. No separate tax filings needed during contract.">
<div class="pill pill-indian mb-2">2.2</div>
<h3 class="font-display font-bold text-base mb-1">Withholding at Source</h3>
<p class="text-sm text-gray-600">Client RO handles ANAF compliance · Impozit + CAS + CASS.</p>
</div>
<div class="info-card" data-popup data-title="Tax Breakdown" data-content="Leveraging the 40% DDA forfetary deduction & CAS/CASS thresholds. Effective tax rate significantly lower than PFA or CIM. Clean, predictable net take-home each month.">
<div class="pill pill-steel mb-2">2.3</div>
<h3 class="font-display font-bold text-base mb-1">Tax Breakdown</h3>
<p class="text-sm text-gray-600">40% forfetary deduction · CAS/CASS thresholds.</p>
</div>
<div class="info-card" data-popup data-title="6-Month Trial Scope" data-content="Zero-overhead onboarding eliminates initial administrative friction. No SRL setup costs, no accountant fees, no registration delays. Alex starts delivering immediately.">
<div class="pill pill-midnight mb-2">2.4</div>
<h3 class="font-display font-bold text-base mb-1">6-Month Trial Scope</h3>
<p class="text-sm text-gray-600">Zero-overhead onboarding · No SRL setup · No accountant fees.</p>
</div>
</div>
<div class="info-card" data-popup data-title="Future-Proofing: SRL Transition" data-content="Post-trial transition strategy to SRL (Micro-Enterprise) for long-term engagement. If the 6-month trial succeeds and extends, Alex sets up his own SRL for ongoing B2B collaboration — clean, scalable, and fully aligned with Client's contracting model.">
<div class="pill pill-indian mb-2">2.5 · FUTURE</div>
<h3 class="font-display font-bold text-base mb-1">Future-Proofing: SRL Transition Post-Trial</h3>
<p class="text-sm text-gray-600">Transition to Micro-Enterprise SRL for long-term engagement.</p>
</div>
</div>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">3. Rate Justification & Market Benchmarking</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Market Baselines" data-content="Bucharest Senior UX market baselines vs. US enterprise contracting standards. Alex's rate sits at the intersection: competitive for Eastern Europe, delivering US-grade enterprise value.">
<div class="pill pill-midnight mb-2">3.1</div>
<h3 class="font-display font-bold text-base mb-1">Bucharest vs. US Enterprise Standards</h3>
<p class="text-sm text-gray-600">Eastern Europe competitive · US-grade value.</p>
</div>
<div class="info-card" data-popup data-title="Base Rate" data-content="Standard Senior UI/UX market value in Eastern Europe for enterprise work. Foundation before premiums applied.">
<div class="pill pill-steel mb-2">3.2</div>
<h3 class="font-display font-bold text-base mb-1">Base Rate</h3>
<p class="text-sm text-gray-600">Standard Senior UI/UX Eastern Europe.</p>
</div>
<div class="info-card" data-popup data-title="Mission-Critical Premium" data-content="Pricing industrial, high-stakes data, & regulated market expertise. Yokogawa CENTUM VP (industrial automation), Microsoft PCoE (WCAG), 200+ iGaming platforms (real-time financial grids).">
<div class="pill pill-indian mb-2">3.3</div>
<h3 class="font-display font-bold text-base mb-1">Mission-Critical Premium</h3>
<p class="text-sm text-gray-600">Industrial · High-stakes · Regulated markets.</p>
</div>
<div class="info-card" data-popup data-title="Modern Skillset Premium" data-content="Financial value of embedded AI & Accessibility compliance. AI-900 + 8 Microsoft certifications + hands-on Firefly/Claude workflows. These skills reduce Client's long-term compliance and R&D costs.">
<div class="pill pill-midnight mb-2">3.4</div>
<h3 class="font-display font-bold text-base mb-1">Modern Skillset Premium</h3>
<p class="text-sm text-gray-600">AI + Accessibility compliance value.</p>
</div>
</div>
</div>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">4. Commercial ROI & Business Value for Client</h2>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
<div class="info-card" data-popup data-title="Cost Avoidance" data-content="Preventing expensive WCAG 2.1 AA/AAA compliance retrofits & legal risks. EU accessibility regulations (EN 301 549) mandate compliance — retrofitting costs 5-10x more than building it in from Day 1.">
<div class="text-3xl mb-2" style="color: var(--color-indian-red);">🛡️</div>
<div class="font-display font-bold text-sm mb-1">Cost Avoidance</div>
<div class="text-xs text-gray-600">Prevents WCAG retrofits · Legal risk reduction.</div>
</div>
<div class="info-card" data-popup data-title="Revenue Acceleration" data-content="AI-driven prototyping, agentic workflows, & R&D velocity. 50% faster prototyping cycles with Adobe Firefly + Claude. Faster time-to-market for Client's energy trading features.">
<div class="text-3xl mb-2" style="color: var(--color-midnight-blue);">⚡</div>
<div class="font-display font-bold text-sm mb-1">Revenue Acceleration</div>
<div class="text-xs text-gray-600">AI prototyping · Agentic workflows · R&D velocity.</div>
</div>
<div class="info-card" data-popup data-title="Risk Mitigation" data-content="Legacy system structuring, technical debt prevention, & zero ramp-up time. Bert Konings testimonial validates ability to bring order to chaos.">
<div class="text-3xl mb-2" style="color: var(--color-indian-red);">🎯</div>
<div class="font-display font-bold text-sm mb-1">Risk Mitigation</div>
<div class="text-xs text-gray-600">Legacy structuring · Tech debt prevention.</div>
</div>
<div class="info-card" data-popup data-title="'Force Multiplier' Effect" data-content="Securing a UX Architect, an AI Prompter, and an Accessibility Auditor in one contract. Three specialized roles consolidated into one strategic partner at a single rate.">
<div class="text-3xl mb-2" style="color: var(--color-midnight-blue);">🚀</div>
<div class="font-display font-bold text-sm mb-1">"Force Multiplier"</div>
<div class="text-xs text-gray-600">UX Architect + AI Prompter + WCAG Auditor.</div>
</div>
</div>
</div>
<div class="mb-12">
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">5. B2B Partnership Terms & Deliverables</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Milestone-Driven Deliverables" data-content="Outcomes over hours. No time-tracking micromanagement. Monthly milestones tied to concrete deliverables: wireframes, prototypes, design systems, accessibility audits.">
<div class="pill pill-midnight mb-2">5.1</div>
<h3 class="font-display font-bold text-base mb-1">Milestone-Driven Deliverables</h3>
<p class="text-sm text-gray-600">Outcomes over hours · No time-tracking micromanagement.</p>
</div>
<div class="info-card" data-popup data-title="IP & Copyright Transfer" data-content="Intellectual Property & copyright transfer clauses under Romanian DDA Law. Client owns all produced work outright. Clean IP chain for enterprise use.">
<div class="pill pill-indian mb-2">5.2</div>
<h3 class="font-display font-bold text-base mb-1">IP & Copyright Transfer</h3>
<p class="text-sm text-gray-600">Romanian DDA Law · Client owns all work.</p>
</div>
<div class="info-card" data-popup data-title="Core Scope of Work" data-content="Energy trading dashboards, capacity auctions, grid UI, & multi-layer forms. Direct mapping to JD requirements with Alex's Yokogawa + iGaming precedent.">
<div class="pill pill-steel mb-2">5.3</div>
<h3 class="font-display font-bold text-base mb-1">Core Scope of Work</h3>
<p class="text-sm text-gray-600">Energy trading · Capacity auctions · Grid UI.</p>
</div>
<div class="info-card" data-popup data-title="Extension Triggers & KPIs" data-content="Clear triggers for contract extension: milestone completion, KPI delivery, stakeholder satisfaction. Long-term retainer scaling path to SRL engagement post-trial.">
<div class="pill pill-midnight mb-2">5.4</div>
<h3 class="font-display font-bold text-base mb-1">Extension Triggers & KPIs</h3>
<p class="text-sm text-gray-600">Milestone completion · Retainer scaling.</p>
</div>
</div>
</div>
<div>
<div class="pill pill-steel mb-3">PART II · 30% STRATEGIC UX VALIDATION</div>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
<div class="info-card" data-popup data-title="INTJ-A Psychological Alignment" data-content="Systems Thinking (Ni): Deconstructing legacy code & holistic information architecture. Structured Execution (Te): Agile alignment, telemetry, objective decision-making. Assertive Leadership (-A): High-stakes corporate navigation & SME pushback.">
<div class="pill pill-midnight mb-2">6</div>
<h3 class="font-display font-bold text-base mb-1">INTJ-A Architect Alignment</h3>
<p class="text-sm text-gray-600">Ni · Te · -A cognitive stack for enterprise R&D.</p>
</div>
<div class="info-card" data-popup data-title="Domain Transferability" data-content="Yokogawa Electric: Industrial HMI, SCADA dashboards, 12-country EU rollouts. iGaming: Real-time grids, sub-100ms latency, multi-layer forms. Microsoft/Shipley: High-stakes B2B data viz & global deal support.">
<div class="pill pill-indian mb-2">7</div>
<h3 class="font-display font-bold text-base mb-1">Domain Expertise Transferability</h3>
<p class="text-sm text-gray-600">Yokogawa · iGaming · Microsoft/Shipley.</p>
</div>
<div class="info-card" data-popup data-title="Third-Party Validation" data-content="Bert Konings (HMS Networks VP): Structuring chaos. Kevin Donlan (Microsoft VP): SME translation. Yokogawa Directors: Reliability & abstract-to-concrete execution. Social proof → quantifiable hiring confidence.">
<div class="pill pill-steel mb-2">8·9</div>
<h3 class="font-display font-bold text-base mb-1">Third-Party Validation</h3>
<p class="text-sm text-gray-600">VP/Director testimonials · Hiring confidence.</p>
</div>
</div>
</div>
</section>
<!-- ============================================= -->
<!-- TAB 6: AI UI - ARCHITECTURAL BLUEPRINT -->
<!-- ============================================= -->
<section id="aiui" class="tab-content">
<div class="section-label mb-4">06 / ARCHITECTURAL BLUEPRINT</div>
<h1 class="font-display text-3xl md:text-5xl font-extrabold mb-4" style="color: var(--color-midnight-blue);">
Architectural Blueprint for the<br>B2B Proposal Website
</h1>
<p class="text-gray-600 text-lg mb-8 max-w-3xl">
Unified Source of Truth for merging Client's brand identity with Salient's advanced aesthetics.
</p>
<div class="mb-12">
<div class="pill pill-midnight mb-3">PART I · Client BRAND DECONSTRUCTION</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">1. Core Color Palette & CSS Variables</h2>
<div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
<div class="info-card" data-popup data-title="Midnight Blue — Primary" data-content="Scraped CSS: --color-midnight-blue: #002060 / Standard: #191970. Psychological impact: trust, authority, and enterprise stability. Used for headers, footers, navigation, primary typography.">
<div class="h-16 rounded-md mb-3" style="background: #002060;"></div>
<div class="font-display font-bold text-xs">MIDNIGHT BLUE</div>
<div class="text-[10px] font-mono text-gray-500 mt-1">#002060</div>
</div>
<div class="info-card" data-popup data-title="Indian Red — Secondary" data-content="Scraped CSS: --color-indian-red: #d04a2f / #d04a30. Strategic use for CTAs, hover states, and drawing the user's eye. Signals innovation, action, urgency.">
<div class="h-16 rounded-md mb-3" style="background: #d04a2f;"></div>
<div class="font-display font-bold text-xs">INDIAN RED</div>
<div class="text-[10px] font-mono text-gray-500 mt-1">#d04a2f</div>
</div>
<div class="info-card" data-popup data-title="White Smoke — Neutral" data-content="Hex: #f2f2f2. Background for content sections, provides structural breathing room between Midnight Blue elements.">
<div class="h-16 rounded-md mb-3 border border-gray-200" style="background: #f2f2f2;"></div>
<div class="font-display font-bold text-xs">WHITE SMOKE</div>
<div class="text-[10px] font-mono text-gray-500 mt-1">#f2f2f2</div>
</div>
<div class="info-card" data-popup data-title="Dark Gray — Steel" data-content="Hex: #202b3a / #333333. Body text, secondary UI elements, card borders.">
<div class="h-16 rounded-md mb-3" style="background: #202b3a;"></div>
<div class="font-display font-bold text-xs">DARK GRAY</div>
<div class="text-[10px] font-mono text-gray-500 mt-1">#202b3a</div>
</div>
<div class="info-card" data-popup data-title="Pure White" data-content="Hex: #ffffff. Primary canvas, card backgrounds, text on dark elements.">
<div class="h-16 rounded-md mb-3 border border-gray-200" style="background: #ffffff;"></div>
<div class="font-display font-bold text-xs">PURE WHITE</div>
<div class="text-[10px] font-mono text-gray-500 mt-1">#ffffff</div>
</div>
</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">2. Typographic Hierarchy & Font Pairing</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
<div class="info-card" data-popup data-title="Roboto — Primary" data-content="Scraped CSS: --font-roboto. Used for body copy, data-heavy UI elements, and long-form readability. Modern geometric sans-serif, neutral, clear, screen-optimized.">
<div class="font-sans text-4xl font-bold mb-2" style="color: var(--color-midnight-blue);">Roboto Aa</div>
<div class="text-sm text-gray-600">Body copy · Data-heavy UI · Long-form readability.</div>
</div>
<div class="info-card" data-popup data-title="Nunito — Secondary" data-content="Scraped CSS: --font-nunito. Used for headings, subheadings, and approachable UI microcopy. Rounded sans-serif with softer curves, humanistic feel.">
<div class="font-display text-4xl font-bold mb-2" style="color: var(--color-indian-red);">Nunito Aa</div>
<div class="text-sm text-gray-600">Headings · Subheadings · Approachable microcopy.</div>
</div>
</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">3. Current State vs. Aspirational Vision</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
<div class="info-card" data-popup data-title="Current State Audit" data-content="Minimalist, functional, but lacking interactive depth and modern B2B 'wow' factor. Basic informational site with limited engagement mechanics.">
<div class="pill pill-steel mb-2">3.1 · CURRENT</div>
<h3 class="font-display font-bold text-base mb-1">Current Web Presence</h3>
<p class="text-sm text-gray-600">Minimalist · Functional · Lacks interactive depth.</p>
</div>
<div class="info-card" data-popup data-title="Upgrade Mandate" data-content="Transforming a static corporate brochure into a dynamic, Salient-inspired interactive proposal platform that reflects Client Power's Grid 2.0 innovation.">
<div class="pill pill-indian mb-2">3.2 · ASPIRATIONAL</div>
<h3 class="font-display font-bold text-base mb-1">The Upgrade Mandate</h3>
<p class="text-sm text-gray-600">Static brochure → dynamic Salient-inspired platform.</p>
</div>
</div>
</div>
<div class="mb-12">
<div class="pill pill-indian mb-3">PART II · SALIENT THEME AESTHETIC ANALYSIS</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">4. Advanced Layout Systems</h2>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
<div class="info-card" data-popup data-title="Multipurpose Row Structures" data-content="Full-width hero sections, nested columns, and asymmetrical data grids. Salient's signature flexible grid system adapted to Client's brand canvas.">
<div class="pill pill-midnight mb-2">4.1</div>
<h3 class="font-display font-bold text-base mb-1">Multipurpose Rows</h3>
<p class="text-sm text-gray-600">Full-width heroes · Nested columns · Asymmetric grids.</p>
</div>
<div class="info-card" data-popup data-title="Visual Composer Equivalents" data-content="Translating Salient's drag-and-drop modular logic into custom HTML/CSS/JS blocks. No heavy plugins — lightweight, maintainable code.">
<div class="pill pill-indian mb-2">4.2</div>
<h3 class="font-display font-bold text-base mb-1">Modular Logic</h3>
<p class="text-sm text-gray-600">Custom HTML/CSS/JS blocks · No heavy plugins.</p>
</div>
<div class="info-card" data-popup data-title="Dynamic Portfolios & Filterable Grids" data-content="Adapting Salient's portfolio modules to showcase Alex Popescu's Yokogawa, Microsoft, and iGaming case studies. Isotope/masonry layouts with category filtering.">
<div class="pill pill-steel mb-2">4.3</div>
<h3 class="font-display font-bold text-base mb-1">Filterable Grids</h3>
<p class="text-sm text-gray-600">Isotope/masonry · Case study showcases.</p>
</div>
</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">5. Motion Design & Micro-Interactions</h2>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
<div class="info-card" data-popup data-title="Parallax Scrolling Effects" data-content="Creating depth between Midnight Blue backgrounds and foreground data-visualizations. Subtle, corporate-appropriate parallax — not consumer-flashy.">
<div class="pill pill-midnight mb-2">5.1</div>
<h3 class="font-display font-bold text-base mb-1">Parallax Scrolling</h3>
<p class="text-sm text-gray-600">Depth between Midnight Blue & data visualizations.</p>
</div>
<div class="info-card" data-popup data-title="Animated Entrances" data-content="Viewport-triggered fade-ins, slide-ups, and scale transformations for text and UI cards as the user scrolls. IntersectionObserver-driven, performant.">
<div class="pill pill-indian mb-2">5.2</div>
<h3 class="font-display font-bold text-base mb-1">Animated Entrances</h3>
<p class="text-sm text-gray-600">Viewport triggers · Fade-ins · Slide-ups.</p>
</div>
<div class="info-card" data-popup data-title="Interactive Hover States" data-content="Card lifts, border transformations, and Indian Red accent reveals on B2B proposal modules. Subtle, professional feedback for user interactions.">
<div class="pill pill-steel mb-2">5.3</div>
<h3 class="font-display font-bold text-base mb-1">Interactive Hover States</h3>
<p class="text-sm text-gray-600">Card lifts · Border transformations · Indian Red reveals.</p>
</div>
<div class="info-card" data-popup data-title="Typography Animations" data-content="Gradient text fills, drop shadows, and staggered character reveals for main headlines. Reserved for hero sections to maintain corporate tone.">
<div class="pill pill-midnight mb-2">5.4</div>
<h3 class="font-display font-bold text-base mb-1">Typography Animations</h3>
<p class="text-sm text-gray-600">Gradient fills · Drop shadows · Character reveals.</p>
</div>
</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">6. Premium UI Components</h2>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
<div class="info-card text-center" data-popup data-title="Stylized CTA Buttons" data-content="Rounded corners, subtle box-shadows, and Indian Red hover transitions. Clear visual hierarchy for primary actions.">
<div class="inline-block px-4 py-2 rounded-md text-white text-xs font-bold" style="background: var(--color-indian-red);">CTA Example</div>
<div class="text-xs text-gray-600 mt-2">Rounded · Shadow · Hover transitions.</div>
</div>
<div class="info-card text-center" data-popup data-title="Video Backgrounds" data-content="Looping, abstract energy/grid animations in Hero section with dark overlays for text contrast. Subtle, corporate-appropriate motion.">
<div class="text-3xl mb-2">🎬</div>
<div class="text-xs text-gray-600">Hero video loops · Dark overlays.</div>
</div>
<div class="info-card text-center" data-popup data-title="Lightbox Galleries & Modals" data-content="Salient-style pop-ups for deep-diving into the 'Master Dossier' financial and technical tables of contents. This very page's modal system is an example.">
<div class="text-3xl mb-2">🔍</div>
<div class="text-xs text-gray-600">Deep-dive pop-ups · Master Dossier.</div>
</div>
<div class="info-card text-center" data-popup data-title="Testimonial Carousels" data-content="Interactive sliders featuring quotes from Bert Konings, Kevin Donlan, and Yokogawa directors. Auto-rotate + manual navigation.">
<div class="text-3xl mb-2">💬</div>
<div class="text-xs text-gray-600">VP quotes · Auto-rotate sliders.</div>
</div>
</div>
</div>
<div class="mb-12">
<div class="pill pill-steel mb-3">PART III · STRATEGIC SYNTHESIS</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">Three Approaches to Merging Brand & Aesthetics</h2>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
<div class="info-card" data-popup data-title="Strategy 1: Elevated Foundation" data-content="Strict adherence to Midnight Blue/Indian Red/Roboto/Nunito. Applying Salient's multipurpose layouts and modular grids over the strict brand canvas. Best for: Maintaining absolute corporate safety while drastically improving visual structure.">
<div class="pill pill-midnight mb-2">STRATEGY 1</div>
<h3 class="font-display font-bold text-base mb-1">Elevated Foundation</h3>
<p class="text-sm text-gray-600">Strict brand + Salient layouts. Corporate safety.</p>
</div>
<div class="info-card" data-popup data-title="Strategy 2: Strategic Accentuation" data-content="Midnight Blue sparingly (Navigation/Footer), White Smoke/White for main content areas. Indian Red strictly as high-contrast 'Action' color for Salient-style animated buttons and interactive data points. Best for: Guiding Robert (the recruiter) through a highly focused, conversion-optimized user journey.">
<div class="pill pill-indian mb-2">STRATEGY 2</div>
<h3 class="font-display font-bold text-base mb-1">Strategic Accentuation</h3>
<p class="text-sm text-gray-600">Focused · Conversion-optimized · Indian Red actions.</p>
</div>
<div class="info-card" data-popup data-title="Strategy 3: Integrated System (Recommended)" data-content="Deep customization of CSS variables to map Salient's default states directly to Client's scraped CSS tokens. Creating bespoke HTML/CSS components that mimic Salient's premium feel but are lightweight and perfectly branded. Best for: A high-performance, bespoke B2B proposal site that looks like a million-dollar enterprise product. THIS IS THE APPROACH USED ON THIS PAGE.">
<div class="pill pill-steel mb-2">STRATEGY 3 · RECOMMENDED</div>
<h3 class="font-display font-bold text-base mb-1">Integrated System</h3>
<p class="text-sm text-gray-600">Deep CSS customization · Bespoke components · Premium feel.</p>
</div>
</div>
</div>
<div class="mb-12">
<div class="pill pill-midnight mb-3">PART IV · ACTIONABLE DESIGN DIRECTIVES</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">Section-by-Section Blueprint</h2>
<div class="space-y-3">
<div class="info-card" data-popup data-title="10. Global Styles & Navigation" data-content="Sticky Navigation Bar: Dark Gray (#202b3a) or Midnight Blue background, Nunito font, Indian Red active-state underlines. Custom Scrollbars: Browser scrollbar styled to match Midnight Blue brand color. Global Focus States: Ensuring WCAG 2.1 AA compliance with visible Indian Red focus rings for keyboard navigation.">
<div class="font-display font-bold text-sm mb-1">10. Global Styles & Navigation</div>
<div class="text-xs text-gray-600">Sticky nav · Custom scrollbars · WCAG focus rings.</div>
</div>
<div class="info-card" data-popup data-title="11. Hero Section (The 'Wow' Factor)" data-content="Background: Subtle, dark-tinted video loop of energy grids or abstract data flows. Typography: Massive Roboto .type-h1 headline with Salient-style staggered text reveal. Primary CTA: Indian Red button with hover-lift effect ('Review the B2B Financial Proposal'). The actual WOW element uses a custom SVG with animated energy flows, Client brand colors, and centered Client text in the orange stroked circle.">
<div class="font-display font-bold text-sm mb-1">11. Hero Section</div>
<div class="text-xs text-gray-600">Video background · Massive typography · Indian Red CTA.</div>
</div>
<div class="info-card" data-popup data-title="12. Master Dossier Navigation Hub" data-content="Filterable Grid Layout: Salient-style masonry or isotope grid representing the 70% Commercial / 30% Technical ToC. Info Pop-ups & Modals: Clicking a grid item opens a sleek, animated modal containing the deep-dive research data (Rate Card, INTJ-A mapping, ag-Grid expertise). Hover Effects: Cards display a subtle Midnight Blue overlay with an Indian Red icon reveal on hover.">
<div class="font-display font-bold text-sm mb-1">12. Master Dossier Navigation Hub</div>
<div class="text-xs text-gray-600">Filterable grid · Info modals · Hover overlays.</div>
</div>
<div class="info-card" data-popup data-title="13. Case Studies & Social Proof" data-content="Yokogawa & Microsoft Showcases: Parallax image backgrounds with floating Roboto text blocks detailing the 12-country rollout and WCAG compliance. Testimonial Carousel: Nunito-font quotes sliding in from the sides, featuring headshots and corporate titles.">
<div class="font-display font-bold text-sm mb-1">13. Case Studies & Social Proof</div>
<div class="text-xs text-gray-600">Parallax showcases · Testimonial carousel.</div>
</div>
<div class="info-card" data-popup data-title="14. Financial Offer & Contract Module" data-content="Data Visualization: Clean, Salient-style progress bars or radial charts showing the DDA tax breakdown (Gross 3,130 EUR vs. Net 2,400 EUR). Interactive Pricing Tables: Hovering over the 'Force Multiplier' ROI metrics highlights the cost-avoidance of AI and Accessibility integration.">
<div class="font-display font-bold text-sm mb-1">14. Financial Offer & Contract Module</div>
<div class="text-xs text-gray-600">Radial charts · Interactive pricing tables.</div>
</div>
</div>
</div>
<div class="mb-12">
<div class="pill pill-indian mb-3">PART V · TECHNICAL IMPLEMENTATION</div>
<h2 class="font-display text-2xl font-bold mb-4" style="color: var(--color-midnight-blue);">Front-End Roadmap</h2>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
<div class="info-card" data-popup data-title="15. CSS Architecture" data-content="Root Variable Setup: Defining :root with Client's exact scraped hex codes and font families. Semantic Class Naming: Using BEM (Block Element Modifier) methodology combined with Client's semantic type classes (e.g., .type-h3, .type-large-body-18). Salient Animation Emulation: Writing custom CSS @keyframes and IntersectionObserver JS scripts to replicate Salient's viewport-triggered entrances without heavy plugins.">
<div class="pill pill-midnight mb-2">15</div>
<h3 class="font-display font-bold text-base mb-1">CSS Architecture & Variable Mapping</h3>
<p class="text-sm text-gray-600">:root setup · BEM methodology · Animation emulation.</p>
</div>
<div class="info-card" data-popup data-title="16. Performance & Accessibility" data-content="Asset Optimization: Lazy-loading images, using WebP formats, and minifying CSS/JS to ensure sub-second load times. Contrast Ratios: Verifying that Indian Red (#d04a2f) on White, and White on Midnight Blue (#002060), pass WCAG AA standards. Keyboard Navigability: Ensuring all Salient-style modals and pop-ups can be opened, read, and closed using only the Tab and Esc keys.">
<div class="pill pill-indian mb-2">16</div>
<h3 class="font-display font-bold text-base mb-1">Performance & Accessibility (WCAG 2.1 AA)</h3>
<p class="text-sm text-gray-600">Lazy-load · Contrast verified · Keyboard nav.</p>
</div>
<div class="info-card" data-popup data-title="17. Responsiveness & Mobile" data-content="Grid Stacking: Converting complex multi-column Salient grids into single-column, high-impact vertical scrolls for mobile devices. Touch Targets: Ensuring all Indian Red CTA buttons and interactive info pop-ups meet the minimum 44x44px touch target requirement.">
<div class="pill pill-steel mb-2">17</div>
<h3 class="font-display font-bold text-base mb-1">Responsiveness & Mobile Adaptation</h3>
<p class="text-sm text-gray-600">Grid stacking · 44x44px touch targets.</p>
</div>
</div>
</div>
<div>
<div class="pill pill-steel mb-3">PART VI · NEXT STEPS</div>
<div class="info-card" data-popup data-title="18. Awaiting the Structural Draft Model" data-content="18.1 Ingesting the user's upcoming HTML/structural draft for information architecture. 18.2 Mapping the user's specific popup/animation references to the Salient-inspired CSS logic defined in Part IV. 18.3 Finalizing the code structure to begin actual HTML/CSS/JS generation. The current build represents the FINAL integration of all research, the WOW animation, and the UI Interface Simulation showcase — all merged into a single, production-ready HTML document.">
<div class="pill pill-midnight mb-2">18</div>
<h3 class="font-display font-bold text-base mb-1">Awaiting the Structural Draft Model</h3>
<p class="text-sm text-gray-600">Ingest draft · Map references · Finalize code structure.</p>
</div>
</div>
</section>
</main>
<footer class="border-t border-gray-200 mt-16 py-10" style="background: var(--color-white-smoke);">
<div class="max-w-7xl mx-auto px-4 md:px-6">
<div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
<div>
<div class="font-display font-bold text-lg mb-2" style="color: var(--color-midnight-blue);">AP-ID × Client</div>
<p class="text-sm text-gray-600">B2B UX Architecture Proposal. Prepared for Robert, Business Partner.</p>
</div>
<div>
<div class="font-display font-bold text-sm mb-2 uppercase tracking-wider">Contact</div>
<div class="text-sm text-gray-600 space-y-1">
<div>apvizual@gmail.com</div>
<div>+40 722 121 752 (WhatsApp)</div>
<div>linkedin.com/in/ap-id</div>
<div>ap-id.ro</div>
</div>
</div>
<div>
<div class="font-display font-bold text-sm mb-2 uppercase tracking-wider">Proposal</div>
<div class="text-sm text-gray-600 space-y-1">
<div>€3,130 gross / month</div>
<div>€20 / hour · 160h base</div>
<div>DDA Contract · 6-month trial</div>
<div>~€2,400 net take-home</div>
</div>
</div>
</div>
<div class="pt-6 border-t border-gray-300 text-xs text-gray-500 flex flex-wrap justify-between gap-2">
<div>© 2026 Alexandru Popescu · AP-ID. All evidence strictly sourced from provided documentation.</div>
<div>Built with Client brand tokens · Salient-inspired architecture</div>
</div>
</div>
</footer>
<div id="modal" class="modal-overlay" onclick="if(event.target===this)closeModal()">
<div class="modal-content">
<div class="modal-close" onclick="closeModal()">✕</div>
<div class="modal-header">
<h2 class="font-display text-xl md:text-2xl font-bold pr-10" id="modal-title" style="color: var(--color-midnight-blue);">Title</h2>
</div>
<div class="modal-body">
<p class="text-sm md:text-base leading-relaxed text-gray-700 whitespace-pre-line" id="modal-content">Content</p>
</div>
</div>
</div>
<script>
function switchTab(tabId) {
document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
document.getElementById(tabId).classList.add('active');
const link = document.querySelector(`.nav-link[data-target="${tabId}"]`);
if (link) {
link.classList.add('active');
link.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
}
window.scrollTo({ top: 0, behavior: 'smooth' });
}
function openModal(title, content) {
document.getElementById('modal-title').textContent = title;
document.getElementById('modal-content').textContent = content;
document.getElementById('modal').classList.add('active');
document.body.style.overflow = 'hidden';
}
function closeModal() {
document.getElementById('modal').classList.remove('active');
document.body.style.overflow = '';
}
document.querySelectorAll('[data-popup]').forEach(el => {
el.addEventListener('click', (e) => {
e.stopPropagation();
openModal(
el.getAttribute('data-title') || 'Details',
el.getAttribute('data-content') || 'No additional information.'
);
});
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
</script>
</body>
</html>

