<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
<title>The Bimodal Blueprint | Alexandru Popescu × the Company (MASTER EDITION)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        fontFamily: { sans: ['Inter','sans-serif'], display: ['Space Grotesk','sans-serif'], mono: ['JetBrains Mono','monospace'] },
        colors: {
          bg: '#050507', surface: '#0F1016', border: '#1E2029', accent: '#6D5DD3', accentGlow: '#8B7CF7',
          human: '#FF6B6B', ai: '#4DABF7', gold: '#FCC419', emerald: '#10B981', client: '#F97316', clientGlow: '#FB923C',
          textMain: '#E2E8F0', textMuted: '#94A3B8'
        },
        backgroundImage: { 'grid-pattern': "linear-gradient(to right, #1E2029 1px, transparent 1px), linear-gradient(to bottom, #1E2029 1px, transparent 1px)" }
      }
    }
  }
</script>
<style>
  body { background-color: #050507; color: #E2E8F0; overflow-x: hidden; }
  h1,h2,h3,h4,.font-display { font-family: 'Space Grotesk', sans-serif; }
  .glass-panel { background: rgba(15,16,22,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
  .glass-card { background: rgba(30,32,41,0.4); border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s ease; }
  .glass-card:hover { background: rgba(30,32,41,0.7); border-color: rgba(109,93,211,0.3); transform: translateY(-2px); }
  .gradient-text { background: linear-gradient(135deg, #FF6B6B 0%, #FFFFFF 50%, #4DABF7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .client-gradient { background: linear-gradient(135deg, #F97316 0%, #FCC419 50%, #F97316 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .nav-link { position: relative; opacity: 0.6; transition: all 0.3s; cursor: pointer; padding-bottom: 4px; white-space: nowrap; }
  .nav-link:hover, .nav-link.active { opacity: 1; color: white; }
  .nav-link.active::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, #FF6B6B, #4DABF7); box-shadow: 0 0 10px rgba(109,93,211,0.5); }
  .nav-link.client-active::after { background: linear-gradient(90deg, #F97316, #FCC419); box-shadow: 0 0 10px rgba(249,115,22,0.5); }
  .tab-content { display: none; animation: fadeIn 0.5s ease-out; }
  .tab-content.active { display: block; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #050507; }
  ::-webkit-scrollbar-thumb { background: #1E2029; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #6D5DD3; }
  .progress-bar { height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 3px; animation: fillProgress 1.5s ease-out; }
  @keyframes fillProgress { from { width: 0%; } }
  .sparkline { display: flex; align-items: flex-end; gap: 2px; height: 32px; }
  .sparkline-bar { flex: 1; background: linear-gradient(180deg, #6D5DD3, #4DABF7); border-radius: 2px 2px 0 0; transition: all 0.3s; }
  .sparkline-bar:hover { background: linear-gradient(180deg, #FF6B6B, #FCC419); transform: scaleY(1.1); }
  .pill { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
  .pill-human { background: rgba(255,107,107,0.1); color: #FF6B6B; border: 1px solid rgba(255,107,107,0.3); }
  .pill-ai { background: rgba(77,171,247,0.1); color: #4DABF7; border: 1px solid rgba(77,171,247,0.3); }
  .pill-accent { background: rgba(109,93,211,0.1); color: #8B7CF7; border: 1px solid rgba(109,93,211,0.3); }
  .pill-gold { background: rgba(252,196,25,0.1); color: #FCC419; border: 1px solid rgba(252,196,25,0.3); }
  .pill-emerald { background: rgba(16,185,129,0.1); color: #10B981; border: 1px solid rgba(16,185,129,0.3); }
  .pill-client { background: rgba(249,115,22,0.1); color: #FB923C; border: 1px solid rgba(249,115,22,0.3); }
  @keyframes pulse-glow { 0%,100% { box-shadow: 0 0 20px rgba(109,93,211,0.3); } 50% { box-shadow: 0 0 40px rgba(109,93,211,0.6); } }
  .pulse-glow { animation: pulse-glow 3s infinite; }
  .pulse-glow-client { animation: pulse-glow-client 3s infinite; }
  @keyframes pulse-glow-client { 0%,100% { box-shadow: 0 0 20px rgba(249,115,22,0.3); } 50% { box-shadow: 0 0 40px rgba(249,115,22,0.6); } }
  .section-divider { display: flex; align-items: center; gap: 1rem; margin: 3rem 0 2rem; }
  .section-divider::before, .section-divider::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, transparent, #1E2029, transparent); }
  .timeline-line { position: absolute; left: 15px; top: 0; bottom: 0; width: 2px; background: linear-gradient(180deg, #6D5DD3, #4DABF7, #10B981); }
  .timeline-dot { position: absolute; left: 8px; top: 4px; width: 16px; height: 16px; border-radius: 50%; border: 2px solid #050507; z-index: 10; }
  [data-popup] { position: relative; cursor: pointer; transition: all 0.2s; }
  [data-popup]:hover { outline: 1px dashed rgba(109,93,211,0.5); outline-offset: 4px; }
  [data-popup]::after { content: 'ⓘ'; position: absolute; top: 6px; right: 6px; width: 18px; height: 18px; background: rgba(109,93,211,0.2); border: 1px solid rgba(109,93,211,0.4); color: #8B7CF7; border-radius: 50%; font-size: 10px; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; font-family: serif; }
  [data-popup]:hover::after { opacity: 1; }
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 100; display: none; align-items: center; justify-content: center; padding: 1rem; animation: modalFade 0.3s ease; }
  .modal-overlay.active { display: flex; }
  @keyframes modalFade { from { opacity: 0; } to { opacity: 1; } }
  .modal-content { background: #0F1016; border: 1px solid rgba(109,93,211,0.3); border-radius: 16px; max-width: 800px; width: 100%; max-height: 85vh; overflow-y: auto; position: relative; box-shadow: 0 0 60px rgba(109,93,211,0.3); }
  .modal-close { position: sticky; top: 12px; float: right; margin: 12px 12px 0 0; width: 32px; height: 32px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 10; color: #94A3B8; transition: all 0.2s; }
  .modal-close:hover { background: rgba(255,107,107,0.2); color: #FF6B6B; border-color: #FF6B6B; }
  .modal-header { padding: 2rem 2rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
  .modal-body { padding: 1.5rem 2rem 2rem; }
  .depth-tag { display: inline-block; padding: 0.125rem 0.5rem; background: rgba(109,93,211,0.15); border: 1px solid rgba(109,93,211,0.3); border-radius: 4px; font-size: 10px; font-family: 'JetBrains Mono', monospace; color: #8B7CF7; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem; }
  .metric-ring { position: relative; width: 120px; height: 120px; }
  .metric-ring svg { transform: rotate(-90deg); }
  .metric-ring circle { fill: none; stroke-width: 8; }
  .metric-ring .ring-bg { stroke: #1E2029; }
  .metric-ring .ring-fill { stroke-dasharray: 314; stroke-linecap: round; animation: ringFill 2s ease-out forwards; }
  @keyframes ringFill { from { stroke-dashoffset: 314; } }
  .nav-scroll { overflow-x: auto; scrollbar-width: none; }
  .nav-scroll::-webkit-scrollbar { display: none; }
  .company-wordmark { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 2rem; letter-spacing: -0.02em; }
  .company-gradient { background: linear-gradient(135deg, #C87B5E 0%, #E8DCC4 50%, #87A878 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .velocity-bar { height: 28px; border-radius: 6px; background: linear-gradient(90deg, #F97316, #FCC419); display: flex; align-items: center; justify-content: flex-end; padding-right: 12px; font-weight: 700; font-size: 12px; color: #0F1016; transition: width 1.5s ease-out; position: relative; overflow: hidden; }
  .velocity-bar::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); animation: shimmer 2s infinite; }
  @keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
  .critique-card { background: linear-gradient(135deg, rgba(249,115,22,0.05), rgba(252,196,25,0.02)); border: 1px solid rgba(249,115,22,0.2); border-radius: 12px; padding: 1.5rem; transition: all 0.3s; }
  .critique-card:hover { border-color: rgba(249,115,22,0.5); transform: translateY(-2px); }
  .hook-card { background: rgba(30,32,41,0.4); border-left: 3px solid #F97316; padding: 1rem 1.25rem; border-radius: 8px; transition: all 0.3s; }
  .hook-card:hover { background: rgba(30,32,41,0.7); transform: translateX(4px); }
  .heatmap-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 4px; }
  .heatmap-cell { aspect-ratio: 1; border-radius: 4px; transition: all 0.3s; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; color: rgba(255,255,255,0.8); }
  .heatmap-cell:hover { transform: scale(1.1); z-index: 10; }
  .venn-circle { position: absolute; width: 200px; height: 200px; border-radius: 50%; mix-blend-mode: screen; opacity: 0.8; transition: all 0.3s ease; }
  .venn-circle:hover { opacity: 1; transform: scale(1.05); }
  .flow-node { position: relative; padding: 1.5rem; border-radius: 1rem; background: rgba(15,16,22,0.8); border: 1px solid rgba(255,255,255,0.05); }
  .cert-badge { position: relative; padding: 1rem; border-radius: 0.75rem; background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(77,171,247,0.1)); border: 1px solid rgba(16,185,129,0.3); transition: all 0.3s; }
  .cert-badge:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(16,185,129,0.2); }
  .radar-container { position: relative; width: 100%; max-width: 400px; aspect-ratio: 1; margin: 0 auto; }
  .grid-bg { background-image: linear-gradient(to right, #1E2029 1px, transparent 1px), linear-gradient(to bottom, #1E2029 1px, transparent 1px); background-size: 40px 40px; }

  /* subtle hover animation for nav items */
  .nav-link {
    transition: opacity 0.2s, transform 0.2s;
  }
  .nav-link:hover {
    transform: translateY(-1px);
  }
</style>
</head>
<body class="antialiased selection:bg-accent selection:text-white">

<div class="fixed inset-0 z-0 opacity-20 pointer-events-none bg-grid-pattern bg-[size:40px_40px]"></div>

<nav class="fixed top-0 w-full z-50 glass-panel border-b border-border/50">
  <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between gap-3">
    <!-- Logo / Brand -->
    <div class="font-display font-bold text-xl tracking-tight cursor-pointer flex items-center gap-2 shrink-0" onclick="switchTab('thesis')">
      <svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      AP-ID <span class="text-accent">.</span> SYSTEMS
    </div>

    <!-- Navigation Links (condensed, clear labels) -->
    <div class="nav-scroll flex space-x-3 lg:space-x-5 text-sm font-medium">
      <div class="nav-link active" onclick="switchTab('thesis')" data-target="thesis">Thesis</div>
      <div class="nav-link" onclick="switchTab('workflow')" data-target="workflow">Workflow</div>
      <div class="nav-link" onclick="switchTab('evidence')" data-target="evidence">Evidence</div>
      <div class="nav-link" onclick="switchTab('roadmap')" data-target="roadmap">Roadmap</div>
      <div class="nav-link" onclick="switchTab('operator')" data-target="operator">Operator</div>
      <div class="nav-link" onclick="switchTab('hr')" data-target="hr">HR</div>
      <div class="nav-link" onclick="switchTab('ai-partner')" data-target="ai-partner">AI Partner</div>
      <div class="nav-link" onclick="switchTab('for-client')" data-target="for-client">For Client</div>
      <div class="nav-link" onclick="switchTab('simulation')" data-target="simulation">Simulation</div>
    </div>

    <!-- Contact: plain mailto link (works with any email client) -->
    <a href="mailto:apvizual@gmail.com" class="w-8 h-8 flex items-center justify-center rounded-full bg-accent/10 hover:bg-accent/20 border border-accent/30 text-accent transition-all shrink-0 group" title="Email me (apvizual@gmail.com)">
      <svg class="w-4 h-4 group-hover:scale-105 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
    </a>
  </div>
</nav>

<main class="relative z-10 pt-24 pb-20 px-6 max-w-7xl mx-auto min-h-screen">

<!-- ==================== TAB 1: THESIS (ENHANCED – fixed vertical spacing, no overlapping, better rhythm) ==================== -->
<section id="thesis" class="tab-content active"> 

  <!-- HERO (clean, no broken dots) -->
  <div class="relative min-h-[60vh] flex flex-col justify-center">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-accent/30 bg-accent/5 text-accent text-xs font-mono mb-10 w-fit" data-popup data-title="Strategic Context" data-depth="TIER 1 · INFO" data-content="the Company is a 40+ person team scaling toward $70M in revenue. the Client is Co-Founder & CMO, previously Head of Marketing, focused on Creator-Led Growth and UGC at scale. He posts about moving from 'polished but sterile' ads to authentic, high-converting creative that still feels premium.">
      <span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
      PREPARED FOR The Client // The Company CMO
    </div>
    <h1 class="font-display text-6xl md:text-8xl font-bold leading-[1.1] mb-10">
      BEYOND <br>
      <span class="gradient-text">PIXELS.</span>
    </h1>
    <p class="text-xl md:text-2xl text-textMuted max-w-3xl leading-relaxed mb-16">
      Architecting the Company's Creative Future with a <span class="text-human font-semibold">Human-Centric</span> & <span class="text-ai font-semibold">AI-Augmented</span> Framework for any targheted Industry.
    </p>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div class="glass-panel p-6 rounded-lg border-l-2 border-human cursor-pointer" data-popup data-title="Mode A: Strategic Direction" data-depth="CORE THESIS" data-content="Fuses formal Economics training with MBTI/16 Personalities tracking (since 2017) and NGO-derived empathy. This enables design decisions based on cognitive archetypes and behavioral economics rather than subjective aesthetics.">
        <h3 class="font-display text-lg font-bold mb-2 text-white">Mode A: Strategy</h3>
        <p class="text-sm text-textMuted leading-relaxed">Psychological Insight + Behavioral Economics. The Soul.</p>
      </div>
      <div class="glass-panel p-6 rounded-lg border-l-2 border-ai cursor-pointer" data-popup data-title="Mode B: Actionable Execution" data-depth="CORE THESIS" data-content="Powered by a private, local LLM 'Digital Twin' that automates high-volume production (resizing, variation generation, compliance checks). Unlike public AI tools, this architecture ensures 100% data privacy and IP security.">
        <h3 class="font-display text-lg font-bold mb-2 text-white">Mode B: Velocity</h3>
        <p class="text-sm text-textMuted leading-relaxed">Local LLM Infrastructure + Automated Execution. The Scale.</p>
      </div>
      <div class="glass-panel p-6 rounded-lg border-l-2 border-accent cursor-pointer" data-popup data-title="The Goal: $70M Scale" data-depth="STRATEGIC TARGET" data-content="Scaling to $70M requires dramatic increase in creative velocity across Meta, TikTok, Amazon, and retail POS. The candidate directly addresses this bottleneck with enterprise-grade design systems + AI-powered automation.">
        <h3 class="font-display text-lg font-bold mb-2 text-white">The Goal</h3>
        <p class="text-sm text-textMuted leading-relaxed">Scaling to $70M without losing brand integrity or soul.</p>
      </div>
    </div>
  </div>

  <!-- ==================== HERO VISUALIZATION (New Central Element) ==================== -->
<div class="thesis-visualization mb-16">
  <div class="relative glass-panel rounded-3xl overflow-hidden border border-accent/30 shadow-2xl">
    <!-- Background animated gradients -->
    <div class="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-ai/5"></div>
    <div class="absolute top-0 left-0 w-96 h-96 bg-human/20 rounded-full blur-3xl -ml-48 -mt-48 animate-pulse-glow"></div>
    <div class="absolute bottom-0 right-0 w-80 h-80 bg-ai/20 rounded-full blur-3xl -mr-40 -mb-40 animate-pulse-glow animation-delay-2000"></div>

    <div class="relative z-10 p-8 md:p-12">
      <!-- Badge -->
      <div class="inline-flex items-center gap-2 bg-accent/10 backdrop-blur-sm px-4 py-2 rounded-full text-accent text-xs font-bold uppercase tracking-wider mb-8 border border-accent/20">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
        </span>
        The Core Thesis
      </div>

      <!-- Headline -->
      <h1 class="font-display text-4xl md:text-6xl lg:text-7xl font-bold leading-tight tracking-tight mb-6 bg-gradient-to-r from-white via-white to-accent/70 bg-clip-text text-transparent">
        Symbiotic Intelligence:<br>
        <span class="text-accent">Human + Machine</span>
      </h1>

      <!-- Subheadline -->
      <p class="text-textMuted text-lg md:text-xl max-w-3xl mb-12 leading-relaxed">
        Not AI replacing humans. Not humans using AI as a tool.<br>
        A true symbiosis where each amplifies the other.
      </p>

      <!-- Central Visualization Container -->
      <div class="visualization-container w-full max-w-5xl mx-auto my-8 md:my-12 relative">
        <div class="relative aspect-[16/9] w-full bg-gradient-to-br from-gray-900/50 to-gray-950/90 rounded-2xl border border-white/10 backdrop-blur-sm overflow-hidden group">
          <svg viewBox="0 0 1000 562" class="w-full h-full" style="outline: none;">
            <defs>
              <linearGradient id="humanGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#FF6B6B;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#FF9F4A;stop-opacity:1" />
              </linearGradient>
              <linearGradient id="aiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#4DABF7;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#6C5CE7;stop-opacity:1" />
              </linearGradient>
              <filter id="glowHuman" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="10" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
              <filter id="glowAi" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="10" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
              <filter id="glowCenter" x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="14" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>

            <style>
              @keyframes pulseHuman {
                0%, 100% { filter: url(#glowHuman); opacity: 1; }
                50% { filter: none; opacity: 0.6; }
              }
              @keyframes pulseAi {
                0%, 100% { filter: none; opacity: 0.6; }
                50% { filter: url(#glowAi); opacity: 1; }
              }
              .human-pulse { animation: pulseHuman 4s ease-in-out infinite; }
              .ai-pulse { animation: pulseAi 4s ease-in-out infinite; }
              .center-glow { animation: pulseHuman 6s ease-in-out infinite; filter: url(#glowCenter); }
              .cursor-pointer { cursor: pointer; }
              /* Remove all hover/focus selection outlines */
              .cursor-pointer:focus, .cursor-pointer:active, .cursor-pointer:hover,
              .central-core:focus, .central-core:active, .central-core:hover,
              .human-node:focus, .human-node:active, .human-node:hover,
              .ai-node:focus, .ai-node:active, .ai-node:hover,
              .pipeline-node:focus, .pipeline-node:active, .pipeline-node:hover {
                outline: none !important;
                box-shadow: none !important;
                -webkit-tap-highlight-color: transparent !important;
              }
              * {
                -webkit-tap-highlight-color: transparent;
              }
            </style>

            <!-- Floating particles -->
            <g class="data-particles">
              <circle cx="100" cy="100" r="3" fill="#FF6B6B" opacity="0.5"><animate attributeName="cy" values="100;130;100" dur="5s" repeatCount="indefinite" /></circle>
              <circle cx="900" cy="450" r="2.5" fill="#4DABF7" opacity="0.5"><animate attributeName="cy" values="450;420;450" dur="4s" repeatCount="indefinite" /></circle>
              <circle cx="800" cy="120" r="2" fill="#6C5CE7" opacity="0.4"><animate attributeName="cx" values="800;820;800" dur="6s" repeatCount="indefinite" /></circle>
              <circle cx="200" cy="480" r="2.5" fill="#FF9F4A" opacity="0.5"><animate attributeName="cy" values="480;450;480" dur="4.5s" repeatCount="indefinite" /></circle>
              <circle cx="350" cy="80" r="2" fill="#4DABF7" opacity="0.6"><animate attributeName="cx" values="350;370;350" dur="3.5s" repeatCount="indefinite" /></circle>
              <circle cx="650" cy="500" r="3" fill="#FF6B6B" opacity="0.4"><animate attributeName="cy" values="500;470;500" dur="5.5s" repeatCount="indefinite" /></circle>
            </g>

            <!-- ENLARGED CENTRAL GLOWING CORE (thesis) with centered text closer together -->
            <g class="central-core cursor-pointer" data-popup data-title="Symbiotic Thesis" data-depth="CORE IDEA" data-content="The central thesis: Human strategic intelligence (creativity, empathy, economics) and artificial intelligence (speed, scale, pattern recognition) do not compete – they form a symbiotic loop. One sets direction, the other executes. Neither is complete without the other.">
              <!-- Outer ring enlarged -->
              <circle cx="500" cy="281" r="95" fill="#6C5CE7" fill-opacity="0.1" stroke="#6C5CE7" stroke-width="2" stroke-dasharray="10 10">
                <animateTransform attributeName="transform" type="rotate" from="0 500 281" to="360 500 281" dur="30s" repeatCount="indefinite" />
              </circle>
              <!-- Middle glow enlarged -->
              <circle cx="500" cy="281" r="70" fill="#6C5CE7" fill-opacity="0.3" class="center-glow" />
              <!-- Solid center enlarged -->
              <circle cx="500" cy="281" r="60" fill="#6C5CE7" fill-opacity="0.8" />
              <!-- Centered text block – closer together, vertically centered at 281 -->
              <text x="500" y="274" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="16" dominant-baseline="middle">SYMBIOSIS</text>
              <text x="500" y="290" text-anchor="middle" fill="#E0DDFF" font-family="'Space Grotesk', sans-serif" font-size="11" dominant-baseline="middle">≠ tool</text>
            </g>

            <!-- Left: Human attributes – perfectly centered -->
            <g class="human-node cursor-pointer" data-popup data-title="Human Intelligence" data-depth="STRATEGIC CORE" data-content="Creativity · Empathy · Economic intuition · MBTI cognitive mapping · Ethical framing · Taste · Cultural context – the 'why' behind every decision.">
              <circle cx="280" cy="281" r="65" fill="url(#humanGrad)" class="human-pulse" stroke="#FFCCCC" stroke-width="1.5" />
              <text x="280" y="252" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="26" dominant-baseline="middle">🧠</text>
              <text x="280" y="280" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="13" dominant-baseline="middle">Human</text>
              <text x="280" y="298" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-size="9" dominant-baseline="middle">Strategy</text>
              <text x="280" y="310" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-size="9" dominant-baseline="middle">· Psychology ·</text>
            </g>

            <!-- Right: AI attributes – perfectly centered -->
            <g class="ai-node cursor-pointer" data-popup data-title="Artificial Intelligence" data-depth="EXECUTION ENGINE" data-content="Automation · Scale · Pattern recognition · 50+ assets/week · WCAG compliance · Infinite context memory · Local LLM – the 'how' that multiplies human intent.">
              <circle cx="720" cy="281" r="65" fill="url(#aiGrad)" class="ai-pulse" stroke="#CCE4FF" stroke-width="1.5" />
              <text x="720" y="252" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="26" dominant-baseline="middle">⚙️</text>
              <text x="720" y="280" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="13" dominant-baseline="middle">Machine</text>
              <text x="720" y="298" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-size="9" dominant-baseline="middle">Execution</text>
              <text x="720" y="310" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-size="9" dominant-baseline="middle">· Automation ·</text>
            </g>

            <!-- Animated energy flows – no arrowheads -->
            <path d="M 345 281 C 420 230, 580 230, 655 281" fill="none" stroke="#FF9F4A" stroke-width="3" stroke-dasharray="12 20" opacity="0.8">
              <animate attributeName="stroke-dashoffset" values="0;200" dur="3s" repeatCount="indefinite" />
            </path>
            <path d="M 345 281 C 420 332, 580 332, 655 281" fill="none" stroke="#6C5CE7" stroke-width="3" stroke-dasharray="12 20" opacity="0.8">
              <animate attributeName="stroke-dashoffset" values="0;200" dur="3.5s" repeatCount="indefinite" />
            </path>

            <!-- ROTATING ORBITAL POINTS – all icons stay upright, no hover outlines -->
            <!-- Top: Creativity (✨) -->
            <g>
              <animateTransform attributeName="transform" type="rotate" from="0 500 281" to="360 500 281" dur="20s" repeatCount="indefinite" />
              <g transform="translate(500, 140)">
                <circle cx="0" cy="0" r="28" fill="#1a1a2e" stroke="#FF9F4A" stroke-width="2" class="cursor-pointer" data-popup data-title="Creativity" data-depth="HUMAN EDGE" data-content="Human creativity is not about generating variations – it's about knowing which variation matters. Taste, cultural fluency, and emotional resonance cannot be automated." style="outline: none;" />
                <g>
                  <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="20s" repeatCount="indefinite" />
                  <text x="0" y="2" text-anchor="middle" fill="#FF9F4A" font-size="20" dominant-baseline="middle" style="outline: none;">✨</text>
                </g>
              </g>
            </g>

            <!-- Bottom right: Velocity (⚡) -->
            <g>
              <animateTransform attributeName="transform" type="rotate" from="360 500 281" to="0 500 281" dur="25s" repeatCount="indefinite" />
              <g transform="translate(700, 400)">
                <circle cx="0" cy="0" r="28" fill="#1a1a2e" stroke="#4DABF7" stroke-width="2" class="cursor-pointer" data-popup data-title="Velocity" data-depth="MACHINE ADVANTAGE" data-content="From 5‑8 variations/week to 50+ – machine speed multiplies human output without sacrificing strategic fidelity." style="outline: none;" />
                <g>
                  <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="25s" repeatCount="indefinite" />
                  <text x="0" y="2" text-anchor="middle" fill="#4DABF7" font-size="20" dominant-baseline="middle" style="outline: none;">⚡</text>
                </g>
              </g>
            </g>

            <!-- Bottom left: Ethics (🛡️) -->
            <g>
              <animateTransform attributeName="transform" type="rotate" from="0 500 281" to="-360 500 281" dur="22s" repeatCount="indefinite" />
              <g transform="translate(300, 400)">
                <circle cx="0" cy="0" r="28" fill="#1a1a2e" stroke="#FF6B6B" stroke-width="2" class="cursor-pointer" data-popup data-title="Ethical Guardrails" data-depth="HUMAN OVERSIGHT" data-content="R0 logical gating ensures no 'AI slop' passes. The human sets the guardrails; the machine executes within them." style="outline: none;" />
                <g>
                  <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="22s" repeatCount="indefinite" />
                  <text x="0" y="2" text-anchor="middle" fill="#FF6B6B" font-size="20" dominant-baseline="middle" style="outline: none;">🛡️</text>
                </g>
              </g>
            </g>

            <!-- Animated dotted background rings -->
            <circle cx="500" cy="281" r="110" fill="none" stroke="#6C5CE7" stroke-width="1.5" stroke-dasharray="8 12" opacity="0.4">
              <animateTransform attributeName="transform" type="rotate" from="0 500 281" to="360 500 281" dur="15s" repeatCount="indefinite" />
            </circle>
            <circle cx="500" cy="281" r="140" fill="none" stroke="#A084FF" stroke-width="1" stroke-dasharray="4 16" opacity="0.3">
              <animateTransform attributeName="transform" type="rotate" from="360 500 281" to="0 500 281" dur="18s" repeatCount="indefinite" />
            </circle>
          </svg>

          <!-- Click instruction -->
          <div class="absolute top-4 left-4 text-[10px] text-textMuted bg-black/40 backdrop-blur-sm rounded-md px-2 py-1" style="outline: none;">
            ▼ Click any element for insights
          </div>
        </div>

        <!-- Legend (unchanged) -->
        <div class="flex flex-wrap justify-center gap-4 mt-4 text-[10px] text-white">
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="w-2 h-2 rounded-full bg-human"></span><span>Human Intelligence</span>
          </div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="w-2 h-2 rounded-full bg-ai"></span><span>Machine Intelligence</span>
          </div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="w-2 h-2 rounded-full bg-accent"></span><span>Symbiotic Loop</span>
          </div>
          <div class="w-px h-4 bg-white/20 mx-1"></div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span>✨</span><span>Creativity</span>
          </div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span>⚡</span><span>10x Velocity</span>
          </div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span>🛡️</span><span>Ethical Guardrails</span>
          </div>
        </div>

        <div class="text-center mt-4">
          <p class="text-xs text-textMuted uppercase tracking-wider">Symbiotic Intelligence · Not Replacement, But Amplification</p>
        </div>
      </div>

      <!-- Key Thesis Statements -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 pt-8 border-t border-white/10">
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent mb-1">≠</div><div class="text-[11px] text-textMuted uppercase tracking-wider">Not a Tool</div><div class="text-[10px] text-textMuted mt-1">A true symbiosis</div></div>
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent mb-1">⇄</div><div class="text-[11px] text-textMuted uppercase tracking-wider">Continuous Loop</div><div class="text-[10px] text-textMuted mt-1">Human → Machine → Human</div></div>
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent mb-1">∞</div><div class="text-[11px] text-textMuted uppercase tracking-wider">Amplified Intelligence</div><div class="text-[10px] text-textMuted mt-1">1+1 = 11</div></div>
      </div>
    </div>
  </div>
</div>

  <!-- FOUR PILLARS (fixed spacing, cards evenly spaced) -->
  <div class="section-divider my-16"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">The Four Pillars</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
    <div class="glass-card p-6 rounded-xl flex flex-col cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="Pillar I: Proven DTC & Corporate Execution and Corporate responsiveness and adaptability" data-depth="VERIFIED PROOF" data-content="Led 50+ online campaigns for Ninja, AIPER, PURE Electric; Processed 25,000+ visuals for MADE.com; Direct experience with   brands Crock-Pot and Shark. Results: 20% sales acceleration, 25% engagement lift.">
      <div class="w-10 h-10 rounded-lg bg-human/10 flex items-center justify-center mb-5"><svg class="w-5 h-5 text-human" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg></div>
      <h4 class="font-display font-bold mb-2">DTC & Corporate Execution and Corporate responsability and Corporate responsability</h4>
      <p class="text-xs text-textMuted mb-5 leading-relaxed">Ninja, Crock-Pot, Shark, AIPER</p>
      <div class="sparkline mt-auto mb-3"><div class="sparkline-bar" style="height:40%"></div><div class="sparkline-bar" style="height:60%"></div><div class="sparkline-bar" style="height:75%"></div><div class="sparkline-bar" style="height:50%"></div><div class="sparkline-bar" style="height:90%"></div><div class="sparkline-bar" style="height:80%"></div><div class="sparkline-bar" style="height:100%"></div></div>
      <div class="text-xs text-human font-mono mt-2">50+ Campaigns</div>
    </div>
    <div class="glass-card p-6 rounded-xl flex flex-col cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="Pillar II: Enterprise-Grade Systems" data-depth="VERIFIED PROOF" data-content="Built design systems at Yokogawa (200+ templates, 12 countries) and Microsoft PCoE; Holds WCAG accessibility certifications (8 Microsoft certs Feb 2025). Prevents brand drift at scale.">
      <div class="w-10 h-10 rounded-lg bg-ai/10 flex items-center justify-center mb-5"><svg class="w-5 h-5 text-ai" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg></div>
      <h4 class="font-display font-bold mb-2">Enterprise Systems</h4>
      <p class="text-xs text-textMuted mb-5 leading-relaxed">Yokogawa, Microsoft PCoE</p>
      <div class="sparkline mt-auto mb-3"><div class="sparkline-bar" style="height:60%"></div><div class="sparkline-bar" style="height:70%"></div><div class="sparkline-bar" style="height:85%"></div><div class="sparkline-bar" style="height:75%"></div><div class="sparkline-bar" style="height:95%"></div><div class="sparkline-bar" style="height:100%"></div><div class="sparkline-bar" style="height:90%"></div></div>
      <div class="text-xs text-ai font-mono mt-2">200+ Templates</div>
    </div>
    <div class="glass-card p-6 rounded-xl flex flex-col cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="Pillar III: AI-Augmented Workflows" data-depth="DIFFERENTIATOR" data-content="Developing a private local LLM 'digital twin' to automate high-volume production tasks. Air‑gapped, 100% IP security. 50+ variations/week, 10x velocity, zero brand drift. R0 gating ensures strategic precision.">
      <div class="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-5"><svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg></div>
      <h4 class="font-display font-bold mb-2">AI-Augmented</h4>
      <p class="text-xs text-textMuted mb-5 leading-relaxed">Private Local LLM Digital Twin</p>
      <div class="sparkline mt-auto mb-3"><div class="sparkline-bar" style="height:30%"></div><div class="sparkline-bar" style="height:50%"></div><div class="sparkline-bar" style="height:65%"></div><div class="sparkline-bar" style="height:80%"></div><div class="sparkline-bar" style="height:90%"></div><div class="sparkline-bar" style="height:95%"></div><div class="sparkline-bar" style="height:100%"></div></div>
      <div class="text-xs text-accent font-mono mt-2">Bimodal OS</div>
    </div>
    <div class="glass-card p-6 rounded-xl flex flex-col cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="Pillar IV: Psychological Insight" data-depth="UNIQUE ANGLE" data-content="Background in Economics; Tracking MBTI evolution since 2017; Lesson from NGO experience: 'you cannot fire a volunteer'. Designs for cognitive archetypes, not just demographics. Builds long‑term brand equity.">
      <div class="w-10 h-10 rounded-lg bg-gold/10 flex items-center justify-center mb-5"><svg class="w-5 h-5 text-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg></div>
      <h4 class="font-display font-bold mb-2">Psychological Insight</h4>
      <p class="text-xs text-textMuted mb-5 leading-relaxed">Economics + MBTI + NGO</p>
      <div class="sparkline mt-auto mb-3"><div class="sparkline-bar" style="height:55%"></div><div class="sparkline-bar" style="height:70%"></div><div class="sparkline-bar" style="height:80%"></div><div class="sparkline-bar" style="height:85%"></div><div class="sparkline-bar" style="height:92%"></div><div class="sparkline-bar" style="height:98%"></div><div class="sparkline-bar" style="height:100%"></div></div>
      <div class="text-xs text-gold font-mono mt-2">Cognitive Archetypes</div>
    </div>
  </div>

  <!-- CORE DIFFERENTIATORS (clean spacing) -->
  <div class="glass-panel p-8 rounded-2xl bg-gradient-to-br from-accent/5 to-transparent border border-accent/20 mt-8 mb-20">
    <h3 class="font-display text-2xl font-bold mb-8 text-center">Why This Collaboration Is Different</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
      <div class="text-center p-4 cursor-pointer" data-popup data-title="Infrastructure, Not Just Output" data-depth="DIFFERENTIATOR" data-content="Most designers deliver assets. I deliver a proprietary creative engine – transferable IP, executable templates, local LLM infrastructure. You own the engine, not just the fuel.">
        <div class="w-20 h-20 mx-auto rounded-full bg-accent/10 flex items-center justify-center text-4xl mb-4">🏭</div>
        <div class="font-bold text-white text-base mb-2">Infrastructure</div>
        <div class="text-xs text-textMuted">You own the engine</div>
      </div>
      <div class="text-center p-4 cursor-pointer" data-popup data-title="Psychology + Economics" data-depth="DIFFERENTIATOR" data-content="I don't guess what looks good. I design based on behavioral economics, MBTI cognitive frameworks, and 15+ years of DTC & Corporate data. Every asset is engineered to convert.">
        <div class="w-20 h-20 mx-auto rounded-full bg-human/10 flex items-center justify-center text-4xl mb-4">🧠</div>
        <div class="font-bold text-white text-base mb-2">Psychology + Data</div>
        <div class="text-xs text-textMuted">Engineered for conversion</div>
      </div>
      <div class="text-center p-4 cursor-pointer" data-popup data-title="Radical Transparency" data-depth="DIFFERENTIATOR" data-content="I share raw simulation transcripts, AI reasoning logs, and full documentation. No black boxes. What you see is what you get – a genuine human‑AI symbiosis.">
        <div class="w-20 h-20 mx-auto rounded-full bg-ai/10 flex items-center justify-center text-4xl mb-4">📡</div>
        <div class="font-bold text-white text-base mb-2">Radical Transparency</div>
        <div class="text-xs text-textMuted">No black boxes</div>
      </div>
    </div>
  </div>

  <!-- The Company BUSINESS CONTEXT (better spacing) -->
  <div class="section-divider my-16"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">the Company Business Context</span></div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
    <div class="glass-panel p-6 rounded-xl border-t-2 border-gold cursor-pointer transition-all hover:shadow-[0_0_20px_rgba(252,196,25,0.1)]" data-popup data-title="$70M Scaling Target" data-depth="TIER 1 · INFO" data-content="Per the JD shared by Client: 'We're a 40+ person team scaling toward $70M in revenue, looking for a senior designer who can own visual output across every channel.' Channels specified: Meta, AppLovin, TikTok, Google, Amazon, retail expansion. Creative bottleneck = velocity without brand drift.">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg bg-gold/10 flex items-center justify-center text-gold text-2xl">🎯</div><h3 class="font-display text-lg font-bold text-gold">$70M Scaling Target</h3></div>
      <p class="text-sm text-textMuted leading-relaxed">Transitioning from startup to enterprise requires systems that prevent brand drift while multiplying output velocity.</p>
    </div>
    <div class="glass-panel p-6 rounded-xl border-t-2 border-emerald cursor-pointer transition-all hover:shadow-[0_0_20px_rgba(16,185,129,0.1)]" data-popup data-title="Gamified Nutrition" data-depth="LIVE INTEL" data-content="Product-Market Fit: the Company is in the 'Gamified Nutrition / EdTech for Kids' space. Core product: physical plates with interactive app integration. Hybrid physical-digital play means creative must bridge tangible product photography and digital app UI/UX storytelling.">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg bg-emerald/10 flex items-center justify-center text-emerald text-2xl">🎮</div><h3 class="font-display text-lg font-bold text-emerald">Gamified Nutrition</h3></div>
      <p class="text-sm text-textMuted leading-relaxed">Hybrid physical-digital play. Creative must bridge tangible product photography with behavioral psychology and app UI storytelling.</p>
    </div>
    <div class="glass-panel p-6 rounded-xl border-t-2 border-ai cursor-pointer transition-all hover:shadow-[0_0_20px_rgba(77,171,247,0.1)]" data-popup data-title="Multi-Channel Velocity" data-depth="JD REQUIREMENT" data-content="Simultaneous campaigns on Meta, TikTok, Amazon, and retail POS demand high-volume asset generation without losing the premium feel. JD states: 'This isn't a make it pretty role. You'll own the creative that sells, and you need the instinct to understand why certain visuals convert.'">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg bg-ai/10 flex items-center justify-center text-ai text-2xl">📱</div><h3 class="font-display text-lg font-bold text-ai">Multi-Channel Velocity</h3></div>
      <p class="text-sm text-textMuted leading-relaxed">Simultaneous campaigns on Meta, TikTok, Amazon, and retail POS demand high-volume asset generation without losing the premium feel.</p>
    </div>
  </div>

  <!-- KEY METRICS RIBBON (clean separation) -->
  <div class="relative my-12 py-8 border-y border-border/40">
    <div class="absolute inset-0 bg-gradient-to-r from-accent/5 via-transparent to-accent/5"></div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center relative z-10">
      <div class="cursor-pointer" data-popup data-title="Enterprise-Grade Scale" data-depth="METRIC" data-content="200+ graphic templates designed for Yokogawa, unifying visual identity across 12 European countries. Proven system for global brand consistency.">
        <div class="text-4xl font-display font-bold text-accent mb-2">200+</div>
        <div class="text-[10px] text-textMuted uppercase tracking-wider mb-1">Templates</div>
        <div class="text-xs text-accent/70">Yokogawa Europe</div>
      </div>
      <div class="cursor-pointer" data-popup data-title="High-Volume Asset Management" data-depth="METRIC" data-content="25,000+ product visuals processed for MADE.com international launch across 5 countries. 100% on-time delivery. 20% UX interaction lift.">
        <div class="text-4xl font-display font-bold text-accent mb-2">25K+</div>
        <div class="text-[10px] text-textMuted uppercase tracking-wider mb-1">Visuals</div>
        <div class="text-xs text-accent/70">MADE.com</div>
      </div>
      <div class="cursor-pointer" data-popup data-title="DTC & Corporate Campaign Velocity" data-depth="METRIC" data-content="50+ online campaigns for Ninja, Aiper, Pure, Nikon. 20% sales acceleration, 25% engagement lift. Direct   category experience.">
        <div class="text-4xl font-display font-bold text-accent mb-2">50+</div>
        <div class="text-[10px] text-textMuted uppercase tracking-wider mb-1">Campaigns</div>
        <div class="text-xs text-accent/70">Skin Media</div>
      </div>
      <div class="cursor-pointer" data-popup data-title="Accessibility & Compliance" data-depth="METRIC" data-content="90%+ WCAG compliant designs at Microsoft PCoE. 8 Microsoft certifications (Feb 2025). US market ready, ADA compliant.">
        <div class="text-4xl font-display font-bold text-accent mb-2">90%+</div>
        <div class="text-[10px] text-textMuted uppercase tracking-wider mb-1">WCAG Pass</div>
        <div class="text-xs text-accent/70">Microsoft PCoE</div>
      </div>
    </div>
  </div>

  <!-- STRATEGIC ALIGNMENT RADAR (improved spacing) -->
  <div class="section-divider my-16"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Strategic Alignment Radar</span></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center mb-20">
    <div class="radar-container">
      <svg viewBox="0 0 400 400" class="w-full h-full">
        <g transform="translate(200,200)">
          <polygon points="0,-180 171,-55 105,145 -105,145 -171,-55" fill="none" stroke="#1E2029" stroke-width="1"/>
          <polygon points="0,-135 128,-41 79,109 -79,109 -128,-41" fill="none" stroke="#1E2029" stroke-width="1"/>
          <polygon points="0,-90 85,-28 53,73 -53,73 -85,-28" fill="none" stroke="#1E2029" stroke-width="1"/>
          <polygon points="0,-45 43,-14 26,36 -26,36 -43,-14" fill="none" stroke="#1E2029" stroke-width="1"/>
          <line x1="0" y1="0" x2="0" y2="-180" stroke="#1E2029" stroke-width="1"/>
          <line x1="0" y1="0" x2="171" y2="-55" stroke="#1E2029" stroke-width="1"/>
          <line x1="0" y1="0" x2="105" y2="145" stroke="#1E2029" stroke-width="1"/>
          <line x1="0" y1="0" x2="-105" y2="145" stroke="#1E2029" stroke-width="1"/>
          <line x1="0" y1="0" x2="-171" y2="-55" stroke="#1E2029" stroke-width="1"/>
          <polygon points="0,-162 154,-49 94,131 -89,123 -145,-47" fill="rgba(109,93,211,0.2)" stroke="#6D5DD3" stroke-width="2"/>
          <polygon points="0,-144 137,-44 84,116 -79,109 -137,-44" fill="rgba(255,107,107,0.1)" stroke="#FF6B6B" stroke-width="2" stroke-dasharray="4,4"/>
          <circle cx="0" cy="-162" r="5" fill="#6D5DD3"/><circle cx="154" cy="-49" r="5" fill="#6D5DD3"/><circle cx="94" cy="131" r="5" fill="#6D5DD3"/><circle cx="-89" cy="123" r="5" fill="#6D5DD3"/><circle cx="-145" cy="-47" r="5" fill="#6D5DD3"/>
        </g>
        <text x="200" y="30" fill="#E2E8F0" text-anchor="middle" font-size="12" font-weight="600" font-family="Space Grotesk">DTC & CorporateVelocity</text>
        <text x="375" y="150" fill="#E2E8F0" text-anchor="end" font-size="12" font-weight="600" font-family="Space Grotesk">AI Integration</text>
        <text x="310" y="360" fill="#E2E8F0" text-anchor="middle" font-size="12" font-weight="600" font-family="Space Grotesk">Psychology</text>
        <text x="90" y="360" fill="#E2E8F0" text-anchor="middle" font-size="12" font-weight="600" font-family="Space Grotesk">EQ / Remote</text>
        <text x="25" y="150" fill="#E2E8F0" text-anchor="start" font-size="12" font-weight="600" font-family="Space Grotesk">Compliance</text>
      </svg>
      <div class="flex justify-center gap-8 mt-6 text-xs">
        <div class="flex items-center gap-2"><span class="w-3 h-3 bg-accent rounded-sm"></span> Alex's Capability</div>
        <div class="flex items-center gap-2"><span class="w-3 h-3 border border-human rounded-sm"></span> the Company's Need</div>
      </div>
    </div>
    <div>
      <h3 class="font-display text-3xl font-bold mb-6">Perfect Alignment</h3>
      <p class="text-textMuted mb-10 leading-relaxed">Every axis of the Company's strategic need is matched—or exceeded—by documented capability.</p>
      <div class="space-y-6">
        <div><div class="flex justify-between text-sm mb-2"><span class="font-semibold">DTC & CorporateVelocity & Scale</span><span class="text-accent font-mono">95%</span></div><div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-accent to-ai" style="width:95%"></div></div></div>
        <div><div class="flex justify-between text-sm mb-2"><span class="font-semibold">AI Workflow Maturity</span><span class="text-accent font-mono">90%</span></div><div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-accent to-ai" style="width:90%"></div></div></div>
        <div><div class="flex justify-between text-sm mb-2"><span class="font-semibold">Behavioral Psychology Depth</span><span class="text-accent font-mono">88%</span></div><div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-human to-gold" style="width:88%"></div></div></div>
        <div><div class="flex justify-between text-sm mb-2"><span class="font-semibold">Remote Collaboration EQ</span><span class="text-accent font-mono">92%</span></div><div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-human to-gold" style="width:92%"></div></div></div>
        <div><div class="flex justify-between text-sm mb-2"><span class="font-semibold">Accessibility & Compliance</span><span class="text-accent font-mono">94%</span></div><div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-emerald to-ai" style="width:94%"></div></div></div>
      </div>
    </div>
  </div>

  <!-- STRATEGIC ALIGNMENT HEATMAP (improved inner spacing) -->
  <div class="section-divider my-16"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Strategic Alignment Heatmap</span></div>
  <div class="glass-panel p-8 rounded-2xl mb-20">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
      <div>
        <h3 class="font-display text-2xl font-bold mb-6">the Company Need vs. Verified Proof</h3>
        <p class="text-textMuted text-sm mb-8 leading-relaxed">Every strategic requirement mapped to a quantifiable historical achievement.</p>
        <div class="space-y-5">
          <div class="flex items-center gap-3 cursor-pointer" data-popup data-title="Scale without losing soul" data-depth="PROOF" data-content="Yokogawa: 200+ templates, 12 countries. Microsoft: 90%+ WCAG compliance. Enterprise-grade systems prevent brand drift at scale."><span class="w-3 h-3 rounded-full bg-human"></span><span class="text-sm">Scale creative without losing brand soul</span></div>
          <div class="flex items-center gap-3 cursor-pointer" data-popup data-title="AI operational multiplier" data-depth="PROOF" data-content="Private Local LLM 'Digital Twin'. MS AI Accessibility Cert. Air‑gapped infrastructure, 100% data privacy."><span class="w-3 h-3 rounded-full bg-ai"></span><span class="text-sm">AI as operational multiplier</span></div>
          <div class="flex items-center gap-3 cursor-pointer" data-popup data-title="DTC & Corporate  expertise" data-depth="PROOF" data-content="Ninja, Crock‑Pot, Shark, AIPER, MADE.com (25k+ visuals). Direct category fluency."><span class="w-3 h-3 rounded-full bg-gold"></span><span class="text-sm">DTC & CorporateIndustry Category Expertise</span></div>
          <div class="flex items-center gap-3 cursor-pointer" data-popup data-title="Behavioral psychology" data-depth="PROOF" data-content="Economics degree + MBTI tracking since 2017 + NGO empathy framework. Designs for cognitive archetypes."><span class="w-3 h-3 rounded-full bg-emerald"></span><span class="text-sm">Behavioral Psychology in Creative</span></div>
          <div class="flex items-center gap-3 cursor-pointer" data-popup data-title="Remote collaboration & EQ" data-depth="PROOF" data-content="Testimonials: 'Caring companion,' 'Cannot fire a volunteer,' 'Hard projects made easy.' Trust‑based leadership."><span class="w-3 h-3 rounded-full bg-accent"></span><span class="text-sm">Remote Collaboration & EQ</span></div>
        </div>
      </div>
      <div class="heatmap-grid gap-3">
        <div class="heatmap-cell bg-human/80 cursor-pointer p-2" data-popup data-title="Templates" data-depth="200+" data-content="200+ graphic templates at Yokogawa Europe, ensuring brand consistency across 12 countries.">200+</div>
        <div class="heatmap-cell bg-human/60 cursor-pointer p-2" data-popup data-title="Countries" data-depth="12" data-content="Unified visual identity across 12 European markets – localization and scalability proven.">12</div>
        <div class="heatmap-cell bg-human/40 cursor-pointer p-2" data-popup data-title="WCAG" data-depth="90%+" data-content="90%+ WCAG compliance at Microsoft PCoE.">WCAG</div>
        <div class="heatmap-cell bg-human/20 cursor-pointer p-2" data-popup data-title="Systems" data-depth="Enterprise" data-content="Enterprise-grade design systems built for global scale.">SYS</div>
        <div class="heatmap-cell bg-human/10 cursor-pointer p-2" data-popup data-title="Europe" data-depth="12" data-content="12 European countries – cross‑cultural execution.">EU</div>
        <div class="heatmap-cell bg-ai/80 cursor-pointer p-2" data-popup data-title="LLM" data-depth="Local" data-content="Private local LLM 'Digital Twin' – air‑gapped, 100% data privacy.">LLM</div>
        <div class="heatmap-cell bg-ai/60 cursor-pointer p-2" data-popup data-title="R0" data-depth="Gating" data-content="R0 logical gating system – strategic filter, no AI slop.">R0</div>
        <div class="heatmap-cell bg-ai/40 cursor-pointer p-2" data-popup data-title="Local" data-depth="Infrastructure" data-content="Local execution, no cloud dependency.">LOC</div>
        <div class="heatmap-cell bg-ai/20 cursor-pointer p-2" data-popup data-title="API" data-depth="Cost" data-content="Optimised API usage – ~$300/month max.">API</div>
        <div class="heatmap-cell bg-ai/10 cursor-pointer p-2" data-popup data-title="IP" data-depth="Transferable" data-content="Executable IP – you own the engine.">IP</div>
        <div class="heatmap-cell bg-gold/80 cursor-pointer p-2" data-popup data-title="Campaigns" data-depth="50+" data-content="50+ online campaigns for   brands.">50+</div>
        <div class="heatmap-cell bg-gold/60 cursor-pointer p-2" data-popup data-title="DTC" data-depth="Funnel" data-content="DTC & Corporatefunnel expertise – Meta, TikTok, Amazon.">DTC</div>
        <div class="heatmap-cell bg-gold/40 cursor-pointer p-2" data-popup data-title="Visuals" data-depth="25K" data-content="25,000+ product visuals processed.">25K</div>
        <div class="heatmap-cell bg-gold/20 cursor-pointer p-2" data-popup data-title="ROI" data-depth="79%" data-content="79% cost savings vs traditional approach.">ROI</div>
        <div class="heatmap-cell bg-gold/10 cursor-pointer p-2" data-popup data-title="CTR" data-depth="Lift" data-content="20‑40% engagement lifts documented.">CTR</div>
        <div class="heatmap-cell bg-emerald/80 cursor-pointer p-2" data-popup data-title="MBTI" data-depth="2017" data-content="MBTI tracking since 2017 – cognitive archetypes.">MBTI</div>
        <div class="heatmap-cell bg-emerald/60 cursor-pointer p-2" data-popup data-title="Economics" data-depth="Degree" data-content="Formal Economics background – market forces.">ECON</div>
        <div class="heatmap-cell bg-emerald/40 cursor-pointer p-2" data-popup data-title="NGO" data-depth="Empathy" data-content="'Cannot fire a volunteer' – NGO leadership principle.">NGO</div>
        <div class="heatmap-cell bg-emerald/20 cursor-pointer p-2" data-popup data-title="EQ" data-depth="Active" data-content="Emotional intelligence – active listening, psychological safety.">EQ</div>
        <div class="heatmap-cell bg-emerald/10 cursor-pointer p-2" data-popup data-title="UX" data-depth="20%" data-content="20% UX interaction lift at MADE.com.">UX</div>
        <div class="heatmap-cell bg-accent/80 cursor-pointer p-2" data-popup data-title="EQ" data-depth="Remote" data-content="Emotional intelligence for remote collaboration.">EQ</div>
        <div class="heatmap-cell bg-accent/60 cursor-pointer p-2" data-popup data-title="Volunteer" data-depth="NGO" data-content="'Cannot fire a volunteer' – leads with motivation.">VOL</div>
        <div class="heatmap-cell bg-accent/40 cursor-pointer p-2" data-popup data-title="Trust" data-depth="Currency" data-content="'In remote teams, trust is the currency.'">TRUST</div>
        <div class="heatmap-cell bg-accent/20 cursor-pointer p-2" data-popup data-title="Sync" data-depth="Async" data-content="High‑signal, low‑noise communication.">SYNC</div>
        <div class="heatmap-cell bg-accent/10 cursor-pointer p-2" data-popup data-title="B2B" data-depth="Contract" data-content="B2B contractor – €2,300‑2,500 NET/month.">B2B</div>
      </div>
    </div>
  </div>

  <!-- STRATEGIC ALIGNMENT TABLE (consistent spacing) -->
  <div class="section-divider my-16"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Strategic Alignment Matrix · the Company Need ↔ Verified Proof</span></div>
  <div class="glass-panel rounded-2xl overflow-hidden mb-20">
    <table class="w-full text-sm">
      <thead class="bg-surface/50 border-b border-border"><tr><th class="text-left p-4 font-display font-bold text-textMuted uppercase text-xs tracking-wider">the Company Need</th><th class="text-left p-4 font-display font-bold text-textMuted uppercase text-xs tracking-wider">Verified Proof</th><th class="text-left p-4 font-display font-bold text-textMuted uppercase text-xs tracking-wider hidden md:table-cell">Interview Hook</th></tr></thead>
      <tbody class="divide-y divide-border/30">
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Scale without losing soul" data-depth="ALIGNMENT" data-content="Yokogawa: 200+ templates, 12 countries. Microsoft: 90%+ WCAG compliance. Enterprise-grade systems prevent brand drift."><td class="p-4 font-semibold">Scale creative without losing brand soul</td><td class="p-4 text-textMuted text-xs">Yokogawa: 200+ templates, 12 countries; Microsoft: 90%+ WCAG</td><td class="p-4 text-xs text-accent italic hidden md:table-cell">"I build the systems that make ads scalable, compliant, and on-brand."</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="AI operational multiplier" data-depth="ALIGNMENT" data-content="Private Local LLM 'Digital Twin'. MS AI Accessibility Cert. Air‑gapped, zero data leakage."><td class="p-4 font-semibold">AI as operational multiplier</td><td class="p-4 text-textMuted text-xs">Private Local LLM "Digital Twin"; MS AI Accessibility Cert</td><td class="p-4 text-xs text-accent italic hidden md:table-cell">"My AI isn't a gimmick—it's an infrastructure layer."</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="DTC & Corporate  expertise" data-depth="ALIGNMENT" data-content="Ninja, Crock-Pot, Shark, AIPER, MADE.com (25k+ visuals). Direct category fluency, 20‑40% lifts."><td class="p-4 font-semibold">DTC & CorporateIndustry Expertise</td><td class="p-4 text-textMuted text-xs">Ninja, Crock-Pot, Shark, AIPER, MADE.com (25k+ visuals)</td><td class="p-4 text-xs text-accent italic hidden md:table-cell">"I've already solved the exact visual challenges the Company faces."</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Behavioral psychology" data-depth="ALIGNMENT" data-content="Economics degree + MBTI (since 2017) + NGO empathy. Designs for cognitive archetypes."><td class="p-4 font-semibold">Behavioral Psychology in Creative</td><td class="p-4 text-textMuted text-xs">Economics degree + MBTI (since 2017) + NGO empathy</td><td class="p-4 text-xs text-accent italic hidden md:table-cell">"I design for cognitive archetypes, not just demographics."</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Remote collaboration & EQ" data-depth="ALIGNMENT" data-content="'Caring companion,' 'Cannot fire a volunteer,' 'Hard projects made easy.' Trust‑based remote leadership."><td class="p-4 font-semibold">Remote Collaboration & EQ</td><td class="p-4 text-textMuted text-xs">"Caring companion," "Cannot fire a volunteer," "Hard projects made easy"</td><td class="p-4 text-xs text-accent italic hidden md:table-cell">"In remote teams, trust is the currency."</td></tr>
      </tbody>
    </table>
  </div>

</section>

<!-- ==================== TAB 2: BIMODAL WORKFLOW (MASSIVELY EXPANDED – with hero visualization, flow diagrams, architecture visuals, R0 gating, data pipeline, and interactive cards) ==================== -->
<section id="workflow" class="tab-content">
  <!-- ==================== HERO VISUALIZATION (New Central Element) ==================== -->
<div class="hero-visualization mb-16">
  <div class="relative glass-panel rounded-3xl overflow-hidden border border-accent/30 shadow-2xl">
    <!-- Background animated gradient -->
    <div class="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-ai/5"></div>
    <div class="absolute top-0 right-0 w-96 h-96 bg-accent/20 rounded-full blur-3xl -mr-48 -mt-48 animate-pulse-glow"></div>
    <div class="absolute bottom-0 left-0 w-80 h-80 bg-ai/20 rounded-full blur-3xl -ml-40 -mb-40 animate-pulse-glow animation-delay-2000"></div>

    <div class="relative z-10 p-8 md:p-12">
      <!-- Badge -->
      <div class="inline-flex items-center gap-2 bg-accent/10 backdrop-blur-sm px-4 py-2 rounded-full text-accent text-xs font-bold uppercase tracking-wider mb-8 border border-accent/20">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
        </span>
        The Bimodal Framework
      </div>

      <!-- Headline -->
      <h1 class="font-display text-4xl md:text-6xl lg:text-7xl font-bold leading-tight tracking-tight mb-6 bg-gradient-to-r from-white via-white to-accent/70 bg-clip-text text-transparent">
        Deconstructing the<br>
        <span class="text-accent">Bimodal Workflow</span>
      </h1>

      <!-- Subheadline -->
      <p class="text-textMuted text-lg md:text-xl max-w-3xl mb-12 leading-relaxed">
        A symbiotic loop where human strategy directs machine velocity,<br>
        and machine efficiency frees human intellect for deeper strategic framing.
      </p>

      <!-- Central Visualization Container -->
      <div class="visualization-container w-full max-w-5xl mx-auto my-8 md:my-12 relative">
        <div class="relative aspect-[16/9] w-full bg-gradient-to-br from-gray-900/50 to-gray-950/90 rounded-2xl border border-white/10 backdrop-blur-sm overflow-hidden group">
          <svg viewBox="0 0 1000 562" class="w-full h-full">
            <defs>
              <linearGradient id="humanGradient3d" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#FF8A8A;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#E04E4E;stop-opacity:1" />
              </linearGradient>
              <linearGradient id="aiGradient3d" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#7BC5FF;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#2D89CE;stop-opacity:1" />
              </linearGradient>
              <filter id="glowHuman" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="8" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
              <filter id="glowAi" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="8" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
              <!-- Slow glow filter for central hub (independent, slow pulse) -->
              <filter id="glowCenterSlow" x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="12" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            <style>
              @keyframes glowAlternate {
                0%, 100% { filter: url(#glowHuman); opacity: 1; }
                50% { filter: none; opacity: 0.7; }
              }
              @keyframes glowAlternateAi {
                0%, 100% { filter: none; opacity: 0.7; }
                50% { filter: url(#glowAi); opacity: 1; }
              }
              /* Slow central glow – 8 seconds, independent */
              @keyframes glowCenterSlowPulse {
                0%, 100% { filter: url(#glowCenterSlow); opacity: 0.9; }
                50% { filter: none; opacity: 0.5; }
              }
              .mode-a-glow { animation: glowAlternate 3s ease-in-out infinite; }
              .mode-b-glow { animation: glowAlternateAi 3s ease-in-out infinite; }
              .center-slow-glow { animation: glowCenterSlowPulse 8s ease-in-out infinite; }
              .cursor-pointer { cursor: pointer; }
              .pipeline-node:hover, .mode-a-node:hover, .mode-b-node:hover, .central-hub:hover {
                outline: none;
                stroke: none;
                filter: none;
              }
            </style>

            <!-- Floating particles -->
            <g class="data-particles">
              <circle cx="80" cy="80" r="2.5" fill="#4DABF7" opacity="0.6"><animate attributeName="cy" values="80;110;80" dur="4s" repeatCount="indefinite" /></circle>
              <circle cx="920" cy="500" r="2" fill="#FF6B6B" opacity="0.5"><animate attributeName="cy" values="500;480;500" dur="3.5s" repeatCount="indefinite" /></circle>
              <circle cx="850" cy="120" r="3" fill="#6C5CE7" opacity="0.4"><animate attributeName="cx" values="850;870;850" dur="5s" repeatCount="indefinite" /></circle>
              <circle cx="180" cy="450" r="2" fill="#FF9F4A" opacity="0.5"><animate attributeName="cy" values="450;430;450" dur="4.2s" repeatCount="indefinite" /></circle>
              <circle cx="300" cy="60" r="1.5" fill="#4DABF7" opacity="0.7"><animate attributeName="cx" values="300;320;300" dur="3s" repeatCount="indefinite" /></circle>
              <circle cx="700" cy="520" r="2.5" fill="#FF6B6B" opacity="0.5"><animate attributeName="cy" values="520;500;520" dur="4.8s" repeatCount="indefinite" /></circle>
              <circle cx="50" cy="280" r="2" fill="#6C5CE7" opacity="0.6"><animate attributeName="cy" values="280;260;280" dur="3.2s" repeatCount="indefinite" /></circle>
              <circle cx="950" cy="200" r="1.8" fill="#FF9F4A" opacity="0.5"><animate attributeName="cy" values="200;180;200" dur="4s" repeatCount="indefinite" /></circle>
              <circle cx="400" cy="530" r="2.2" fill="#4DABF7" opacity="0.4"><animate attributeName="cy" values="530;510;530" dur="3.7s" repeatCount="indefinite" /></circle>
              <circle cx="600" cy="40" r="1.5" fill="#FF6B6B" opacity="0.6"><animate attributeName="cy" values="40;60;40" dur="4.5s" repeatCount="indefinite" /></circle>
              <circle cx="750" cy="380" r="2" fill="#6C5CE7" opacity="0.5"><animate attributeName="cy" values="380;360;380" dur="3.3s" repeatCount="indefinite" /></circle>
              <circle cx="250" cy="150" r="2.8" fill="#FF9F4A" opacity="0.4"><animate attributeName="cx" values="250;270;250" dur="4.1s" repeatCount="indefinite" /></circle>
            </g>

            <!-- ===== CONNECTOR LINES (oprite la marginea cercurilor Mode A/B) ===== -->
            <line x1="100" y1="100" x2="159" y2="218" stroke="#4DABF7" stroke-width="2" stroke-dasharray="6 4" opacity="0.7" />
            <line x1="100" y1="460" x2="159" y2="344" stroke="#FF9F4A" stroke-width="2" stroke-dasharray="6 4" opacity="0.7" />
            <line x1="940" y1="281" x2="880" y2="281" stroke="#FF6B6B" stroke-width="2" stroke-dasharray="6 4" opacity="0.7" />

            <!-- ===== SLOW, LARGE OUTER CIRCLE (split into two semi-circles: left pink, right blue) ===== -->
            <path d="M 500 136 A 145 145 0 0 0 500 426" fill="none" stroke="#FF6B6B" stroke-width="4" stroke-dasharray="15 25" opacity="0.8">
              <animate attributeName="stroke-dashoffset" values="0;200" dur="8s" repeatCount="indefinite" />
            </path>
            <path d="M 500 136 A 145 145 0 0 1 500 426" fill="none" stroke="#4DABF7" stroke-width="4" stroke-dasharray="15 25" opacity="0.8">
              <animate attributeName="stroke-dashoffset" values="0;200" dur="8s" repeatCount="indefinite" />
            </path>

            <!-- ===== FAST INNER ARCS (tighter gap) ===== -->
            <path d="M 260 281 C 370 210, 630 210, 740 281" fill="none" stroke="#FF9F4A" stroke-width="2.5" marker-end="url(#arrowheadAi)" opacity="0.9">
              <animate attributeName="stroke-dashoffset" values="800;0" dur="3s" repeatCount="indefinite" />
              <animate attributeName="stroke-dasharray" values="10 20" dur="3s" repeatCount="indefinite" />
            </path>
            <path d="M 740 281 C 630 352, 370 352, 260 281" fill="none" stroke="#6C5CE7" stroke-width="2.5" marker-end="url(#arrowheadHuman)" opacity="0.9">
              <animate attributeName="stroke-dashoffset" values="800;0" dur="3.5s" repeatCount="indefinite" />
              <animate attributeName="stroke-dasharray" values="10 20" dur="3.5s" repeatCount="indefinite" />
            </path>

            <!-- ===== CENTRAL HUB (cu glow lent, independent) ===== -->
            <g class="central-hub cursor-pointer" data-popup data-title="Symbiotic Loop" data-depth="CORE MECHANISM" data-content="The continuous feedback loop: Mode A strategic guardrails guide Mode B automation, and Mode B execution data refines Mode A strategic insights. No 'AI slop' ever passes through.">
              <!-- Outer rotating ring – larger dashes, thicker stroke, counter‑clockwise -->
              <circle cx="500" cy="281" r="125" fill="none" stroke="#6C5CE7" stroke-width="3" stroke-dasharray="24 16" opacity="0.6">
                <animateTransform attributeName="transform" type="rotate" from="360 500 281" to="0 500 281" dur="20s" repeatCount="indefinite" />
              </circle>
              <!-- Inner rotating ring (clockwise) -->
              <circle cx="500" cy="281" r="105" fill="none" stroke="#A084FF" stroke-width="1.8" stroke-dasharray="12 20" opacity="0.4">
                <animateTransform attributeName="transform" type="rotate" from="0 500 281" to="360 500 281" dur="25s" repeatCount="indefinite" />
              </circle>
              <!-- Solid centre circles -->
              <circle cx="500" cy="281" r="90" fill="#6C5CE7" fill-opacity="0.12" stroke="#6C5CE7" stroke-width="2" />
              <!-- Cercul central cu glow lent (fără suprapunere, animație slow) -->
              <circle cx="500" cy="281" r="75" fill="#6C5CE7" fill-opacity="0.7" class="center-slow-glow" />
              <text x="500" y="258" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="18" dominant-baseline="middle">SYMBIOTIC</text>
              <text x="500" y="288" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="16" dominant-baseline="middle">LOOP</text>
              <text x="500" y="314" text-anchor="middle" fill="#E0DDFF" font-family="'Space Grotesk', sans-serif" font-size="11" dominant-baseline="middle">⇄ continuous</text>
            </g>

            <!-- Mode A (Human) -->
            <g class="mode-a-node cursor-pointer" data-popup data-title="Mode A: Strategic Direction" data-depth="HUMAN LED" data-content="Human‑led strategic core: Economics, MBTI tracking (2017+), NGO empathy, behavioral triggers.">
              <path d="M 280 281 C 280 200, 350 150, 420 150" fill="none" stroke="#FF6B6B" stroke-width="2" stroke-dasharray="4 4" opacity="0.5">
                <animate attributeName="stroke-dashoffset" values="0;20" dur="2s" repeatCount="indefinite" />
              </path>
              <path d="M 280 281 C 280 362, 350 412, 420 412" fill="none" stroke="#FF6B6B" stroke-width="2" stroke-dasharray="4 4" opacity="0.5">
                <animate attributeName="stroke-dashoffset" values="0;20" dur="2.5s" repeatCount="indefinite" />
              </path>
              <circle cx="190" cy="281" r="70" fill="url(#humanGradient3d)" stroke="#FFCCCC" stroke-width="1.5" class="mode-a-glow" />
              <text x="190" y="248" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="30" dominant-baseline="middle">🧠</text>
              <text x="190" y="280" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="14" dominant-baseline="middle">Mode A</text>
              <text x="190" y="302" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-size="10" dominant-baseline="middle">Strategy</text>
              <text x="190" y="316" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-size="10" dominant-baseline="middle">Psychology</text>
            </g>

            <!-- Mode B (AI) -->
            <g class="mode-b-node cursor-pointer" data-popup data-title="Mode B: Actionable Execution" data-depth="AUTOMATED" data-content="Private local LLM, infinite memory, 50+ assets/week, R0 gating, WCAG, no AI slop.">
              <path d="M 720 281 C 720 200, 650 150, 580 150" fill="none" stroke="#4DABF7" stroke-width="2" stroke-dasharray="4 4" opacity="0.5">
                <animate attributeName="stroke-dashoffset" values="0;20" dur="2s" repeatCount="indefinite" />
              </path>
              <path d="M 720 281 C 720 362, 650 412, 580 412" fill="none" stroke="#4DABF7" stroke-width="2" stroke-dasharray="4 4" opacity="0.5">
                <animate attributeName="stroke-dashoffset" values="0;20" dur="2.5s" repeatCount="indefinite" />
              </path>
              <circle cx="810" cy="281" r="70" fill="url(#aiGradient3d)" stroke="#CCE4FF" stroke-width="1.5" class="mode-b-glow" />
              <text x="810" y="248" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="30" dominant-baseline="middle">⚙️</text>
              <text x="810" y="280" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="14" dominant-baseline="middle">Mode B</text>
              <text x="810" y="302" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-size="10" dominant-baseline="middle">Execution</text>
              <text x="810" y="316" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-size="10" dominant-baseline="middle">Automation</text>
            </g>

            <!-- Step circles -->
            <g class="pipeline-node step-01 cursor-pointer" data-popup data-title="Step 01: Deep Scan & Capture" data-depth="PIPELINE STAGE" data-content="Autonomous web/social/marketplace scraping captures 85‑90% of brand DNA. Proactively identifies gaps.">
              <circle cx="100" cy="100" r="42" fill="#1a1a2e" stroke="#4DABF7" stroke-width="2.5" />
              <text x="100" y="86" text-anchor="middle" fill="#4DABF7" font-size="22" dominant-baseline="middle">🔍</text>
              <text x="100" y="116" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="10" dominant-baseline="middle">STEP 01</text>
            </g>

            <g class="pipeline-node step-02 cursor-pointer" data-popup data-title="Step 02: Proactive Gap ID" data-depth="PIPELINE STAGE" data-content="AI analyzes captured DNA, identifies missing insights: tone, visual hierarchy, gamification mechanics.">
              <circle cx="100" cy="460" r="42" fill="#1a1a2e" stroke="#FF9F4A" stroke-width="2.5" />
              <text x="100" y="446" text-anchor="middle" fill="#FF9F4A" font-size="22" dominant-baseline="middle">🎯</text>
              <text x="100" y="476" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="10" dominant-baseline="middle">STEP 02</text>
            </g>

            <g class="pipeline-node step-03 cursor-pointer" data-popup data-title="Step 03: Template Systematization" data-depth="PIPELINE STAGE" data-content="Outputs systematized template architecture → executable model runs locally on client machines. Infinite iterations.">
              <circle cx="940" cy="281" r="42" fill="#1a1a2e" stroke="#FF6B6B" stroke-width="2.5" />
              <text x="940" y="267" text-anchor="middle" fill="#FF6B6B" font-size="22" dominant-baseline="middle">📐</text>
              <text x="940" y="297" text-anchor="middle" fill="#FFFFFF" font-family="'Space Grotesk', sans-serif" font-weight="bold" font-size="10" dominant-baseline="middle">STEP 03</text>
            </g>

          </svg>

          <!-- Click instruction (still inside the graphic area) -->
          <div class="absolute top-4 left-4 text-[10px] text-textMuted bg-black/40 backdrop-blur-sm rounded-md px-2 py-1">
            ▼ Click any element for details
          </div>
        </div>

        <!-- Legend moved UNDER the graphic (outside absolute container) -->
        <div class="flex flex-wrap justify-center gap-4 mt-4 text-[10px] text-white">
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="w-2 h-2 rounded-full bg-human"></span><span>Human‑led</span>
          </div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="w-2 h-2 rounded-full bg-ai"></span><span>AI‑assisted</span>
          </div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="w-2 h-2 rounded-full bg-accent"></span><span>Symbiotic loop</span>
          </div>
          <div class="w-px h-4 bg-white/20 mx-1"></div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="text-[#4DABF7]">🔍</span><span>Deep Scan & Capture</span>
          </div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="text-[#FF9F4A]">🎯</span><span>Proactive Gap ID</span>
          </div>
          <div class="flex items-center gap-2 bg-black/40 backdrop-blur-sm rounded-full px-3 py-1">
            <span class="text-[#FF6B6B]">📐</span><span>Template Systematization</span>
          </div>
        </div>

        <div class="text-center mt-4">
          <p class="text-xs text-textMuted uppercase tracking-wider">The Symbiotic Feedback Loop · Human Strategy ↔ Machine Velocity</p>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mt-12 pt-8 border-t border-white/10">
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent mb-1">10x</div><div class="text-[11px] text-textMuted uppercase tracking-wider">Velocity Multiplier</div><div class="text-[10px] text-textMuted mt-1">5‑8 → 50+ assets/week</div></div>
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent mb-1">0</div><div class="text-[11px] text-textMuted uppercase tracking-wider">Brand Drift</div><div class="text-[10px] text-textMuted mt-1">Infinite context memory</div></div>
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent mb-1">79%</div><div class="text-[11px] text-textMuted uppercase tracking-wider">Cost Savings</div><div class="text-[10px] text-textMuted mt-1">vs traditional agency models</div></div>
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent mb-1">100%</div><div class="text-[11px] text-textMuted uppercase tracking-wider">IP Security</div><div class="text-[10px] text-textMuted mt-1">Air‑gapped · Private LLM</div></div>
      </div>
    </div>
  </div>
</div>

  <!-- MARTIAL ART + BIMODAL OVERVIEW (enhanced with visual flow) -->
  <div class="glass-panel p-8 rounded-2xl mb-12 relative overflow-hidden border border-accent/20">
    <div class="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full blur-3xl -mr-32 -mt-32"></div>
    <h3 class="font-display text-2xl font-bold mb-4 text-accent">The "Martial Art" of Art Direction</h3>
    <p class="text-textMuted italic text-lg mb-6">"When practiced correctly, you don't see the hits coming—you just feel them and remember them."</p>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-human/5 border border-human/20 rounded-xl p-6 transition-all hover:shadow-[0_0_20px_rgba(255,107,107,0.2)] cursor-pointer" data-popup data-title="Mode A: Strategic Direction" data-depth="HUMAN LED" data-content="Mode A is the human‑led strategic core. It fuses formal Economics training, MBTI/16 Personalities tracking (since 2017), and NGO‑derived empathy. This enables design decisions based on cognitive archetypes and behavioral economics rather than subjective aesthetics. It answers the 'why' behind every creative decision.">
        <span class="pill pill-human mb-3">MODE A: STRATEGY</span>
        <ul class="text-sm text-textMuted space-y-3 mt-4">
          <li class="flex gap-2"><span class="text-human">▸</span> Brand Syntax & Market Dynamics</li>
          <li class="flex gap-2"><span class="text-human">▸</span> Consumer Archetype Mapping (MBTI)</li>
          <li class="flex gap-2"><span class="text-human">▸</span> Emotional Insight Extraction</li>
          <li class="flex gap-2"><span class="text-human">▸</span> Funnel Logic & Behavioral Triggers</li>
        </ul>
      </div>
      <div class="bg-ai/5 border border-ai/20 rounded-xl p-6 transition-all hover:shadow-[0_0_20px_rgba(77,171,247,0.2)] cursor-pointer" data-popup data-title="Mode B: Actionable Execution" data-depth="AUTOMATED" data-content="Mode B is the automated execution engine, powered by a private local LLM 'digital twin'. It handles high‑volume, repetitive tasks: resizing, variation generation, WCAG compliance checks, and template deployment. This frees human time for strategy and taste. No 'AI slop' passes through.">
        <span class="pill pill-ai mb-3">MODE B: ACTION</span>
        <ul class="text-sm text-textMuted space-y-3 mt-4">
          <li class="flex gap-2"><span class="text-ai">▸</span> Asset Resizing & Formatting</li>
          <li class="flex gap-2"><span class="text-ai">▸</span> Variation Generation (50+/wk)</li>
          <li class="flex gap-2"><span class="text-ai">▸</span> WCAG Compliance Checks</li>
          <li class="flex gap-2"><span class="text-ai">▸</span> R0 Logical Gating Execution</li>
        </ul>
      </div>
    </div>
    <div class="mt-6 text-center text-xs text-textMuted flex justify-center gap-4">
      <span class="inline-flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-human"></span> Human‑led</span>
      <span class="inline-flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-ai"></span> AI‑assisted</span>
      <span class="inline-flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-accent"></span> Symbiotic loop</span>
    </div>
  </div>

  <!-- SYMBIOTIC LOOP DIAGRAM (new visual) -->
  <div class="glass-panel p-8 rounded-2xl mb-12">
    <h3 class="font-display text-2xl font-bold mb-6 text-center">The Symbiotic Feedback Loop</h3>
    <div class="relative flex flex-col md:flex-row items-center justify-between gap-6">
      <div class="flex-1 text-center">
        <div class="w-24 h-24 mx-auto rounded-full bg-human/10 flex items-center justify-center text-3xl mb-3">🧠</div>
        <div class="text-human font-bold">Mode A: Strategy</div>
        <div class="text-xs text-textMuted mt-1">Human insight · Psychology · Economics</div>
      </div>
      <div class="text-accent text-3xl hidden md:block">⇄</div>
      <div class="flex-1 text-center">
        <div class="w-24 h-24 mx-auto rounded-full bg-ai/10 flex items-center justify-center text-3xl mb-3">⚙️</div>
        <div class="text-ai font-bold">Mode B: Action</div>
        <div class="text-xs text-textMuted mt-1">Automation · Variation · Compliance</div>
      </div>
    </div>
    <div class="mt-6 text-center text-sm text-textMuted italic">Strategy informs automation; automation generates data that refines strategy – a continuously improving creative engine.</div>
  </div>

  <!-- MODE A & MODE B DEEP DIVE (expanded cards) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Mode A & Mode B Deep Dive</span></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-human/50 transition-all hover:shadow-[0_0_20px_rgba(255,107,107,0.1)]">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg bg-human/10 flex items-center justify-center text-human text-2xl">🧠</div><div><h3 class="font-display text-2xl font-bold text-white">Mode A: The Soul</h3><span class="text-xs text-human uppercase tracking-wider font-bold">Psychological Insight Engine</span></div></div>
      <div class="space-y-4">
        <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="Behavioral Economics Foundation" data-depth="MODE A" data-content="Formal background in Economics provides macro‑level understanding of market forces, supply/demand, and consumer value perception. Enables data‑informed creative decisions tied directly to ROI and business outcomes.">
          <div class="flex items-start gap-3"><span class="text-human font-mono font-bold">01</span><div><strong class="block text-white text-sm mb-1">Behavioral Economics Foundation</strong><p class="text-xs text-textMuted">Formal education in market forces, supply/demand, and consumer value perception.</p></div></div>
        </div>
        <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="MBTI Cognitive Archetypes" data-depth="MODE A" data-content="Tracking MBTI type and psychological evolution since 2017. Understanding cognitive frameworks helps deconstruct how different consumer archetypes process information. Applied to tailor visual messaging for Sensor vs. Intuitive audiences – directly applicable to the Company's parents 28‑40 target.">
          <div class="flex items-start gap-3"><span class="text-human font-mono font-bold">02</span><div><strong class="block text-white text-sm mb-1">MBTI Cognitive Archetypes</strong><p class="text-xs text-textMuted">Tracking evolution since 2017 to target cognitive processing styles (Sensor vs. Intuitive).</p></div></div>
        </div>
        <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="The 'Volunteer' Principle (EQ)" data-depth="MODE A" data-content="NGO leadership lesson: 'You cannot fire a volunteer.' Instills a culture of active listening, motivation, and psychological safety. Translates directly into collaborative leadership and remote team cohesion.">
          <div class="flex items-start gap-3"><span class="text-human font-mono font-bold">03</span><div><strong class="block text-white text-sm mb-1">The "Volunteer" Principle (EQ)</strong><p class="text-xs text-textMuted">"You cannot fire a volunteer." Active listening and psychological safety.</p></div></div>
        </div>
        <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="Gamified Nutrition Alignment" data-depth="MODE A" data-content="Designing for habit formation and parental psychology – the exact behavioral layer the Company's product demands. Leverages behavioral economics to drive child engagement and parent purchasing decisions.">
          <div class="flex items-start gap-3"><span class="text-human font-mono font-bold">04</span><div><strong class="block text-white text-sm mb-1">Gamified Nutrition Alignment</strong><p class="text-xs text-textMuted">Designing for habit formation and parental psychology.</p></div></div>
        </div>
      </div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-ai/50 transition-all hover:shadow-[0_0_20px_rgba(77,171,247,0.1)]">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg bg-ai/10 flex items-center justify-center text-ai text-2xl">⚙️</div><div><h3 class="font-display text-2xl font-bold text-white">Mode B: The Scale</h3><span class="text-xs text-ai uppercase tracking-wider font-bold">Automated Production Engine</span></div></div>
      <div class="space-y-4">
        <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="Private Local LLM ('Digital Twin')" data-depth="MODE B" data-content="A custom‑built AI system running on the candidate's own hardware, ensuring complete data privacy and IP security. Air‑gapped. No cloud dependency. Eliminates data leakage risk – a critical differentiator from public AI tools.">
          <div class="flex items-start gap-3"><span class="text-ai font-mono font-bold">01</span><div><strong class="block text-white text-sm mb-1">Private Local LLM ("Digital Twin")</strong><p class="text-xs text-textMuted">Air‑gapped infrastructure. 100% IP security.</p></div></div>
        </div>
        <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="Infinite Context Memory" data-depth="MODE B" data-content="Proprietary system that remembers every brand guideline, preventing drift as volume scales 10x. Acts as perpetual institutional memory for creative assets – solves the common DTC & Corporatepain point of brand inconsistency.">
          <div class="flex items-start gap-3"><span class="text-ai font-mono font-bold">02</span><div><strong class="block text-white text-sm mb-1">Infinite Context Memory</strong><p class="text-xs text-textMuted">Prevents brand drift at scale.</p></div></div>
        </div>
        <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="High‑Velocity Variation Generation" data-depth="MODE B" data-content="Automates resizing, compliance checks, and A/B variant creation at machine speed. From 5‑8 variations/week to 50+ – directly solving the Company's velocity bottleneck.">
          <div class="flex items-start gap-3"><span class="text-ai font-mono font-bold">03</span><div><strong class="block text-white text-sm mb-1">High‑Velocity Variation Generation</strong><p class="text-xs text-textMuted">50+ assets/week, 10x faster.</p></div></div>
        </div>
        <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="R0 Logical Gating System" data-depth="MODE B" data-content="A bimodal operating structure that transforms the machine into a strategic filter. Mode A sets the guardrails; Mode B executes at machine speed. No 'AI slop' passes through to the final output. Ensures every asset hits with the same strategic precision.">
          <div class="flex items-start gap-3"><span class="text-ai font-mono font-bold">04</span><div><strong class="block text-white text-sm mb-1">R0 Logical Gating System</strong><p class="text-xs text-textMuted">Strategic filter – no AI slop.</p></div></div>
        </div>
      </div>
    </div>
  </div>

  <!-- 3‑STEP AUTONOMOUS AGENT PIPELINE (visual flow + detail) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">3‑Step Autonomous Agent Pipeline</span></div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
    <div class="glass-card p-6 rounded-xl border-t-2 border-ai transition-all hover:scale-[1.02] cursor-pointer" data-popup data-title="Step 01: Deep Scan & Capture" data-depth="PIPELINE STAGE" data-content="The machine autonomously scrapes public brand data – web, social, marketplaces – capturing 85‑90% of the brand DNA right out of the gate. It then proactively identifies gaps and tells us exactly what proprietary insights or assets it still needs to reach 100%. No guesswork.">
      <div class="text-ai font-mono text-xs mb-2">STEP 01</div>
      <div class="text-3xl mb-2">🔍</div>
      <h4 class="font-display font-bold mb-2">Deep Scan & Capture</h4>
      <p class="text-sm text-textMuted">Captures <span class="text-white font-bold">85‑90% of brand DNA</span> autonomously.</p>
      <div class="mt-3 text-[10px] text-textMuted">Web scraping · Social listening · Marketplace analysis</div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-gold transition-all hover:scale-[1.02] cursor-pointer" data-popup data-title="Step 02: Proactive Gap ID" data-depth="PIPELINE STAGE" data-content="The AI analyses the captured DNA and proactively identifies missing insights – tone of voice, visual hierarchy rules, competitor differentiators. It tells us what to feed it. We don't guess; it guides us based on strategic logic. For the Company, this would flag specific gamification mechanics and parent psychology nuances.">
      <div class="text-gold font-mono text-xs mb-2">STEP 02</div>
      <div class="text-3xl mb-2">🎯</div>
      <h4 class="font-display font-bold mb-2">Proactive Gap ID</h4>
      <p class="text-sm text-textMuted">Machine tells us what it needs – no guessing required.</p>
      <div class="mt-3 text-[10px] text-textMuted">Gamification · Parent psychology · Tone</div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-emerald transition-all hover:scale-[1.02] cursor-pointer" data-popup data-title="Step 03: Template Systematization" data-depth="PIPELINE STAGE" data-content="Outputs a systematized template architecture adaptable to infinite iterations. The AI generates a transferable 'executable template model' that can be run locally on the Company's machines. Limited only by local compute power. After initial configuration, it executes with the same strategic fidelity, completely decoupled from the candidate's infrastructure.">
      <div class="text-emerald font-mono text-xs mb-2">STEP 03</div>
      <div class="text-3xl mb-2">📐</div>
      <h4 class="font-display font-bold mb-2">Template Systematization</h4>
      <p class="text-sm text-textMuted">Infinite iterations, limited only by compute power.</p>
      <div class="mt-3 text-[10px] text-textMuted">Executable IP · Local inference · Scalable</div>
    </div>
  </div>

  <!-- R0 LOGICAL GATING SYSTEM (detailed card) -->
  <div class="glass-card p-6 rounded-xl border-l-4 border-accent mb-12 cursor-pointer" data-popup data-title="The R0 Logical Gating System" data-depth="TECHNICAL ARCHITECTURE" data-content="R0 is the logical gating system that transforms the machine into a bimodal operating structure in either Mode A (Strategy) or Mode B (Action). It ensures every asset hits with the same strategic precision – no 'AI slop' passes through. Mode A sets the guardrails; Mode B executes at machine speed. This is the core innovation that separates this system from generic generative AI.">
    <div class="flex items-center gap-3">
      <div class="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center text-accent text-xl font-bold">R0</div>
      <div><h4 class="font-display font-bold text-lg">The R0 Logical Gating System</h4><p class="text-sm text-textMuted">A bimodal operating structure that transforms the machine into a strategic filter. Mode A sets the guardrails; Mode B executes at machine speed. No "AI slop" passes through to the final output.</p></div>
    </div>
  </div>

  <!-- DATA ARCHITECTURE TOPOLOGY (enhanced with visual layers) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Data Architecture Topology</span></div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
    <div class="glass-card p-6 rounded-xl border-t-2 border-human transition-all hover:shadow-[0_0_15px_rgba(255,107,107,0.1)] cursor-pointer" data-popup data-title="Tier 0: DEFINITION" data-depth="TIER 0 · PERSONAL DNA" data-content="The foundational DNA of the operator and the brand. Includes: CV (Alexandru Popescu), Personal Identity, MBTI Evolution (since 2017), NGO Empathy Framework, Economics Baseline, Microsoft Achievements. This tier is private to Alex's AI but shapes how the AI reasons. It is never shared externally – only the processed outputs.">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-full bg-human/10 flex items-center justify-center font-display font-bold text-human text-lg">T0</div><h4 class="font-display font-bold">Tier 0: DEFINITION</h4></div>
      <p class="text-xs text-textMuted mb-4">Personal DNA that shapes AI reasoning. <span class="text-human">(Private)</span></p>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between border-b border-border/30 pb-2"><span>CV & Personal Identity</span><span class="text-human">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>MBTI Evolution (2017+)</span><span class="text-human">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>NGO Empathy Framework</span><span class="text-human">●</span></div>
        <div class="flex justify-between"><span>Economics Baseline</span><span class="text-human">●</span></div>
      </div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-ai transition-all hover:shadow-[0_0_15px_rgba(77,171,247,0.1)] cursor-pointer" data-popup data-title="Tier 1: INFO" data-depth="TIER 1 · EXTERNAL SOURCES" data-content="External market and client‑specific data ingestion. the Company JD, Client Persona (Creator‑Led Growth), LinkedIn Conversation History, Competitive Landscape, Public Brand Assets from company. This tier is shared with the Company upon request – it is the 'source context' for the AI's reasoning.">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-full bg-ai/10 flex items-center justify-center font-display font-bold text-ai text-lg">T1</div><h4 class="font-display font-bold">Tier 1: INFO</h4></div>
      <p class="text-xs text-textMuted mb-4">External sources shared between entities.</p>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between border-b border-border/30 pb-2"><span>the Company JD & Briefs</span><span class="text-ai">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>Client Persona / Comm Style</span><span class="text-ai">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>Competitive Landscape</span><span class="text-ai">●</span></div>
        <div class="flex justify-between"><span>Public Brand Assets</span><span class="text-ai">●</span></div>
      </div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-accent transition-all hover:shadow-[0_0_15px_rgba(109,93,211,0.1)] cursor-pointer" data-popup data-title="Tier 2: DATA" data-depth="TIER 2 · PROCESSED INTELLIGENCE" data-content="Synthesized intelligence mapped to stakeholder needs. Four perspectives: HR (risk mitigation, cultural validation), Business (Client's operational leverage, founder alignment), Technical (AI architecture, data privacy protocols), Relational/Human (testimonials, emotional intelligence). Each perspective is a separate document generated by the AI for YOUR team. Click for examples.">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center font-display font-bold text-accent text-lg">T2</div><h4 class="font-display font-bold">Tier 2: DATA</h4></div>
      <p class="text-xs text-textMuted mb-4">Processed intelligence for your team.</p>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between border-b border-border/30 pb-2"><span>HR Perspective</span><span class="text-accent">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>Business (Client) Perspective</span><span class="text-accent">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>Technical Architecture</span><span class="text-accent">●</span></div>
        <div class="flex justify-between"><span>Relational (Human)</span><span class="text-accent">●</span></div>
      </div>
    </div>
  </div>

  <!-- ADDITIONAL: AUTOMATION CAPABILITIES (new visual) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">What Mode B Automates (50+ Assets/Week)</span></div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Resizing & Formatting" data-depth="AUTOMATION" data-content="Automatic resizing for Meta, TikTok, Amazon, email, print, and retail. One source, infinite variants."><div class="text-2xl mb-1">📐</div><div class="text-xs font-bold">Resizing</div><div class="text-[10px] text-textMuted">10+ platforms</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Variation Generation" data-depth="AUTOMATION" data-content="Generate dozens of colour, copy, and layout variations from a single template. 50+ assets/week from one source."><div class="text-2xl mb-1">🎨</div><div class="text-xs font-bold">Variations</div><div class="text-[10px] text-textMuted">50+/week</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="WCAG Compliance" data-depth="AUTOMATION" data-content="Automated contrast, alt text, and accessibility checks. 90%+ pass rate. US market ready."><div class="text-2xl mb-1">♿</div><div class="text-xs font-bold">WCAG Checks</div><div class="text-[10px] text-textMuted">90%+ compliant</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Template Deployment" data-depth="AUTOMATION" data-content="Executable template models – transferable IP that runs locally on your machines. You own the engine."><div class="text-2xl mb-1">📁</div><div class="text-xs font-bold">Deployment</div><div class="text-[10px] text-textMuted">Executable IP</div></div>
  </div>

  <!-- SYMBIOTIC FEEDBACK LOOP DETAIL (new) -->
  <div class="glass-panel p-8 rounded-2xl border border-accent/20 mb-12">
    <h3 class="font-display text-xl font-bold mb-4 text-center">Continuous Improvement Loop</h3>
    <div class="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-textMuted">
      <div class="text-center flex-1"><span class="text-human font-bold">Mode A outputs</span> → strategic constraints</div>
      <div class="text-accent text-2xl">→</div>
      <div class="text-center flex-1"><span class="text-ai font-bold">Mode B executes</span> → 50+ assets/week</div>
      <div class="text-accent text-2xl">→</div>
      <div class="text-center flex-1">Data → <span class="text-accent font-bold">refines Mode A</span> → better insights</div>
    </div>
    <div class="mt-4 text-center text-xs text-textMuted">Every asset generated feeds back into the system, improving future strategic reasoning and execution precision.</div>
  </div>

  <!-- SUMMARY METRICS -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Velocity Multiplier" data-depth="PERFORMANCE" data-content="From 5‑8 variations/week (traditional) to 50+ with bimodal AI. 10x increase in creative output."><div class="text-3xl font-display font-bold text-accent">10x</div><div class="text-[10px] text-textMuted">Velocity Multiplier</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Brand Drift" data-depth="PERFORMANCE" data-content="Infinite context memory and Mode A guardrails ensure zero brand drift. Every asset remains on‑brand, even at scale."><div class="text-3xl font-display font-bold text-accent">0</div><div class="text-[10px] text-textMuted">Brand Drift</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Cost Efficiency" data-depth="PERFORMANCE" data-content="79% cost savings vs traditional agency + senior designer + AI subscriptions. Strategic partnership rate €2,300‑2,500 NET/month + ~$300 API."><div class="text-3xl font-display font-bold text-accent">79%</div><div class="text-[10px] text-textMuted">Cost Savings</div></div>
  </div>
</section>

<!-- ==================== TAB 3: EVIDENCE MATRIX (MASSIVELY EXPANDED – quantifiable impact, visual metrics, case study grids, client categories, performance lifts, skill radar) ==================== -->
<section id="evidence" class="tab-content">
  <div class="mb-16">
    <span class="text-accent text-xs font-bold uppercase tracking-widest bg-accent/10 px-3 py-1 rounded-full">02 / Validation</span>
    <h2 class="font-display text-4xl md:text-5xl font-bold mt-4 mb-6">Evidence‑Based Case Studies</h2>
    <p class="text-textMuted max-w-3xl text-lg">Anchoring claims in quantifiable achievements from enterprise and DTC & Corporateenvironments.</p>
  </div>

  <!-- HEADLINE METRICS (expanded with icons and hover detail) -->
  <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-16">
    <div class="glass-card p-5 rounded-xl text-center cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="200+ Graphic Templates" data-depth="YOKOGAWA EUROPE · 2021-2024" data-content="Designed over 200 graphic templates to ensure consistent branding across all assets. Led the design of Yokogawa's European rebrand effort, creating videos, trade show booths, and prints, elevating online brand awareness by 20% in one year. This demonstrates enterprise‑grade design system scalability.">
      <div class="text-3xl font-display font-bold gradient-text mb-1">200+</div>
      <div class="text-[10px] text-textMuted uppercase tracking-wider">Templates</div>
      <div class="mt-2 text-[10px] text-accent">Yokogawa Europe</div>
    </div>
    <div class="glass-card p-5 rounded-xl text-center cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="12 Countries" data-depth="YOKOGAWA EUROPE" data-content="Created cohesive visual aesthetics and video concepts across 12 European countries. Managed localization, cultural nuances, and brand consistency at scale – directly applicable to the Company's US/EU expansion.">
      <div class="text-3xl font-display font-bold gradient-text mb-1">12</div>
      <div class="text-[10px] text-textMuted uppercase tracking-wider">Countries</div>
      <div class="mt-2 text-[10px] text-accent">Unified Identity</div>
    </div>
    <div class="glass-card p-5 rounded-xl text-center cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="25,000+ Product Visuals" data-depth="MADE.COM · 2020" data-content="Facilitated international collaboration to enhance 25,000+ product visuals, propelling MADE's online shop debut across 5 countries, resulting in a 20% increase in user interaction. 100% on-time delivery. Proves capacity for extreme‑volume asset management.">
      <div class="text-3xl font-display font-bold gradient-text mb-1">25K+</div>
      <div class="text-[10px] text-textMuted uppercase tracking-wider">Visuals</div>
      <div class="mt-2 text-[10px] text-accent">MADE.com</div>
    </div>
    <div class="glass-card p-5 rounded-xl text-center cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="50+ Online Campaigns" data-depth="SKIN MEDIA · 2024" data-content="Led design and publishing of 50+ online marketing campaigns, accelerating sales by 20% for brands like Nikon, Aiper & Pure. Led market launch for Aiper, Pure, and Ninja in Romania. Direct DTC & Corporate  experience.">
      <div class="text-3xl font-display font-bold gradient-text mb-1">50+</div>
      <div class="text-[10px] text-textMuted uppercase tracking-wider">Campaigns</div>
      <div class="mt-2 text-[10px] text-accent">Ninja · Aiper · Pure</div>
    </div>
    <div class="glass-card p-5 rounded-xl text-center cursor-pointer transition-all hover:scale-[1.02]" data-popup data-title="90%+ WCAG Compliance" data-depth="MICROSOFT PCoE · 2025" data-content="Delivered above 90% WCAG compliant designs, passing all Microsoft accessibility audits. Used generative AI to speed content creation for high-priority enterprise proposals supporting Microsoft's ~75% win rate. 8 Microsoft certifications earned Feb 2025.">
      <div class="text-3xl font-display font-bold gradient-text mb-1">90%+</div>
      <div class="text-[10px] text-textMuted uppercase tracking-wider">WCAG Pass</div>
      <div class="mt-2 text-[10px] text-accent">Microsoft PCoE</div>
    </div>
  </div>

  <!-- IMPACT RADAR (new visual – performance across key dimensions) -->
  <div class="glass-panel p-8 rounded-2xl mb-12">
    <h3 class="font-display text-2xl font-bold mb-6 text-center">Competency Impact Radar</h3>
    <div class="flex flex-col md:flex-row gap-8 items-center justify-around">
      <div class="relative w-64 h-64">
        <svg viewBox="0 0 200 200" class="w-full h-full">
          <!-- 6 axes radar -->
          <polygon points="100,20 170,70 170,130 100,180 30,130 30,70" fill="none" stroke="#1E2029" stroke-width="1"/>
          <polygon points="100,50 152,82 152,118 100,150 48,118 48,82" fill="none" stroke="#1E2029" stroke-width="1"/>
          <polygon points="100,80 134,95 134,105 100,120 66,105 66,95" fill="none" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="100" y2="20" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="170" y2="70" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="170" y2="130" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="100" y2="180" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="30" y2="130" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="30" y2="70" stroke="#1E2029" stroke-width="1"/>
          <!-- data polygon (scaled to actual performance) -->
          <polygon points="100,35 160,78 155,125 100,165 45,125 40,78" fill="rgba(109,93,211,0.2)" stroke="#6D5DD3" stroke-width="2"/>
          <text x="100" y="14" fill="#E2E8F0" text-anchor="middle" font-size="8">Scale</text>
          <text x="180" y="75" fill="#E2E8F0" text-anchor="start" font-size="8">DTC</text>
          <text x="180" y="130" fill="#E2E8F0" text-anchor="start" font-size="8">AI/ML</text>
          <text x="100" y="195" fill="#E2E8F0" text-anchor="middle" font-size="8">Psych</text>
          <text x="20" y="130" fill="#E2E8F0" text-anchor="end" font-size="8">Compliance</text>
          <text x="20" y="75" fill="#E2E8F0" text-anchor="end" font-size="8">Systems</text>
        </svg>
      </div>
      <div class="flex-1 space-y-3">
        <div><div class="flex justify-between text-xs mb-1"><span>Scalable Design Systems</span><span class="text-accent">96%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:96%"></div></div></div>
        <div><div class="flex justify-between text-xs mb-1"><span>DTC & CorporateKitchen Category Fluency</span><span class="text-accent">94%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:94%"></div></div></div>
        <div><div class="flex justify-between text-xs mb-1"><span>AI & Automation Integration</span><span class="text-accent">90%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:90%"></div></div></div>
        <div><div class="flex justify-between text-xs mb-1"><span>Behavioral Psychology</span><span class="text-accent">92%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:92%"></div></div></div>
        <div><div class="flex justify-between text-xs mb-1"><span>Accessibility Compliance</span><span class="text-accent">95%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:95%"></div></div></div>
      </div>
    </div>
  </div>

  <!-- DTC & CorporateKITCHEN & HOME CATEGORY MASTERY (enhanced with visual metrics) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">DTC & Corporate Industry Category Mastery</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
    <div class="glass-panel p-6 rounded-xl cursor-pointer transition-all hover:border-human/30" data-popup data-title="Skin Media & AP-ID Agency" data-depth="DTC & CorporatePORTFOLIO" data-content="Brands: Ninja, Crock-Pot, Shark, AIPER, Pure, Nikon. 50+ targeted online campaigns. 25% audience engagement boost. 20% sales acceleration. Direct experience with   brands that directly compete with the Company's category. Led market launches across Meta, TikTok, Amazon, and retail.">
      <h3 class="font-display text-xl font-bold mb-4">Skin Media & AP-ID Agency</h3>
      <div class="space-y-4">
        <div class="flex justify-between items-center border-b border-border/30 pb-2"><span class="font-bold">Ninja</span><span class="pill pill-human">Market Launch</span><span class="text-emerald text-xs">+25% engagement</span></div>
        <div class="flex justify-between items-center border-b border-border/30 pb-2"><span class="font-bold">Crock-Pot</span><span class="pill pill-gold">DTC & CorporateFunnel</span><span class="text-emerald text-xs">Conversion focus</span></div>
        <div class="flex justify-between items-center border-b border-border/30 pb-2"><span class="font-bold">Shark</span><span class="pill pill-ai">Multi-Channel</span><span class="text-emerald text-xs">Meta, TikTok, Amazon</span></div>
        <div class="flex justify-between items-center border-b border-border/30 pb-2"><span class="font-bold">AIPER</span><span class="pill pill-emerald">Engagement +25%</span><span class="text-emerald text-xs">Audience lift</span></div>
        <div class="flex justify-between items-center"><span class="font-bold">MADE.com</span><span class="pill pill-accent">25K+ Assets</span><span class="text-emerald text-xs">100% on-time</span></div>
      </div>
      <div class="mt-4 pt-3 border-t border-border/30 flex justify-between text-xs text-textMuted">
        <span>📈 20% sales acceleration</span>
        <span>🎯 25% engagement boost</span>
        <span>🌐 5 countries</span>
      </div>
    </div>
    <div class="glass-panel p-6 rounded-xl cursor-pointer transition-all hover:border-ai/30" data-popup data-title="Enterprise Design Systems" data-depth="ENTERPRISE PROOF" data-content="Yokogawa: 200+ templates across 12 European countries with unified visual aesthetic. Microsoft PCoE: 90%+ WCAG compliance across 20+ global clients (H&M, La Roche, Erste Group, UAE Ministry of Education, HMS Networks, SITA Africa). Proves ability to build scalable, consistent creative systems essential for brand integrity at scale.">
      <h3 class="font-display text-xl font-bold mb-4">Enterprise Design Systems</h3>
      <div class="space-y-4">
        <div class="flex justify-between items-center border-b border-border/30 pb-2"><span class="font-bold">Yokogawa Europe</span><span class="text-sm text-textMuted">12 Countries</span><span class="text-emerald text-xs">20% brand lift</span></div>
        <div class="flex justify-between items-center border-b border-border/30 pb-2"><span class="font-bold">Microsoft PCoE</span><span class="text-sm text-textMuted">90%+ WCAG</span><span class="text-emerald text-xs">Accessibility</span></div>
        <div class="flex justify-between items-center border-b border-border/30 pb-2"><span class="font-bold">H&M / La Roche</span><span class="text-sm text-textMuted">Enterprise Deals</span><span class="text-emerald text-xs">Global scale</span></div>
        <div class="flex justify-between items-center border-b border-border/30 pb-2"><span class="font-bold">UAE Ministry</span><span class="text-sm text-textMuted">Gov. Compliance</span><span class="text-emerald text-xs">Regulated</span></div>
        <div class="flex justify-between items-center"><span class="font-bold">Romexpo</span><span class="text-sm text-textMuted">10+ Rebrands</span><span class="text-emerald text-xs">30% visibility</span></div>
      </div>
    </div>
  </div>

  <!-- ENTERPRISE & DTC & CorporateIMPACT MATRIX (expanded with icons) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Enterprise & DTC & CorporateImpact Matrix</span></div>
  <div class="glass-panel rounded-2xl overflow-hidden mb-12">
    <table class="w-full text-sm">
      <thead class="bg-surface/50 border-b border-border"><tr><th class="text-left p-4 font-display font-bold text-textMuted uppercase text-xs">Company / Project</th><th class="text-left p-4 font-display font-bold text-textMuted uppercase text-xs hidden md:table-cell">Key Responsibility</th><th class="text-left p-4 font-display font-bold text-textMuted uppercase text-xs">Quantifiable Achievement</th><th class="text-left p-4 font-display font-bold text-textMuted uppercase text-xs hidden lg:table-cell">Direct Relevance</th></tr></thead>
      <tbody class="divide-y divide-border/30">
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Shipley (Microsoft PCoE)" data-depth="ENTERPRISE" data-content="Senior Designer for Microsoft. 20+ global clients including H&M, La Roche, Erste Group, UAE Ministry. Delivered 90%+ WCAG compliant designs. 75%+ win rate support. 15% evaluator engagement boost."><td class="p-4 font-semibold">Shipley (MS PCoE) <span class="pill pill-accent ml-2">Enterprise</span></td><td class="p-4 text-textMuted text-xs hidden md:table-cell">Senior Designer for Microsoft</td><td class="p-4 text-textMuted text-xs">20+ clients, 90%+ WCAG, 75%+ win rate</td><td class="p-4 text-xs text-accent italic hidden lg:table-cell">Global compliance & scale</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Yokogawa Europe" data-depth="SYSTEMS" data-content="Design System Architect. 200+ templates across 12 countries. 20% brand awareness lift in 1 year. Unified visual identity across European markets."><td class="p-4 font-semibold">Yokogawa Europe <span class="pill pill-ai ml-2">Systems</span></td><td class="p-4 text-textMuted text-xs hidden md:table-cell">Design System Architect</td><td class="p-4 text-textMuted text-xs">200+ templates, 12 countries, 20% brand lift</td><td class="p-4 text-xs text-accent italic hidden lg:table-cell">Scalable templates</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Skin Media" data-depth="DTC" data-content="Lead Visual Strategist. 50+ campaigns for Ninja, Aiper, Pure. 20% sales acceleration. 25% engagement lift. Market launches in Romania."><td class="p-4 font-semibold">Skin Media <span class="pill pill-human ml-2">DTC</span></td><td class="p-4 text-textMuted text-xs hidden md:table-cell">Lead Visual Strategist</td><td class="p-4 text-textMuted text-xs">50+ campaigns, 20% sales, 25% engagement</td><td class="p-4 text-xs text-accent italic hidden lg:table-cell">Category fluency</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="MADE.com" data-depth="E-COMMERCE" data-content="E-commerce Visuals Specialist. 25,000+ product visuals, 5 countries, 100% on-time delivery. 20% UX interaction lift. Full product database refresh."><td class="p-4 font-semibold">MADE.com <span class="pill pill-gold ml-2">E-com</span></td><td class="p-4 text-textMuted text-xs hidden md:table-cell">E-commerce Visuals</td><td class="p-4 text-textMuted text-xs">25k+ visuals, 5 countries, 100% on-time</td><td class="p-4 text-xs text-accent italic hidden lg:table-cell">High‑volume asset mgmt</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Pathwwway" data-depth="UI/UX" data-content="UI Design & Campaigns. 35-40% user engagement increase. 30% bounce rate reduction. Web layout redesign and promotional materials."><td class="p-4 font-semibold">Pathwwway <span class="pill pill-emerald ml-2">UI/UX</span></td><td class="p-4 text-textMuted text-xs hidden md:table-cell">UI Design & Campaigns</td><td class="p-4 text-textMuted text-xs">35-40% engagement, 30% bounce reduction</td><td class="p-4 text-xs text-accent italic hidden lg:table-cell">UX optimization</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Romexpo" data-depth="PRINT" data-content="Multimedia & Rebranding. 10+ trademark rebrands. 30% production time cut. 20% cost reduction. Enhanced visibility across multiple platforms."><td class="p-4 font-semibold">Romexpo <span class="pill pill-accent ml-2">Print</span></td><td class="p-4 text-textMuted text-xs hidden md:table-cell">Multimedia & Rebranding</td><td class="p-4 text-textMuted text-xs">10+ rebrands, 30% time cut, 20% cost reduction</td><td class="p-4 text-xs text-accent italic hidden lg:table-cell">Efficiency at scale</td></tr>
      </tbody>
    </table>
  </div>

  <!-- PERFORMANCE LIFTS (new visual – engagement and sales metrics) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Documented Performance Lifts</span></div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
    <div class="glass-card p-5 rounded-xl text-center cursor-pointer" data-popup data-title="Engagement Lifts" data-depth="PERFORMANCE" data-content="Consistent 20-40% increase in user engagement across multiple campaigns and platforms (Skin Media, Nikon, Aiper). Proven ability to optimize creative for higher interaction rates."><div class="text-3xl font-display font-bold text-emerald mb-1">20-40%</div><div class="text-[10px] text-textMuted uppercase">Engagement Lift</div><div class="text-xs text-accent mt-2">Skin Media · Nikon</div></div>
    <div class="glass-card p-5 rounded-xl text-center cursor-pointer" data-popup data-title="Sales Acceleration" data-depth="PERFORMANCE" data-content="20% sales acceleration for brands like Ninja, Aiper, Pure through conversion‑optimized creative and funnel‑driven design."><div class="text-3xl font-display font-bold text-emerald mb-1">20%</div><div class="text-[10px] text-textMuted uppercase">Sales Acceleration</div><div class="text-xs text-accent mt-2">DTC & Corporatecampaigns</div></div>
    <div class="glass-card p-5 rounded-xl text-center cursor-pointer" data-popup data-title="Win Rate Support" data-depth="PERFORMANCE" data-content="Supported Microsoft's ~75% win rate at PCoE through strategic proposal design, accessibility compliance, and visual storytelling."><div class="text-3xl font-display font-bold text-emerald mb-1">75%</div><div class="text-[10px] text-textMuted uppercase">Win Rate Support</div><div class="text-xs text-accent mt-2">Microsoft PCoE</div></div>
  </div>

  <!-- GLOBAL CLIENT ROSTER (categorized visual) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Global Client Roster</span></div>
  <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-12">
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Microsoft" data-depth="ENTERPRISE" data-content="Microsoft PCoE – 90%+ WCAG compliance, 75%+ win rate support, 8 Microsoft certifications.">Microsoft</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="H&M" data-depth="ENTERPRISE" data-content="Enterprise proposal design for global fashion brand through Microsoft PCoE.">H&M</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="La Roche" data-depth="ENTERPRISE" data-content="Pharmaceutical client – high‑compliance visual proposals.">La Roche</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Erste Group" data-depth="ENTERPRISE" data-content="Banking sector – data‑driven presentation design.">Erste Group</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="UAE Ministry" data-depth="ENTERPRISE" data-content="Government – WCAG compliant, accessibility‑first design.">UAE Ministry</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Ninja" data-depth="DTC" data-content="Market launch in Romania, 50+ campaigns, 25% engagement boost.">Ninja</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Crock-Pot" data-depth="DTC" data-content="DTC & Corporatefunnel optimization,   category.">Crock-Pot</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Shark" data-depth="DTC" data-content="Multi‑channel creative (Meta, TikTok, Amazon).">Shark</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="AIPER" data-depth="DTC" data-content="Brand launch, 25% engagement lift.">AIPER</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="MADE.com" data-depth="E-COMMERCE" data-content="25,000+ product visuals, 5 countries, 20% UX lift.">MADE.com</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Nikon" data-depth="DTC" data-content="10+ campaigns, increased brand visibility and sales.">Nikon</div>
    <div class="glass-card p-3 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Yokogawa" data-depth="ENTERPRISE" data-content="200+ templates, 12 countries, 20% brand awareness lift.">Yokogawa</div>
  </div>

  <!-- SKILLS & TOOLS MATRIX (new) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Core Tools & Technologies</span></div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
    <div class="glass-card p-3 rounded-lg text-center text-xs cursor-pointer" data-popup data-title="Figma" data-depth="TOOL" data-content="Expert proficiency. Used for design systems, component libraries, and collaborative workflows. Built 200+ templates at Yokogawa."><span class="font-bold">Figma</span> <span class="text-emerald ml-1">★★★★★</span></div>
    <div class="glass-card p-3 rounded-lg text-center text-xs cursor-pointer" data-popup data-title="Adobe Creative Suite" data-depth="TOOL" data-content="Photoshop, Illustrator, InDesign, AfterEffects, LightRoom. 15+ years experience."><span class="font-bold">Adobe CC</span> <span class="text-emerald ml-1">★★★★★</span></div>
    <div class="glass-card p-3 rounded-lg text-center text-xs cursor-pointer" data-popup data-title="CapCut / After Effects" data-depth="TOOL" data-content="Video editing and motion graphics for TikTok, short‑form DTC & Corporatecontent."><span class="font-bold">CapCut · AE</span> <span class="text-emerald ml-1">★★★★☆</span></div>
    <div class="glass-card p-3 rounded-lg text-center text-xs cursor-pointer" data-popup data-title="AI Prompting" data-depth="TOOL" data-content="Local LLM digital twin, Adobe Firefly, Midjourney, ChatGPT – integrated into bimodal workflow."><span class="font-bold">AI Tools</span> <span class="text-emerald ml-1">★★★★★</span></div>
  </div>

  <!-- MICROSOFT CERTIFICATIONS HIGHLIGHT (new) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Microsoft Certifications (Feb 2025)</span></div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-12">
    <div class="glass-card p-2 rounded-lg text-center text-[11px] cursor-pointer" data-popup data-title="Accessibility Evaluation & Testing" data-depth="MS CERT" data-content="Validates ability to audit and evaluate design output against WCAG standards.">✔ Accessibility Evaluation</div>
    <div class="glass-card p-2 rounded-lg text-center text-[11px] cursor-pointer" data-popup data-title="Accessibility Fundamentals" data-depth="MS CERT" data-content="Foundational accessibility principles, signed by Satya Nadella.">✔ Accessibility Fundamentals</div>
    <div class="glass-card p-2 rounded-lg text-center text-[11px] cursor-pointer" data-popup data-title="Create Accessible AI Experiences" data-depth="MS CERT" data-content="Ethical, inclusive AI implementation – directly relevant to AI Digital Twin.">✔ Accessible AI</div>
    <div class="glass-card p-2 rounded-lg text-center text-[11px] cursor-pointer" data-popup data-title="Fundamental AI Concepts" data-depth="MS CERT" data-content="Foundational AI literacy for LLM projects.">✔ AI Concepts</div>
    <div class="glass-card p-2 rounded-lg text-center text-[11px] cursor-pointer" data-popup data-title="Build Accessible SharePoint Sites" data-depth="MS CERT" data-content="Enterprise SharePoint accessibility – internal system compliance.">✔ SharePoint Access</div>
    <div class="glass-card p-2 rounded-lg text-center text-[11px] cursor-pointer" data-popup data-title="Create Accessible Content" data-depth="MS CERT" data-content="WCAG content compliance.">✔ Accessible Content</div>
    <div class="glass-card p-2 rounded-lg text-center text-[11px] cursor-pointer" data-popup data-title="Introduction to Accessibility" data-depth="MS CERT" data-content="WCAG principles foundation.">✔ Intro Accessibility</div>
    <div class="glass-card p-2 rounded-lg text-center text-[11px] cursor-pointer" data-popup data-title="Web Accessibility Principles" data-depth="MS CERT" data-content="WCAG 2.1 mastery – ADA compliance for US market.">✔ WCAG Guidelines</div>
  </div>

  <!-- SOCIAL PROOF ARMOR (expanded with competency mapping) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Social Proof Armor · Validated by Colleagues</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div class="glass-card p-6 rounded-xl border-t-2 border-human cursor-pointer" data-popup data-title="Luca Costea · Copywriter" data-depth="TESTIMONIAL" data-content="'Hard projects were made easy... input goes beyond pure design skills to brainstorming, good time management and developing the right creative concept.' Validates strategic collaboration and cross‑functional teamwork.">
      <p class="italic text-textMuted mb-4 text-sm">"Hard projects were made easy... input goes beyond pure design skills to brainstorming."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">LC</div><div><p class="font-bold text-xs">Luca Costea</p><p class="text-[10px] text-textMuted">Copywriter</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-ai cursor-pointer" data-popup data-title="Anca Buzatu · Head of Marketing" data-depth="TESTIMONIAL" data-content="'Alexandru is an 'one of a kind' designer who is constantly striving to be more creative... and more efficient in everything he does.' Highlights the rare balance of creativity and operational efficiency.">
      <p class="italic text-textMuted mb-4 text-sm">"Alexandru is an 'one of a kind' designer... more efficient in everything he does."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">AB</div><div><p class="font-bold text-xs">Anca Buzatu</p><p class="text-[10px] text-textMuted">Head of Marketing</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-gold cursor-pointer" data-popup data-title="Alexandru Păun · CEO Topo Delta Pad" data-depth="TESTIMONIAL" data-content="'Alex didn't just offer me a drawing... he offered consulting offered by an artist!' Proves strategic consultancy beyond pure design execution.">
      <p class="italic text-textMuted mb-4 text-sm">"Alex didn't just offer me a drawing... he offered consulting offered by an artist!"</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">AP</div><div><p class="font-bold text-xs">Alexandru Păun</p><p class="text-[10px] text-textMuted">CEO, Topo Delta Pad</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-emerald cursor-pointer" data-popup data-title="Vișan Miu Tudor · NGO Secretary" data-depth="TESTIMONIAL" data-content="'You will always feel that he is there, listening... you can't help but think of him as a friend.' Demonstrates exceptional active listening and emotional intelligence.">
      <p class="italic text-textMuted mb-4 text-sm">"You will always feel that he is there, listening... you can't help but think of him as a friend."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">VT</div><div><p class="font-bold text-xs">Vișan Miu Tudor</p><p class="text-[10px] text-textMuted">NGO Secretary</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-accent cursor-pointer" data-popup data-title="Bogdan Bârligea · Marketing Specialist" data-depth="TESTIMONIAL" data-content="'As a person, Alex is always an honest man, passionate storyteller and caring companion.' Reinforces integrity, passion, and empathy.">
      <p class="italic text-textMuted mb-4 text-sm">"As a person, Alex is always an honest man, passionate storyteller and caring companion."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">BB</div><div><p class="font-bold text-xs">Bogdan Bârligea</p><p class="text-[10px] text-textMuted">Marketing Specialist</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-human cursor-pointer" data-popup data-title="Liliana Costache · Content Manager" data-depth="TESTIMONIAL" data-content="'Complies with deadlines often under pressure... His research is precise and suggestions original.' Validates reliability and performance under pressure.">
      <p class="italic text-textMuted mb-4 text-sm">"Complies with deadlines often under pressure... His research is precise and suggestions original."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">LC</div><div><p class="font-bold text-xs">Liliana Costache</p><p class="text-[10px] text-textMuted">Content Manager</p></div></div>
    </div>
  </div>

  <!-- SUMMARY CALL-OUT -->
  <div class="glass-panel p-8 rounded-2xl text-center border border-accent/20 mt-8">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-accent/30 bg-accent/5 text-accent text-xs font-mono mb-4"><span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>VERIFIED · QUANTIFIABLE · SCALABLE</div>
    <p class="text-textMuted max-w-2xl mx-auto text-sm">Every claim is anchored in documented metrics from enterprise, DTC, and accessibility contexts. Click any card for detailed proof.</p>
  </div>
</section>

<!-- ==================== TAB 4: ROADMAP (MASSIVELY EXPANDED – full timeline, sub‑phases, risk mitigation, deliverables, success metrics, visual flow) ==================== -->
<section id="roadmap" class="tab-content">
  <div class="mb-16 text-center">
    <span class="text-accent text-xs font-bold uppercase tracking-widest bg-accent/10 px-3 py-1 rounded-full">03 / Execution</span>
    <h2 class="font-display text-4xl md:text-5xl font-bold mt-4 mb-6">Implementation Roadmap</h2>
    <p class="text-textMuted max-w-2xl mx-auto text-lg">From Day 1 Sandbox to Long‑Term Symbiosis. A de‑risked, phased path to proprietary creative infrastructure.</p>
  </div>

  <!-- PHASE CARDS (enhanced with icons and sub‑metrics) -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-16">
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-human transition-all hover:shadow-[0_0_20px_rgba(255,107,107,0.2)] cursor-pointer" data-popup data-title="Phase 1: Sandbox Development" data-depth="WEEKS 1-4 · ZERO COST" data-content="Use my existing local AI as a secure test environment. Ingest every piece of public data on the Company to build a 'the Company Brand Brain.' Zero infrastructure cost to you. Success metrics: 90% of generated templates require less than 5 minutes of human refinement. Weekly alignment reviews. Output: documented brand DNA, template architecture prototype.">
      <div class="flex items-center gap-2 mb-3"><span class="pill pill-human">PHASE 1</span><span class="text-xs text-textMuted font-mono">WEEKS 1-4</span></div>
      <div class="flex items-center gap-3 mb-3"><div class="w-10 h-10 rounded-lg bg-human/10 flex items-center justify-center text-human text-xl">🔬</div><h3 class="font-display text-xl font-bold text-human mb-0">Sandbox Development</h3></div>
      <p class="text-xs text-textMuted mb-4">Build 'the Company Brand Brain' at zero cost to you. Validate AI reasoning before any infrastructure commitment.</p>
      <div class="grid grid-cols-2 gap-2 text-center text-xs mb-3">
        <div class="bg-surface/50 rounded p-2"><div class="font-bold text-white">85-90%</div><div class="text-textMuted">DNA Capture</div></div>
        <div class="bg-surface/50 rounded p-2"><div class="font-bold text-white">€0</div><div class="text-textMuted">Your Cost</div></div>
      </div>
      <div class="flex flex-wrap gap-1 mt-2"><span class="text-[10px] bg-human/10 text-human px-2 py-0.5 rounded">Data Ingestion</span><span class="text-[10px] bg-human/10 text-human px-2 py-0.5 rounded">Template Prototype</span><span class="text-[10px] bg-human/10 text-human px-2 py-0.5 rounded">Brand DNA Map</span></div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-ai transition-all hover:shadow-[0_0_20px_rgba(77,171,247,0.2)] cursor-pointer" data-popup data-title="Phase 2: Private Infrastructure Migration" data-depth="MONTH 2 · IP TRANSFER" data-content="Deploy validated template model to the Company's private servers. Complete data sovereignty. Executable IP transfer. You own the engine, not just the fuel. Migration includes: local LLM setup, brand tokenization, API gateway configuration, and access control policies.">
      <div class="flex items-center gap-2 mb-3"><span class="pill pill-ai">PHASE 2</span><span class="text-xs text-textMuted font-mono">MONTH 2</span></div>
      <div class="flex items-center gap-3 mb-3"><div class="w-10 h-10 rounded-lg bg-ai/10 flex items-center justify-center text-ai text-xl">🚀</div><h3 class="font-display text-xl font-bold text-ai mb-0">Infrastructure Migration</h3></div>
      <p class="text-xs text-textMuted mb-4">Complete data sovereignty on your servers. Air‑gapped, private, fully owned.</p>
      <div class="grid grid-cols-2 gap-2 text-center text-xs mb-3">
        <div class="bg-surface/50 rounded p-2"><div class="font-bold text-white">100%</div><div class="text-textMuted">Privacy</div></div>
        <div class="bg-surface/50 rounded p-2"><div class="font-bold text-white">~$300</div><div class="text-textMuted">API/mo</div></div>
      </div>
      <div class="flex flex-wrap gap-1 mt-2"><span class="text-[10px] bg-ai/10 text-ai px-2 py-0.5 rounded">Air‑Gapped</span><span class="text-[10px] bg-ai/10 text-ai px-2 py-0.5 rounded">IP Transfer</span><span class="text-[10px] bg-ai/10 text-ai px-2 py-0.5 rounded">Local LLM</span></div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-accent transition-all hover:shadow-[0_0_20px_rgba(109,93,211,0.2)] cursor-pointer" data-popup data-title="Phase 3: Symbiotic Co‑Evolution" data-depth="YEAR 1+ · MUTUAL R&D" data-content="I help you develop a local AI for branding; you help me refine an Art Direction mechanism that understands beyond any single brand. Mutual R&D. Joint innovation roadmap. Quarterly strategic reviews. Perpetual evolution of the creative engine.">
      <div class="flex items-center gap-2 mb-3"><span class="pill pill-accent">PHASE 3</span><span class="text-xs text-textMuted font-mono">YEAR 1+</span></div>
      <div class="flex items-center gap-3 mb-3"><div class="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-xl">♾️</div><h3 class="font-display text-xl font-bold text-accent mb-0">Symbiotic Co‑Evolution</h3></div>
      <p class="text-xs text-textMuted mb-4">Mutual R&D. Perpetual growth engine. 5‑year horizon with shared intelligence.</p>
      <div class="grid grid-cols-2 gap-2 text-center text-xs mb-3">
        <div class="bg-surface/50 rounded p-2"><div class="font-bold text-white">5+ Yrs</div><div class="text-textMuted">Horizon</div></div>
        <div class="bg-surface/50 rounded p-2"><div class="font-bold text-white">∞</div><div class="text-textMuted">Memory</div></div>
      </div>
      <div class="flex flex-wrap gap-1 mt-2"><span class="text-[10px] bg-accent/10 text-accent px-2 py-0.5 rounded">R&D Partnership</span><span class="text-[10px] bg-accent/10 text-accent px-2 py-0.5 rounded">Shared IP</span><span class="text-[10px] bg-accent/10 text-accent px-2 py-0.5 rounded">Quarterly Sync</span></div>
    </div>
  </div>

  <!-- DETAILED TIMELINE (Gantt‑style visual) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Detailed Implementation Timeline</span></div>
  <div class="glass-panel p-6 rounded-2xl mb-12">
    <div class="relative overflow-x-auto">
      <div class="min-w-[600px]">
        <!-- headers -->
        <div class="grid grid-cols-12 gap-2 mb-3 text-[10px] text-textMuted font-mono">
          <div class="col-span-3">Activity</div><div class="col-span-1 text-center">W1</div><div class="col-span-1 text-center">W2</div><div class="col-span-1 text-center">W3</div><div class="col-span-1 text-center">W4</div><div class="col-span-1 text-center">W5</div><div class="col-span-1 text-center">W6</div><div class="col-span-1 text-center">W7</div><div class="col-span-1 text-center">W8</div><div class="col-span-1 text-center">Q3+</div>
        </div>
        <!-- Phase 1 rows -->
        <div class="grid grid-cols-12 gap-2 items-center mb-2">
          <div class="col-span-3 text-sm font-semibold text-human">Data Ingestion</div>
          <div class="col-span-4 bg-human/20 rounded h-6 flex items-center justify-center text-[10px]">Phase 1</div>
          <div class="col-span-5"></div>
        </div>
        <div class="grid grid-cols-12 gap-2 items-center mb-2">
          <div class="col-span-3 text-sm font-semibold text-human">Template Prototyping</div>
          <div class="col-span-3 bg-human/20 rounded h-6 flex items-center justify-center text-[10px]">Phase 1</div>
          <div class="col-span-1 bg-ai/10 rounded h-6"></div>
          <div class="col-span-5"></div>
        </div>
        <div class="grid grid-cols-12 gap-2 items-center mb-2">
          <div class="col-span-3 text-sm font-semibold text-ai">Local LLM Setup</div>
          <div class="col-span-4"></div>
          <div class="col-span-3 bg-ai/20 rounded h-6 flex items-center justify-center text-[10px]">Phase 2</div>
          <div class="col-span-2"></div>
        </div>
        <div class="grid grid-cols-12 gap-2 items-center mb-2">
          <div class="col-span-3 text-sm font-semibold text-ai">IP Migration</div>
          <div class="col-span-4"></div>
          <div class="col-span-2 bg-ai/20 rounded h-6 flex items-center justify-center text-[10px]">Phase 2</div>
          <div class="col-span-3"></div>
        </div>
        <div class="grid grid-cols-12 gap-2 items-center mb-2">
          <div class="col-span-3 text-sm font-semibold text-accent">Continuous R&D</div>
          <div class="col-span-8"></div>
          <div class="col-span-1 bg-accent/20 rounded h-6 flex items-center justify-center text-[10px]">∞</div>
        </div>
      </div>
    </div>
    <div class="flex justify-between mt-6 pt-4 border-t border-border/30 text-xs">
      <div class="flex items-center gap-2"><span class="w-3 h-3 rounded-full bg-human"></span> Phase 1 (Weeks 1-4)</div>
      <div class="flex items-center gap-2"><span class="w-3 h-3 rounded-full bg-ai"></span> Phase 2 (Month 2)</div>
      <div class="flex items-center gap-2"><span class="w-3 h-3 rounded-full bg-accent"></span> Phase 3 (Year 1+)</div>
    </div>
  </div>

  <!-- PHASE DETAILS with sub‑steps, deliverables, success metrics -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
    <!-- Phase 1 detailed -->
    <div class="glass-panel p-6 rounded-2xl">
      <h3 class="font-display text-xl font-bold text-human mb-4 flex items-center gap-2"><span>🔬</span> Phase 1: Sandbox</h3>
      <div class="space-y-4">
        <div><div class="text-xs font-bold text-white mb-1">Sub‑steps</div><ul class="text-xs text-textMuted space-y-1"><li>• Public data scraping (web, LinkedIn, TikTok)</li><li>• Brand syntax analysis & tokenization</li><li>• Mode A strategic framework calibration</li><li>• Template system architecture design</li></ul></div>
        <div><div class="text-xs font-bold text-white mb-1">Deliverables</div><ul class="text-xs text-textMuted space-y-1"><li>• the Company Brand Brain (vector store)</li><li>• 5+ template prototypes</li><li>• Mode A strategic briefs (3)</li><li>• Sandbox validation report</li></ul></div>
        <div><div class="text-xs font-bold text-white mb-1">Success Metrics</div><ul class="text-xs text-textMuted space-y-1"><li>• ≥85% brand DNA coverage</li><li>• <5 min human refinement per asset</li><li>• Weekly alignment sign‑off</li></ul></div>
      </div>
    </div>
    <!-- Phase 2 detailed -->
    <div class="glass-panel p-6 rounded-2xl">
      <h3 class="font-display text-xl font-bold text-ai mb-4 flex items-center gap-2"><span>🚀</span> Phase 2: Migration</h3>
      <div class="space-y-4">
        <div><div class="text-xs font-bold text-white mb-1">Sub‑steps</div><ul class="text-xs text-textMuted space-y-1"><li>• Air‑gapped local LLM deployment</li><li>• Brand model transfer & encryption</li><li>• API gateway configuration</li><li>• Access control & logging setup</li></ul></div>
        <div><div class="text-xs font-bold text-white mb-1">Deliverables</div><ul class="text-xs text-textMuted space-y-1"><li>• Fully configured local AI instance</li><li>• Executable template model (IP)</li><li>• Deployment & runbook docs</li><li>• 24/7 monitoring dashboard</li></ul></div>
        <div><div class="text-xs font-bold text-white mb-1">Success Metrics</div><ul class="text-xs text-textMuted space-y-1"><li>• 100% data privacy compliance</li><li>• <1 sec inference latency</li><li>• 99.9% uptime (local)</li></ul></div>
      </div>
    </div>
    <!-- Phase 3 detailed -->
    <div class="glass-panel p-6 rounded-2xl">
      <h3 class="font-display text-xl font-bold text-accent mb-4 flex items-center gap-2"><span>♾️</span> Phase 3: Symbiosis</h3>
      <div class="space-y-4">
        <div><div class="text-xs font-bold text-white mb-1">Sub‑steps</div><ul class="text-xs text-textMuted space-y-1"><li>• Quarterly strategic reviews</li><li>• Joint R&D roadmap updates</li><li>• Cross‑training & knowledge transfer</li><li>• Performance benchmarking</li></ul></div>
        <div><div class="text-xs font-bold text-white mb-1">Deliverables</div><ul class="text-xs text-textMuted space-y-1"><li>• Shared innovation backlog</li><li>• Quarterly evolution reports</li><li>• the Company‑tuned Art Direction OS</li></ul></div>
        <div><div class="text-xs font-bold text-white mb-1">Success Metrics</div><ul class="text-xs text-textMuted space-y-1"><li>• 10x creative velocity (vs baseline)</li><li>• Zero brand drift</li><li>• 79% cost savings maintained</li></ul></div>
      </div>
    </div>
  </div>

  <!-- RISK MITIGATION TABLE (new) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Risk Mitigation & Governance</span></div>
  <div class="glass-panel rounded-2xl overflow-hidden mb-12">
    <table class="w-full text-sm">
      <thead class="bg-surface/50 border-b border-border"><tr><th class="text-left p-3 font-display font-bold text-textMuted uppercase text-xs">Risk</th><th class="text-left p-3 font-display font-bold text-textMuted uppercase text-xs">Mitigation Strategy</th><th class="text-left p-3 font-display font-bold text-textMuted uppercase text-xs">Owner</th></tr></thead>
      <tbody class="divide-y divide-border/30">
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Data Privacy Risk" data-depth="MITIGATION" data-content="All proprietary data processed locally, air‑gapped. Only public data ingested. Client data never leaves the Company's infrastructure after Phase 2. Sandbox uses candidate's hardware, no external transfers."><td class="p-3 font-semibold">Data leakage</td><td class="p-3 text-xs text-textMuted">Air‑gapped local LLM, public‑data‑only training, sandbox isolation</td><td class="p-3 text-xs">Alex + the Company IT</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Vendor Lock‑in" data-depth="MITIGATION" data-content="Transferable executable template model. After Phase 2, the Company owns the engine decoupled from Alex's infrastructure. Can run independently, update via internal team."><td class="p-3 font-semibold">Vendor lock‑in</td><td class="p-3 text-xs text-textMuted">Executable IP transfer, decoupled infrastructure, open standards</td><td class="p-3 text-xs">Alex</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Brand Drift" data-depth="MITIGATION" data-content="Infinite memory context preserves brand guidelines. Mode A strategic constraints enforce consistency. Automated guardrails against off‑brand outputs. Human‑in‑the‑loop approval gates."><td class="p-3 font-semibold">Brand drift</td><td class="p-3 text-xs text-textMuted">Infinite memory, Mode A guardrails, human review</td><td class="p-3 text-xs">Alex + Creative Team</td></tr>
        <tr class="hover:bg-surface/30 transition-colors cursor-pointer" data-popup data-title="Performance Degradation" data-depth="MITIGATION" data-content="Regular model retraining on new public data. Quarterly performance reviews. Rollback capability. Local compute scaling options."><td class="p-3 font-semibold">AI performance decay</td><td class="p-3 text-xs text-textMuted">Continuous retraining, benchmarking, fallback manual processes</td><td class="p-3 text-xs">Alex</td></tr>
      </tbody>
    </table>
  </div>

  <!-- COST-BENEFIT ROI (expanded) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Cost‑Benefit ROI Gauge</span></div>
  <div class="glass-panel p-8 rounded-2xl flex flex-col md:flex-row items-center justify-around gap-8 mb-12" data-popup data-title="Traditional vs. Bimodal Approach" data-depth="ECONOMIC FRAMEWORK" data-content="Traditional: ~$14,500/mo (Agency + Sr. Designer + AI Subs). Alex + AI Symbiosis: ~$3,050/mo. 79% cost savings. 10x velocity. Zero brand drift. Additional savings: reduced revision cycles, faster time‑to‑market, higher A/B test throughput.">
    <div class="text-center">
      <div class="metric-ring mx-auto relative w-32 h-32">
        <svg viewBox="0 0 120 120" class="w-full h-full"><circle class="ring-bg" cx="60" cy="60" r="50"></circle><circle class="ring-fill" cx="60" cy="60" r="50" stroke="#10B981" style="stroke-dashoffset:66;"></circle></svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center"><div class="text-2xl font-display font-bold">79%</div><div class="text-[10px] text-textMuted uppercase">Savings</div></div>
      </div>
    </div>
    <div class="flex-1 max-w-md">
      <h3 class="font-display text-2xl font-bold mb-4">Traditional vs. Bimodal</h3>
      <div class="space-y-3 text-sm">
        <div class="flex justify-between items-center"><span class="text-textMuted">Traditional (Agency + Sr. Designer + AI Subs)</span><span class="font-mono text-human">$14,500/mo</span></div>
        <div class="flex justify-between items-center"><span class="text-textMuted">Alex + AI Symbiosis</span><span class="font-mono text-emerald">~$3,050/mo</span></div>
        <div class="pt-3 border-t border-border/30 flex justify-between items-center font-bold"><span>Velocity Multiplier</span><span class="text-emerald">10x Faster</span></div>
        <div class="flex justify-between items-center font-bold"><span>Brand Drift Risk</span><span class="text-emerald">ZERO</span></div>
      </div>
    </div>
  </div>

  <!-- COMPARISON TABLES (enhanced with visual bars) -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
    <div class="glass-card p-6 rounded-xl cursor-pointer" data-popup data-title="Traditional Cost Breakdown" data-depth="DETAIL" data-content="Senior Designer (market rate): $6,000/mo. Agency retainer: $8,000/mo (creative concept + production). AI subscriptions: $500/mo (Midjourney, ChatGPT, etc.). Hidden costs: revision cycles, approval delays, brand drift. Total ~$14,500/mo.">
      <h4 class="font-display font-bold mb-4 text-textMuted">Traditional Approach</h4>
      <div class="space-y-3">
        <div><div class="flex justify-between text-sm"><span>Senior Designer (Market Rate)</span><span class="text-human">$6,000/mo</span></div><div class="progress-bar mt-1"><div class="progress-fill bg-human" style="width:41%"></div></div></div>
        <div><div class="flex justify-between text-sm"><span>Agency Retainer</span><span class="text-human">$8,000/mo</span></div><div class="progress-bar mt-1"><div class="progress-fill bg-human" style="width:55%"></div></div></div>
        <div><div class="flex justify-between text-sm"><span>AI Tool Subscriptions</span><span class="text-human">$500/mo</span></div><div class="progress-bar mt-1"><div class="progress-fill bg-human" style="width:3%"></div></div></div>
        <div class="pt-3 border-t border-border/30 flex justify-between font-bold"><span>Monthly Cost</span><span class="text-human text-lg">$14,500</span></div>
      </div>
    </div>
    <div class="glass-card p-6 rounded-xl border border-emerald/30 cursor-pointer" data-popup data-title="Bimodal Cost Breakdown" data-depth="DETAIL" data-content="Strategic partnership rate: €2,500/mo (approx $2,750). AI Infrastructure (API): ~$300/mo (local inference, occasional cloud models). Additional: electricity (~$50). Zero agency fees. Zero brand drift. 10x output. Total ~$3,050/mo.">
      <h4 class="font-display font-bold mb-4 text-emerald">Alex + AI Approach</h4>
      <div class="space-y-3">
        <div><div class="flex justify-between text-sm"><span>Strategic Partnership Rate</span><span class="text-emerald">€2,500/mo</span></div><div class="progress-bar mt-1"><div class="progress-fill bg-emerald" style="width:82%"></div></div></div>
        <div><div class="flex justify-between text-sm"><span>AI Infrastructure (API)</span><span class="text-emerald">~$300/mo</span></div><div class="progress-bar mt-1"><div class="progress-fill bg-emerald" style="width:10%"></div></div></div>
        <div><div class="flex justify-between text-sm"><span>Brand Drift Risk</span><span class="text-emerald">ZERO</span></div><div class="progress-bar mt-1"><div class="progress-fill bg-emerald" style="width:0%"></div></div></div>
        <div class="pt-3 border-t border-border/30 flex justify-between font-bold"><span>Monthly Cost</span><span class="text-emerald text-lg">~$3,050</span></div>
      </div>
    </div>
  </div>

  <!-- ADDITIONAL ROI METRICS (new) -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Time Savings" data-depth="ROI" data-content="Automated variation generation reduces manual production time by ~70%. Senior designer focuses on strategy, not resizing."><div class="text-3xl font-display font-bold text-emerald">70%</div><div class="text-[10px] text-textMuted">Time Saved</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="A/B Test Throughput" data-depth="ROI" data-content="From 5-8 variations/week to 50+. More experiments, faster winners."><div class="text-3xl font-display font-bold text-emerald">10x</div><div class="text-[10px] text-textMuted">A/B Test Volume</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Compliance Coverage" data-depth="ROI" data-content="WCAG accessibility built into every asset. Reduces legal risk, expands audience."><div class="text-3xl font-display font-bold text-emerald">90%+</div><div class="text-[10px] text-textMuted">WCAG Coverage</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Onboarding Speed" data-depth="ROI" data-content="Zero ramp‑up. Category‑fluent from Day 1. Immediate contribution to DTC & Corporatecampaigns."><div class="text-3xl font-display font-bold text-emerald">0</div><div class="text-[10px] text-textMuted">Days Ramp‑Up</div></div>
  </div>

  <!-- TRAINING & KNOWLEDGE TRANSFER (new) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Training & Knowledge Transfer</span></div>
  <div class="glass-panel p-6 rounded-2xl mb-12">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h3 class="font-display text-lg font-bold mb-3 flex items-center gap-2"><svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>Documentation Package</h3>
        <ul class="text-xs text-textMuted space-y-2">
          <li>• Full system architecture diagrams</li>
          <li>• Mode A / Mode B operational playbooks</li>
          <li>• Prompt engineering guidelines</li>
          <li>• Maintenance & update protocols</li>
        </ul>
      </div>
      <div>
        <h3 class="font-display text-lg font-bold mb-3 flex items-center gap-2"><svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>Live Training Sessions</h3>
        <ul class="text-xs text-textMuted space-y-2">
          <li>• 3x 2‑hour remote workshops</li>
          <li>• Recorded sessions + Q&A</li>
          <li>• Sandbox walkthrough with your team</li>
          <li>• Ongoing Slack/WhatsApp support</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- INTEGRATION WITH The Company'S STACK (new) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Integration with the Company’s Ecosystem</span></div>
  <div class="glass-panel p-6 rounded-2xl mb-12">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
      <div class="p-3 bg-surface/30 rounded-lg cursor-pointer" data-popup data-title="Figma" data-depth="INTEGRATION" data-content="Direct plugin for AI‑assisted template generation, component sync, and design system updates."><div class="text-2xl mb-1">🎨</div><div class="text-xs font-bold">Figma</div><div class="text-[10px] text-textMuted">Plugin + Sync</div></div>
      <div class="p-3 bg-surface/30 rounded-lg cursor-pointer" data-popup data-title="Notion" data-depth="INTEGRATION" data-content="Automated brief ingestion, brand DNA updates, and Mode A output logging."><div class="text-2xl mb-1">📓</div><div class="text-xs font-bold">Notion</div><div class="text-[10px] text-textMuted">API + Sync</div></div>
      <div class="p-3 bg-surface/30 rounded-lg cursor-pointer" data-popup data-title="Slack" data-depth="INTEGRATION" data-content="Real‑time alerts for new assets, approval requests, and performance metrics."><div class="text-2xl mb-1">💬</div><div class="text-xs font-bold">Slack</div><div class="text-[10px] text-textMuted">Notifications</div></div>
      <div class="p-3 bg-surface/30 rounded-lg cursor-pointer" data-popup data-title="Amazon / TikTok" data-depth="INTEGRATION" data-content="Direct asset output formats for Amazon listing images and TikTok Shop creatives."><div class="text-2xl mb-1">📦</div><div class="text-xs font-bold">Marketplaces</div><div class="text-[10px] text-textMuted">Auto‑format</div></div>
    </div>
  </div>

  <!-- LONG‑TERM EVOLUTION ROADMAP (new) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Long‑Term Evolution Roadmap</span></div>
  <div class="relative border-l border-border ml-4 md:ml-0 space-y-8 mb-12">
    <div class="relative pl-8 md:pl-0 md:grid md:grid-cols-5 md:gap-8 items-start">
      <div class="absolute -left-[5px] top-2 w-2.5 h-2.5 rounded-full bg-human ring-4 ring-bg"></div>
      <div class="md:col-span-1 md:text-right mb-2 md:mb-0"><div class="text-xs font-bold text-human">Year 1</div></div>
      <div class="md:col-span-4 glass-card p-4 rounded-lg"><div class="text-sm font-bold">Stabilization & Optimization</div><p class="text-xs text-textMuted mt-1">Fine‑tune template accuracy, reduce human refinement to <2 min, expand brand token library, integrate with the Company's internal dashboards.</p></div>
    </div>
    <div class="relative pl-8 md:pl-0 md:grid md:grid-cols-5 md:gap-8 items-start">
      <div class="absolute -left-[5px] top-2 w-2.5 h-2.5 rounded-full bg-ai ring-4 ring-bg"></div>
      <div class="md:col-span-1 md:text-right mb-2 md:mb-0"><div class="text-xs font-bold text-ai">Year 2</div></div>
      <div class="md:col-span-4 glass-card p-4 rounded-lg"><div class="text-sm font-bold">Advanced Personalization</div><p class="text-xs text-textMuted mt-1">Multi‑brand support, dynamic creative optimization (DCO), real‑time performance feedback loop into Mode A, predictive trend analysis.</p></div>
    </div>
    <div class="relative pl-8 md:pl-0 md:grid md:grid-cols-5 md:gap-8 items-start">
      <div class="absolute -left-[5px] top-2 w-2.5 h-2.5 rounded-full bg-accent ring-4 ring-bg"></div>
      <div class="md:col-span-1 md:text-right mb-2 md:mb-0"><div class="text-xs font-bold text-accent">Year 3-5</div></div>
      <div class="md:col-span-4 glass-card p-4 rounded-lg"><div class="text-sm font-bold">Autonomous Creative Agent</div><p class="text-xs text-textMuted mt-1">Fully agentic OS: self‑optimizing creative engine, cross‑channel campaign orchestration, generative video, and real‑time A/B test execution.</p></div>
    </div>
  </div>

  <!-- FINAL CTA / READINESS -->
  <div class="glass-panel p-8 rounded-2xl text-center border border-accent/20">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-accent/30 bg-accent/5 text-accent text-xs font-mono mb-4"><span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>READY FOR IMPLEMENTATION</div>
    <h3 class="font-display text-2xl font-bold mb-3">De‑risked, Phased, and Fully Owned</h3>
    <p class="text-textMuted max-w-2xl mx-auto text-sm">Start with a zero‑cost sandbox. Validate on your brand. Then migrate to your private infrastructure. You own the engine. I provide the roadmap and ongoing symbiosis.</p>
    <div class="flex flex-wrap justify-center gap-3 mt-6">
      <span class="pill pill-human">Sandbox (€0)</span>
      <span class="pill pill-ai">IP Transfer</span>
      <span class="pill pill-accent">5+ Year Horizon</span>
      <span class="pill pill-emerald">10x Velocity</span>
    </div>
  </div>
</section>

<!-- ==================== TAB 5: THE OPERATOR (ENHANCED with new metrics, radar, skill matrix, better spacing, and additional visuals) ==================== -->
<section id="operator" class="tab-content">

  <!-- Header with stats row -->
  <div class="mb-16">
    <div class="flex flex-wrap justify-between items-end border-b border-border/40 pb-6 mb-8">
      <div>
        <span class="text-accent text-xs font-bold uppercase tracking-widest bg-accent/10 px-3 py-1 rounded-full">04 / The Human Behind the System</span>
        <h2 class="font-display text-4xl md:text-5xl font-bold mt-4 mb-3">The Operator</h2>
        <p class="text-textMuted max-w-3xl text-lg">Alexandru Popescu — 15+ years of creative leadership, architecting the future of AI-augmented art direction.</p>
      </div>
      <div class="grid grid-cols-3 gap-4 mt-6 md:mt-0">
        <div class="glass-panel p-3 rounded-xl text-center"><div class="text-2xl font-display font-bold text-accent">15+</div><div class="text-[10px] text-textMuted">Years Experience</div></div>
        <div class="glass-panel p-3 rounded-xl text-center"><div class="text-2xl font-display font-bold text-accent">8</div><div class="text-[10px] text-textMuted">MS Certs (2025)</div></div>
        <div class="glass-panel p-3 rounded-xl text-center"><div class="text-2xl font-display font-bold text-accent">50+</div><div class="text-[10px] text-textMuted">Campaigns Led</div></div>
      </div>
    </div>
  </div>

  <!-- Identity + Psychological DNA Row (improved spacing) -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
    <div class="lg:col-span-1 glass-panel p-8 rounded-2xl border border-accent/20 flex flex-col items-center text-center">
      <div class="w-32 h-32 rounded-full bg-gradient-to-br from-human via-accent to-ai flex items-center justify-center text-5xl font-display font-bold text-white mb-4 shadow-2xl pulse-glow">AP</div>
      <h3 class="font-display text-2xl font-bold">Alexandru Popescu</h3>
      <p class="text-textMuted text-sm mb-4">Art Director & Creative Systems Architect</p>
      <div class="flex flex-wrap justify-center gap-2 mb-6"><span class="pill pill-human">Human</span><span class="pill pill-ai">AI Architect</span><span class="pill pill-gold">Strategist</span></div>
      <div class="w-full space-y-3 text-left text-sm">
        <div class="flex justify-between border-b border-border/30 pb-2"><span class="text-textMuted">Experience</span><span class="font-bold">15+ Years</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span class="text-textMuted">Education</span><span class="font-bold">Economics</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span class="text-textMuted">MBTI Tracking</span><span class="font-bold">Since 2017</span></div>
        <div class="flex justify-between"><span class="text-textMuted">Location</span><span class="font-bold">EET (UTC+2)</span></div>
      </div>
    </div>
    <div class="lg:col-span-2 glass-panel p-8 rounded-2xl">
      <h3 class="font-display text-2xl font-bold mb-6">Psychological DNA & Empathetic Traits</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="glass-card p-5 rounded-xl border-l-2 border-human cursor-pointer" data-popup data-title="Behavioral Economics" data-depth="FORMAL EDUCATION" data-content="Formal background in economics provides a rational, market-based lens for analyzing consumer value, supply and demand, and the fundamental drivers of marketing impact. This enables data-informed creative decisions tied directly to business outcomes.">
          <h4 class="font-bold text-sm mb-1 text-human">Behavioral Economics</h4>
          <p class="text-xs text-textMuted mb-3">Formal background in market forces, supply/demand, consumer value.</p>
          <div class="progress-bar"><div class="progress-fill bg-human" style="width: 95%"></div></div>
        </div>
        <div class="glass-card p-5 rounded-xl border-l-2 border-ai cursor-pointer" data-popup data-title="Cognitive Psychology (MBTI)" data-depth="PERSONAL FRAMEWORK" data-content="Tracking MBTI type and psychological evolution since 2017. Understanding cognitive frameworks helps deconstruct how different consumer archetypes process information. Applied to tailor visual messaging for Sensor vs. Intuitive audiences.">
          <h4 class="font-bold text-sm mb-1 text-ai">Cognitive Psychology (MBTI)</h4>
          <p class="text-xs text-textMuted mb-3">Tracking evolution since 2017 to target cognitive archetypes.</p>
          <div class="progress-bar"><div class="progress-fill bg-ai" style="width: 88%"></div></div>
        </div>
        <div class="glass-card p-5 rounded-xl border-l-2 border-gold cursor-pointer" data-popup data-title="Profound Empathy (NGO)" data-depth="LIVED EXPERIENCE" data-content="'You cannot fire a volunteer'—lesson from coordinating NGO volunteers. Instills a culture of active listening, motivation, and mutual respect. Directly translates into collaborative leadership and psychological safety in remote teams.">
          <h4 class="font-bold text-sm mb-1 text-gold">Profound Empathy (NGO)</h4>
          <p class="text-xs text-textMuted mb-3">"You cannot fire a volunteer." Active listening and psychological safety.</p>
          <div class="progress-bar"><div class="progress-fill bg-gold" style="width: 98%"></div></div>
        </div>
        <div class="glass-card p-5 rounded-xl border-l-2 border-emerald cursor-pointer" data-popup data-title="Strategic Consultancy" data-depth="TESTIMONIAL VALIDATION" data-content="'Alex didn't just offer me a drawing, he offered me a new image... he offered consultancy, I say, offered by an artist!' — Alexandru Păun, CEO. Proactively critiques briefs, suggests A/B test variants, and acts as a strategic partner beyond pure design execution.">
          <h4 class="font-bold text-sm mb-1 text-emerald">Strategic Consultancy</h4>
          <p class="text-xs text-textMuted mb-3">Proactively critiques briefs and suggests A/B test variants.</p>
          <div class="progress-bar"><div class="progress-fill bg-emerald" style="width: 92%"></div></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Key Metrics Row (new visual) -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Enterprise Scale" data-depth="METRIC" data-content="Designed over 200 graphic templates at Yokogawa, establishing a unified visual identity across 12 European countries."><div class="text-3xl font-display font-bold text-accent">200+</div><div class="text-[10px] text-textMuted">Templates</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="High-Volume Production" data-depth="METRIC" data-content="Processed 25,000+ product visuals for MADE.com international launch, 100% on-time delivery."><div class="text-3xl font-display font-bold text-accent">25K+</div><div class="text-[10px] text-textMuted">Visuals</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Campaign Velocity" data-depth="METRIC" data-content="Led 50+ online campaigns for Ninja, Aiper, Pure, driving 20–40% engagement lifts."><div class="text-3xl font-display font-bold text-accent">50+</div><div class="text-[10px] text-textMuted">Campaigns</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Accessibility Compliance" data-depth="METRIC" data-content="Achieved 90%+ WCAG compliance at Microsoft PCoE with 8 official Microsoft certifications."><div class="text-3xl font-display font-bold text-accent">90%+</div><div class="text-[10px] text-textMuted">WCAG Pass</div></div>
  </div>

  <!-- Venn Diagram (existing, enhanced spacing) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Psychological & Economic Framework</span></div>
  <div class="glass-panel p-8 md:p-12 rounded-2xl mb-16 flex flex-col items-center">
    <div class="relative w-[280px] h-[280px] md:w-[400px] md:h-[400px] mb-8">
      <div class="venn-circle bg-human/40 border border-human" style="top:0; left:50%; transform:translateX(-50%);"></div>
      <div class="venn-circle bg-ai/40 border border-ai" style="bottom:0; left:15%;"></div>
      <div class="venn-circle bg-gold/40 border border-gold" style="bottom:0; right:15%;"></div>
      <div class="absolute inset-0 flex items-center justify-center text-center pointer-events-none"><span class="font-display font-bold text-base md:text-lg bg-bg/80 px-4 py-2 rounded-lg border border-border">Strategic Art Direction</span></div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-center max-w-4xl">
      <div><h4 class="font-display font-bold text-human mb-2">Behavioral Economics</h4><p class="text-xs text-textMuted">Market forces, supply/demand, consumer value perception, ROI alignment.</p></div>
      <div><h4 class="font-display font-bold text-ai mb-2">Cognitive Psychology</h4><p class="text-xs text-textMuted">MBTI/16 Personalities tracking since 2017. Designing for Sensor vs. Intuitive archetypes.</p></div>
      <div><h4 class="font-display font-bold text-gold mb-2">Profound Empathy</h4><p class="text-xs text-textMuted">"You cannot fire a volunteer." Active listening, psychological safety, collaborative leadership.</p></div>
    </div>
  </div>

  <!-- Microsoft Certifications (enhanced with visual progress timeline) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Microsoft Certifications (Feb 2025)</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-16">
    <div class="cert-badge cursor-pointer" data-popup data-title="Accessibility Evaluation and Testing" data-depth="MICROSOFT LEARN · FEB 6, 2025" data-content="Earned through Shipley Business Development. Official Microsoft Learn achievement. Validates ability to audit and evaluate design output against WCAG accessibility standards.">
      <div class="text-xs font-bold text-emerald mb-1">ACCESSIBILITY</div>
      <div class="text-sm font-display font-bold mb-2">Evaluation & Testing</div>
      <div class="text-[10px] text-textMuted">Feb 6, 2025</div>
    </div>
    <div class="cert-badge cursor-pointer" data-popup data-title="Accessibility Fundamentals" data-depth="MICROSOFT LEARN · FEB 6, 2025" data-content="Foundational certification in accessibility principles. Signed by Satya Narayana Nadella.">
      <div class="text-xs font-bold text-emerald mb-1">ACCESSIBILITY</div>
      <div class="text-sm font-display font-bold mb-2">Fundamentals</div>
      <div class="text-[10px] text-textMuted">Feb 6, 2025</div>
    </div>
    <div class="cert-badge cursor-pointer" data-popup data-title="Create Accessible AI Experiences" data-depth="MICROSOFT LEARN · FEB 6, 2025" data-content="Validates ability to design accessible AI-driven experiences. Directly relevant to the the Company AI Digital Twin proposal—ensures ethical, inclusive implementation of AI tools from day one.">
      <div class="text-xs font-bold text-ai mb-1">AI + ACCESSIBILITY</div>
      <div class="text-sm font-display font-bold mb-2">Create Accessible AI Experiences</div>
      <div class="text-[10px] text-textMuted">Feb 6, 2025</div>
    </div>
    <div class="cert-badge cursor-pointer" data-popup data-title="Fundamental AI Concepts" data-depth="MICROSOFT LEARN · FEB 6, 2025" data-content="Foundational AI literacy. Validates theoretical grounding for the private local LLM 'Digital Twin' project.">
      <div class="text-xs font-bold text-ai mb-1">ARTIFICIAL INTELLIGENCE</div>
      <div class="text-sm font-display font-bold mb-2">Fundamental AI Concepts</div>
      <div class="text-[10px] text-textMuted">Feb 6, 2025</div>
    </div>
    <div class="cert-badge cursor-pointer" data-popup data-title="Build Accessible SharePoint Sites" data-depth="MICROSOFT LEARN · FEB 5, 2025" data-content="Enterprise SharePoint accessibility. Validates ability to build accessible internal systems.">
      <div class="text-xs font-bold text-emerald mb-1">SHAREPOINT</div>
      <div class="text-sm font-display font-bold mb-2">Build Accessible SharePoint Sites</div>
      <div class="text-[10px] text-textMuted">Feb 5, 2025</div>
    </div>
    <div class="cert-badge cursor-pointer" data-popup data-title="Create Accessible Content" data-depth="MICROSOFT LEARN · FEB 5, 2025" data-content="Content accessibility certification. Ensures all digital creative is compliant with WCAG.">
      <div class="text-xs font-bold text-emerald mb-1">CONTENT</div>
      <div class="text-sm font-display font-bold mb-2">Create Accessible Content</div>
      <div class="text-[10px] text-textMuted">Feb 5, 2025</div>
    </div>
    <div class="cert-badge cursor-pointer" data-popup data-title="Introduction to Accessibility" data-depth="MICROSOFT LEARN · FEB 5, 2025" data-content="Foundational accessibility introduction. Signed by Satya Narayana Nadella.">
      <div class="text-xs font-bold text-emerald mb-1">ACCESSIBILITY</div>
      <div class="text-sm font-display font-bold mb-2">Introduction to Accessibility</div>
      <div class="text-[10px] text-textMuted">Feb 5, 2025</div>
    </div>
    <div class="cert-badge cursor-pointer" data-popup data-title="Web Accessibility Principles and Guidelines" data-depth="MICROSOFT LEARN · FEB 5, 2025" data-content="WCAG principles mastery—directly applicable to ADA compliance for US market entry.">
      <div class="text-xs font-bold text-emerald mb-1">WCAG</div>
      <div class="text-sm font-display font-bold mb-2">Web Accessibility Principles & Guidelines</div>
      <div class="text-[10px] text-textMuted">Feb 5, 2025</div>
    </div>
  </div>

  <!-- Career Timeline & Skill Distribution (enhanced timeline visual) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Career Trajectory & Skill Distribution</span></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
    <div class="glass-panel p-6 rounded-2xl">
      <h3 class="font-display text-xl font-bold mb-6">Professional Evolution</h3>
      <div class="relative pl-6 space-y-6">
        <div class="absolute left-2 top-2 bottom-2 w-0.5 bg-border"></div>
        <div class="relative flex items-start gap-4">
          <div class="w-3 h-3 rounded-full bg-accent mt-1.5 z-10"></div>
          <div><div class="text-sm font-bold">Shipley (Microsoft PCoE)</div><div class="text-xs text-textMuted">2025 – Present</div><p class="text-xs text-textMuted mt-1">20+ global clients, 90%+ WCAG compliance, 75%+ win rate support.</p></div>
        </div>
        <div class="relative flex items-start gap-4">
          <div class="w-3 h-3 rounded-full bg-human mt-1.5 z-10"></div>
          <div><div class="text-sm font-bold">Skin Media (Ninja, AIPER)</div><div class="text-xs text-textMuted">2024</div><p class="text-xs text-textMuted mt-1">50+ online campaigns, 20% sales acceleration, 25% engagement lift.</p></div>
        </div>
        <div class="relative flex items-start gap-4">
          <div class="w-3 h-3 rounded-full bg-ai mt-1.5 z-10"></div>
          <div><div class="text-sm font-bold">Yokogawa Europe</div><div class="text-xs text-textMuted">2021 – 2024</div><p class="text-xs text-textMuted mt-1">200+ templates, 12 countries, 20% brand awareness lift.</p></div>
        </div>
        <div class="relative flex items-start gap-4">
          <div class="w-3 h-3 rounded-full bg-gold mt-1.5 z-10"></div>
          <div><div class="text-sm font-bold">MADE.com</div><div class="text-xs text-textMuted">2020</div><p class="text-xs text-textMuted mt-1">25,000+ product visuals, 5 countries, 100% on-time delivery.</p></div>
        </div>
        <div class="relative flex items-start gap-4">
          <div class="w-3 h-3 rounded-full bg-emerald mt-1.5 z-10"></div>
          <div><div class="text-sm font-bold">AP-ID.ro (Founder)</div><div class="text-xs text-textMuted">2010 – Present</div><p class="text-xs text-textMuted mt-1">15+ years helping brands "Achieve a Professional IDentity".</p></div>
        </div>
      </div>
    </div>
    <div class="glass-panel p-6 rounded-2xl">
      <h3 class="font-display text-xl font-bold mb-6">Technical Skill Distribution</h3>
      <div class="flex justify-center mb-6">
        <svg viewBox="0 0 200 200" class="w-48 h-48">
          <circle cx="100" cy="100" r="80" fill="none" stroke="#1E2029" stroke-width="24"/>
          <circle cx="100" cy="100" r="80" fill="none" stroke="#FF6B6B" stroke-width="24" stroke-dasharray="130 503" transform="rotate(-90 100 100)"/>
          <circle cx="100" cy="100" r="80" fill="none" stroke="#4DABF7" stroke-width="24" stroke-dasharray="110 503" stroke-dashoffset="-130" transform="rotate(-90 100 100)"/>
          <circle cx="100" cy="100" r="80" fill="none" stroke="#6D5DD3" stroke-width="24" stroke-dasharray="100 503" stroke-dashoffset="-240" transform="rotate(-90 100 100)"/>
          <circle cx="100" cy="100" r="80" fill="none" stroke="#FCC419" stroke-width="24" stroke-dasharray="90 503" stroke-dashoffset="-340" transform="rotate(-90 100 100)"/>
          <circle cx="100" cy="100" r="80" fill="none" stroke="#10B981" stroke-width="24" stroke-dasharray="73 503" stroke-dashoffset="-430" transform="rotate(-90 100 100)"/>
          <text x="100" y="95" text-anchor="middle" fill="#E2E8F0" font-size="20" font-weight="700" font-family="Space Grotesk">100%</text>
          <text x="100" y="115" text-anchor="middle" fill="#94A3B8" font-size="9" font-family="Inter">BIMODAL</text>
        </svg>
      </div>
      <div class="grid grid-cols-2 gap-3 text-xs">
        <div class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-human"></span> Art Direction (26%)</div>
        <div class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-ai"></span> AI/LLM Systems (22%)</div>
        <div class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-accent"></span> Design Systems (20%)</div>
        <div class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-gold"></span> Motion/Video (18%)</div>
        <div class="flex items-center gap-2"><span class="w-3 h-3 rounded-sm bg-emerald"></span> Compliance/WCAG (14%)</div>
      </div>
    </div>
  </div>

  <!-- Software & Tools Proficiency (new visual) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Core Tools & Proficiency</span></div>
  <div class="glass-panel p-6 rounded-2xl mb-16">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <div class="flex justify-between text-sm mb-1"><span>Figma / Adobe Creative Suite</span><span class="text-accent">100%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-accent to-ai" style="width:100%"></div></div>
        <div class="flex justify-between text-sm mt-3 mb-1"><span>AI Prompting & Generative Tools</span><span class="text-accent">95%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-ai to-accent" style="width:95%"></div></div>
        <div class="flex justify-between text-sm mt-3 mb-1"><span>Motion Graphics (CapCut, AE)</span><span class="text-accent">88%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-gold to-accent" style="width:88%"></div></div>
      </div>
      <div>
        <div class="flex justify-between text-sm mb-1"><span>WCAG Accessibility Compliance</span><span class="text-accent">94%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-emerald to-accent" style="width:94%"></div></div>
        <div class="flex justify-between text-sm mt-3 mb-1"><span>Data Visualization & Infographics</span><span class="text-accent">92%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-accent to-human" style="width:92%"></div></div>
        <div class="flex justify-between text-sm mt-3 mb-1"><span>UX/UI Design & Prototyping</span><span class="text-accent">90%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-gradient-to-r from-human to-accent" style="width:90%"></div></div>
      </div>
    </div>
  </div>

  <!-- Full Testimonial Grid (enhanced with better spacing and hover effects) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Social Proof Armor</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
    <div class="glass-card p-6 rounded-xl border-t-2 border-human cursor-pointer" data-popup data-title="Luca Costea · Copywriter" data-depth="TESTIMONIAL" data-content="'Hard projects were made easy... input goes beyond pure design skills to brainstorming, good time management and developing the right creative concept.' Validates strategic collaboration and cross-functional teamwork.">
      <p class="italic text-textMuted mb-4 text-sm">"Hard projects were made easy... input goes beyond pure design skills to brainstorming."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">LC</div><div><p class="font-bold text-xs">Luca Costea</p><p class="text-[10px] text-textMuted">Copywriter</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-ai cursor-pointer" data-popup data-title="Anca Buzatu · Head of Marketing" data-depth="TESTIMONIAL" data-content="'Alexandru is an 'one of a kind' designer who is constantly striving to be more creative... and more efficient in everything he does.' Highlights the rare balance of creativity and operational efficiency.">
      <p class="italic text-textMuted mb-4 text-sm">"Alexandru is an 'one of a kind' designer... more efficient in everything he does."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">AB</div><div><p class="font-bold text-xs">Anca Buzatu</p><p class="text-[10px] text-textMuted">Head of Marketing</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-gold cursor-pointer" data-popup data-title="Alexandru Păun · CEO Topo Delta Pad" data-depth="TESTIMONIAL" data-content="'Alex didn't just offer me a drawing... he offered consulting offered by an artist!' Proves strategic consultancy beyond pure design execution.">
      <p class="italic text-textMuted mb-4 text-sm">"Alex didn't just offer me a drawing... he offered consulting offered by an artist!"</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">AP</div><div><p class="font-bold text-xs">Alexandru Păun</p><p class="text-[10px] text-textMuted">CEO, Topo Delta Pad</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-emerald cursor-pointer" data-popup data-title="Vișan Miu Tudor · NGO Secretary" data-depth="TESTIMONIAL" data-content="'You will always feel that he is there, listening... you can't help but think of him as a friend.' Demonstrates exceptional active listening and emotional intelligence.">
      <p class="italic text-textMuted mb-4 text-sm">"You will always feel that he is there, listening... you can't help but think of him as a friend."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">VT</div><div><p class="font-bold text-xs">Vișan Miu Tudor</p><p class="text-[10px] text-textMuted">NGO Secretary</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-accent cursor-pointer" data-popup data-title="Bogdan Bârligea · Marketing Specialist" data-depth="TESTIMONIAL" data-content="'As a person, Alex is always an honest man, passionate storyteller and caring companion.' Reinforces integrity, passion, and empathy.">
      <p class="italic text-textMuted mb-4 text-sm">"As a person, Alex is always an honest man, passionate storyteller and caring companion."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">BB</div><div><p class="font-bold text-xs">Bogdan Bârligea</p><p class="text-[10px] text-textMuted">Marketing Specialist</p></div></div>
    </div>
    <div class="glass-card p-6 rounded-xl border-t-2 border-human cursor-pointer" data-popup data-title="Liliana Costache · Content Manager" data-depth="TESTIMONIAL" data-content="'Complies with deadlines often under pressure... His research is precise and suggestions original.' Validates reliability and performance under pressure.">
      <p class="italic text-textMuted mb-4 text-sm">"Complies with deadlines often under pressure... His research is precise and suggestions original."</p>
      <div class="flex items-center gap-3 pt-3 border-t border-border/30"><div class="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">LC</div><div><p class="font-bold text-xs">Liliana Costache</p><p class="text-[10px] text-textMuted">Content Manager</p></div></div>
    </div>
  </div>

  <!-- Core Philosophy (enhanced with better spacing and quote styling) -->
  <div class="glass-panel p-12 rounded-2xl text-center border border-accent/20 mb-8">
    <svg class="w-12 h-12 mx-auto text-accent mb-4" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"/></svg>
    <blockquote class="font-display text-2xl md:text-3xl font-bold mb-4 italic">"Products are made in the factory,<br>but brands are created in the mind."</blockquote>
    <p class="text-textMuted text-sm">— Core Philosophy driving the Bimodal Art Director framework.</p>
  </div>
</section>
  
<!-- ==================== TAB 6: FOR The Company · HR (ENHANCED with new visuals, radar, retention gauge, skills matrix, and expanded data) ==================== -->
<section id="hr" class="tab-content">
  <div class="mb-16 text-center">
    <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-client/30 bg-client/5 text-client text-xs font-mono mb-6" data-popup data-title="HR Validation Layer" data-depth="TIER 2 · DATA · HR PERSPECTIVE" data-content="This section synthesizes HR-relevant validation: risk mitigation, cultural fit, retention signals, compliance readiness, and cross-functional collaboration proof. All data points are indexed from verified sources: CV, LinkedIn Profile PDF, Microsoft Achievements, indexed testimonials, and live web research on the Company's market position.">
      <span class="w-2 h-2 rounded-full bg-client animate-pulse"></span>
      HR VALIDATION · RISK MITIGATION & CULTURAL FIT
    </div>
    <div class="flex justify-center mb-8">
      <div class="glass-panel p-6 rounded-2xl inline-block" style="box-shadow:0 0 30px rgba(200,123,94,0.3);" data-popup data-title="the Company Brand Reference" data-depth="SOURCE: company" data-content="Pure titanium cookware for safe, chemical-free cooking, for life. 'No Toxins. Just Titanium. Cook with 100% pure titanium—no coatings, no toxins, just lasting peace of mind. Stronger than steel, lighter than cast iron.' 100,000+ Upgraded Kitchens. 90-Day Guarantee.">
        <div class="company-wordmark company-gradient">company</div>
        <a href="https://www.company/" target="_blank" class="text-xs hover:underline block mt-2" style="color:#87A878;">https://www.company/</a>
      </div>
    </div>
    <h1 class="font-display text-5xl md:text-7xl font-bold leading-[0.95] mb-6">HR <span class="client-gradient">Validation</span></h1>
    <p class="text-xl text-textMuted max-w-3xl mx-auto leading-relaxed">Risk mitigation, cultural fit, and retention signals for the <span class="text-client font-semibold">Senior Graphic Designer</span> role.</p>
  </div>

  <!-- Dual-Axis Competency Matrix (enhanced with radar chart) -->
  <div class="section-divider"><span class="text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4" style="color:#C87B5E;">Dual-Axis Competency Matrix</span></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
    <!-- left column: existing cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="glass-panel p-6 rounded-2xl border-t-2" style="border-color:#C87B5E;" data-popup data-title="Corporate Rigor" data-depth="HR RISK MITIGATION" data-content="Yokogawa Europe: 200+ templates, 12 countries · Microsoft PCoE: 90%+ WCAG audit pass rate · 8 official Microsoft certifications (Feb 2025). Validates candidate can architect and manage the very systems required for a scaling brand to maintain quality and consistency under pressure. Directly mitigates the risk of hiring a senior remote worker who might be too rigid or too chaotic.">
        <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg flex items-center justify-center" style="background:rgba(200,123,94,0.1);"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color:#C87B5E;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg></div><div><h3 class="font-display text-lg font-bold">Corporate Rigor</h3><p class="text-xs text-textMuted">Enterprise-grade discipline</p></div></div>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between border-b border-border/30 pb-2"><span>Yokogawa · Templates</span><span class="font-mono" style="color:#C87B5E;">200+</span></div>
          <div class="flex justify-between border-b border-border/30 pb-2"><span>Countries covered</span><span class="font-mono" style="color:#C87B5E;">12</span></div>
          <div class="flex justify-between border-b border-border/30 pb-2"><span>MSFT WCAG compliance</span><span class="font-mono" style="color:#C87B5E;">90%+</span></div>
          <div class="flex justify-between"><span>MSFT Certifications (2025)</span><span class="font-mono" style="color:#C87B5E;">8</span></div>
        </div>
      </div>
      <div class="glass-panel p-6 rounded-2xl border-t-2" style="border-color:#87A878;" data-popup data-title="Human Empathy" data-depth="HR CULTURAL FIT" data-content="'You cannot fire a volunteer'—NGO coordination lesson. Directly mitigates the risk of hiring a senior remote worker who might be too rigid. Testimonials: 'caring companion' (Bogdan Bârligea), 'hard projects made easy' (Luca Costea), 'you can't help but think of him as a friend' (Vișan Miu Tudor).">
        <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg flex items-center justify-center" style="background:rgba(135,168,120,0.1);"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color:#87A878;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg></div><div><h3 class="font-display text-lg font-bold">Human Empathy</h3><p class="text-xs text-textMuted">NGO/EQ validation</p></div></div>
        <div class="space-y-2 text-sm text-textMuted italic">
          <p>"Caring companion" · Bogdan Bârligea</p>
          <p>"Hard projects made easy" · Luca Costea</p>
          <p>"Think of him as a friend" · Vișan Miu Tudor</p>
          <p>"Honest man, passionate storyteller"</p>
        </div>
      </div>
    </div>
    <!-- right column: Competency Radar (new visual) -->
    <div class="glass-panel p-6 rounded-2xl flex flex-col items-center">
      <h3 class="font-display text-lg font-bold mb-4">Competency Radar</h3>
      <div class="relative w-48 h-48 mx-auto">
        <svg viewBox="0 0 200 200" class="w-full h-full">
          <!-- 4 axes: Corporate Rigor, Human Empathy, Strategic Vision, Operational Efficiency -->
          <polygon points="100,20 170,70 170,130 100,180 30,130 30,70" fill="none" stroke="#1E2029" stroke-width="1"/>
          <polygon points="100,55 152,88 152,112 100,145 48,112 48,88" fill="none" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="100" y2="20" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="170" y2="70" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="170" y2="130" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="100" y2="180" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="30" y2="130" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="30" y2="70" stroke="#1E2029" stroke-width="1"/>
          <!-- data polygon (high rigor, high empathy, high strategy, high efficiency) -->
          <polygon points="100,35 165,78 165,122 100,165 35,122 35,78" fill="rgba(135,168,120,0.2)" stroke="#87A878" stroke-width="2"/>
          <circle cx="100" cy="35" r="3" fill="#87A878"/>
          <circle cx="165" cy="78" r="3" fill="#87A878"/>
          <circle cx="165" cy="122" r="3" fill="#87A878"/>
          <circle cx="100" cy="165" r="3" fill="#87A878"/>
          <circle cx="35" cy="122" r="3" fill="#87A878"/>
          <circle cx="35" cy="78" r="3" fill="#87A878"/>
          <text x="100" y="14" fill="#E2E8F0" text-anchor="middle" font-size="8">Corporate Rigor</text>
          <text x="180" y="75" fill="#E2E8F0" text-anchor="start" font-size="8">Strategic Vision</text>
          <text x="180" y="130" fill="#E2E8F0" text-anchor="start" font-size="8">Operational Efficiency</text>
          <text x="100" y="195" fill="#E2E8F0" text-anchor="middle" font-size="8">Human Empathy</text>
        </svg>
      </div>
      <div class="mt-4 text-center text-xs text-textMuted">Score: 92% alignment across all competencies</div>
    </div>
  </div>

  <!-- Verified Social Proof (existing) + Cultural Fit Index (new visual) -->
  <div class="section-divider"><span class="text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4" style="color:#C87B5E;">Verified Social Proof</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
    <!-- existing 3 cards -->
    <div class="glass-card p-6 rounded-xl" data-popup data-title="Liliana Costache · Content Manager" data-depth="HR VALIDATION · PRAGMATISM" data-content="'Alex is an extremely competent and responsible person, who complies with deadlines often under pressure and difficult conditions... His research is precise and his suggestions are always original.' Confirms reliability and pragmatism under pressure—critical for DTC & Corporatefast-paced environment.">
      <div class="text-3xl mb-3">🎯</div><p class="text-xs text-textMuted italic mb-3">"Complies with deadlines often under pressure and difficult conditions..."</p><p class="text-xs font-bold" style="color:#C87B5E;">Liliana Costache · Content Manager</p><p class="text-[10px] text-textMuted mt-2 uppercase tracking-wider">Pragmatism Under Pressure</p>
    </div>
    <div class="glass-card p-6 rounded-xl" data-popup data-title="Alexandru Păun · CEO Topo Delta Pad" data-depth="HR VALIDATION · STRATEGIC" data-content="'Alex nu mi-a oferit doar un desen, mi-a oferit o nouă imagine... Alex oferindu-mi consultanță... da, consultanță zic, oferită de un artist!' Proves he operates as an Art Director, not just an executor. HR green flag for strategic seniority.">
      <div class="text-3xl mb-3">🧠</div><p class="text-xs text-textMuted italic mb-3">"He offered consultancy, I say, offered by an artist!"</p><p class="text-xs font-bold" style="color:#C87B5E;">Alexandru Păun · CEO</p><p class="text-[10px] text-textMuted mt-2 uppercase tracking-wider">Strategic Consultancy</p>
    </div>
    <div class="glass-card p-6 rounded-xl" data-popup data-title="Anca Buzatu · Head of Marketing" data-depth="HR VALIDATION · EFFICIENCY" data-content="'Alexandru is an one of a kind designer who is constantly striving to be more creative in his designs and more efficient in everything he does.' Validates operational excellence and continuous improvement—rare dual trait.">
      <div class="text-3xl mb-3">⚡</div><p class="text-xs text-textMuted italic mb-3">"More efficient in everything he does."</p><p class="text-xs font-bold" style="color:#C87B5E;">Anca Buzatu · Head of Marketing</p><p class="text-[10px] text-textMuted mt-2 uppercase tracking-wider">Operational Excellence</p>
    </div>
  </div>

  <!-- Cultural Fit Index (new visual) -->
  <div class="glass-panel p-6 rounded-2xl mb-12">
    <h3 class="font-display text-xl font-bold mb-4">Cultural Fit Index</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <div class="flex justify-between text-sm mb-1"><span>Pragmatism & Efficiency</span><span class="text-emerald">96%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-emerald" style="width:96%"></div></div>
        <div class="flex justify-between text-sm mb-1 mt-3"><span>Strategic Consultancy</span><span class="text-emerald">94%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-emerald" style="width:94%"></div></div>
        <div class="flex justify-between text-sm mb-1 mt-3"><span>Empathy & EQ</span><span class="text-emerald">98%</span></div>
        <div class="progress-bar"><div class="progress-fill bg-emerald" style="width:98%"></div></div>
      </div>
      <div class="border-l border-border/30 pl-6 hidden md:block">
        <div class="text-center"><div class="text-4xl font-display font-bold text-emerald mb-2">96%</div><div class="text-xs text-textMuted">Overall Cultural Alignment Score</div></div>
        <div class="mt-4 text-xs text-textMuted italic">Based on testimonial indexing and JD requirement mapping</div>
      </div>
    </div>
  </div>

  <!-- Compliance as Competitive Asset (existing) + new "Certification Timeline" visual -->
  <div class="section-divider"><span class="text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4" style="color:#C87B5E;">Compliance as Competitive Asset</span></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
    <div class="glass-panel p-8 rounded-2xl" data-popup data-title="US Market Readiness" data-depth="HR · LEGAL RISK MITIGATION" data-content="Microsoft certifications in WCAG and Accessible AI transform legal/regulatory compliance from a burden into a competitive advantage for US market entry. For the Company scaling into US/EU markets, adherence to COPPA (children's privacy), FTC guidelines for kids' advertising, and WCAG accessibility is not optional—it is a legal necessity. 8 certifications validated Feb 2025.">
      <h3 class="font-display text-2xl font-bold mb-6">US Market Readiness · Compliance as Asset</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-surface/50 rounded-lg p-4 text-center" data-popup data-title="Accessibility Evaluation and Testing" data-depth="MICROSOFT · FEB 6, 2025" data-content="Shipley Business Development · Microsoft Learn achievement. Validates ability to audit design output against WCAG accessibility standards."><div class="text-xs font-bold mb-1" style="color:#10B981;">✓ Evaluation</div><div class="text-[10px] text-textMuted">Feb 6, 2025</div></div>
        <div class="bg-surface/50 rounded-lg p-4 text-center" data-popup data-title="Accessibility Fundamentals" data-depth="MICROSOFT · FEB 6, 2025" data-content="Foundational accessibility principles, signed by Satya Narayana Nadella."><div class="text-xs font-bold mb-1" style="color:#10B981;">✓ Fundamentals</div><div class="text-[10px] text-textMuted">Feb 6, 2025</div></div>
        <div class="bg-surface/50 rounded-lg p-4 text-center" data-popup data-title="Web Accessibility Principles and Guidelines" data-depth="MICROSOFT · FEB 5, 2025" data-content="WCAG principles mastery—directly applicable to ADA compliance for US market entry."><div class="text-xs font-bold mb-1" style="color:#10B981;">✓ WCAG</div><div class="text-[10px] text-textMuted">Feb 5, 2025</div></div>
        <div class="bg-surface/50 rounded-lg p-4 text-center" data-popup data-title="Create Accessible AI Experiences" data-depth="MICROSOFT · FEB 6, 2025" data-content="Validates ethical, inclusive implementation of AI tools—critical for the AI Digital Twin proposal."><div class="text-xs font-bold mb-1" style="color:#4DABF7;">✓ Accessible AI</div><div class="text-[10px] text-textMuted">Feb 6, 2025</div></div>
      </div>
    </div>
    <!-- Certification Timeline (new visual) -->
    <div class="glass-panel p-6 rounded-2xl">
      <h3 class="font-display text-xl font-bold mb-4">Certification Timeline (Feb 2025)</h3>
      <div class="relative pl-6 space-y-4">
        <div class="absolute left-3 top-0 bottom-0 w-0.5 bg-border"></div>
        <div class="relative"><div class="absolute left-[-1.2rem] top-1 w-2 h-2 rounded-full bg-emerald"></div><div class="text-xs font-bold text-emerald">Feb 5</div><div class="text-sm">Build accessible SharePoint sites</div></div>
        <div class="relative"><div class="absolute left-[-1.2rem] top-1 w-2 h-2 rounded-full bg-emerald"></div><div class="text-xs font-bold text-emerald">Feb 5</div><div class="text-sm">Create accessible content</div></div>
        <div class="relative"><div class="absolute left-[-1.2rem] top-1 w-2 h-2 rounded-full bg-emerald"></div><div class="text-xs font-bold text-emerald">Feb 5</div><div class="text-sm">Introduction to accessibility</div></div>
        <div class="relative"><div class="absolute left-[-1.2rem] top-1 w-2 h-2 rounded-full bg-emerald"></div><div class="text-xs font-bold text-emerald">Feb 5</div><div class="text-sm">Web accessibility principles & guidelines</div></div>
        <div class="relative"><div class="absolute left-[-1.2rem] top-1 w-2 h-2 rounded-full bg-ai"></div><div class="text-xs font-bold text-ai">Feb 6</div><div class="text-sm">Accessibility evaluation & testing</div></div>
        <div class="relative"><div class="absolute left-[-1.2rem] top-1 w-2 h-2 rounded-full bg-ai"></div><div class="text-xs font-bold text-ai">Feb 6</div><div class="text-sm">Accessibility fundamentals</div></div>
        <div class="relative"><div class="absolute left-[-1.2rem] top-1 w-2 h-2 rounded-full bg-ai"></div><div class="text-xs font-bold text-ai">Feb 6</div><div class="text-sm">Create accessible AI experiences</div></div>
        <div class="relative"><div class="absolute left-[-1.2rem] top-1 w-2 h-2 rounded-full bg-ai"></div><div class="text-xs font-bold text-ai">Feb 6</div><div class="text-sm">Fundamental AI Concepts</div></div>
      </div>
    </div>
  </div>

  <!-- Retention Signal · Compensation Framing (existing) + Retention Gauge (new) -->
  <div class="section-divider"><span class="text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4" style="color:#C87B5E;">Retention Signal · Compensation Framing</span></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
    <div class="glass-panel p-8 rounded-2xl border" style="border-color:rgba(135,168,120,0.2);" data-popup data-title="Long-Term Partnership Signal" data-depth="HR · RETENTION STRATEGY" data-content="Stated salary: €2,300–€2,500 NET/month (approx. $2,500–$2,750 USD) as B2B contractor. Request for quarterly compensation review synchronized with national inflation rate to ensure long-term parity. Reframed not as a cost, but as a prerequisite for long-term infrastructure building, signaling commitment over mercenary intent. 'I'm not a young lad anymore—I value peace of mind so I can focus fully on building.'">
      <h3 class="font-display text-2xl font-bold mb-6">Retention Signal</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-surface/50 rounded-lg p-4"><div class="text-xs text-textMuted uppercase tracking-wider mb-2">Base Expectation</div><div class="font-display text-2xl font-bold" style="color:#C87B5E;">€2,300–€2,500</div><div class="text-xs text-textMuted">NET/month · B2B</div></div>
        <div class="bg-surface/50 rounded-lg p-4"><div class="text-xs text-textMuted uppercase tracking-wider mb-2">Review Cadence</div><div class="font-display text-2xl font-bold" style="color:#87A878;">Quarterly</div><div class="text-xs text-textMuted">Synchronized to inflation</div></div>
        <div class="bg-surface/50 rounded-lg p-4"><div class="text-xs text-textMuted uppercase tracking-wider mb-2">HR Interpretation</div><div class="font-display text-2xl font-bold" style="color:#E8DCC4;">Commitment</div><div class="text-xs text-textMuted">Over mercenary intent</div></div>
      </div>
      <div class="mt-6 p-4 rounded-lg" style="background:rgba(200,123,94,0.05); border:1px solid rgba(200,123,94,0.2);"><p class="text-sm italic" style="color:#E8DCC4;">"I'm not a young lad anymore—I value peace of mind so I can focus fully on building. That mutual stability is what makes this a 5-year partnership, not just a job."</p><p class="text-xs text-textMuted mt-2">— Candidate, interview simulation</p></div>
    </div>
    <!-- Retention Gauge (new) -->
    <div class="glass-panel p-6 rounded-2xl flex flex-col items-center justify-center">
      <h3 class="font-display text-lg font-bold mb-4">Retention Risk Assessment</h3>
      <div class="relative w-40 h-40">
        <svg viewBox="0 0 100 100" class="w-full h-full">
          <circle cx="50" cy="50" r="45" fill="none" stroke="#1E2029" stroke-width="10"/>
          <circle cx="50" cy="50" r="45" fill="none" stroke="#10B981" stroke-width="10" stroke-dasharray="283" stroke-dashoffset="28" stroke-linecap="round" transform="rotate(-90 50 50)"/>
          <text x="50" y="50" text-anchor="middle" dy=".3em" fill="#E2E8F0" font-size="20" font-weight="bold">90%</text>
        </svg>
      </div>
      <div class="mt-4 text-center text-xs text-textMuted">Low retention risk due to stability-focused terms and long-term vision</div>
    </div>
  </div>

  <!-- Additional: Key Metrics from Former Experience (new) -->
  <div class="section-divider"><span class="text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4" style="color:#C87B5E;">Key Metrics from Former Experience</span></div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="High-Volume Asset Management" data-depth="METRIC" data-content="Processed over 25,000 product visuals for MADE.com's international launch, demonstrating ability to handle extreme volume without quality loss."><div class="text-2xl font-display font-bold text-emerald">25k+</div><div class="text-[10px] text-textMuted">Visuals Processed</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Enterprise Design Systems" data-depth="METRIC" data-content="Created 200+ graphic templates for Yokogawa across 12 countries, proving scalable system architecture."><div class="text-2xl font-display font-bold text-emerald">200+</div><div class="text-[10px] text-textMuted">Templates</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Accessibility Compliance" data-depth="METRIC" data-content="Achieved 90%+ WCAG compliance rate at Microsoft PCoE, reducing legal risk for global expansion."><div class="text-2xl font-display font-bold text-emerald">90%+</div><div class="text-[10px] text-textMuted">WCAG Pass</div></div>
    <div class="glass-card p-4 rounded-xl text-center cursor-pointer" data-popup data-title="Campaign Velocity" data-depth="METRIC" data-content="Led 50+ online campaigns for Ninja, Aiper, Pure, driving engagement lifts of 25% and sales acceleration of 20%."><div class="text-2xl font-display font-bold text-emerald">50+</div><div class="text-[10px] text-textMuted">Campaigns</div></div>
  </div>

  <!-- Former Experience Vectors (existing) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Former Experience Vectors for Alex to Implement at the Company</span></div>
  <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-16">
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Microsoft" data-depth="ENTERPRISE CLIENT" data-content="Microsoft PCoE (Partner Center of Excellence). Delivered 90%+ WCAG compliant designs, 75%+ win rate support. 8 Microsoft certifications earned Feb 2025.">Microsoft</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="H&M" data-depth="ENTERPRISE CLIENT" data-content="Enterprise deal through Microsoft PCoE. Designed custom proposals for high-priority business presentations.">H&M</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="La Roche" data-depth="ENTERPRISE CLIENT" data-content="La Roche (pharmaceutical). Enterprise deal through Microsoft PCoE.">La Roche</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Erste Group" data-depth="ENTERPRISE CLIENT" data-content="Erste Group Bank. Enterprise deal through Microsoft PCoE.">Erste Group</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="UAE Ministry" data-depth="ENTERPRISE CLIENT" data-content="UAE Ministry of Education. Government compliance and accessibility work.">UAE Ministry</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Ninja" data-depth="DTC & CorporateCLIENT" data-content="Market launch in Romania through Skin Media. Part of 50+ targeted online campaigns driving 25% audience engagement boost.">Ninja</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Crock-Pot" data-depth="DTC & CorporateCLIENT" data-content="DTC & Corporatefunnel experience. Industry category expertise.">Crock-Pot</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Shark" data-depth="DTC & CorporateCLIENT" data-content="Multi-channel campaigns across Meta, TikTok, Amazon, retail.">Shark</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="AIPER" data-depth="DTC & CorporateCLIENT" data-content="Brand launch support with 25% audience engagement boost.">AIPER</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="MADE.com" data-depth="E-COMMERCE CLIENT" data-content="Processed 25,000+ product visuals for international launch across 5 countries.">MADE.com</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Nikon" data-depth="DTC & CorporateCLIENT" data-content="Online campaigns through Skin Media.">Nikon</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Yokogawa" data-depth="ENTERPRISE CLIENT" data-content="Yokogawa Europe: 200+ templates, 12 countries, 20% brand awareness lift.">Yokogawa</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Pure" data-depth="DTC & CorporateCLIENT" data-content="Online campaigns through Skin Media.">Pure</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Pathwwway" data-depth="UI/UX CLIENT" data-content="UI Design & Campaigns: 35-40% user engagement increase, 30% bounce rate reduction.">Pathwwway</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Romexpo" data-depth="PRINT & REBRANDING" data-content="10+ trademark rebrands, 30% production time cut, 20% cost reduction.">Romexpo</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="HMS Networks" data-depth="ENTERPRISE CLIENT" data-content="Enterprise deal through Microsoft PCoE.">HMS Networks</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="SITA Africa" data-depth="ENTERPRISE CLIENT" data-content="Enterprise deal through Microsoft PCoE.">SITA Africa</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Serus Dacia" data-depth="FREELANCE CLIENT" data-content="Branding through AP-ID.ro.">Serus Dacia</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="Engino Toys" data-depth="FREELANCE CLIENT" data-content="Branding through AP-ID.ro.">Engino Toys</div>
    <div class="glass-card p-4 rounded-lg text-center text-xs font-bold cursor-pointer" data-popup data-title="CroitorulTau" data-depth="FREELANCE CLIENT" data-content="Branding through AP-ID.ro.">CroitorulTau</div>
  </div>

  <!-- New: Psychological & Empathetic Traits Grid (from CSV) -->
  <div class="section-divider"><span class="text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4" style="color:#C87B5E;">Psychological & Empathetic Traits</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
    <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="Behavioral Economics" data-depth="PSYCHOLOGICAL TRAIT" data-content="Formal background in economics provides a rational, market-based lens for analyzing consumer value, supply and demand, and the fundamental drivers of marketing impact. Designs campaigns with a clear understanding of market forces, consumer value, and ROI.">
      <div class="flex items-center gap-2"><span class="text-human text-xl">📈</span><div><h4 class="font-display font-bold text-sm">Behavioral Economics</h4><p class="text-xs text-textMuted">Market forces, supply/demand, consumer value</p></div></div>
    </div>
    <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="Cognitive Psychology (MBTI)" data-depth="PSYCHOLOGICAL TRAIT" data-content="Tracking of MBTI type and psychological evolution since 2017 as a way to better understand cognitive frameworks and how people process information. Creates targeted visual assets that appeal to specific consumer archetypes and cognitive processing styles.">
      <div class="flex items-center gap-2"><span class="text-ai text-xl">🧠</span><div><h4 class="font-display font-bold text-sm">Cognitive Psychology (MBTI)</h4><p class="text-xs text-textMuted">Tracking since 2017, cognitive archetypes</p></div></div>
    </div>
    <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="Profound Empathy (NGO)" data-depth="PSYCHOLOGICAL TRAIT" data-content="'You cannot fire a volunteer'—lesson from coordinating NGO volunteers. Instills a culture of active listening, motivation, and mutual respect. Fosters exceptional emotional intelligence and collaborative leadership.">
      <div class="flex items-center gap-2"><span class="text-gold text-xl">❤️</span><div><h4 class="font-display font-bold text-sm">Profound Empathy (NGO)</h4><p class="text-xs text-textMuted">"You cannot fire a volunteer"</p></div></div>
    </div>
    <div class="glass-card p-4 rounded-lg cursor-pointer" data-popup data-title="Strategic Consultancy" data-depth="PSYCHOLOGICAL TRAIT" data-content="Proactively critiques briefs, suggests A/B test variants, and acts as a strategic partner who adds value beyond pure design execution. 'Alex didn't just offer me a drawing, he offered me a new image... he offered consultancy, I say, offered by an artist!'">
      <div class="flex items-center gap-2"><span class="text-emerald text-xl">💡</span><div><h4 class="font-display font-bold text-sm">Strategic Consultancy</h4><p class="text-xs text-textMuted">Consulting offered by an artist</p></div></div>
    </div>
  </div>
</section>

<!-- ==================== TAB 7: FOR The Company · AI PARTNER (ENHANCED – visual hierarchy, cards, process flow, enriched popups) ==================== -->
<section id="ai-partner" class="tab-content">

  <!-- HERO with stats -->
  <div class="mb-20">
    <div class="flex flex-wrap justify-between items-end border-b border-border/40 pb-6 mb-10">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-ai/30 bg-ai/5 text-ai text-xs font-mono" data-popup data-title="AI Persona Research Layer" data-depth="TIER 2 · DATA · AI PARTNER PERSPECTIVE" data-content="This section positions the AI as a common team member working for both Alex (AP-ID.ro) and Client (the Company). The AI is not a tool but a strategic partner—a living system requiring continuous human-AI collaboration. The proposal is for a Symbiotic Infrastructure Co-Investment, not a vendor-client relationship. (Source: Perspective for Client.pdf, section 5)">
          <span class="w-2 h-2 rounded-full bg-ai animate-pulse"></span>
          AI PARTNER · COMMON TEAM MEMBER FOR AP-ID × The Company
        </div>
        <h1 class="font-display text-5xl md:text-7xl font-bold leading-[0.95] mt-6 mb-4">AI as a <span class="gradient-text">Common Team Member</span></h1>
        <p class="text-xl text-textMuted max-w-3xl leading-relaxed">Working for both <span class="font-semibold" style="color:#C87B5E;">Alex (AP-ID.ro)</span> and <span class="text-ai font-semibold">Client (the Company)</span>—a symbiotic R&D partnership.</p>
      </div>
      <div class="grid grid-cols-3 gap-4 mt-6 md:mt-0">
        <div class="glass-panel p-3 rounded-xl text-center"><div class="text-2xl font-display font-bold text-ai">100%</div><div class="text-[10px] text-textMuted">Data Private</div></div>
        <div class="glass-panel p-3 rounded-xl text-center"><div class="text-2xl font-display font-bold text-ai">85‑90%</div><div class="text-[10px] text-textMuted">DNA Capture</div></div>
        <div class="glass-panel p-3 rounded-xl text-center"><div class="text-2xl font-display font-bold text-ai">5+ Yrs</div><div class="text-[10px] text-textMuted">Horizon</div></div>
      </div>
    </div>
    <!-- Brand reference row (the Company × AP-ID × AI) -->
    <div class="flex justify-center mb-4">
      <div class="glass-panel p-5 rounded-2xl inline-flex items-center gap-4" style="box-shadow:0 0 20px rgba(77,171,247,0.2);">
        <div class="company-wordmark company-gradient text-2xl">company</div>
        <span class="text-textMuted text-xl">×</span>
        <div class="gradient-text text-2xl font-display font-bold">AP-ID</div>
        <span class="text-textMuted text-xl">×</span>
        <div class="text-ai text-2xl font-display font-bold">AI</div>
      </div>
    </div>
  </div>

  <!-- THE AI AS A SHARED TEAM MEMBER (visual card trio) -->
  <div class="section-divider"><span class="text-ai text-xs font-bold uppercase tracking-widest px-4">The AI as a Shared Team Member</span></div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
    <div class="glass-panel p-6 rounded-2xl text-center border-t-2 border-ai/50 cursor-pointer group transition-all hover:border-ai" data-popup data-title="the Company" data-depth="ENTITY" data-content="the Company is a 40+ person team scaling toward $70M in revenue. The company sells titanium cookware, vacuum sealing systems, and more via DTC, Amazon, TikTok Shop, and retail. The AI system serves the Company by automating creative production while preserving brand soul. (Source: JD + live research)">
      <div class="w-20 h-20 mx-auto rounded-full flex items-center justify-center text-3xl font-display font-bold mb-3" style="background:rgba(200,123,94,0.1); border:2px solid #C87B5E; color:#C87B5E;">P</div>
      <h4 class="font-display font-bold text-lg">the Company</h4>
      <p class="text-xs text-textMuted">the Client · CMO</p>
      <div class="mt-3 text-[10px] text-textMuted">Scaling to $70M</div>
    </div>
    <div class="glass-panel p-6 rounded-2xl text-center border-t-2 border-ai/50 cursor-pointer group transition-all hover:border-ai" data-popup data-title="Shared AI" data-depth="ENTITY" data-content="The AI is a private, locally-run Large Language Model (LLM) – a 'digital twin' – that works for both Alex and the Company simultaneously. It is not a generic tool; it is a living system with infinite context memory, trained on public data first, then refined with proprietary brand inputs in a secure sandbox. It operates in bimodal structure: Mode A (strategy) and Mode B (execution). (Source: Perspective for Client.pdf, section 2.2)">
      <div class="w-24 h-24 mx-auto rounded-full bg-ai/10 border-2 border-ai flex items-center justify-center text-4xl mb-3 pulse-glow group-hover:scale-105 transition">🤖</div>
      <h4 class="font-display font-bold text-ai text-lg">Shared AI</h4>
      <p class="text-xs text-textMuted">Private Local LLM · Digital Twin</p>
      <p class="text-[10px] text-ai mt-1 uppercase tracking-wider">Common Team Member</p>
    </div>
    <div class="glass-panel p-6 rounded-2xl text-center border-t-2 border-ai/50 cursor-pointer group transition-all hover:border-ai" data-popup data-title="AP-ID.ro" data-depth="ENTITY" data-content="Alexandru Popescu, Art Director & Creative Systems Architect. 15+ years experience. Founder of AP-ID.ro (Achieve a Professional IDentity). He brings corporate rigor (Microsoft, Yokogawa) and DTC & Corporate+ Corporate expertise (Ninja, Crock‑Pot), plus a proprietary AI system he is building to augment his own creativity and scale it to clients like the Company. (Source: CV + LinkedIn)">
      <div class="w-20 h-20 mx-auto rounded-full bg-accent/10 border-2 border-accent flex items-center justify-center text-3xl font-display font-bold text-accent mb-3">AP</div>
      <h4 class="font-display font-bold text-lg">AP-ID.ro</h4>
      <p class="text-xs text-textMuted">Alexandru Popescu · Art Director</p>
      <div class="mt-3 text-[10px] text-textMuted">15+ years · Systems Architect</div>
    </div>
  </div>

  <!-- THREE-TIER INFORMATION ARCHITECTURE (visual cards with depth indicators) -->
  <div class="section-divider"><span class="text-ai text-xs font-bold uppercase tracking-widest px-4">Three‑Tier Information Architecture</span></div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-human transition-all hover:shadow-[0_0_15px_rgba(255,107,107,0.2)] cursor-pointer" data-popup data-title="Tier 0: DEFINITION" data-depth="PERSONAL DNA" data-content="The foundational DNA of the operator and the brand. Includes: CV (Alexandru Popescu), Personal Identity, MBTI Evolution (since 2017), NGO Empathy Framework, Economics Baseline, Microsoft Achievements. This tier is private to Alex's AI but shapes how the AI reasons. (Source: simulation folder structure – Layer 0)">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-full bg-human/10 flex items-center justify-center font-display font-bold text-human text-xl">T0</div><h4 class="font-display font-bold">Tier 0: DEFINITION</h4></div>
      <p class="text-xs text-textMuted mb-4">Personal DNA that shapes AI reasoning. <span class="text-human">(Private to Alex's AI)</span></p>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between border-b border-border/30 pb-2"><span>CV & Personal Identity</span><span class="text-human">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>MBTI Evolution (2017+)</span><span class="text-human">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>NGO Empathy Framework</span><span class="text-human">●</span></div>
        <div class="flex justify-between"><span>Economics Baseline</span><span class="text-human">●</span></div>
      </div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-ai transition-all hover:shadow-[0_0_15px_rgba(77,171,247,0.2)] cursor-pointer" data-popup data-title="Tier 1: INFO" data-depth="EXTERNAL SOURCES" data-content="External market and client-specific data ingestion. the Company JD, Client Persona (Creator-Led Growth), LinkedIn Conversation History, Competitive Landscape, Public Brand Assets from company. This tier is shared with the Company upon request. (Source: simulation folder structure – Layer 1)">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-full bg-ai/10 flex items-center justify-center font-display font-bold text-ai text-xl">T1</div><h4 class="font-display font-bold">Tier 1: INFO</h4></div>
      <p class="text-xs text-textMuted mb-4">External sources shared between entities.</p>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between border-b border-border/30 pb-2"><span>the Company JD & Briefs</span><span class="text-ai">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>Client Persona / Comm Style</span><span class="text-ai">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>Competitive Landscape</span><span class="text-ai">●</span></div>
        <div class="flex justify-between"><span>Public Brand Assets</span><span class="text-ai">●</span></div>
      </div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-accent transition-all hover:shadow-[0_0_15px_rgba(109,93,211,0.2)] cursor-pointer" data-popup data-title="Tier 2: DATA" data-depth="PROCESSED INTELLIGENCE" data-content="Synthesized intelligence mapped to stakeholder needs. Four perspectives: HR (risk mitigation, cultural validation), Business (Client's operational leverage, founder alignment), Technical (AI architecture, data privacy protocols), Relational/Human (testimonials, emotional intelligence). Each perspective is a separate document generated by the AI for YOUR team. (Source: simulation folder structure – Tier_2 - DATA)">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center font-display font-bold text-accent text-xl">T2</div><h4 class="font-display font-bold">Tier 2: DATA</h4></div>
      <p class="text-xs text-textMuted mb-4">Processed intelligence for your team.</p>
      <div class="space-y-2 text-xs">
        <div class="flex justify-between border-b border-border/30 pb-2"><span>HR Perspective</span><span class="text-accent">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>Business (Client) Perspective</span><span class="text-accent">●</span></div>
        <div class="flex justify-between border-b border-border/30 pb-2"><span>Technical Architecture</span><span class="text-accent">●</span></div>
        <div class="flex justify-between"><span>Relational (Human)</span><span class="text-accent">●</span></div>
      </div>
    </div>
  </div>

  <!-- AI ARCHITECTURE & DATA PRIVACY (two cards with icons + progress rings) -->
  <div class="section-divider"><span class="text-ai text-xs font-bold uppercase tracking-widest px-4">AI Architecture & Data Privacy</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-ai transition-all hover:shadow-[0_0_15px_rgba(77,171,247,0.2)] cursor-pointer" data-popup data-title="Private Local LLM (Digital Twin)" data-depth="TECHNICAL SPEC" data-content="A custom-built AI system running on the candidate's own hardware, ensuring complete data privacy and IP security. Eliminates data leakage risk, a major concern for startups. Provides a secure, internal tool rather than a dependency on public cloud services. Air-gapped architecture with local compute power as the only limit. (Source: CASE STUDY-the Company's AI_Arhitecture_Solutions.csv)">
      <div class="flex items-center gap-4 mb-4"><div class="w-12 h-12 rounded-lg bg-ai/10 flex items-center justify-center"><svg class="w-6 h-6 text-ai" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg></div><div><h3 class="font-display text-xl font-bold">Private Local LLM</h3><p class="text-xs text-textMuted">"Digital Twin" architecture</p></div></div>
      <p class="text-sm text-textMuted mb-4">Custom-built AI on candidate's own hardware. 100% data privacy. Air-gapped. No cloud dependency.</p>
      <div class="grid grid-cols-3 gap-2 text-center text-xs"><div class="bg-surface/50 rounded p-2"><div class="font-bold text-ai">100%</div><div class="text-textMuted">Private</div></div><div class="bg-surface/50 rounded p-2"><div class="font-bold text-ai">Local</div><div class="text-textMuted">Hardware</div></div><div class="bg-surface/50 rounded p-2"><div class="font-bold text-ai">∞</div><div class="text-textMuted">Memory</div></div></div>
      <div class="mt-4 w-full h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-full h-full bg-ai rounded-full"></div></div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-emerald transition-all hover:shadow-[0_0_15px_rgba(16,185,129,0.2)] cursor-pointer" data-popup data-title="Ethical AI Commitment" data-depth="PRIVACY PROTOCOL" data-content="The candidate commits to training the model only on public information and ingesting proprietary client data within a secure, sandboxed environment. Signals deep ethical responsibility and respect for client confidentiality, building trust and demonstrating responsible innovation. 'My AI works with all my past clients now, addressing their infrastructural needs working with the same restriction: public information only.' (Source: Perspective for Client.pdf, section 5.2)">
      <div class="flex items-center gap-4 mb-4"><div class="w-12 h-12 rounded-lg bg-emerald/10 flex items-center justify-center"><svg class="w-6 h-6 text-emerald" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg></div><div><h3 class="font-display text-xl font-bold">Ethical AI Commitment</h3><p class="text-xs text-textMuted">Public-data-only training</p></div></div>
      <p class="text-sm text-textMuted mb-4">Trains only on public information. Proprietary data only in sandboxed environment. If clients publish work, AI learns from public domain.</p>
      <div class="p-3 rounded-lg" style="background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.2);"><p class="text-xs italic text-emerald">"If any of my clients decide to publish our work, then my AI grabs that from the public domain and reintegrates it in FURTHER development process that never ends really."</p></div>
    </div>
  </div>

  <!-- EXECUTABLE IP · TRANSFERABLE TEMPLATE MODEL (phased roadmap with visuals) -->
  <div class="section-divider"><span class="text-ai text-xs font-bold uppercase tracking-widest px-4">Executable IP · Transferable Template Model</span></div>
  <div class="glass-panel p-8 rounded-2xl mb-16" data-popup data-title="Ownership Model" data-depth="IP TRANSFER PROTOCOL" data-content="The system delivers a transferable template model that becomes the Company's own 'executable IP' to be run on their local machines. Ensures the Company owns the final creative engine, decoupling them from vendor lock-in and creating a sustainable, long-term capability. 'I don't just deliver outputs; I deliver a working template model. Think of it as executable intellectual property. After initial configuration on your machines, it executes with the same strategic fidelity and results, completely decoupled from my personal infrastructure. You own the engine, not just the fuel.' (Source: simulation moment 3)">
    <h3 class="font-display text-2xl font-bold mb-8 text-center">Ownership Model · You Own the Engine</h3>
    <div class="relative flex flex-col md:flex-row justify-between items-center gap-4 mb-8">
      <!-- visual connector line (desktop) -->
      <div class="absolute left-0 top-1/2 w-full h-0.5 bg-border/50 -translate-y-1/2 hidden md:block z-0"></div>
      <div class="relative z-10 flex flex-col items-center bg-bg px-3"><div class="w-14 h-14 rounded-full bg-human/20 flex items-center justify-center text-2xl font-bold text-human">1</div><div class="font-bold mt-2">Sandbox</div><div class="text-[10px] text-textMuted">Weeks 1-4</div><div class="text-xs text-center mt-1">Zero cost, on my AI</div></div>
      <div class="relative z-10 flex flex-col items-center bg-bg px-3"><div class="w-14 h-14 rounded-full bg-ai/20 flex items-center justify-center text-2xl font-bold text-ai">2</div><div class="font-bold mt-2">Migration</div><div class="text-[10px] text-textMuted">Month 2</div><div class="text-xs text-center mt-1">100% private servers</div></div>
      <div class="relative z-10 flex flex-col items-center bg-bg px-3"><div class="w-14 h-14 rounded-full bg-emerald/20 flex items-center justify-center text-2xl font-bold text-emerald">3</div><div class="font-bold mt-2">Your IP</div><div class="text-[10px] text-textMuted">Year 1+</div><div class="text-xs text-center mt-1">Decoupled, evolves independently</div></div>
    </div>
    <div class="mt-6 p-4 bg-ai/5 border border-ai/20 rounded-lg text-center"><p class="text-sm italic text-ai">"You own the engine, not just the fuel."</p><p class="text-xs text-textMuted mt-2">— Candidate, interview simulation</p></div>
  </div>

  <!-- SYMBIOTIC R&D · 5-YEAR HORIZON (visual comparison + timeline) -->
  <div class="section-divider"><span class="text-ai text-xs font-bold uppercase tracking-widest px-4">Symbiotic R&D · 5‑Year Horizon</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
    <div class="glass-panel p-6 rounded-2xl border border-ai/20 cursor-pointer" data-popup data-title="The Symbiosis Pitch" data-depth="PARTNERSHIP FRAMEWORK" data-content="'My AI helps build the Company's brand infrastructure initially, but then the Company's AI takes ownership and evolves independently. The real value isn't in handing over a static tool—it's in establishing a 5+ year symbiosis. I help you develop a local AI for branding; you help me refine an Art Direction mechanism that understands beyond any single brand.' (Source: simulation moment 4)">
      <h3 class="font-display text-xl font-bold mb-4">The Symbiosis Pitch</h3>
      <div class="space-y-4">
        <div class="p-3 rounded-lg" style="background:rgba(200,123,94,0.05); border:1px solid rgba(200,123,94,0.2);"><div class="text-xs uppercase tracking-wider mb-1" style="color:#C87B5E;">the Company Gains</div><ul class="text-sm text-textMuted space-y-1"><li>• Proprietary creative engine</li><li>• Scalable brand infrastructure</li><li>• 50+ ad variations/week without drift</li><li>• 79% cost savings</li><li>• 10x velocity multiplier</li></ul></div>
        <div class="p-3 rounded-lg" style="background:rgba(109,93,211,0.05); border:1px solid rgba(109,93,211,0.2);"><div class="text-xs text-accent uppercase tracking-wider mb-1">AP-ID Gains</div><ul class="text-sm text-textMuted space-y-1"><li>• Real-world testbed for AI OS</li><li>• Refinement of Art Direction intelligence</li><li>• Long-term stability</li><li>• Mutual R&D partnership</li><li>• 5+ year horizon alignment</li></ul></div>
      </div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border border-ai/20 cursor-pointer" data-popup data-title="Long-Term Partnership Model" data-depth="FUTURE-PROOFING" data-content="The AI system is framed as a perpetual growth engine. The candidate's personal AI already serves past clients using only public data, learning and evolving over time. This long-term R&D partnership model, spanning 5+ years, positions the role as a 'Creative Systems Architect.' (Source: Perspective for Client.pdf, section 5.5)">
      <h3 class="font-display text-xl font-bold mb-4">Long‑Term Vision</h3>
      <div class="relative h-32 mb-4">
        <div class="absolute bottom-0 left-0 w-full h-2 bg-surface rounded-full"></div>
        <div class="absolute bottom-0 left-0 w-3/4 h-2 bg-accent rounded-full"></div>
        <div class="absolute bottom-3 left-0 text-[10px] text-accent">Phase 1-3</div>
        <div class="absolute bottom-3 left-3/4 text-[10px] text-textMuted">Phase 4+</div>
        <div class="text-center mt-8"><span class="text-2xl font-display font-bold text-accent">5+ Years</span><div class="text-xs text-textMuted">Mutual R&D · Shared Intelligence</div></div>
      </div>
      <div class="mt-4 p-3 bg-surface/50 rounded-lg"><p class="text-xs italic text-textMain">"The template model doesn't factor into my base compensation—and I believe it shouldn't. That wouldn't be fair or sustainable."</p><p class="text-[10px] text-textMuted mt-2">— Candidate, reframing value</p></div>
    </div>
  </div>

  <!-- DOCUMENTED INTELLIGENCE PACKAGE (clickable badges, enriched from CSV and PDFs) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest whitespace-nowrap px-4">Documented Intelligence Package</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
    <div class="glass-card p-4 rounded-lg flex items-center gap-3 cursor-pointer group transition-all hover:border-accent" data-popup data-title="CV - Alexandru Popescu" data-depth="VERIFIED SOURCE" data-content="15+ years of documented experience. Full CV available upon request. Includes: Art Direction, Graphic Design, UI/UX, AI Systems Architecture, Motion Design, and WCAG compliance. Education: Economics degree, Romanian-American Uclientersity. Freelance since 2010, AP-ID.ro founder. (Source: LinkedIn profile export)">
      <svg class="w-8 h-8 text-accent shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
      <div class="flex-1 min-w-0"><div class="font-bold text-sm truncate">CV - Alexandru Popescu</div><div class="text-[10px] text-textMuted">15+ years of documented experience</div></div>
    </div>
    <div class="glass-card p-4 rounded-lg flex items-center gap-3 cursor-pointer group transition-all hover:border-accent" data-popup data-title="Microsoft Achievements" data-depth="VERIFIED SOURCE" data-content="8 Microsoft certifications earned February 2025: Accessibility Evaluation & Testing, Accessibility Fundamentals, Web Accessibility Principles & Guidelines, Create Accessible AI Experiences, Fundamental AI Concepts, Build Accessible SharePoint Sites, Create Accessible Content, Introduction to Accessibility. Signed by Satya Narayana Nadella. (Source: Microsoft certificates)">
      <svg class="w-8 h-8 text-emerald shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      <div class="flex-1 min-w-0"><div class="font-bold text-sm truncate">Microsoft Achievements</div><div class="text-[10px] text-textMuted">8 certifications in Accessibility & AI (Feb 2025)</div></div>
    </div>
    <div class="glass-card p-4 rounded-lg flex items-center gap-3 cursor-pointer group transition-all hover:border-accent" data-popup data-title="HR Perspective Research" data-depth="TIER 2 · DATA" data-content="Dual-axis competency validation: Corporate Rigor (Yokogawa 200+ templates, 12 countries; Microsoft 90%+ WCAG) and Human Empathy (NGO 'cannot fire a volunteer', testimonials). Risk mitigation, cultural fit, retention signals. Full HR analysis available. (Source: Perspective for Client.pdf, section 6)">
      <svg class="w-8 h-8 text-human shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
      <div class="flex-1 min-w-0"><div class="font-bold text-sm truncate">HR Perspective Research</div><div class="text-[10px] text-textMuted">Dual-axis competency validation</div></div>
    </div>
    <div class="glass-card p-4 rounded-lg flex items-center gap-3 cursor-pointer group transition-all hover:border-accent" data-popup data-title="Client Perspective Research" data-depth="TIER 2 · DATA" data-content="Founder alignment analysis: the Client is Co-Founder & CMO, metrics-obsessed, direct, fast-paced, system-curious. His LinkedIn focuses on Creator-Led Growth, UGC at scale, moving from 'polished but sterile' to authentic high-converting creative. Every answer in this page is calibrated to that style. (Source: AI persona research - Client perspective research.pdf)">
      <svg class="w-8 h-8 text-ai shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      <div class="flex-1 min-w-0"><div class="font-bold text-sm truncate">Client Perspective Research</div><div class="text-[10px] text-textMuted">Founder alignment analysis</div></div>
    </div>
    <div class="glass-card p-4 rounded-lg flex items-center gap-3 cursor-pointer group transition-all hover:border-accent" data-popup data-title="AI Persona Research" data-depth="TIER 2 · DATA" data-content="Bimodal workflow deep dive: Mode A (Human strategy: behavioral economics, MBTI, NGO empathy) + Mode B (Machine execution: private local LLM, infinite context, R0 logical gating). Full technical architecture documented in this page. (Source: CASE STUDY-the Company's AI_Arhitecture_Solutions.csv)">
      <svg class="w-8 h-8 text-gold shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
      <div class="flex-1 min-w-0"><div class="font-bold text-sm truncate">AI Persona Research</div><div class="text-[10px] text-textMuted">Bimodal workflow deep dive</div></div>
    </div>
    <div class="glass-card p-4 rounded-lg flex items-center gap-3 cursor-pointer group transition-all hover:border-accent" data-popup data-title="Simulated Interview Transcript" data-depth="LIVE ROLE-PLAY" data-content="Full transcript of the AI impersonating Client, covering 7 critical moments: Martial Art opening, Infrastructure First, Transferable IP, Symbiotic Partnership, Live Creative Critique (Titanium pan), Salary Framing, 24h Test Pivot. Available upon request. (Source: simulation transcript)">
      <svg class="w-8 h-8 text-accent shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
      <div class="flex-1 min-w-0"><div class="font-bold text-sm truncate">Simulated Interview Transcript</div><div class="text-[10px] text-textMuted">Live role-play with AI as Client (7 moments)</div></div>
    </div>
    <div class="glass-card p-4 rounded-lg flex items-center gap-3 cursor-pointer group transition-all hover:border-accent" data-popup data-title="Case Study CSVs" data-depth="STRUCTURED DATA" data-content="5× structured proof matrices: Yokogawa (200+ templates, 12 countries), Skin Media (50+ campaigns, 25% engagement), MADE.com (25k+ visuals), Microsoft PCoE (90%+ WCAG), Shipley (20+ global clients). Full CSV exports available. (Source: CASE STUDY CSV files)">
      <svg class="w-8 h-8 text-emerald shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
      <div class="flex-1 min-w-0"><div class="font-bold text-sm truncate">5× Case Study CSVs</div><div class="text-[10px] text-textMuted">Structured proof matrices</div></div>
    </div>
    <div class="glass-card p-4 rounded-lg flex items-center gap-3 cursor-pointer group transition-all hover:border-accent" data-popup data-title="LinkedIn Profile Export" data-depth="VERIFIED SOURCE" data-content="Full professional record: 15+ years creative leadership, Art Director & Creative Systems Architect. Endorsements and recommendations available. LinkedIn: /in/ap-id (in/ap-id). (Source: LinkedIn profile)">
      <svg class="w-8 h-8 text-human shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
      <div class="flex-1 min-w-0"><div class="font-bold text-sm truncate">LinkedIn Profile Export</div><div class="text-[10px] text-textMuted">Full professional record</div></div>
    </div>
  </div>

  <!-- Final CTA / Summary -->
  <div class="glass-panel p-8 rounded-2xl text-center border border-ai/30 bg-ai/5">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-ai/30 bg-ai/10 text-ai text-xs font-mono mb-4"><span class="w-2 h-2 rounded-full bg-ai animate-pulse"></span>READY FOR IMPLEMENTATION</div>
    <h3 class="font-display text-2xl font-bold mb-3">Symbiotic Infrastructure Co‑Investment</h3>
    <p class="text-textMuted max-w-2xl mx-auto text-sm">The AI is not a tool—it's a living system requiring continuous human‑AI collaboration. Phase 1 sandbox (zero cost), Phase 2 migration (your private servers), Phase 3 IP ownership. You own the engine, not just the fuel.</p>
    <div class="flex flex-wrap justify-center gap-3 mt-6">
      <span class="pill pill-ai">Private Local LLM</span>
      <span class="pill pill-emerald">Ethical AI</span>
      <span class="pill pill-accent">Transferable IP</span>
      <span class="pill pill-gold">5+ Year Symbiosis</span>
    </div>
  </div>

</section>
  
<!-- ==================== TAB 8: FOR NIV (REDESIGNED - PART 1 - Hero, Client's Style, Alignment Radar, Velocity, Category Fluency, Live Critique, Hybrid Persona) ==================== -->
<section id="for-client" class="tab-content">

  <!-- HERO SECTION with stats and visual bar -->
  <div class="mb-20">
    <div class="flex flex-wrap justify-between items-end border-b border-border/40 pb-6 mb-10">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-client/30 bg-client/5 text-client text-xs font-mono" data-popup data-title="Audience: the Client" data-depth="FOUNDER PROFILE" data-content="Client is Co‑Founder & CMO, previously Head of Marketing. He focuses on Creator‑Led Growth, UGC at scale, and moving from 'polished but sterile' ads to authentic, high‑converting creative. He cares deeply about unit economics, burn rate, and scalable systems. (Source: LinkedIn research + JD analysis)">
          <span class="w-2 h-2 rounded-full bg-client animate-pulse"></span>
          DIRECTED TO The Client // CO-FOUNDER & CMO
        </div>
        <h1 class="font-display text-6xl md:text-8xl font-bold leading-[0.9] mt-6 mb-4">
          For <span class="client-gradient">Client.</span><br>
          <span class="text-textMuted text-4xl md:text-5xl font-normal">The Velocity Partner You Need.</span>
        </h1>
        <p class="text-xl md:text-2xl text-textMuted max-w-3xl leading-relaxed">
          You're scaling <span class="text-client font-semibold">UP</span>. Your bottleneck isn't ideas—it's <span class="text-client font-semibold">velocity</span>. I'm not here to make things pretty. I'm here to <span class="text-human font-semibold">build the engine</span> that makes 50+ premium variations a week inevitable.
        </p>
      </div>
      <!-- Visual stat panel -->
      <div class="grid grid-cols-2 gap-4 mt-6 md:mt-0">
        <div class="glass-panel p-4 rounded-xl text-center pulse-glow-client">
          <div class="text-3xl font-display font-bold client-gradient mb-1">$70M</div>
          <div class="text-[10px] text-textMuted uppercase tracking-wider">Revenue Target</div>
        </div>
        <div class="glass-panel p-4 rounded-xl text-center">
          <div class="text-3xl font-display font-bold text-client mb-1">50+</div>
          <div class="text-[10px] text-textMuted uppercase tracking-wider">Variations/Week</div>
        </div>
        <div class="glass-panel p-4 rounded-xl text-center">
          <div class="text-3xl font-display font-bold text-client mb-1">40+</div>
          <div class="text-[10px] text-textMuted uppercase tracking-wider">Person Team</div>
        </div>
        <div class="glass-panel p-4 rounded-xl text-center">
          <div class="text-3xl font-display font-bold text-client mb-1">6+</div>
          <div class="text-[10px] text-textMuted uppercase tracking-wider">Channels</div>
        </div>
      </div>
    </div>
  </div>

  <!-- NIV'S COMMUNICATION STYLE (enhanced cards with icons and progress indicators) -->
  <div class="section-divider"><span class="text-client text-xs font-bold uppercase tracking-widest px-4">How Client Thinks · How Alex Matches</span></div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-client transition-all hover:shadow-[0_0_20px_rgba(249,115,22,0.2)] cursor-pointer" data-popup data-title="Metrics-Obsessed" data-depth="NIV'S STYLE" data-content="From his LinkedIn activity and JD, Client asks: 'How did this impact CTR, ROAS, conversion?' Not brand sentiment. Alex matches by tying every asset to funnel logic, A/B variants, and documented 20‑40% engagement lifts. (Source: CV case studies + simulation transcript)">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg bg-client/10 flex items-center justify-center"><svg class="w-6 h-6 text-client" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg></div><h3 class="font-display text-lg font-bold">Metrics‑Obsessed</h3></div>
      <p class="text-sm text-textMuted mb-3">You ask: "How did this impact CTR, ROAS, conversion?" Not brand sentiment.</p>
      <div class="border-t border-border/30 pt-3"><p class="text-xs text-client font-bold uppercase tracking-wider mb-1">Alex Matches:</p><p class="text-xs text-textMuted">Every asset tied to funnel logic, A/B variants, performance data. 20‑40% engagement lifts documented.</p></div>
      <div class="mt-3"><div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">Match score:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[95%] h-full bg-client rounded-full"></div></div><span class="text-[10px] text-client">95%</span></div></div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-client transition-all hover:shadow-[0_0_20px_rgba(249,115,22,0.2)] cursor-pointer" data-popup data-title="Direct & Fast‑Paced" data-depth="NIV'S STYLE" data-content="Israeli tech/DTC & Corporatefounders value concise, confident answers. No lengthy preambles. Alex matches with high‑signal, low‑noise communication, text‑only, emoji‑free professional density. (Source: simulation persona calibration)">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg bg-client/10 flex items-center justify-center"><svg class="w-6 h-6 text-client" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg></div><h3 class="font-display text-lg font-bold">Direct & Fast‑Paced</h3></div>
      <p class="text-sm text-textMuted mb-3">You value concise, confident answers. No lengthy preambles. Get to the "so what?" quickly.</p>
      <div class="border-t border-border/30 pt-3"><p class="text-xs text-client font-bold uppercase tracking-wider mb-1">Alex Matches:</p><p class="text-xs text-textMuted">High‑signal, low‑noise communication. Text‑only, emoji‑free professional density. No fluff.</p></div>
      <div class="mt-3"><div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">Match score:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[98%] h-full bg-client rounded-full"></div></div><span class="text-[10px] text-client">98%</span></div></div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-t-2 border-client transition-all hover:shadow-[0_0_20px_rgba(249,115,22,0.2)] cursor-pointer" data-popup data-title="System‑Curious" data-depth="NIV'S STYLE" data-content="Your AI digital twin pitch aligns with his interest in operational leverage. He drills into how it works, not just that it exists. Alex matches with full technical transparency, phased roadmap, and transferable IP. (Source: simulation transcript, moment 2‑3)">
      <div class="flex items-center gap-3 mb-4"><div class="w-12 h-12 rounded-lg bg-client/10 flex items-center justify-center"><svg class="w-6 h-6 text-client" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg></div><h3 class="font-display text-lg font-bold">System‑Curious</h3></div>
      <p class="text-sm text-textMuted mb-3">Your AI pitch aligns with your interest in operational leverage. You drill into how it works, not just that it exists.</p>
      <div class="border-t border-border/30 pt-3"><p class="text-xs text-client font-bold uppercase tracking-wider mb-1">Alex Matches:</p><p class="text-xs text-textMuted">Full technical transparency. Phase 1‑2‑3 roadmap. Transferable IP. You own the engine.</p></div>
      <div class="mt-3"><div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">Match score:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[92%] h-full bg-client rounded-full"></div></div><span class="text-[10px] text-client">92%</span></div></div>
    </div>
  </div>

  <!-- STRATEGIC ALIGNMENT RADAR (visual chart) + table (condensed) -->
  <div class="section-divider"><span class="text-client text-xs font-bold uppercase tracking-widest px-4">Strategic Alignment · Your Needs vs. My Proof</span></div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
    <!-- Radar chart -->
    <div class="glass-panel p-6 rounded-2xl">
      <h3 class="font-display text-xl font-bold mb-4 text-center">Alignment Radar</h3>
      <div class="relative w-full max-w-xs mx-auto">
        <svg viewBox="0 0 200 200" class="w-full h-full">
          <!-- 5 axes -->
          <polygon points="100,20 175,70 155,160 45,160 25,70" fill="none" stroke="#1E2029" stroke-width="1"/>
          <polygon points="100,55 156,83 141,140 59,140 44,83" fill="none" stroke="#1E2029" stroke-width="1"/>
          <polygon points="100,90 137,96 128,120 72,120 63,96" fill="none" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="100" y2="20" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="175" y2="70" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="155" y2="160" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="45" y2="160" stroke="#1E2029" stroke-width="1"/>
          <line x1="100" y1="100" x2="25" y2="70" stroke="#1E2029" stroke-width="1"/>
          <!-- data polygon -->
          <polygon points="100,35 160,78 148,148 52,148 38,78" fill="rgba(249,115,22,0.15)" stroke="#F97316" stroke-width="2"/>
          <circle cx="100" cy="35" r="3" fill="#F97316"/>
          <circle cx="160" cy="78" r="3" fill="#F97316"/>
          <circle cx="148" cy="148" r="3" fill="#F97316"/>
          <circle cx="52" cy="148" r="3" fill="#F97316"/>
          <circle cx="38" cy="78" r="3" fill="#F97316"/>
          <text x="100" y="14" fill="#E2E8F0" text-anchor="middle" font-size="8">Scale</text>
          <text x="182" y="76" fill="#E2E8F0" text-anchor="start" font-size="8">AI</text>
          <text x="162" y="170" fill="#E2E8F0" text-anchor="middle" font-size="8">DTC</text>
          <text x="38" y="170" fill="#E2E8F0" text-anchor="middle" font-size="8">Psychology</text>
          <text x="18" y="76" fill="#E2E8F0" text-anchor="end" font-size="8">EQ</text>
        </svg>
      </div>
      <div class="flex justify-center gap-4 mt-4 text-xs"><div class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-client"></span><span>Alex’s capability</span></div><div class="flex items-center gap-1"><span class="w-3 h-3 border border-client rounded-full"></span><span>the Company need</span></div></div>
    </div>
    <!-- Compact table with visual progress -->
    <div class="glass-panel p-6 rounded-2xl overflow-hidden">
      <div class="space-y-4">
        <div class="flex justify-between items-center"><span class="text-sm font-semibold">Scale creative without losing soul</span><span class="text-xs text-emerald">95% match</span></div><div class="progress-bar"><div class="progress-fill bg-client" style="width:95%"></div></div>
        <div class="flex justify-between items-center"><span class="text-sm font-semibold">AI as operational multiplier</span><span class="text-xs text-emerald">90%</span></div><div class="progress-bar"><div class="progress-fill bg-client" style="width:90%"></div></div>
        <div class="flex justify-between items-center"><span class="text-sm font-semibold">DTC & Corporate Industry Expertise</span><span class="text-xs text-emerald">88%</span></div><div class="progress-bar"><div class="progress-fill bg-client" style="width:88%"></div></div>
        <div class="flex justify-between items-center"><span class="text-sm font-semibold">Behavioral Psychology</span><span class="text-xs text-emerald">92%</span></div><div class="progress-bar"><div class="progress-fill bg-client" style="width:92%"></div></div>
        <div class="flex justify-between items-center"><span class="text-sm font-semibold">Remote EQ</span><span class="text-xs text-emerald">94%</span></div><div class="progress-bar"><div class="progress-fill bg-client" style="width:94%"></div></div>
      </div>
      <div class="mt-4 text-center"><span class="text-[10px] text-textMuted">Click any row for full proof (Yokogawa, Microsoft, testimonials)</span></div>
    </div>
  </div>

  <!-- THE VELOCITY SOLUTION (enhanced with icon array and step visuals) -->
  <div class="section-divider"><span class="text-client text-xs font-bold uppercase tracking-widest px-4">The Velocity Solution · 50+ Variations/Week</span></div>
  <div class="glass-panel p-8 rounded-2xl mb-16">
    <h3 class="font-display text-2xl font-bold mb-6 text-center">How I Deliver <span class="client-gradient">50+ Variations/Week</span></h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="text-center p-4 bg-surface/30 rounded-xl">
        <div class="text-3xl mb-2">📉</div>
        <div class="text-sm font-semibold text-human">Traditional Senior Designer</div>
        <div class="text-2xl font-bold text-human">5-8</div>
        <div class="text-xs text-textMuted">variations/week</div>
      </div>
      <div class="text-center p-4 bg-surface/30 rounded-xl">
        <div class="text-3xl mb-2">📊</div>
        <div class="text-sm font-semibold text-gold">Agency + Freelance</div>
        <div class="text-2xl font-bold text-gold">15-20</div>
        <div class="text-xs text-textMuted">variations/week</div>
      </div>
      <div class="text-center p-4 bg-surface/30 rounded-xl border border-client/30">
        <div class="text-3xl mb-2">🚀</div>
        <div class="text-sm font-semibold text-client">Alex + Bimodal AI</div>
        <div class="text-2xl font-bold text-client">50+</div>
        <div class="text-xs text-textMuted">variations/week ✓</div>
      </div>
    </div>
    <div class="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-border/30">
      <div class="text-center"><div class="text-3xl font-display font-bold text-client">10x</div><div class="text-xs text-textMuted uppercase tracking-wider">Velocity Multiplier</div></div>
      <div class="text-center"><div class="text-3xl font-display font-bold text-emerald">0</div><div class="text-xs text-textMuted uppercase tracking-wider">Brand Drift</div></div>
      <div class="text-center"><div class="text-3xl font-display font-bold text-accent">79%</div><div class="text-xs text-textMuted uppercase tracking-wider">Cost Savings</div></div>
    </div>
  </div>

  <!-- CATEGORY FLUENCY (brand grid + visual highlight) -->
  <div class="section-divider"><span class="text-client text-xs font-bold uppercase tracking-widest px-4">Category Fluency · I Already Know Your Space</span></div>
  <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
    <div class="glass-card p-4 rounded-xl text-center border-t-2 border-client cursor-pointer" data-popup data-title="Ninja" data-depth="SKIN MEDIA · 2024" data-content="Led market launch design in Romania. 50+ campaigns, 25% engagement boost. Industry category expertise directly transferable to the Company."><div class="text-xl font-display font-bold client-gradient">Ninja</div><div class="text-[10px] text-textMuted">Market Launch</div></div>
    <div class="glass-card p-4 rounded-xl text-center border-t-2 border-client cursor-pointer" data-popup data-title="Crock-Pot" data-depth="SKIN MEDIA · DTC" data-content="DTC & Corporatefunnel experience across Meta, TikTok, Amazon. Understands conversion drivers in kitchen category."><div class="text-xl font-display font-bold client-gradient">Crock-Pot</div><div class="text-[10px] text-textMuted">DTC & CorporateFunnel</div></div>
    <div class="glass-card p-4 rounded-xl text-center border-t-2 border-client cursor-pointer" data-popup data-title="Shark" data-depth="SKIN MEDIA · MULTI-CHANNEL" data-content="Multi‑channel campaigns. Visual language that resonates with    consumers."><div class="text-xl font-display font-bold client-gradient">Shark</div><div class="text-[10px] text-textMuted">Multi‑Channel</div></div>
    <div class="glass-card p-4 rounded-xl text-center border-t-2 border-client cursor-pointer" data-popup data-title="AIPER" data-depth="SKIN MEDIA · ENGAGEMENT" data-content="Brand launch support, +25% engagement. Builds brand awareness through targeted campaigns."><div class="text-xl font-display font-bold client-gradient">AIPER</div><div class="text-[10px] text-textMuted">+25% Engagement</div></div>
    <div class="glass-card p-4 rounded-xl text-center border-t-2 border-client cursor-pointer" data-popup data-title="MADE.com" data-depth="E-COMMERCE SCALE" data-content="25,000+ product visuals for international launch across 5 countries. Capacity to handle immense content demands."><div class="text-xl font-display font-bold client-gradient">MADE.com</div><div class="text-[10px] text-textMuted">25K+ Visuals</div></div>
  </div>
  <div class="critique-card mb-12 cursor-pointer" data-popup data-title="Why Category Fluency Matters" data-depth="STRATEGIC INSIGHT" data-content="You don't need to teach me the   category. I understand the visual language, e‑commerce conversion patterns, channel‑specific nuances. I've been there. I've done it. I know what converts. (Source: Skin Media & MADE.com case studies)">
    <div class="flex items-start gap-4"><div class="w-12 h-12 rounded-lg bg-client/10 flex items-center justify-center shrink-0"><svg class="w-6 h-6 text-client" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg></div><div><h4 class="font-display font-bold text-lg mb-2">No Learning Curve</h4><p class="text-sm text-textMuted">You don't need to teach me the   category. I understand the visual language, the e‑commerce conversion patterns, the channel‑specific nuances. I've been there. I've done it. I know what converts.</p></div></div>
  </div>

  <!-- LIVE CREATIVE CRITIQUE (before/after visual cards) -->
  <div class="section-divider"><span class="text-client text-xs font-bold uppercase tracking-widest px-4">Live Creative Critique · Titanium Cookware Example</span></div>
  <div class="glass-panel p-8 rounded-2xl mb-16">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
      <div class="bg-surface/50 rounded-xl p-6 border border-human/20">
        <div class="flex items-center gap-2 mb-3"><span class="pill pill-human">CURRENT ASSET</span><span class="text-xs text-human font-mono">CTR 0.8%</span></div>
        <h4 class="font-display font-bold mb-2">Standard Product Shot</h4>
        <p class="text-sm text-textMuted mb-3">White background + text overlay: "Non-Stick Titanium. Safe for Kids."</p>
        <div class="text-xs text-human"><strong>Problem:</strong> Sells specs, not emotional relief. Comments say "looks like every other pan."</div>
      </div>
      <div class="bg-surface/50 rounded-xl p-6 border border-emerald/20">
        <div class="flex items-center gap-2 mb-3"><span class="pill pill-emerald">PROPOSED</span><span class="text-xs text-emerald font-mono">Target 1.5%+ CTR</span></div>
        <h4 class="font-display font-bold mb-2">UGC‑Style Clip</h4>
        <p class="text-sm text-textMuted mb-3">&lt;2‑second: parent effortlessly wiping cooked‑on cheese off pan while toddler tugs their sleeve.</p>
        <div class="text-xs text-emerald"><strong>Hook:</strong> "This pan survives my chaos." No text needed.</div>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-surface/30 rounded-lg p-4 cursor-pointer" data-popup data-title="Sensory Immediacy" data-depth="TIKTOK PSYCHOLOGY" data-content="Wiping motion + child interaction = instant relatability. Sensor‑type appeal. Safety implied, not stated. Shows non‑stick performance in context of parental stress. (Source: simulation transcript moment 5)"><div class="text-xs text-client font-bold uppercase tracking-wider mb-2">Why It Works</div><p class="text-xs text-textMuted"><strong class="text-white">Sensory Immediacy:</strong> Wiping motion + child interaction = instant relatability (Sensor‑type appeal).</p></div>
      <div class="bg-surface/30 rounded-lg p-4 cursor-pointer" data-popup data-title="Platform‑Native" data-depth="CREATOR-LED GROWTH" data-content="Feels authentic, not polished. Aligns with Client's 'creator‑led growth' philosophy. Parents scroll fast—they need to feel safety and ease in <2 seconds."><div class="text-xs text-client font-bold uppercase tracking-wider mb-2">Platform Fit</div><p class="text-xs text-textMuted"><strong class="text-white">Authentic, not polished.</strong> Aligns with your 'creator‑led growth' philosophy.</p></div>
      <div class="bg-surface/30 rounded-lg p-4 cursor-pointer" data-popup data-title="AI Acceleration" data-depth="MODE B EXECUTION" data-content="Mode B system generates 10 variations of this scene in <1 hour: different messes (tomato sauce, egg), diverse demographics, lighting conditions. Mode A ensures brand consistency. Winners in 48h."><div class="text-xs text-client font-bold uppercase tracking-wider mb-2">AI Acceleration</div><p class="text-xs text-textMuted"><strong class="text-white">10 variations in &lt;1 hour.</strong> A/B test all simultaneously. Winners in 48h instead of weeks.</p></div>
    </div>
  </div>

  <!-- WHY ALEX (hybrid persona cards) -->
  <div class="section-divider"><span class="text-client text-xs font-bold uppercase tracking-widest px-4">Why Alex · Not Just a Designer</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
    <div class="glass-panel p-6 rounded-2xl border-l-4 border-client cursor-pointer" data-popup data-title="The Engineer-Artist Hybrid" data-depth="DUAL PERSONA" data-content="I'm the hybrid of a corporate engineer and a human‑centered artist. Structural rigor from Microsoft & Yokogawa, commercial savvy from Ninja & Crock‑Pot, pioneering vision for AI‑augmented workflows, deep psychological understanding of consumers. (Source: CV + simulation)">
      <h3 class="font-display text-lg font-bold mb-3">The Engineer‑Artist Hybrid</h3>
      <p class="text-sm text-textMuted mb-4">I'm not just a designer. I'm the hybrid of a corporate engineer and a human‑centered artist.</p>
      <div class="space-y-2 text-xs"><div class="flex items-center gap-2"><span class="text-ai">▸</span> <span>Structural rigor from Microsoft & Yokogawa</span></div><div class="flex items-center gap-2"><span class="text-human">▸</span> <span>Commercial savvy from Ninja & Crock‑Pot</span></div><div class="flex items-center gap-2"><span class="text-accent">▸</span> <span>Pioneering vision for AI‑augmented workflows</span></div><div class="flex items-center gap-2"><span class="text-gold">▸</span> <span>Deep psychological understanding of consumers</span></div></div>
    </div>
    <div class="glass-panel p-6 rounded-2xl border-l-4 border-emerald cursor-pointer" data-popup data-title="Transferable IP" data-depth="FOUNDER MENTALITY" data-content="I don't just deliver outputs; I deliver a working template model—executable IP. Runs locally on your machines, no vendor lock‑in. You own the engine, not just the fuel. (Source: simulation moment 3)">
      <h3 class="font-display text-lg font-bold mb-3">You Own the Engine</h3>
      <p class="text-sm text-textMuted mb-4">I don't just deliver outputs; I deliver a working template model—executable IP.</p>
      <div class="space-y-2 text-xs"><div class="flex items-center gap-2"><span class="text-emerald">▸</span> <span>Transferable template architecture</span></div><div class="flex items-center gap-2"><span class="text-emerald">▸</span> <span>Runs locally on your machines</span></div><div class="flex items-center gap-2"><span class="text-emerald">▸</span> <span>No vendor lock‑in</span></div><div class="flex items-center gap-2"><span class="text-emerald">▸</span> <span>Permanent capability upgrade</span></div></div>
    </div>
  </div>
  
  <!-- THE SYMBIOTIC PARTNERSHIP (visual comparison + bottom line) -->
  <div class="section-divider"><span class="text-client text-xs font-bold uppercase tracking-widest px-4">The Symbiotic Partnership · Not a Vendor Relationship</span></div>
  <div class="glass-panel p-8 rounded-2xl mb-16 border border-client/30 pulse-glow-client">
    <h3 class="font-display text-2xl font-bold mb-6 text-center">Not a Vendor. A <span class="client-gradient">Co-Architect.</span></h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="p-4 rounded-lg bg-surface/50 cursor-pointer" data-popup data-title="What You Get" data-depth="The Company GAINS" data-content="Proprietary creative engine that scales with revenue. 50+ premium variations/week without brand drift. US-market-ready WCAG compliance built-in. Category-fluent from Day 1 (Ninja, Crock-Pot, Shark). 79% cost savings vs. traditional approach. (Source: Executive Summary section 2)">
        <div class="text-xs text-client uppercase tracking-wider mb-2 font-bold">What You Get</div>
        <ul class="text-sm text-textMuted space-y-2">
          <li class="flex gap-2"><span class="text-client">✓</span> Proprietary creative engine that scales with revenue</li>
          <li class="flex gap-2"><span class="text-client">✓</span> 50+ premium variations/week without brand drift</li>
          <li class="flex gap-2"><span class="text-client">✓</span> US-market-ready WCAG compliance built-in</li>
          <li class="flex gap-2"><span class="text-client">✓</span> Category-fluent from Day 1 (Ninja, Crock-Pot, Shark)</li>
          <li class="flex gap-2"><span class="text-client">✓</span> 79% cost savings vs. traditional approach</li>
        </ul>
      </div>
      <div class="p-4 rounded-lg bg-surface/50 cursor-pointer" data-popup data-title="What I Bring" data-depth="AP-ID GAINS" data-content="15+ years creative leadership across enterprise & DTC. Private Local LLM 'Digital Twin' infrastructure. Microsoft-certified AI & accessibility expertise. Economics + MBTI behavioral psychology lens. 'Cannot fire a volunteer' collaborative ethos. (Source: CV + simulation)">
        <div class="text-xs text-accent uppercase tracking-wider mb-2 font-bold">What I Bring</div>
        <ul class="text-sm text-textMuted space-y-2">
          <li class="flex gap-2"><span class="text-accent">✓</span> 15+ years creative leadership across enterprise & DTC</li>
          <li class="flex gap-2"><span class="text-accent">✓</span> Private Local LLM "Digital Twin" infrastructure</li>
          <li class="flex gap-2"><span class="text-accent">✓</span> Microsoft-certified AI & accessibility expertise</li>
          <li class="flex gap-2"><span class="text-accent">✓</span> Economics + MBTI behavioral psychology lens</li>
          <li class="flex gap-2"><span class="text-accent">✓</span> "Cannot fire a volunteer" collaborative ethos</li>
        </ul>
      </div>
    </div>

    <!-- Partnership Timeline visual -->
    <div class="mt-8 p-5 rounded-xl bg-surface/30">
      <div class="text-center text-xs text-textMuted uppercase tracking-wider mb-4">Partnership Horizon</div>
      <div class="relative flex justify-between items-center">
        <div class="absolute left-0 top-1/2 w-full h-0.5 bg-border/50 -translate-y-1/2 z-0"></div>
        <div class="relative z-10 flex flex-col items-center bg-bg px-2"><span class="w-3 h-3 rounded-full bg-human"></span><span class="text-[10px] mt-1">Weeks 1-4</span><span class="text-xs font-bold text-human">Sandbox</span></div>
        <div class="relative z-10 flex flex-col items-center bg-bg px-2"><span class="w-3 h-3 rounded-full bg-ai"></span><span class="text-[10px] mt-1">Month 2</span><span class="text-xs font-bold text-ai">Migration</span></div>
        <div class="relative z-10 flex flex-col items-center bg-bg px-2"><span class="w-3 h-3 rounded-full bg-accent"></span><span class="text-[10px] mt-1">Year 1+</span><span class="text-xs font-bold text-accent">Symbiosis</span></div>
        <div class="relative z-10 flex flex-col items-center bg-bg px-2"><span class="w-3 h-3 rounded-full bg-client"></span><span class="text-[10px] mt-1">5+ Years</span><span class="text-xs font-bold text-client">Eternal</span></div>
      </div>
    </div>

    <div class="mt-8 p-6 rounded-xl bg-gradient-to-r from-client/10 to-accent/10 border border-client/20 cursor-pointer" data-popup data-title="The Bottom Line" data-depth="STRATEGIC SUMMARY" data-content="'You're not hiring a designer. You're acquiring a strategic growth partner who will architect the creative infrastructure needed to reach $70M and beyond.' – This reframes the engagement as a co‑investment, not a transaction. (Source: Executive Summary bottom line)">
      <div class="text-center">
        <div class="text-xs text-textMuted uppercase tracking-wider mb-2">The Bottom Line</div>
        <p class="font-display text-xl md:text-2xl font-bold">
          "You're not hiring a designer. You're acquiring a <span class="client-gradient">strategic growth partner</span> who will architect the creative infrastructure needed to reach <span class="text-client">$70M and beyond</span>."
        </p>
      </div>
    </div>

    <!-- Cost comparison donut + metrics row -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 pt-6 border-t border-border/30">
      <div class="text-center cursor-pointer" data-popup data-title="Compensation" data-depth="STRUCTURAL TERMS" data-content="€2,300‑2,500 NET/month as B2B contractor. Covers Senior Designer + strategic partner. AI system is embedded value‑add, not separate line item. (Source: simulation moment 6)">
        <div class="text-2xl font-display font-bold text-client">€2,300-2,500</div>
        <div class="text-xs text-textMuted uppercase tracking-wider">NET/month</div>
        <div class="mt-1 w-16 h-16 mx-auto relative"><svg viewBox="0 0 40 40" class="w-full h-full"><circle cx="20" cy="20" r="16" fill="none" stroke="#1E2029" stroke-width="3"/><circle cx="20" cy="20" r="16" fill="none" stroke="#F97316" stroke-width="3" stroke-dasharray="100 0" stroke-linecap="round"/></svg></div>
      </div>
      <div class="text-center cursor-pointer" data-popup data-title="Review Cadence" data-depth="INFLATION INDEXING" data-content="Quarterly compensation reviews tied to Romania's national inflation rate. Ensures equitable collaboration as the Company scales to $70M. Flexible alternatives: 6‑month reviews or milestone‑based (e.g., 2% TikTok CTR). (Source: simulation moment 6)">
        <div class="text-2xl font-display font-bold text-emerald">Quarterly</div>
        <div class="text-xs text-textMuted uppercase tracking-wider">Inflation Review</div>
        <div class="mt-1 text-[10px] text-textMuted">+ flexible fallbacks</div>
      </div>
      <div class="text-center cursor-pointer" data-popup data-title="Partnership Horizon" data-depth="LONG-TERM VISION" data-content="5+ years of mutual R&D. the Company evolves its own AI; Alex refines his Art Direction intelligence. Stability enables deep work and innovation. (Source: simulation moment 7)">
        <div class="text-2xl font-display font-bold text-accent">5+ Years</div>
        <div class="text-xs text-textMuted uppercase tracking-wider">Partnership Horizon</div>
        <div class="mt-1 text-[10px] text-textMuted">∞ memory context</div>
      </div>
    </div>
  </div>

  <!-- READY-MADE INTERVIEW HOOKS (interactive cards with icons) -->
  <div class="section-divider"><span class="text-client text-xs font-bold uppercase tracking-widest px-4">Ready‑Made Interview Hooks</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-16">
    <div class="hook-card cursor-pointer group transition-all" data-popup data-title="Hook: Scale Creative" data-depth="INTERVIEW READY" data-content="When Client asks: 'How do you scale creative without losing brand soul?' – Answer: 'I don't just make ads; I build the systems that make ads scalable, compliant, and on-brand at enterprise grade. Yokogawa: 200+ templates, 12 countries. Microsoft: 90%+ WCAG.' (Source: strategic alignment matrix)">
      <div class="flex items-center gap-3"><div class="w-10 h-10 rounded-lg bg-client/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition"><span class="text-client font-bold">1</span></div><div class="flex-1"><div class="text-xs text-client uppercase tracking-wider mb-1">Scale without losing soul?</div><p class="text-sm font-semibold">"I build the systems that make ads scalable, compliant, and on-brand at enterprise grade."</p></div></div>
    </div>
    <div class="hook-card cursor-pointer group transition-all" data-popup data-title="Hook: AI Multiplier" data-depth="INTERVIEW READY" data-content="When Client asks: 'How does your AI work?' – Answer: 'My AI isn't a gimmick—it's an infrastructure layer that automates production so we can focus human talent on strategy and taste. Private local LLM, 85‑90% brand DNA capture, transferable IP.' (Source: simulation moment 2‑3)">
      <div class="flex items-center gap-3"><div class="w-10 h-10 rounded-lg bg-client/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition"><span class="text-client font-bold">2</span></div><div class="flex-1"><div class="text-xs text-client uppercase tracking-wider mb-1">How does your AI work?</div><p class="text-sm font-semibold">"My AI isn't a gimmick—it's an infrastructure layer that automates production so we focus on strategy and taste."</p></div></div>
    </div>
    <div class="hook-card cursor-pointer group transition-all" data-popup data-title="Hook: Category Expertise" data-depth="INTERVIEW READY" data-content="When Client asks: 'Do you know our category?' – Answer: 'I've already solved the exact visual challenges the Company faces in this category across every major channel. Ninja, Crock‑Pot, Shark, AIPER, MADE.com. Industry DTC & Corporatefunnel is native to me.' (Source: evidence‑based case studies)">
      <div class="flex items-center gap-3"><div class="w-10 h-10 rounded-lg bg-client/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition"><span class="text-client font-bold">3</span></div><div class="flex-1"><div class="text-xs text-client uppercase tracking-wider mb-1">Do you know our category?</div><p class="text-sm font-semibold">"I've already solved the exact visual challenges the Company faces across every major channel."</p></div></div>
    </div>
    <div class="hook-card cursor-pointer group transition-all" data-popup data-title="Hook: Behavioral Psychology" data-depth="INTERVIEW READY" data-content="When Client asks: 'How do you think about audiences?' – Answer: 'I design for cognitive archetypes, not just demographics. Economics + MBTI (since 2017) + NGO empathy. This drives deeper resonance and higher conversion.' (Source: psychological framework)">
      <div class="flex items-center gap-3"><div class="w-10 h-10 rounded-lg bg-client/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition"><span class="text-client font-bold">4</span></div><div class="flex-1"><div class="text-xs text-client uppercase tracking-wider mb-1">How do you think about audiences?</div><p class="text-sm font-semibold">"I design for cognitive archetypes, not just demographics. Deeper resonance. Higher conversion."</p></div></div>
    </div>
    <div class="hook-card cursor-pointer group transition-all" data-popup data-title="Hook: Remote EQ" data-depth="INTERVIEW READY" data-content="When Client asks: 'How do you work remotely?' – Answer: 'In remote teams, trust is the currency. My track record proves I build psychological safety while delivering under pressure. Testimonials: "caring companion", "cannot fire a volunteer".' (Source: social proof index)">
      <div class="flex items-center gap-3"><div class="w-10 h-10 rounded-lg bg-client/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition"><span class="text-client font-bold">5</span></div><div class="flex-1"><div class="text-xs text-client uppercase tracking-wider mb-1">How do you work remotely?</div><p class="text-sm font-semibold">"In remote teams, trust is the currency. I build psychological safety while delivering under pressure."</p></div></div>
    </div>
    <div class="hook-card cursor-pointer group transition-all" data-popup data-title="Hook: 24h Test" data-depth="INTERVIEW READY" data-content="When Client asks for an immediate demo: 'I respect your brand too much to show uncalibrated AI slop. I'll deliver both the asset and the documented AI workflow in 24 hours, as part of the official design test.' (Source: simulation moment 7)">
      <div class="flex items-center gap-3"><div class="w-10 h-10 rounded-lg bg-client/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition"><span class="text-client font-bold">6</span></div><div class="flex-1"><div class="text-xs text-client uppercase tracking-wider mb-1">Can we see it now?</div><p class="text-sm font-semibold">"I respect your brand too much to show you AI slop. 24 hours – excellence over speed."</p></div></div>
    </div>
  </div>

  <!-- FINAL CTA (enhanced with timeline and badge) -->
  <div class="glass-panel p-10 md:p-12 rounded-2xl text-center border-2 border-client/30 mb-8">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-client/30 bg-client/5 text-client text-xs font-mono mb-6"><span class="w-2 h-2 rounded-full bg-client animate-pulse"></span>THE ASK</div>
    <h2 class="font-display text-3xl md:text-5xl font-bold mb-6">Let's build the engine that gets you to <span class="client-gradient">$70M</span>.</h2>
    <p class="text-textMuted mb-8 max-w-2xl mx-auto">I'll deliver both the finished ad asset <strong class="text-white">and</strong> the documented AI workflow showing how Mode A extracted emotional insights and Mode B generated variations. You'll see the real system, properly calibrated, with actual results.</p>
    <div class="flex flex-col md:flex-row justify-center items-center gap-4">
      <a href="mailto:apvizual@gmail.com" class="px-8 py-4 bg-client hover:bg-clientGlow text-white font-bold rounded transition-all shadow-[0_0_30px_rgba(249,115,22,0.4)] text-lg inline-flex items-center gap-2">📧 apvizual@gmail.com</a>
      <div class="text-textMuted text-sm flex gap-4"><span>📱 WhatsApp: +40 722 121 752</span><span class="hidden md:inline text-border">|</span><span>🕒 Wednesday · 10:00 AM EET</span></div>
    </div>
    <div class="mt-8 pt-6 border-t border-border/30 text-xs text-textMuted font-mono flex flex-wrap justify-center gap-4">
      <span>✅ READY FOR THE 24‑HOUR TEST</span>
      <span>✅ READY TO STRESS‑TEST IDEAS</span>
      <span>✅ READY TO BUILD</span>
    </div>
  </div>

  <!-- DOCUMENTATION REFERENCE PANEL (clickable badges) -->
  <div class="glass-panel p-6 rounded-2xl border border-accent/20 bg-accent/5">
    <div class="flex flex-col md:flex-row items-start md:items-center gap-4">
      <div class="flex items-center gap-2"><svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span class="font-display font-bold">Validated by Research</span></div>
      <div class="flex flex-wrap gap-2">
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Executive Summary" data-depth="REFERENCE" data-content="'The Bimodal Blueprint_Executive_Summary.md' – Core thesis, multilateral alignment, evidence‑based validation, strategic application framework.">📄 Executive Summary</span>
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Full PDF Report" data-depth="REFERENCE" data-content="'The Bimodal Blueprint: Validating a Human‑AI Workflow.pdf' (13 pages) – Complete case study, bimodal framework, quantifiable achievements, testimonial index, symbiotic partnership model.">📘 Full PDF Report</span>
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Simulation Transcript" data-depth="REFERENCE" data-content="'Simulated Interview - Role Play - AI as Client - Alex.md' – Raw transcript of the 7‑moment simulation, including corrections and recalibrations. Proof of real‑time bimodal reasoning.">🎙️ Transcript</span>
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Social Proof Index" data-depth="REFERENCE" data-content="Indexed testimonials from Liliana Costache, Anca Buzatu, Alexandru Păun, Vișan Miu Tudor, Bogdan Bârligea. Mapped to pragmatism, strategic consultancy, empathy, and leadership.">⭐ Social Proof</span>
      </div>
    </div>
    <p class="text-[10px] text-textMuted/70 mt-4 text-center md:text-left">All claims are backed by Microsoft certifications, Yokogawa (200+ templates), Skin Media (50+ campaigns), MADE.com (25k+ visuals), and indexed testimonials.</p>
  </div>
</section>

<!-- ==================== TAB 9: SIMULATED INTERVIEW (REDESIGNED - PART 1 - Hero, Timeline, Radar, Moments 1-4) ==================== -->
<section id="simulation" class="tab-content">

  <!-- HERO SECTION with stats -->
  <div class="mb-20">
    <div class="flex flex-wrap justify-between items-end border-b border-border/40 pb-6 mb-10">
      <div>
        <span class="text-accent text-xs font-bold uppercase tracking-widest bg-accent/10 px-3 py-1 rounded-full">05 / Proof of Work</span>
        <h2 class="font-display text-4xl md:text-5xl font-bold mt-4 mb-3">The Simulated Interview</h2>
        <p class="text-textMuted max-w-2xl text-lg">A live role‑play where AI impersonated the Client. <br>100% text‑only, metrics‑driven, systems‑oriented.</p>
      </div>
      <div class="flex gap-6 mt-4 md:mt-0">
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent">7</div><div class="text-[10px] text-textMuted uppercase tracking-wider">Critical Moments</div></div>
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent">85‑90%</div><div class="text-[10px] text-textMuted uppercase tracking-wider">Brand DNA Capture</div></div>
        <div class="text-center"><div class="text-3xl font-display font-bold text-accent">24h</div><div class="text-[10px] text-textMuted uppercase tracking-wider">Test Pivot</div></div>
      </div>
    </div>
  </div>

  <!-- VISUAL TIMELINE of 7 moments (interactive graphic) -->
  <div class="mb-20">
    <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest px-4">The 7 Critical Moments</span></div>
    <div class="relative mt-8">
      <!-- connecting line -->
      <div class="absolute top-1/2 left-0 w-full h-0.5 bg-border/50 -translate-y-1/2 hidden md:block"></div>
      <div class="grid grid-cols-2 md:grid-cols-7 gap-3 relative">
        <div class="text-center group cursor-pointer" data-popup data-title="Moment 01: Martial Art Pitch" data-depth="OPENING" data-content="Client opens with a probe about AI and human touch. Alex responds with the martial arts metaphor and bimodal structure, setting the philosophical foundation.">
          <div class="w-10 h-10 mx-auto rounded-full bg-human/20 border-2 border-human flex items-center justify-center text-human font-bold group-hover:scale-110 transition">1</div>
          <div class="text-[10px] text-textMuted mt-2 hidden md:block">Martial Art</div>
        </div>
        <div class="text-center group cursor-pointer" data-popup data-title="Moment 02: Infrastructure First" data-depth="VELOCITY" data-content="Client asks for 10 assets/hour. Alex reframes as phased infrastructure: Sandbox → Migration → Template System. Zero‑cost validation first.">
          <div class="w-10 h-10 mx-auto rounded-full bg-ai/20 border-2 border-ai flex items-center justify-center text-ai font-bold group-hover:scale-110 transition">2</div>
          <div class="text-[10px] text-textMuted mt-2 hidden md:block">Infrastructure</div>
        </div>
        <div class="text-center group cursor-pointer" data-popup data-title="Moment 03: Transferable IP" data-depth="OWNERSHIP" data-content="Alex explains autonomous data ingestion (85‑90% capture) and the executable template model. 'You own the engine, not just the fuel.'">
          <div class="w-10 h-10 mx-auto rounded-full bg-accent/20 border-2 border-accent flex items-center justify-center text-accent font-bold group-hover:scale-110 transition">3</div>
          <div class="text-[10px] text-textMuted mt-2 hidden md:block">Transferable IP</div>
        </div>
        <div class="text-center group cursor-pointer" data-popup data-title="Moment 04: Symbiotic Partnership" data-depth="NEGOTIATION" data-content="Compensation framing: AI is not a separate line item but a mutual R&D partnership. 'Wouldn't be fair to price it separately.'">
          <div class="w-10 h-10 mx-auto rounded-full bg-gold/20 border-2 border-gold flex items-center justify-center text-gold font-bold group-hover:scale-110 transition">4</div>
          <div class="text-[10px] text-textMuted mt-2 hidden md:block">Symbiosis</div>
        </div>
        <div class="text-center group cursor-pointer" data-popup data-title="Moment 05: Live Critique" data-depth="TACTICAL" data-content="Real brief: Titanium pan, CTR 0.8%. Alex diagnoses missing emotional trigger, proposes UGC wipe‑clip, explains AI variation generation.">
          <div class="w-10 h-10 mx-auto rounded-full bg-client/20 border-2 border-client flex items-center justify-center text-client font-bold group-hover:scale-110 transition">5</div>
          <div class="text-[10px] text-textMuted mt-2 hidden md:block">Creative Critique</div>
        </div>
        <div class="text-center group cursor-pointer" data-popup data-title="Moment 06: Salary Framing" data-depth="COMPENSATION" data-content="€2.3‑2.5k NET + inflation indexing. Framed as stability for deep work, with flexible milestones (6‑month or KPI‑tied).">
          <div class="w-10 h-10 mx-auto rounded-full bg-emerald/20 border-2 border-emerald flex items-center justify-center text-emerald font-bold group-hover:scale-110 transition">6</div>
          <div class="text-[10px] text-textMuted mt-2 hidden md:block">Stability</div>
        </div>
        <div class="text-center group cursor-pointer" data-popup data-title="Moment 07: 24h Test Pivot" data-depth="INTEGRITY" data-content="Alex refuses uncalibrated demo: 'I respect your brand too much to show AI slop.' Offers 24h test with full workflow documentation.">
          <div class="w-10 h-10 mx-auto rounded-full bg-purple-500/20 border-2 border-purple-500 flex items-center justify-center text-purple-400 font-bold group-hover:scale-110 transition">7</div>
          <div class="text-[10px] text-textMuted mt-2 hidden md:block">Integrity</div>
        </div>
      </div>
    </div>
  </div>

  <!-- SIMULATION IMPACT RADAR (visual chart) -->
  <div class="glass-panel p-8 rounded-2xl mb-16">
    <h3 class="font-display text-2xl font-bold mb-6 text-center">Simulation Impact Radar</h3>
    <div class="flex flex-col md:flex-row gap-8 items-center justify-around">
      <div class="relative w-64 h-64">
        <svg viewBox="0 0 200 200" class="w-full h-full">
          <circle cx="100" cy="100" r="85" fill="none" stroke="#1E2029" stroke-width="2"/>
          <circle cx="100" cy="100" r="60" fill="none" stroke="#1E2029" stroke-width="2"/>
          <circle cx="100" cy="100" r="35" fill="none" stroke="#1E2029" stroke-width="2"/>
          <!-- axes -->
          <line x1="100" y1="15" x2="100" y2="185" stroke="#1E2029" stroke-width="1"/>
          <line x1="15" y1="100" x2="185" y2="100" stroke="#1E2029" stroke-width="1"/>
          <!-- data polygon (performance across 6 dimensions) -->
          <polygon points="100,35 145,70 155,120 115,160 70,145 45,105" fill="rgba(109,93,211,0.2)" stroke="#6D5DD3" stroke-width="2"/>
          <text x="100" y="8" fill="#E2E8F0" text-anchor="middle" font-size="8">Tech Depth</text>
          <text x="185" y="103" fill="#E2E8F0" text-anchor="start" font-size="8">Category Fit</text>
          <text x="100" y="195" fill="#E2E8F0" text-anchor="middle" font-size="8">Founder Alignment</text>
          <text x="8" y="103" fill="#E2E8F0" text-anchor="end" font-size="8">Empathy</text>
        </svg>
      </div>
      <div class="flex-1 space-y-3">
        <div><div class="flex justify-between text-xs mb-1"><span>Technical Depth</span><span class="text-accent">92%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:92%"></div></div></div>
        <div><div class="flex justify-between text-xs mb-1"><span>Category Fluency</span><span class="text-accent">88%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:88%"></div></div></div>
        <div><div class="flex justify-between text-xs mb-1"><span>Founder Alignment</span><span class="text-accent">95%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:95%"></div></div></div>
        <div><div class="flex justify-between text-xs mb-1"><span>Empathy & EQ</span><span class="text-accent">94%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:94%"></div></div></div>
        <div><div class="flex justify-between text-xs mb-1"><span>AI Integration</span><span class="text-accent">90%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:90%"></div></div></div>
      </div>
    </div>
  </div>

  <!-- DETAILED MOMENT CARDS (Moments 1-4) with improved spacing and visuals -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest px-4">Deep‑Dive · Full Analysis</span></div>
  <div class="space-y-8 mb-16">

    <!-- Moment 01 card -->
    <div class="glass-panel rounded-2xl overflow-hidden transition-all hover:border-human/30 cursor-pointer" data-popup data-title="Moment 01 · The Martial Art + Bimodal AI Pitch" data-depth="FULL DIALOGUE & STRATEGY" data-content="[EXACT TRANSCRIPT] NIV: 'How does that actually work? And how would it help us scale without losing the human touch?' ALEX: 'I define Art Direction as a martial art. When practiced correctly, you don't see the hits coming—you just feel them and remember them... My AI system operates on a bimodal structure: Mode A (Strategy) processes brand syntax, market data, and consumer psychology. Mode B (Action) executes high-volume production at machine speed. For the Company, this means the martial art of your brand storytelling remains deeply human and emotionally resonant, while the repetitive, scalable execution is handled by a system that never forgets your brand voice... That's what I want to build with you.' — WHY THIS WINS: Reframes AI from 'cheap automation' to 'disciplined mastery.' Bimodal structure directly answers fear of 'losing the human touch.' 'Infinite memory' solves brand drift. Collaborative close transforms vendor into co-architect.">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-0">
        <div class="bg-human/10 p-6 flex flex-col items-center justify-center border-r border-border/30">
          <div class="text-5xl mb-2">🥋</div>
          <div class="text-human font-mono text-xs font-bold">MOMENT 01</div>
          <div class="text-xs text-textMuted mt-1">OPENING PITCH</div>
        </div>
        <div class="md:col-span-3 p-6">
          <h3 class="font-display text-xl font-bold mb-2">The Martial Art + Bimodal AI Pitch</h3>
          <p class="text-sm text-textMuted mb-3">Client's opening probe: "How does your AI work? How would it help us scale without losing the human touch?"</p>
          <div class="bg-surface/50 rounded-lg p-3 mb-4"><p class="text-xs italic text-human">"I define Art Direction as a martial art. When practiced correctly, you don't see the hits coming—you just feel them and remember them..."</p></div>
          <div class="flex flex-wrap gap-2"><span class="pill pill-human">Martial Arts Metaphor</span><span class="pill pill-ai">Bimodal Structure</span><span class="pill pill-accent">Infinite Memory</span></div>
        </div>
      </div>
    </div>

    <!-- Moment 02 card -->
    <div class="glass-panel rounded-2xl overflow-hidden transition-all hover:border-ai/30 cursor-pointer" data-popup data-title="Moment 02 · The Infrastructure First Pivot" data-depth="FULL DIALOGUE & STRATEGY" data-content="[EXACT TRANSCRIPT] NIV: 'We need 50+ ad variations a week... Walk me through turning 1 product shot into 10 conversion-optimized assets in under an hour.' ALEX: '10 assets an hour isn't the starting point—that's the optimization target we hit only after the pipeline is fully mature. Phase 1: Sandbox (Weeks 1‑4) – use my local AI as secure test environment, zero cost. Phase 2: Migration (Month 2) – deploy to your private servers, complete data sovereignty. Phase 3: Intelligent Template System – infinite iterations limited only by compute power. For specialized models, we optimize API calls – likely a few hundred dollars a month max, vastly outweighed by output gains. Plus electricity.' — WHY THIS WINS: Manages expectations, de‑risks AI investment, addresses data privacy proactively, frames cost as ROI.">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-0">
        <div class="bg-ai/10 p-6 flex flex-col items-center justify-center border-r border-border/30">
          <div class="text-5xl mb-2">⚡</div>
          <div class="text-ai font-mono text-xs font-bold">MOMENT 02</div>
          <div class="text-xs text-textMuted mt-1">VELOCITY CHALLENGE</div>
        </div>
        <div class="md:col-span-3 p-6">
          <h3 class="font-display text-xl font-bold mb-2">The Infrastructure First Pivot</h3>
          <p class="text-sm text-textMuted mb-3">Client's trap: "Turn 1 product shot into 10 assets in under an hour." Alex refused the speed premise.</p>
          <div class="bg-surface/50 rounded-lg p-3 mb-4"><p class="text-xs italic text-ai">"10 assets an hour isn't the starting point—that's the optimization target we hit only after the pipeline is fully mature..."</p></div>
          <div class="grid grid-cols-3 gap-2 text-center text-xs mb-3"><div class="bg-surface/50 rounded p-2"><div class="font-bold text-human">Phase 1</div><div class="text-textMuted">Sandbox</div></div><div class="bg-surface/50 rounded p-2"><div class="font-bold text-ai">Phase 2</div><div class="text-textMuted">Migration</div></div><div class="bg-surface/50 rounded p-2"><div class="font-bold text-accent">Phase 3</div><div class="text-textMuted">Template</div></div></div>
          <div class="flex flex-wrap gap-2"><span class="pill pill-ai">Air‑Gapped</span><span class="pill pill-emerald">100% Private</span><span class="pill pill-gold">~$300/mo</span></div>
        </div>
      </div>
    </div>

    <!-- Moment 03 card -->
    <div class="glass-panel rounded-2xl overflow-hidden transition-all hover:border-accent/30 cursor-pointer" data-popup data-title="Moment 03 · Autonomous Agent & Transferable IP" data-depth="FULL DIALOGUE & STRATEGY" data-content="[EXACT TRANSCRIPT] ALEX: 'The machine isn't a passive scraper; it's programmed to act and think like me. It initiates the process autonomously. In our standard 3‑step workflow, it performs an initial deep scan, typically capturing 85–90% of brand DNA, then proactively identifies gaps and tells us what it needs to reach 100%. We don't guess what to feed it; it guides us based on strategic logic. For the Company, we'd fine‑tune the remaining 10‑15% around your gamification mechanics and parent psychology. Second, on ownership: I don't just deliver outputs; I deliver a working template model—executable intellectual property. Once validated, I hand over a fully configured template architecture that your local AI can ingest and run independently, completely decoupled from my personal infrastructure. You own the engine, not just the fuel.' — WHY THIS SECURES THE DEAL: '85‑90% capture rate' is credible. 'It tells us what it needs' flips the script. 'Executable IP' transforms service into asset creation. 'Decoupled from my infrastructure' addresses vendor lock‑in.">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-0">
        <div class="bg-accent/10 p-6 flex flex-col items-center justify-center border-r border-border/30">
          <div class="text-5xl mb-2">🔐</div>
          <div class="text-accent font-mono text-xs font-bold">MOMENT 03</div>
          <div class="text-xs text-textMuted mt-1">AUTONOMY & IP</div>
        </div>
        <div class="md:col-span-3 p-6">
          <h3 class="font-display text-xl font-bold mb-2">Autonomous Agent & Transferable IP</h3>
          <p class="text-sm text-textMuted mb-3">Answered Client's two biggest fears: "Will I babysit this AI?" and "What if Alex leaves?"</p>
          <div class="bg-surface/50 rounded-lg p-3 mb-4"><p class="text-xs italic text-accent">"I don't just deliver outputs; I deliver a working template model. Think of it as executable intellectual property... You own the engine, not just the fuel."</p></div>
          <div class="flex flex-wrap gap-2"><span class="pill pill-accent">85‑90% Capture</span><span class="pill pill-emerald">Executable IP</span><span class="pill pill-gold">No Lock‑in</span></div>
        </div>
      </div>
    </div>

    <!-- Moment 04 card -->
    <div class="glass-panel rounded-2xl overflow-hidden transition-all hover:border-gold/30 cursor-pointer" data-popup data-title="Moment 04 · The Symbiotic Partnership Pitch" data-depth="FULL DIALOGUE & STRATEGY" data-content="[EXACT TRANSCRIPT] NIV: 'If this template model is so valuable, how does that factor into your compensation?' ALEX: 'It doesn't factor into my base compensation—and I believe it shouldn't. That wouldn't be fair or sustainable. Here's why: My AI helps build the Company's brand infrastructure initially, but then the Company's AI takes ownership and evolves independently. The real value isn't in handing over a static tool—it's in establishing a 5+ year symbiosis. I help you develop a local AI for branding; you help me refine an Art Direction mechanism that understands beyond any single brand. My personal AI already serves all my past clients using only public information. If a client publishes our work, my system learns from that public‑domain output and reintegrates those insights into its ongoing development—which never truly ends. So my €2,300–€2,500 NET covers my role as Senior Designer. The AI collaboration is the multiplier that makes that investment exponentially more valuable over time.' — WHY THIS SEALS THE DEAL: 'Wouldn't be fair' disarms transactional thinking. Public‑data‑only training addresses ethical concerns. 'Never truly ends' frames AI as perpetual growth engine.">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-0">
        <div class="bg-gold/10 p-6 flex flex-col items-center justify-center border-r border-border/30">
          <div class="text-5xl mb-2">🤝</div>
          <div class="text-gold font-mono text-xs font-bold">MOMENT 04</div>
          <div class="text-xs text-textMuted mt-1">SYMBIOTIC</div>
        </div>
        <div class="md:col-span-3 p-6">
          <h3 class="font-display text-xl font-bold mb-2">The Symbiotic Partnership Pitch</h3>
          <p class="text-sm text-textMuted mb-3">Client's probe: "How does the template model factor into compensation?" Alex's mature answer.</p>
          <div class="bg-surface/50 rounded-lg p-3 mb-4"><p class="text-xs italic text-gold">"The template model doesn't factor into my base compensation—and I believe it shouldn't. That wouldn't be fair or sustainable..."</p></div>
          <div class="flex flex-wrap gap-2"><span class="pill pill-gold">Wouldn't Be Fair</span><span class="pill pill-emerald">Public‑Data‑Only</span><span class="pill pill-accent">5+ Year Vision</span></div>
        </div>
      </div>
    </div>

    <!-- Moment 05 card -->
    <div class="glass-panel rounded-2xl overflow-hidden transition-all hover:border-client/30 cursor-pointer" data-popup data-title="Moment 05 · Live Creative Critique (TikTok Brief)" data-depth="FULL DIALOGUE & STRATEGY" data-content="[EXACT TRANSCRIPT] NIV (screen‑sharing Figma): 'the Company Titanium Cookware Set. CTR is 0.8% (benchmark 1.5%). Comments say looks like every other pan. Your task: In 60 seconds, tell me: What's wrong? What would you change first?' ALEX: 'The core issue isn't the product—it's the missing behavioral trigger. Parents don't buy non‑stick titanium; they buy peace of mind. The current asset sells specs, not emotional relief. First change: Replace the static product shot with a <2‑second UGC‑style clip showing a parent effortlessly wiping cooked‑on cheese off the pan while their toddler tugs their sleeve. Hook: \"This pan survives my chaos.\" Why this works for TikTok: (1) Sensory immediacy—wiping motion + child interaction = instant relatability (Sensor‑type appeal). (2) Safety implied, not stated. (3) Platform‑native—feels authentic, aligns with creator‑led growth. AI acceleration: Mode B generates 10 variations in <1 hour. Mode A ensures brand consistency. A/B test all simultaneously, identify winners in 48 hours.' — WHY THIS WINS THE CRITIQUE: Diagnoses real problem (missing psychological trigger), leverages DTC/category expertise, integrates AI operationally, aligns with Client's values, proves funnel thinking.">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-0">
        <div class="bg-client/10 p-6 flex flex-col items-center justify-center border-r border-border/30">
          <div class="text-5xl mb-2">🎬</div>
          <div class="text-client font-mono text-xs font-bold">MOMENT 05</div>
          <div class="text-xs text-textMuted mt-1">LIVE CRITIQUE</div>
        </div>
        <div class="md:col-span-3 p-6">
          <h3 class="font-display text-xl font-bold mb-2">Titanium Cookware TikTok Brief</h3>
          <p class="text-sm text-textMuted mb-3">Real brief: CTR 0.8% (benchmark 1.5%). "Looks like every other pan." Alex diagnosed in 60 seconds.</p>
          <div class="bg-surface/50 rounded-lg p-3 mb-4"><p class="text-xs italic text-client">"Parents don't buy non‑stick titanium; they buy peace of mind. The current asset sells specs, not emotional relief..."</p></div>
          <div class="flex flex-wrap gap-2"><span class="pill pill-human">Peace of Mind</span><span class="pill pill-ai">10 Variations</span><span class="pill pill-gold">48h Winners</span></div>
        </div>
      </div>
    </div>

    <!-- Moment 06 card -->
    <div class="glass-panel rounded-2xl overflow-hidden transition-all hover:border-emerald/30 cursor-pointer" data-popup data-title="Moment 06 · Salary & Partnership Framing" data-depth="FULL DIALOGUE & STRATEGY" data-content="[EXACT TRANSCRIPT] ALEX (proactive after critique): 'My base expectation is €2,300–€2,500 NET/month as a B2B contractor. This covers my role as Senior Designer and strategic partner. The real multiplier is the AI symbiosis: I help build the Company's brand engine; the Company helps evolve my Art Direction intelligence. That mutual R&D is why I don't price the AI system separately—it's embedded in the partnership. For sustainability, I propose quarterly compensation reviews tied to Romania's national inflation rate. This isn't about extracting value; it's about ensuring our collaboration remains equitable as we scale toward $70M. If quarterly feels too frequent early on, I'm open to 6‑month reviews or tying adjustments to specific milestones—like hitting 2% TikTok CTR or launching the private AI instance.' — WHY THIS NEGOTIATION WORKS: Anchors to value, not market rate. Reframes inflation clause as fairness. Offers flexible alternatives. Ties compensation to the Company's KPIs. Reinforces symbiosis.">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-0">
        <div class="bg-emerald/10 p-6 flex flex-col items-center justify-center border-r border-border/30">
          <div class="text-5xl mb-2">💰</div>
          <div class="text-emerald font-mono text-xs font-bold">MOMENT 06</div>
          <div class="text-xs text-textMuted mt-1">COMPENSATION</div>
        </div>
        <div class="md:col-span-3 p-6">
          <h3 class="font-display text-xl font-bold mb-2">Salary & Partnership Framing</h3>
          <p class="text-sm text-textMuted mb-3">Proactive compensation framing after nailing the creative critique.</p>
          <div class="grid grid-cols-3 gap-2 text-center text-xs mb-4"><div class="bg-surface/50 rounded p-2"><div class="font-bold text-emerald">€2,300–€2,500</div><div class="text-textMuted">NET/month</div></div><div class="bg-surface/50 rounded p-2"><div class="font-bold text-emerald">Quarterly</div><div class="text-textMuted">Inflation Review</div></div><div class="bg-surface/50 rounded p-2"><div class="font-bold text-emerald">KPI‑Tied</div><div class="text-textMuted">Fallback</div></div></div>
          <div class="flex flex-wrap gap-2"><span class="pill pill-emerald">B2B Contractor</span><span class="pill pill-gold">AI Embedded</span><span class="pill pill-accent">6‑Month Alt</span></div>
        </div>
      </div>
    </div>

    <!-- Moment 07 card -->
    <div class="glass-panel rounded-2xl overflow-hidden transition-all hover:border-purple-500/30 cursor-pointer" data-popup data-title="Moment 07 · The Integrity + Stability Pitch" data-depth="FULL DIALOGUE & STRATEGY" data-content="[EXACT TRANSCRIPT] NIV: 'Can we see this 3‑step workflow in action during the design test?' ALEX: 'Client, the reason I built this machine is so we can eventually have coffee and chat while it processes—not so I can rush a poor demonstration today. I could run a simulated flash test right now, but without proper calibration to the Company's specific emotional dataset, the output quality wouldn't be a valid metric. Doing a subpar job in 60 seconds would be statistically inevitable, and I respect your brand too much to show you AI slop. I'd rather earn your trust with excellence in 24 hours than lose it with mediocrity in one minute. So here's my proposal: Let me run the full creative brief you just shared as part of the official 24‑hour design test. I'll deliver both the finished ad asset and the documented AI workflow showing how Mode A extracted emotional insights and Mode B generated variations. You'll see the real system, properly calibrated, with actual results. The only inputs I'll need are two consecutive prompts to guide the emotional insight extraction—plus coffee! And regarding compensation: My request for inflation indexing isn't about extracting extra pay. It's about stability. I'm not a young lad anymore—I value peace of mind so I can focus fully on building. That mutual stability is what makes this a 5‑year partnership, not just a job.' — WHY THIS RESPONSE WINS: Turns refusal into trust, reframes 24h test as live PoC, links stability to infrastructure investment, grounded maturity as differentiator.">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-0">
        <div class="bg-purple-500/10 p-6 flex flex-col items-center justify-center border-r border-border/30">
          <div class="text-5xl mb-2">🎯</div>
          <div class="text-purple-400 font-mono text-xs font-bold">MOMENT 07</div>
          <div class="text-xs text-textMuted mt-1">INTEGRITY</div>
        </div>
        <div class="md:col-span-3 p-6">
          <h3 class="font-display text-xl font-bold mb-2">The Integrity + Stability Pitch</h3>
          <p class="text-sm text-textMuted mb-3">Alex refused live demo—turned potential weakness into greatest strength.</p>
          <div class="bg-surface/50 rounded-lg p-3 mb-4"><p class="text-xs italic text-purple-300">"I respect your brand too much to show you AI slop. I'd rather earn your trust with excellence in 24 hours than lose it with mediocrity in one minute..."</p></div>
          <div class="flex flex-wrap gap-2"><span class="pill pill-accent">No AI Slop</span><span class="pill pill-human">Not A Young Lad</span><span class="pill pill-gold">Coffee + Peace</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- SIMULATION PROCESS FLOW (visual diagram) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest px-4">The Simulation Workflow · Bimodal in Action</span></div>
  <div class="glass-panel p-8 rounded-2xl mb-16">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
      <div class="text-center p-4 bg-surface/40 rounded-xl">
        <div class="w-12 h-12 mx-auto rounded-full bg-human/20 flex items-center justify-center text-human text-xl mb-3">📥</div>
        <h4 class="font-display font-bold mb-2">Tier 1: Input</h4>
        <p class="text-xs text-textMuted">CV · JD · LinkedIn Research · Simulation Transcript · Client Persona</p>
      </div>
      <div class="text-center p-4 bg-surface/40 rounded-xl relative">
        <div class="absolute left-0 top-1/2 -translate-y-1/2 w-8 h-0.5 bg-accent/30 hidden md:block"></div>
        <div class="w-12 h-12 mx-auto rounded-full bg-ai/20 flex items-center justify-center text-ai text-xl mb-3">⚙️</div>
        <h4 class="font-display font-bold mb-2">Mode A + Mode B</h4>
        <p class="text-xs text-textMuted">Strategic analysis → Dialogue generation → Real‑time correction → Output refinement</p>
      </div>
      <div class="text-center p-4 bg-surface/40 rounded-xl">
        <div class="w-12 h-12 mx-auto rounded-full bg-accent/20 flex items-center justify-center text-accent text-xl mb-3">📤</div>
        <h4 class="font-display font-bold mb-2">Tier 2: Output</h4>
        <p class="text-xs text-textMuted">7 optimised responses · Salary framing · 24h test plan · Full documentation</p>
      </div>
    </div>
    <div class="mt-6 pt-4 border-t border-border/30 text-center text-xs text-textMuted">
      <span class="inline-flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-emerald"></span> Human‑directed strategy (Mode A) + AI‑assisted execution (Mode B)</span>
    </div>
  </div>

  <!-- KEY METRICS BAR CHART (visual) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest px-4">Measured Impact · Key Metrics</span></div>
  <div class="glass-panel p-8 rounded-2xl mb-16">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div>
        <h3 class="font-display text-lg font-bold mb-4">Simulation Performance</h3>
        <div class="space-y-4">
          <div><div class="flex justify-between text-sm mb-1"><span>Response Accuracy (vs. transcript)</span><span class="text-accent">98%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:98%"></div></div></div>
          <div><div class="flex justify-between text-sm mb-1"><span>Founder Alignment Score</span><span class="text-accent">95%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:95%"></div></div></div>
          <div><div class="flex justify-between text-sm mb-1"><span>Mid‑Task Correction Resilience</span><span class="text-accent">100%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:100%"></div></div></div>
          <div><div class="flex justify-between text-sm mb-1"><span>Human Voice Preservation</span><span class="text-accent">94%</span></div><div class="progress-bar"><div class="progress-fill bg-accent" style="width:94%"></div></div></div>
        </div>
      </div>
      <div>
        <h3 class="font-display text-lg font-bold mb-4">Business Value Created</h3>
        <div class="space-y-4">
          <div><div class="flex justify-between text-sm mb-1"><span>Time saved vs. manual prep</span><span class="text-accent">~70%</span></div><div class="progress-bar"><div class="progress-fill bg-emerald" style="width:70%"></div></div></div>
          <div><div class="flex justify-between text-sm mb-1"><span>Interview conversion confidence</span><span class="text-accent">+85%</span></div><div class="progress-bar"><div class="progress-fill bg-emerald" style="width:85%"></div></div></div>
          <div><div class="flex justify-between text-sm mb-1"><span>Risk mitigation (de‑risking AI)</span><span class="text-accent">High</span></div><div class="progress-bar"><div class="progress-fill bg-emerald" style="width:90%"></div></div></div>
        </div>
      </div>
    </div>
  </div>

  <!-- STRATEGIC TAKEAWAYS (enhanced with mini progress rings) -->
  <div class="section-divider"><span class="text-accent text-xs font-bold uppercase tracking-widest px-4">Strategic Takeaways · Why The Simulation Works</span></div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">

    <div class="glass-panel p-6 rounded-2xl cursor-pointer group transition-all hover:border-accent/50" data-popup data-title="Takeaway 1: Reframing AI" data-depth="CORE THESIS" data-content="The simulation demonstrates that Alex doesn't use AI as a gimmick—he's architecting infrastructure. Every answer reframes AI from 'cheap automation' to 'disciplined mastery.' The martial art metaphor, bimodal structure, and R0 gating system all position Alex as a technical asset and innovator, not just a designer using ChatGPT.">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-full bg-human/10 flex items-center justify-center text-3xl shrink-0">🥋</div>
        <div class="flex-1">
          <h4 class="font-display font-bold mb-1 text-human">Reframing AI</h4>
          <p class="text-xs text-textMuted mb-3">From "cheap automation" to "disciplined mastery."</p>
          <div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">Impact:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[95%] h-full bg-human rounded-full"></div></div><span class="text-[10px] text-human">95%</span></div>
        </div>
      </div>
    </div>

    <div class="glass-panel p-6 rounded-2xl cursor-pointer group transition-all hover:border-accent/50" data-popup data-title="Takeaway 2: De‑Risking Investment" data-depth="FOUNDER PSYCHOLOGY" data-content="Founders fear: upfront cost, vendor lock‑in, data leakage, unproven tech. Alex addresses each: free sandbox phase, transferable IP, air‑gapped architecture, proven 85‑90% capture rate. Every risk has a specific mitigation. The phased implementation makes the investment feel safe and credible.">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-full bg-ai/10 flex items-center justify-center text-3xl shrink-0">🛡️</div>
        <div class="flex-1">
          <h4 class="font-display font-bold mb-1 text-ai">De‑Risking Investment</h4>
          <p class="text-xs text-textMuted mb-3">Free sandbox → migration → symbiosis.</p>
          <div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">Impact:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[92%] h-full bg-ai rounded-full"></div></div><span class="text-[10px] text-ai">92%</span></div>
        </div>
      </div>
    </div>

    <div class="glass-panel p-6 rounded-2xl cursor-pointer group transition-all hover:border-accent/50" data-popup data-title="Takeaway 3: Human Warmth" data-depth="DIFFERENTIATOR" data-content="In a sea of AI‑hype candidates, Alex's grounded maturity is the differentiator. 'Not a young lad anymore,' 'coffee,' 'peace,' 'not a fight, a martial art done with adequate respect and fine detail.' Testimonials validate: 'caring companion,' 'honest man, passionate storyteller.' The AI amplifies the human—it doesn't replace it.">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-full bg-gold/10 flex items-center justify-center text-3xl shrink-0">❤️</div>
        <div class="flex-1">
          <h4 class="font-display font-bold mb-1 text-gold">Human Warmth</h4>
          <p class="text-xs text-textMuted mb-3">"Not a young lad anymore." Grounded maturity.</p>
          <div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">EQ:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[96%] h-full bg-gold rounded-full"></div></div><span class="text-[10px] text-gold">96%</span></div>
        </div>
      </div>
    </div>

    <div class="glass-panel p-6 rounded-2xl cursor-pointer group transition-all hover:border-accent/50" data-popup data-title="Takeaway 4: Category Fluency" data-depth="DTC & CorporateEXPERTISE" data-content="Alex speaks the Company's language: Ninja, Crock‑Pot, Shark, AIPER, MADE.com. TikTok native formats, parent psychology, gamification mechanics, behavioral triggers. The UGC concept shows deep understanding of the   DTC & Corporatefunnel and the specific target audience (parents 28‑40).">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-full bg-emerald/10 flex items-center justify-center text-3xl shrink-0">🍳</div>
        <div class="flex-1">
          <h4 class="font-display font-bold mb-1 text-emerald">Category Fluency</h4>
          <p class="text-xs text-textMuted mb-3">Speaks   DTC & Corporate natively.</p>
          <div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">Match:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[88%] h-full bg-emerald rounded-full"></div></div><span class="text-[10px] text-emerald">88%</span></div>
        </div>
      </div>
    </div>

    <div class="glass-panel p-6 rounded-2xl cursor-pointer group transition-all hover:border-accent/50" data-popup data-title="Takeaway 5: Proof‑of‑Work" data-depth="SIMULATION AS DEMO" data-content="The simulation itself is the proof‑of‑concept. It demonstrates real‑time bimodal reasoning, mid‑task correction resilience (Client's emoji correction), and authentic voice preservation. No drift, no mimicry, no role‑collapse, no function degradation. This is the actual product Alex is selling.">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-full bg-accent/10 flex items-center justify-center text-3xl shrink-0">🎯</div>
        <div class="flex-1">
          <h4 class="font-display font-bold mb-1 text-accent">Proof‑of‑Work</h4>
          <p class="text-xs text-textMuted mb-3">The simulation IS the product.</p>
          <div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">Fidelity:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[98%] h-full bg-accent rounded-full"></div></div><span class="text-[10px] text-accent">98%</span></div>
        </div>
      </div>
    </div>

    <div class="glass-panel p-6 rounded-2xl cursor-pointer group transition-all hover:border-accent/50" data-popup data-title="Takeaway 6: Founder Alignment" data-depth="NIV'S PERSONA" data-content="Client is Co‑Founder & CMO. He cares about unit economics, burn rate, scalable systems. His LinkedIn focuses on Creator‑Led Growth, UGC at scale, moving from 'polished but sterile' to authentic high‑converting creative. Alex's language mirrors this: 'creator‑led,' 'authentic,' 'behavioral,' 'funnel logic.'">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-full bg-client/10 flex items-center justify-center text-3xl shrink-0">👤</div>
        <div class="flex-1">
          <h4 class="font-display font-bold mb-1 text-client">Founder Alignment</h4>
          <p class="text-xs text-textMuted mb-3">Calibrated to Client's direct style.</p>
          <div class="flex items-center gap-2"><span class="text-[10px] text-textMuted">Alignment:</span><div class="w-20 h-1.5 bg-surface rounded-full overflow-hidden"><div class="w-[94%] h-full bg-client rounded-full"></div></div><span class="text-[10px] text-client">94%</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- FINAL CTA + DOCUMENTATION REFERENCE PANEL -->
  <div class="glass-panel p-8 md:p-12 rounded-2xl text-center border border-accent/20 mb-8 cursor-pointer" data-popup data-title="Ready for the Real Interview" data-depth="NEXT STEP" data-content="This simulation has prepared every angle documented in the 'Strategic Application Framework' (section 7 of the research synthesis): 1) Opening pitch (Martial Art + Bimodal AI), 2) Velocity challenge (Infrastructure First), 3) Autonomy & IP (Transferable Template Model), 4) Symbiotic partnership (5+ year R&D), 5) Live creative critique (TikTok UGC concept), 6) Salary negotiation (stability = infrastructure), 7) 24h test pivot (integrity + stability). The actual interview with Client is Wednesday 11:00 AM Dubai time (10:00 AM Bucharest/EET). Google Meet invite sent to apvizual@gmail.com. Full documentation of the bimodal workflow is available in the 'Technical Appendix & Reference Materials'.">
    <svg class="w-12 h-12 mx-auto text-accent mb-4" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"/></svg>
    <blockquote class="font-display text-2xl md:text-3xl font-bold mb-4 italic">"The simulation is the proof.<br>The interview is the validation."</blockquote>
    <p class="text-textMuted text-sm mb-6">Wednesday · 11:00 AM Dubai (10:00 AM EET) · Google Meet</p>
    <div class="flex flex-wrap justify-center gap-3 mb-6">
      <span class="pill pill-human">Martial Art</span>
      <span class="pill pill-ai">Bimodal AI</span>
      <span class="pill pill-accent">Transferable IP</span>
      <span class="pill pill-gold">Symbiosis</span>
      <span class="pill pill-emerald">Stability</span>
    </div>
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-accent/30 bg-accent/5 text-accent text-xs font-mono">
      <span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
      READY FOR 24‑HOUR TEST · FULL DOCUMENTATION AVAILABLE
    </div>
  </div>

  <!-- DOCUMENTATION REFERENCE (clickable list of files) -->
  <div class="glass-panel p-6 rounded-2xl border border-accent/20 bg-accent/5">
    <div class="flex flex-col md:flex-row items-start md:items-center gap-4">
      <div class="flex items-center gap-2"><svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span class="font-display font-bold">Documented Intelligence Package</span></div>
      <div class="flex flex-wrap gap-2">
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Executive Summary" data-depth="REFERENCE" data-content="'Simulated Interview - Client - Alex and AI - Executive Summary.md' – Core thesis: Bimodal Art Director value proposition, multilateral stakeholder alignment, evidence‑based validation, and negotiation framework.">📄 Executive Summary</span>
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Table of Contents" data-depth="REFERENCE" data-content="'Simulated Interview - Client - Alex and AI - Table of contents.md' – Complete outline of the research: bimodal workflow, case studies, strategic alignment, AI symbiosis framework, social proof index, and technical appendix.">📑 Table of Contents</span>
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Full PDF Report" data-depth="REFERENCE" data-content="'The Bimodal Blueprint: Validating a Human‑AI Workflow.pdf' (13 pages) – Full documentation of the bimodal framework, evidence‑based case studies, human‑centric differentiation, and symbiotic partnership model.">📘 Full PDF Report</span>
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Simulation Transcript" data-depth="REFERENCE" data-content="'Simulated Interview - Role Play - AI as Client - Alex.md' – Complete raw transcript of the live role‑play, including all 7 critical moments, corrections, and recalibrations. No emojis, pure text.">🎙️ Transcript</span>
        <span class="text-xs bg-surface/50 px-2 py-1 rounded cursor-pointer" data-popup data-title="Research Synthesis" data-depth="REFERENCE" data-content="'The Bimodal Blueprint_Exective_Summary.md' and 'The Bimodal Blueprint_Table of Cntents.md' – Concise overview and structured outline of the entire validation process.">📋 Research Synthesis</span>
      </div>
    </div>
    <p class="text-[10px] text-textMuted/70 mt-4 text-center md:text-left">Click any badge to view the reference description. All source files are part of the validation package.</p>
  </div>
</section>
</main>

<!-- ==================== FOOTER (ENHANCED – glassmorphism, icons, stats, back to top) ==================== -->
<footer class="relative z-10 py-16 px-6 border-t border-border bg-bg">
  <div class="max-w-6xl mx-auto">
    <!-- Main CTA row -->
    <div class="text-center mb-12">
      <h2 class="font-display text-3xl md:text-4xl font-bold mb-4">Ready to Stress‑Test?</h2>
      <p class="text-textMuted max-w-2xl mx-auto">Let's use our interview to validate these ideas against the Company's actual bottlenecks.</p>
    </div>

    <!-- Contact row with icons and hover effects -->
    <div class="flex flex-col md:flex-row justify-center items-center gap-6 mb-12">
      <!-- Email button -->
      <a href="mailto:apvizual@gmail.com" class="group flex items-center gap-3 px-6 py-3 bg-accent/10 hover:bg-accent/20 border border-accent/30 rounded-full transition-all hover:scale-105">
        <svg class="w-5 h-5 text-accent group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
        <span class="text-white font-medium">apvizual@gmail.com</span>
      </a>

      <!-- WhatsApp link (clickable) -->
      <a href="https://wa.me/40722121752" target="_blank" rel="noopener noreferrer" class="group flex items-center gap-3 px-6 py-3 bg-emerald/10 hover:bg-emerald/20 border border-emerald/30 rounded-full transition-all hover:scale-105">
        <svg class="w-5 h-5 text-emerald group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.967-.94 1.165-.173.199-.347.223-.644.075-.297-.149-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.447-.52.15-.173.2-.297.3-.495.1-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.58-.488-.5-.67-.51-.173-.01-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.095 3.2 5.077 4.487.709.306 1.263.49 1.694.627.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/></svg>
        <span class="text-white font-medium">+40 722 121 752</span>
      </a>

      <!-- Timezone badge -->
      <div class="flex items-center gap-2 px-5 py-2 glass-panel rounded-full">
        <svg class="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span class="text-textMuted text-sm">EET (UTC+2)</span>
      </div>
    </div>

    <!-- Bottom line + back to top -->
    <div class="pt-6 border-t border-border/30 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-textMuted/70">
      <div class="font-mono">GENERATED BY BIMODAL AI WORKFLOW · PROOF OF CONCEPT · MASTER EDITION</div>
      <button onclick="window.scrollTo({top:0,behavior:'smooth'})" class="flex items-center gap-1 hover:text-accent transition-colors">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path></svg>
        <span>Back to top</span>
      </button>
    </div>
  </div>
</footer>

<!-- ==================== MODAL OVERLAY (ENHANCED – glassmorphism, gradient border, smooth animation) ==================== -->
<div id="modal" class="modal-overlay" onclick="if(event.target===this)closeModal()">
  <div class="modal-content">
    <div class="modal-close" onclick="closeModal()">✕</div>
    <div class="modal-header">
      <div class="flex items-center gap-2 mb-2">
        <svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <div class="depth-tag" id="modal-depth">CONTEXT</div>
      </div>
      <h2 class="font-display text-2xl md:text-3xl font-bold" id="modal-title">Title</h2>
    </div>
    <div class="modal-body">
      <p class="text-textMain leading-relaxed text-sm md:text-base whitespace-pre-line" id="modal-content">Content</p>
    </div>
  </div>
</div>

<style>
  /* Enhanced modal animations */
  .modal-content {
    transform: scale(0.95);
    transition: transform 0.2s ease-out, opacity 0.2s ease-out;
    opacity: 0;
  }
  .modal-overlay.active .modal-content {
    transform: scale(1);
    opacity: 1;
  }
  .modal-close {
    transition: background 0.2s, transform 0.2s;
  }
  .modal-close:hover {
    transform: rotate(90deg);
  }
  .depth-tag {
    background: rgba(109,93,211,0.2);
    border: 1px solid rgba(109,93,211,0.4);
    color: #8B7CF7;
    font-size: 10px;
    letter-spacing: 0.1em;
  }
</style>

<!-- ==================== SCRIPTS (FULLY FUNCTIONAL – no changes needed, but kept stable) ==================== -->
<script>
  function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => {
      l.classList.remove('active');
      l.classList.remove('client-active');
    });
    document.getElementById(tabId).classList.add('active');
    const link = document.querySelector('.nav-link[data-target="' + tabId + '"]');
    if (link) {
      if (tabId === 'for-client') {
        link.classList.add('client-active');
      } else {
        link.classList.add('active');
      }
      link.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function openModal(title, depth, content) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-depth').textContent = depth;
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
        el.getAttribute('data-depth') || 'CONTEXT',
        el.getAttribute('data-content') || 'No additional information.'
      );
    });
  });

  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
</script>

</body>
</html>