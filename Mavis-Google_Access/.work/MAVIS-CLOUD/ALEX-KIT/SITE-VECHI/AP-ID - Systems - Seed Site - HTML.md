<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Bimodal Blueprint | Alexandru Popescu x Plateful</title>
    
    <!-- Fonts: Space Grotesk (Display) & Inter (Body) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Configuration to match Reference Style -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        display: ['Space Grotesk', 'sans-serif'],
                    },
                    colors: {
                        bg: '#050507', // Deep black/blue
                        surface: '#0F1016', // Card background
                        border: '#1E2029', // Subtle borders
                        accent: '#6D5DD3', // Primary Purple
                        accentGlow: '#8B7CF7',
                        human: '#FF6B6B', // Coral for Human/Mode A
                        ai: '#4DABF7', // Cyan for AI/Mode B
                        textMain: '#E2E8F0',
                        textMuted: '#94A3B8',
                    },
                    backgroundImage: {
                        'grid-pattern': "linear-gradient(to right, #1E2029 1px, transparent 1px), linear-gradient(to bottom, #1E2029 1px, transparent 1px)",
                    }
                }
            }
        }
    </script>

    <style>
        /* Custom Utilities */
        body {
            background-color: #050507;
            color: #E2E8F0;
            overflow-x: hidden;
        }
        
        .glass-panel {
            background: rgba(15, 16, 22, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .glow-text-human { text-shadow: 0 0 20px rgba(255, 107, 107, 0.3); }
        .glow-text-ai { text-shadow: 0 0 20px rgba(77, 171, 247, 0.3); }
        
        .gradient-text {
            background: linear-gradient(135deg, #FF6B6B 0%, #FFFFFF 50%, #4DABF7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Smooth Scroll */
        html { scroll-behavior: smooth; }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #050507; }
        ::-webkit-scrollbar-thumb { background: #1E2029; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #6D5DD3; }

        /* Animation Classes */
        .fade-in-up {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease-out, transform 0.6s ease-out;
        }
        .fade-in-up.visible {
            opacity: 1;
            transform: translateY(0);
        }
    </style>
</head>
<body class="antialiased selection:bg-accent selection:text-white">

    <!-- Background Grid -->
    <div class="fixed inset-0 z-0 opacity-20 pointer-events-none bg-grid-pattern bg-[size:40px_40px]"></div>
    
    <!-- Navigation -->
    <nav class="fixed top-0 w-full z-50 glass-panel border-b border-border/50">
        <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div class="font-display font-bold text-xl tracking-tight">
                AP-ID <span class="text-accent">.</span> SYSTEMS
            </div>
            <div class="hidden md:flex space-x-8 text-sm font-medium text-textMuted">
                <a href="#thesis" class="hover:text-white transition-colors">The Thesis</a>
                <a href="#workflow" class="hover:text-white transition-colors">Bimodal Workflow</a>
                <a href="#evidence" class="hover:text-white transition-colors">Evidence</a>
                <a href="#roadmap" class="hover:text-white transition-colors">Roadmap</a>
            </div>
            <a href="mailto:apvizual@gmail.com" class="px-4 py-2 bg-accent/10 hover:bg-accent/20 border border-accent/30 text-accent rounded text-xs font-bold uppercase tracking-wider transition-all">
                Initiate Contact
            </a>
        </div>
    </nav>

    <!-- Hero Section -->
    <header id="thesis" class="relative z-10 pt-32 pb-20 px-6 max-w-7xl mx-auto min-h-screen flex flex-col justify-center">
        <div class="fade-in-up">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-accent/30 bg-accent/5 text-accent text-xs font-mono mb-8">
                <span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
                PREPARED FOR The Client
            </div>
            
            <h1 class="font-display text-6xl md:text-8xl font-bold leading-[0.9] mb-8">
                BEYOND <br>
                <span class="gradient-text">PIXELS.</span>
            </h1>
            
            <p class="text-xl md:text-2xl text-textMuted max-w-3xl leading-relaxed mb-12">
                Architecting Plateful's Creative Future with a 
                <span class="text-human font-semibold">Human-Centric</span> & 
                <span class="text-ai font-semibold">AI-Augmented</span> Framework.
            </p>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
                <div class="glass-panel p-6 rounded-lg border-l-2 border-human">
                    <h3 class="font-display text-lg font-bold mb-2 text-white">Mode A: Strategy</h3>
                    <p class="text-sm text-textMuted">Psychological Insight + Behavioral Economics. The Soul.</p>
                </div>
                <div class="glass-panel p-6 rounded-lg border-l-2 border-ai">
                    <h3 class="font-display text-lg font-bold mb-2 text-white">Mode B: Velocity</h3>
                    <p class="text-sm text-textMuted">Local LLM Infrastructure + Automated Execution. The Scale.</p>
                </div>
                <div class="glass-panel p-6 rounded-lg border-l-2 border-accent">
                    <h3 class="font-display text-lg font-bold mb-2 text-white">The Goal</h3>
                    <p class="text-sm text-textMuted">Scaling to $70M without losing brand integrity.</p>
                </div>
            </div>
        </div>
    </header>

    <!-- The Bimodal Workflow Section -->
    <section id="workflow" class="py-24 px-6 relative z-10">
        <div class="max-w-7xl mx-auto">
            <div class="mb-16 fade-in-up">
                <h2 class="font-display text-4xl font-bold mb-4">Deconstructing the Workflow</h2>
                <p class="text-textMuted max-w-2xl">A symbiotic loop where human strategy directs machine velocity, and machine efficiency frees human intellect.</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-stretch">
                <!-- Mode A -->
                <div class="glass-panel p-8 rounded-2xl relative overflow-hidden group fade-in-up">
                    <div class="absolute top-0 right-0 w-64 h-64 bg-human/10 rounded-full blur-3xl -mr-16 -mt-16 transition-opacity group-hover:opacity-75"></div>
                    <div class="relative z-10">
                        <div class="text-human font-mono text-sm mb-4">// MODE_A :: STRATEGY</div>
                        <h3 class="font-display text-3xl font-bold mb-6 glow-text-human">Psychological Insight</h3>
                        
                        <ul class="space-y-6">
                            <li class="flex gap-4">
                                <div class="w-8 h-8 rounded bg-human/20 flex items-center justify-center text-human shrink-0">🧠</div>
                                <div>
                                    <strong class="block text-white mb-1">Behavioral Economics</strong>
                                    <span class="text-sm text-textMuted">Leveraging formal education to understand market forces and consumer value perception.</span>
                                </div>
                            </li>
                            <li class="flex gap-4">
                                <div class="w-8 h-8 rounded bg-human/20 flex items-center justify-center text-human shrink-0">🧩</div>
                                <div>
                                    <strong class="block text-white mb-1">MBTI / Cognitive Archetypes</strong>
                                    <span class="text-sm text-textMuted">Tracking evolution since 2017 to target specific cognitive processing styles (Sensor vs. Intuitive).</span>
                                </div>
                            </li>
                            <li class="flex gap-4">
                                <div class="w-8 h-8 rounded bg-human/20 flex items-center justify-center text-human shrink-0">❤️</div>
                                <div>
                                    <strong class="block text-white mb-1">The "Volunteer" Principle</strong>
                                    <span class="text-sm text-textMuted">Leading with empathy. "You cannot fire a volunteer." Building trust in remote teams.</span>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>

                <!-- Connector Arrow (Desktop) -->
                <div class="hidden lg:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20 w-12 h-12 bg-surface border border-border rounded-full items-center justify-center shadow-2xl">
                    <svg class="w-6 h-6 text-accent animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                </div>

                <!-- Mode B -->
                <div class="glass-panel p-8 rounded-2xl relative overflow-hidden group fade-in-up">
                    <div class="absolute top-0 right-0 w-64 h-64 bg-ai/10 rounded-full blur-3xl -mr-16 -mt-16 transition-opacity group-hover:opacity-75"></div>
                    <div class="relative z-10">
                        <div class="text-ai font-mono text-sm mb-4">// MODE_B :: EXECUTION</div>
                        <h3 class="font-display text-3xl font-bold mb-6 glow-text-ai">Machine Velocity</h3>
                        
                        <ul class="space-y-6">
                            <li class="flex gap-4">
                                <div class="w-8 h-8 rounded bg-ai/20 flex items-center justify-center text-ai shrink-0">🔒</div>
                                <div>
                                    <strong class="block text-white mb-1">Private Local LLM</strong>
                                    <span class="text-sm text-textMuted">Air-gapped infrastructure. Zero data leakage. 100% IP security for Plateful.</span>
                                </div>
                            </li>
                            <li class="flex gap-4">
                                <div class="w-8 h-8 rounded bg-ai/20 flex items-center justify-center text-ai shrink-0">⚡</div>
                                <div>
                                    <strong class="block text-white mb-1">Automated Production</strong>
                                    <span class="text-sm text-textMuted">Resizing, variation generation, and compliance checks at machine speed.</span>
                                </div>
                            </li>
                            <li class="flex gap-4">
                                <div class="w-8 h-8 rounded bg-ai/20 flex items-center justify-center text-ai shrink-0">♾️</div>
                                <div>
                                    <strong class="block text-white mb-1">Infinite Context Memory</strong>
                                    <span class="text-sm text-textMuted">Proprietary system that remembers every brand guideline, preventing drift at scale.</span>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Evidence Matrix -->
    <section id="evidence" class="py-24 px-6 bg-surface/30 border-y border-border/30 relative z-10">
        <div class="max-w-7xl mx-auto">
            <div class="mb-16 fade-in-up">
                <h2 class="font-display text-4xl font-bold mb-4">Evidence-Based Validation</h2>
                <p class="text-textMuted">Anchoring claims in quantifiable achievements from enterprise and DTC environments.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 fade-in-up">
                <!-- Card 1 -->
                <div class="bg-bg border border-border p-6 rounded-lg hover:border-accent/50 transition-colors">
                    <div class="text-4xl font-display font-bold text-white mb-2">200+</div>
                    <div class="text-accent text-xs font-bold uppercase tracking-wider mb-4">Templates Created</div>
                    <p class="text-sm text-textMuted">Unified visual aesthetic across 12 European countries at <span class="text-white">Yokogawa</span>.</p>
                </div>
                <!-- Card 2 -->
                <div class="bg-bg border border-border p-6 rounded-lg hover:border-accent/50 transition-colors">
                    <div class="text-4xl font-display font-bold text-white mb-2">90%+</div>
                    <div class="text-accent text-xs font-bold uppercase tracking-wider mb-4">WCAG Compliance</div>
                    <p class="text-sm text-textMuted">Passed strict accessibility audits at <span class="text-white">Microsoft PCoE</span>.</p>
                </div>
                <!-- Card 3 -->
                <div class="bg-bg border border-border p-6 rounded-lg hover:border-accent/50 transition-colors">
                    <div class="text-4xl font-display font-bold text-white mb-2">25k+</div>
                    <div class="text-accent text-xs font-bold uppercase tracking-wider mb-4">Visuals Processed</div>
                    <p class="text-sm text-textMuted">High-volume asset management for <span class="text-white">MADE.com</span> intl. launch.</p>
                </div>
                <!-- Card 4 -->
                <div class="bg-bg border border-border p-6 rounded-lg hover:border-accent/50 transition-colors">
                    <div class="text-4xl font-display font-bold text-white mb-2">50+</div>
                    <div class="text-accent text-xs font-bold uppercase tracking-wider mb-4">DTC Campaigns</div>
                    <p class="text-sm text-textMuted">Led strategies for <span class="text-white">Ninja, Crock-Pot, Shark</span>.</p>
                </div>
            </div>

            <!-- Social Proof Ticker -->
            <div class="mt-16 glass-panel p-8 rounded-xl fade-in-up">
                <h3 class="font-display text-xl font-bold mb-6 text-center">Validated by Collaborators</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                    <div>
                        <p class="italic text-textMuted mb-4">"Hard projects were made easy... input goes beyond pure design skills."</p>
                        <cite class="text-white text-sm font-bold not-italic">Luca Costea, Copywriter</cite>
                    </div>
                    <div>
                        <p class="italic text-textMuted mb-4">"Alex didn't just offer a drawing, he offered consultancy from an artist!"</p>
                        <cite class="text-white text-sm font-bold not-italic">Alexandru Păun, CEO</cite>
                    </div>
                    <div>
                        <p class="italic text-textMuted mb-4">"Passionate storyteller and caring companion."</p>
                        <cite class="text-white text-sm font-bold not-italic">Bogdan Bârligea, Marketing</cite>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Strategic Roadmap -->
    <section id="roadmap" class="py-24 px-6 relative z-10">
        <div class="max-w-5xl mx-auto">
            <div class="mb-16 text-center fade-in-up">
                <h2 class="font-display text-4xl font-bold mb-4">Implementation Roadmap</h2>
                <p class="text-textMuted">From Day 1 Sandbox to Long-Term Symbiosis.</p>
            </div>

            <div class="relative border-l border-border ml-4 md:ml-0 space-y-12 fade-in-up">
                <!-- Phase 1 -->
                <div class="relative pl-8 md:pl-0 md:grid md:grid-cols-5 md:gap-8 items-center">
                    <div class="absolute -left-[5px] top-0 w-2.5 h-2.5 rounded-full bg-human ring-4 ring-bg"></div>
                    <div class="md:col-span-2 md:text-right mb-2 md:mb-0">
                        <h3 class="font-display text-xl font-bold text-human">Phase 1: Sandbox</h3>
                        <span class="text-xs text-textMuted uppercase tracking-widest">Weeks 1-4</span>
                    </div>
                    <div class="md:col-span-3 glass-panel p-6 rounded-lg border-l-2 border-human/50">
                        <p class="text-sm text-textMuted">Utilize my local AI as a secure test environment. Ingest public Plateful data to build the "Brand Brain." Zero infrastructure cost to you.</p>
                    </div>
                </div>

                <!-- Phase 2 -->
                <div class="relative pl-8 md:pl-0 md:grid md:grid-cols-5 md:gap-8 items-center">
                    <div class="absolute -left-[5px] top-0 w-2.5 h-2.5 rounded-full bg-ai ring-4 ring-bg"></div>
                    <div class="md:col-span-2 md:text-right mb-2 md:mb-0">
                        <h3 class="font-display text-xl font-bold text-ai">Phase 2: Migration</h3>
                        <span class="text-xs text-textMuted uppercase tracking-widest">Month 2</span>
                    </div>
                    <div class="md:col-span-3 glass-panel p-6 rounded-lg border-l-2 border-ai/50">
                        <p class="text-sm text-textMuted">Deploy the validated template model to Plateful's private servers. Complete data sovereignty. Executable IP transfer.</p>
                    </div>
                </div>

                <!-- Phase 3 -->
                <div class="relative pl-8 md:pl-0 md:grid md:grid-cols-5 md:gap-8 items-center">
                    <div class="absolute -left-[5px] top-0 w-2.5 h-2.5 rounded-full bg-accent ring-4 ring-bg"></div>
                    <div class="md:col-span-2 md:text-right mb-2 md:mb-0">
                        <h3 class="font-display text-xl font-bold text-accent">Phase 3: Symbiosis</h3>
                        <span class="text-xs text-textMuted uppercase tracking-widest">Year 1+</span>
                    </div>
                    <div class="md:col-span-3 glass-panel p-6 rounded-lg border-l-2 border-accent/50">
                        <p class="text-sm text-textMuted">Continuous R&D partnership. I help evolve your engine; Plateful helps refine my Art Direction intelligence. Mutual growth.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer / CTA -->
    <footer class="py-20 px-6 border-t border-border bg-bg relative z-10">
        <div class="max-w-4xl mx-auto text-center">
            <h2 class="font-display text-3xl md:text-5xl font-bold mb-8">Ready to Stress-Test?</h2>
            <p class="text-textMuted mb-10 text-lg">
                The attached documentation serves as the baseline configuration. <br>
                Let's use our interview to validate these ideas against Plateful's actual bottlenecks.
            </p>
            
            <div class="flex flex-col md:flex-row justify-center items-center gap-6">
                <a href="mailto:apvizual@gmail.com" class="px-8 py-4 bg-accent hover:bg-accentGlow text-white font-bold rounded transition-all shadow-[0_0_20px_rgba(109,93,211,0.4)]">
                    apvizual@gmail.com
                </a>
                <div class="text-textMuted text-sm">
                    <span class="block md:inline">WhatsApp: +40 722 121 752</span>
                    <span class="hidden md:inline mx-2">|</span>
                    <span class="block md:inline">Timezone: EET (UTC+2)</span>
                </div>
            </div>
            
            <div class="mt-16 text-xs text-textMuted/50 font-mono">
                GENERATED BY BIMODAL AI WORKFLOW // PROOF OF CONCEPT
            </div>
        </div>
    </footer>

    <!-- Scripts -->
    <script>
        // Intersection Observer for Fade-in animations
        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        document.querySelectorAll('.fade-in-up').forEach(el => {
            observer.observe(el);
        });
    </script>
</body>
</html>

