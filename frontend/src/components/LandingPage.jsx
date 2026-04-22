import React, { useState, useEffect } from 'react';
import { motion, useScroll, useTransform, useMotionTemplate, useMotionValue } from 'framer-motion';
import {
    Search, FileText, Zap, Globe, Layers, Workflow,
    Shield, ChevronRight, Play, Star, Sparkles, Database, Code, Activity, Hexagon,
    Terminal, ArrowRight, Scale, CheckCircle2, Loader2
} from 'lucide-react';

export default function LandingPage({ onGetStarted }) {
    const [scrolled, setScrolled] = useState(false);
    const { scrollYProgress } = useScroll();

    // Parallax effects
    const heroY = useTransform(scrollYProgress, [0, 0.2], [0, 50]);
    const mockY = useTransform(scrollYProgress, [0, 0.2], [0, -50]);
    const opacityY = useTransform(scrollYProgress, [0, 0.15], [1, 0]);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const fadeUp = {
        hidden: { opacity: 0, y: 40 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } }
    };

    const stagger = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { staggerChildren: 0.15 } }
    };

    return (
        <div className="min-h-screen bg-nyaya-bg text-nyaya-text font-sans selection:bg-nyaya-accent/30 selection:text-white overflow-x-hidden relative">

            {/* Ultra-Premium Dark Ambient Background */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                {/* Noise Texture Overlay */}
                <div className="absolute inset-0 bg-[url('/noise.svg')] opacity-[0.03] mix-blend-multiply"></div>
                {/* Subtle Glows */}
                <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] rounded-full bg-nyaya-accent/10 blur-[120px] mix-blend-multiply" />
                <div className="absolute top-[20%] right-[-10%] w-[30vw] h-[30vw] rounded-full bg-purple-500/5 blur-[120px] mix-blend-multiply" />
            </div>

            {/* Elite Navigation */}
            <nav className={`fixed w-full z-50 transition-all duration-700 border-b ${scrolled
                ? 'bg-nyaya-surface/80 backdrop-blur-xl border-nyaya-border shadow-sm py-4'
                : 'bg-transparent border-transparent py-8'
                }`}>
                <div className="max-w-[88rem] mx-auto px-6 lg:px-12 flex items-center justify-between">
                    <div className="flex items-center gap-3 relative group">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-100 to-purple-100 border border-indigo-200 flex items-center justify-center shadow-lg transition-transform duration-300 group-hover:scale-105">
                            <Sparkles size={18} className="text-nyaya-primary" />
                        </div>
                        <span className="text-xl font-bold tracking-tight text-nyaya-text">Lumina<span className="text-nyaya-muted">.ai</span></span>
                    </div>

                    <div className="hidden md:flex items-center gap-10 text-sm font-medium text-nyaya-muted">
                        <a href="#features" className="hover:text-nyaya-primary transition-colors duration-300">Features</a>
                        <a href="#how-it-works" className="hover:text-nyaya-primary transition-colors duration-300">Architecture</a>
                        <a href="#customers" className="hover:text-nyaya-primary transition-colors duration-300">Customers</a>
                        <a href="#pricing" className="hover:text-nyaya-primary transition-colors duration-300">Pricing</a>
                    </div>

                    <div className="flex items-center gap-6">
                        <button onClick={onGetStarted} className="hidden md:block text-sm font-semibold text-nyaya-muted hover:text-nyaya-primary transition-colors duration-300">Sign in</button>

                        <div className="relative group">
                            <button
                                onClick={onGetStarted}
                                className="relative px-6 py-2.5 bg-nyaya-text text-nyaya-bg text-[13px] font-bold rounded-full hover:bg-nyaya-text/90 transition-all flex items-center gap-2 tracking-wide shadow-lg"
                            >
                                Start Free <ArrowRight size={14} />
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="relative z-10 pt-40 lg:pt-52 bg-gradient-to-b from-transparent via-indigo-100/40 to-transparent">

                {/* Mega Hero Section */}
                <section className="px-6 lg:px-12 max-w-[88rem] mx-auto relative flex flex-col items-center">

                    <motion.div style={{ y: heroY, opacity: opacityY }} className="max-w-4xl mx-auto text-center relative z-20 flex flex-col items-center">

                        {/* Animated Pill Badge */}
                        <motion.button
                            onClick={onGetStarted}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, ease: "easeOut" }}
                            className="group flex mx-auto items-center gap-2 px-4 py-1.5 rounded-full bg-nyaya-surface border border-nyaya-border text-xs font-semibold text-nyaya-muted uppercase tracking-[0.2em] mb-12 hover:bg-nyaya-border/50 hover:text-nyaya-text transition-all cursor-pointer shadow-sm"
                        >
                            <span className="w-1.5 h-1.5 rounded-full bg-nyaya-text opacity-80" />
                            Lumina Precedent Engine is now live
                            <ChevronRight size={14} className="text-nyaya-muted group-hover:text-nyaya-text group-hover:translate-x-1 transition-all" />
                        </motion.button>

                        <motion.h1
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.9, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                            className="text-[3.5rem] leading-[1.05] sm:text-6xl lg:text-[5.5rem] lg:leading-[1.02] font-semibold text-nyaya-text tracking-tighter mb-8"
                        >
                            Intelligent Research.<br />
                            <span className="text-nyaya-muted">
                                Predictive Outcomes.
                            </span>
                        </motion.h1>

                        <motion.p
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.9, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                            className="text-lg md:text-xl text-nyaya-muted mb-12 max-w-2xl leading-relaxed tracking-tight"
                        >
                            Upload complex legal documents. Find exactly matching precedents via semantic similarity.
                            Predict case outcomes with ensemble ML models. The cognitive engine for modern law.
                        </motion.p>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.9, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
                            className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto"
                        >
                            <button
                                onClick={onGetStarted}
                                className="w-full sm:w-auto px-8 py-3.5 bg-nyaya-text text-nyaya-bg text-[15px] font-semibold rounded-full hover:bg-nyaya-text/90 transition-all flex items-center justify-center shadow-lg"
                            >
                                Start Researching Free
                            </button>

                            <button
                                onClick={onGetStarted}
                                className="w-full sm:w-auto px-8 py-3.5 bg-transparent text-nyaya-text border border-nyaya-border text-[15px] font-semibold rounded-full hover:bg-nyaya-surface transition-all flex items-center justify-center gap-3 backdrop-blur-sm"
                            >
                                <Play size={14} className="text-nyaya-muted ml-0.5" />
                                Watch Platform Demo
                            </button>
                        </motion.div>
                    </motion.div>

                    {/* Legal AI Interface Mockup */}
                    <div className="w-full mt-24 relative perspective-1000 mb-20 lg:mb-40">
                        <motion.div
                            style={{ y: mockY }}
                            initial={{ opacity: 0, rotateX: 20, y: 100 }}
                            animate={{ opacity: 1, rotateX: 0, y: 0 }}
                            transition={{ delay: 0.4, duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                            className="relative w-full max-w-4xl mx-auto rounded-[2rem] border border-nyaya-border bg-nyaya-surface/80 backdrop-blur-2xl shadow-2xl overflow-hidden flex flex-col transform-gpu"
                        >
                            {/* Mac OS Window Controls */}
                            <div className="w-full h-16 border-b border-nyaya-border bg-nyaya-bg/50 flex items-center justify-between px-6">
                                <div className="flex gap-2">
                                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                                    <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                                    <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                                </div>
                                <div className="text-sm font-semibold text-nyaya-text flex items-center gap-2">
                                    <Sparkles size={16} className="text-nyaya-primary" /> Lumina Legal Assistant
                                </div>
                                <div className="w-16"></div> {/* Spacer to center the title */}
                            </div>

                            {/* Chat Body */}
                            <div className="p-6 md:p-8 space-y-6 bg-nyaya-bg/30 min-h-[400px]">
                                {/* User Message */}
                                <div className="flex justify-end">
                                    <div className="bg-nyaya-text text-nyaya-surface px-5 py-4 rounded-2xl rounded-tr-sm max-w-[85%] md:max-w-[70%] shadow-sm text-[15px]">
                                        What is the precedent for breach of contract in software development agreements under Indian Law?
                                    </div>
                                </div>

                                {/* AI Response */}
                                <div className="flex justify-start">
                                    <div className="flex gap-4 max-w-[95%] md:max-w-[85%]">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 border border-indigo-200 flex items-center justify-center shrink-0 shadow-sm hidden md:flex">
                                            <Sparkles size={16} className="text-nyaya-primary" />
                                        </div>
                                        <div className="bg-nyaya-surface border border-nyaya-border p-6 rounded-2xl rounded-tl-sm shadow-sm space-y-5">
                                            <p className="text-[15px] leading-relaxed text-nyaya-text font-medium">
                                                Under Indian Law, the precedent for breach of contract in software agreements is primarily governed by the <span className="text-nyaya-primary font-bold">Indian Contract Act, 1872</span> combined with the <span className="text-nyaya-primary font-bold">Information Technology Act, 2000</span>.
                                            </p>

                                            <div className="bg-nyaya-bg p-4 rounded-xl border border-nyaya-border shadow-inner">
                                                <h4 className="text-sm font-bold text-nyaya-text mb-2 flex items-center gap-2">
                                                    <Scale size={16} className="text-nyaya-muted" /> Key Case Law
                                                </h4>
                                                <p className="text-[14px] text-nyaya-text font-semibold">Tata Consultancy Services v. State of A.P. (2004)</p>
                                                <p className="text-[13px] text-nyaya-muted mt-1 leading-relaxed">This Supreme Court case established that custom software can be considered "goods", setting a major precedent for liability and breach assessment in IT development contracts.</p>
                                            </div>

                                            <div className="flex items-center gap-2">
                                                <div className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse"></div>
                                                <div className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                                                <div className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                                                <span className="text-xs text-nyaya-muted ml-2 font-medium">Synthesizing further arguments...</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Input Bar */}
                            <div className="p-4 bg-nyaya-surface border-t border-nyaya-border">
                                <div className="relative">
                                    <div className="w-full h-14 bg-nyaya-bg border border-nyaya-border rounded-xl flex items-center px-4 shadow-inner">
                                        <span className="text-nyaya-muted text-[15px]">Analyzing relevant case laws matching your query...</span>
                                    </div>
                                    <div className="absolute right-3 top-3 w-8 h-8 rounded-lg bg-nyaya-primary/10 flex items-center justify-center">
                                        <Loader2 size={16} className="text-nyaya-primary animate-spin" />
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        {/* Floating Micro-Interaction Cards */}
                        <motion.div
                            animate={{ y: [-10, 10, -10], rotate: [0, 1, 0] }}
                            transition={{ repeat: Infinity, duration: 5, ease: "easeInOut" }}
                            className="absolute -right-8 top-20 z-30 p-4 rounded-2xl bg-nyaya-surface/90 backdrop-blur-3xl border border-nyaya-border shadow-xl hidden lg:flex items-center gap-4"
                        >
                            <div className="w-12 h-12 rounded-full bg-emerald-100 border border-emerald-200 flex items-center justify-center">
                                <CheckCircle2 size={20} className="text-emerald-600" />
                            </div>
                            <div>
                                <div className="text-[15px] font-bold text-nyaya-text">Precedents Found</div>
                                <div className="text-[13px] text-nyaya-muted">42 relevant cases analyzed</div>
                            </div>
                        </motion.div>

                        <motion.div
                            animate={{ y: [10, -10, 10], rotate: [0, -1, 0] }}
                            transition={{ repeat: Infinity, duration: 7, ease: "easeInOut", delay: 1 }}
                            className="absolute -left-12 bottom-32 z-30 p-4 rounded-2xl bg-nyaya-surface/90 backdrop-blur-3xl border border-nyaya-border shadow-xl hidden lg:flex items-center gap-4"
                        >
                            <div className="w-12 h-12 rounded-full bg-purple-100 border border-purple-200 flex items-center justify-center">
                                <FileText size={20} className="text-purple-600" />
                            </div>
                            <div>
                                <div className="text-[15px] font-bold text-nyaya-text">Auto-Drafting</div>
                                <div className="text-[13px] text-nyaya-muted">Preparing summary brief...</div>
                            </div>
                        </motion.div>
                    </div>
                </section>

                {/* Sub-hero Logos Grid */}
                <section id="customers" className="mt-32 border-y border-nyaya-border bg-nyaya-bg py-12 relative overflow-hidden">
                    {/* Fades for carousel effect */}
                    <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-nyaya-bg to-transparent z-10" />
                    <div className="absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-nyaya-bg to-transparent z-10" />

                    <div className="max-w-[88rem] mx-auto px-6 flex flex-col items-center">
                        <p className="text-xs font-bold text-nyaya-muted uppercase tracking-[0.2em] mb-10">Trusted framework for elite legal research</p>
                        <div className="flex flex-wrap justify-center gap-12 md:gap-24 items-center opacity-60 hover:opacity-100 transition-opacity duration-500 text-nyaya-text">
                            {/* Legal-grade dummy logos */}
                            <span className="text-xl md:text-2xl font-black font-serif tracking-tighter flex items-center gap-2">Amarchand</span>
                            <span className="text-xl md:text-2xl font-bold tracking-tight flex items-center gap-2"><Layers size={28} /> Khaitan & Co</span>
                            <span className="text-xl md:text-2xl font-black italic flex items-center gap-2">Trilegal</span>
                            <span className="text-xl md:text-2xl font-bold font-serif tracking-tight flex items-center gap-2"><Database size={28} /> JSA</span>
                            <span className="text-xl md:text-2xl font-bold uppercase tracking-widest flex items-center gap-2"><Shield size={28} /> AZB</span>
                        </div>
                    </div>
                </section>

                {/* Asymmetrical Apple-esque Bento Grid */}
                <section id="features" className="py-24 px-6 lg:px-12 max-w-[88rem] mx-auto relative z-10">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[420px]">

                        {/* 1. Internet-powered */}
                        <InteractiveBentoCard className="col-span-1 bg-nyaya-surface p-10 flex flex-col relative border border-nyaya-border/50 shadow-sm hover:shadow-2xl hover:border-nyaya-border transition-all duration-500">
                            <h3 className="text-3xl font-medium text-nyaya-text mb-3 tracking-tight">Live Legal Web</h3>
                            <p className="text-nyaya-muted text-base leading-relaxed max-w-[90%] text-balance">Real-time citation across state & federal databases in seconds.</p>

                            {/* Center Graphic */}
                            <div className="absolute inset-x-0 bottom-0 h-[65%] flex items-center justify-center pointer-events-none">
                                {/* Lines */}
                                <div className="absolute w-[70%] h-[1px] bg-nyaya-border"></div>
                                <div className="absolute h-[70%] w-[1px] bg-nyaya-border"></div>
                                {/* Center Node */}
                                <div className="relative z-10 w-20 h-20 rounded-3xl bg-nyaya-text text-nyaya-bg flex items-center justify-center shadow-[0_0_40px_rgba(255,255,255,0.1)] group-hover:scale-105 transition-transform duration-500">
                                    <span className="font-bold text-3xl italic tracking-tighter pr-1">A</span>
                                    <div className="absolute -inset-6 rounded-[2.5rem] bg-nyaya-text/5 blur-xl -z-10 group-hover:bg-nyaya-text/10 transition-colors"></div>
                                </div>
                                {/* Peripheral Nodes */}
                                <div className="absolute left-[13%] w-8 h-8 rounded-full bg-nyaya-surface flex items-center justify-center border border-nyaya-border shadow-sm">
                                    <div className="w-1.5 h-1.5 rounded-full bg-nyaya-text opacity-50"></div>
                                </div>
                                <div className="absolute right-[13%] w-6 h-6 rounded-full bg-nyaya-surface flex items-center justify-center border border-nyaya-border shadow-sm">
                                    <div className="w-1.5 h-1.5 bg-nyaya-text opacity-50 rounded-sm"></div>
                                </div>
                                <div className="absolute bottom-[10%] w-8 h-8 rounded-[0.4rem] bg-nyaya-surface flex items-center justify-center border border-nyaya-border shadow-sm">
                                    <FileText size={12} className="text-nyaya-muted" />
                                </div>
                            </div>
                        </InteractiveBentoCard>

                        {/* 2. Ask AI Lawyer */}
                        <InteractiveBentoCard className="md:col-span-2 bg-nyaya-surface p-10 flex flex-col justify-end relative border border-nyaya-border/50 shadow-sm hover:shadow-2xl transition-all duration-500 overflow-hidden">
                            {/* Top Mockup Graphics */}
                            <div className="absolute top-10 left-10 w-full pointer-events-none z-10">
                                {/* Chat container */}
                                <div className="w-[380px] bg-nyaya-bg border border-nyaya-border rounded-3xl p-7 shadow-2xl group-hover:-translate-y-1 transition-transform duration-500">
                                    <div className="text-[15px] font-medium text-nyaya-text mb-2">Hello, Chris! 👋</div>
                                    <div className="text-[14px] text-nyaya-muted leading-relaxed mb-5">Please select a question from the "Prompts" library below or write your own question.<br /><br />You can also add context from any of the already existing chat from history</div>
                                    <div className="w-full py-3 rounded-2xl bg-nyaya-surface text-nyaya-muted text-[14px] font-medium flex items-center justify-center gap-2 border border-nyaya-border/50">
                                        <span className="text-[16px] font-normal">+</span> Add
                                    </div>
                                </div>
                                {/* Floating elements */}
                                <div className="absolute top-[180px] left-[320px] bg-nyaya-text text-nyaya-bg px-6 py-4 rounded-3xl rounded-tl-sm text-[14px] font-semibold shadow-[0_30px_60px_rgba(0,0,0,0.5)] group-hover:scale-105 transition-transform duration-500 origin-bottom-left z-20 w-max max-w-[300px]">
                                    Summarize recent precedent on fair use in the 9th Circuit.
                                </div>
                                <div className="absolute top-[300px] left-10 bg-nyaya-bg border border-nyaya-border px-5 py-3 rounded-[1.25rem] text-[14px] text-nyaya-muted shadow-lg">
                                    Respond...
                                </div>
                            </div>

                            {/* Ambient Glow */}
                            <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-nyaya-accent/10 blur-[100px] pointer-events-none rounded-full"></div>

                            {/* Bottom Text */}
                            <div className="relative z-30 mt-[260px]">
                                <h3 className="text-3xl font-medium text-nyaya-text mb-3 tracking-tight">Lumina Copilot</h3>
                                <p className="text-nyaya-muted text-base leading-relaxed max-w-2xl text-balance">Draft memos, analyze opposing counsel's arguments, and synthesize complex caselaw through an intuitive conversation.</p>
                            </div>
                        </InteractiveBentoCard>

                        {/* 3. AI document handling */}
                        <InteractiveBentoCard className="col-span-1 bg-nyaya-surface p-10 flex flex-col relative border border-nyaya-border/50 shadow-sm hover:shadow-2xl transition-all duration-500">
                            {/* Mockups */}
                            <div className="absolute top-14 inset-x-0 w-full px-8 flex flex-col gap-3 pointer-events-none">
                                <div className="bg-nyaya-bg border border-nyaya-border rounded-[1.25rem] p-4 flex items-center gap-4 shadow-lg group-hover:-translate-y-1 transition-transform duration-500 delay-75">
                                    <div className="p-2 border border-nyaya-border bg-nyaya-surface rounded-xl"><FileText size={16} className="text-nyaya-text" /></div>
                                    <div>
                                        <div className="text-[14px] font-medium text-nyaya-text">Defendant_Summary_Motion.pdf</div>
                                        <div className="text-[12px] text-nyaya-muted">2.4MB</div>
                                    </div>
                                </div>
                                <div className="bg-nyaya-bg border border-nyaya-border rounded-[1.25rem] p-4 flex items-center gap-4 shadow-lg group-hover:-translate-y-1 transition-transform duration-500 delay-150">
                                    <div className="p-2 border border-nyaya-border bg-nyaya-surface rounded-xl"><FileText size={16} className="text-nyaya-text" /></div>
                                    <div>
                                        <div className="text-[14px] font-medium text-nyaya-text">Plaintiff_Exhibits_A_to_D.pdf</div>
                                        <div className="text-[12px] text-nyaya-muted">18MB</div>
                                    </div>
                                </div>
                                {/* Compare Button */}
                                <div className="bg-nyaya-text text-nyaya-bg rounded-[1.25rem] py-4 mt-2 flex items-center justify-center gap-2 text-[15px] font-bold shadow-[0_20px_50px_rgba(255,255,255,0.1)] group-hover:-translate-y-1 group-hover:shadow-[0_25px_60px_rgba(255,255,255,0.15)] transition-all duration-500">
                                    <Sparkles size={16} className="text-nyaya-bg/70" /> Cross-Reference
                                </div>
                            </div>

                            {/* Bottom Text */}
                            <div className="mt-auto relative z-10">
                                <h3 className="text-3xl font-medium text-nyaya-text mb-3 tracking-tight">Multi-Document RAG</h3>
                                <p className="text-nyaya-muted text-base leading-relaxed text-balance">Instantly identify contradictions and extract key facts across hundreds of dense legal PDFs automatically.</p>
                            </div>
                        </InteractiveBentoCard>

                        {/* 4. Precedent Similarity */}
                        <InteractiveBentoCard className="col-span-1 bg-nyaya-surface border border-nyaya-border/50 p-10 flex flex-col relative shadow-sm hover:shadow-2xl transition-all duration-500 overflow-hidden">
                            <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-purple-500/10 blur-[80px] pointer-events-none rounded-full"></div>

                            <div className="relative z-10">
                                <h3 className="text-3xl font-medium text-nyaya-text mb-3 tracking-tight">Similarity Engine</h3>
                                <p className="text-nyaya-muted text-base leading-relaxed text-balance">Our bespoke LLM encoder extracts factual similarity scores between uploaded briefs and millions of precedents.</p>
                            </div>

                            {/* Mockup */}
                            <div className="absolute -bottom-8 -right-8 h-[65%] w-full flex justify-end items-end group-hover:-translate-y-3 transition-transform duration-700 pointer-events-none px-8 z-20">
                                <div className="w-[110%] h-[90%] bg-nyaya-bg rounded-tl-3xl border-t border-l border-nyaya-border shadow-2xl overflow-hidden flex flex-col">
                                    {/* Dashboard header mock */}
                                    <div className="bg-nyaya-surface px-4 py-3 border-b border-nyaya-border flex items-center justify-between">
                                        <div className="h-2 w-16 bg-nyaya-border rounded-full"></div>
                                        <div className="text-[10px] font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md border border-emerald-400/20">84% Match</div>
                                    </div>
                                    {/* Content mock */}
                                    <div className="p-4 flex flex-col gap-3 flex-1 bg-nyaya-bg/50">
                                        <div className="h-3 w-3/4 bg-nyaya-border rounded-full"></div>
                                        <div className="h-2 w-full bg-nyaya-border/80 rounded-full mt-2"></div>
                                        <div className="h-2 w-5/6 bg-nyaya-border/80 rounded-full"></div>

                                        <div className="mt-auto bg-nyaya-surface p-3 rounded-xl border border-nyaya-border shadow-sm">
                                            <div className="flex justify-between items-center mb-2">
                                                <div className="h-2 w-12 bg-nyaya-border rounded-full"></div>
                                                <div className="h-2 w-8 bg-nyaya-accent rounded-full"></div>
                                            </div>
                                            <div className="w-full bg-nyaya-border h-1.5 rounded-full overflow-hidden">
                                                <div className="bg-nyaya-accent w-[84%] h-full rounded-full"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </InteractiveBentoCard>

                        {/* 5. Personalized for you */}
                        <InteractiveBentoCard className="col-span-1 bg-nyaya-surface p-10 flex flex-col relative border border-nyaya-border/50 shadow-sm hover:shadow-2xl transition-all duration-500 overflow-hidden">
                            <div className="relative z-10">
                                <h3 className="text-3xl font-medium text-nyaya-text mb-3 tracking-tight">Practice-specific</h3>
                                <p className="text-nyaya-muted text-base leading-relaxed text-balance">Custom system prompts tune the engine's tone and methodology to your specific practice area.</p>
                            </div>

                            {/* Icon Grid Mockup */}
                            <div className="absolute -bottom-16 -right-16 w-[130%] h-[70%] pointer-events-none group-hover:scale-[1.03] transition-transform duration-700">
                                <div className="grid grid-cols-4 gap-[14px] p-8 opacity-40">
                                    {[
                                        { I: Hexagon }, { I: Globe }, { I: Shield }, { I: Hexagon },
                                        { I: Hexagon }, { I: Layers }, { I: Hexagon }, { I: Code },
                                        { I: Code }, { I: Shield }, { I: Search }, { I: Shield },
                                        { I: Activity }, { I: Layers }, { I: Hexagon }, { I: Activity },
                                    ].map((item, i) => (
                                        <div key={i} className={`w-[3.25rem] h-[3.25rem] rounded-[1.1rem] bg-nyaya-bg shadow-inner flex items-center justify-center border border-nyaya-border text-nyaya-muted backdrop-blur-sm ${i === 6 ? 'bg-nyaya-text shadow-glow text-nyaya-bg border-transparent' : ''}`}>
                                            <item.I size={18} strokeWidth={1.5} />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </InteractiveBentoCard>

                    </div>
                </section>

                {/* Upcoming Mobile App Feature Showcase */}
                <section id="mobile-app" className="py-24 px-6 lg:px-12 max-w-[88rem] mx-auto relative z-10">
                    <div className="bg-nyaya-surface rounded-[3rem] border border-nyaya-border/50 overflow-hidden flex flex-col md:flex-row items-center relative min-h-[500px] shadow-2xl">

                        {/* Abstract Background Glows */}
                        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-500/10 blur-[120px] rounded-full mix-blend-multiply pointer-events-none"></div>
                        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-slate-500/10 blur-[100px] rounded-full mix-blend-multiply pointer-events-none"></div>

                        {/* Left Side: Elaborate Phone Mockup */}
                        <div className="flex-1 w-full h-full relative min-h-[450px] md:min-h-auto flex items-end justify-center pt-20 px-8 lg:px-20 overflow-hidden perspective-1000">

                            {/* iPhone Frame */}
                            <div className="relative w-80 h-[580px] bg-[#1a1a1c] rounded-[3.5rem] border-x-[12px] border-y-[12px] border-[#2A2A2E] shadow-[20px_0_60px_rgba(0,0,0,0.8)] flex flex-col items-center pt-3 overflow-hidden transform md:-rotate-3 hover:rotate-0 transition-transform duration-700 translate-y-16 group z-10">

                                {/* Dynamic Island */}
                                <div className="w-28 h-7 bg-black rounded-full mb-6 z-20 flex items-center justify-end px-3 gap-2 border border-nyaya-border/50">
                                    <div className="w-2 h-2 rounded-full bg-emerald-500/80 shadow-[0_0_10px_rgba(16,185,129,0.8)]"></div>
                                </div>

                                {/* App UI Canvas */}
                                <div className="absolute inset-x-0 bottom-0 top-3 bg-nyaya-bg border border-nyaya-border rounded-[2.8rem] flex flex-col pt-16 px-6 overflow-hidden">
                                    <h4 className="text-3xl font-bold text-nyaya-text mb-8 tracking-tighter">Chats</h4>

                                    {/* New Chat Button */}
                                    <div className="w-full bg-nyaya-surface border border-nyaya-border rounded-[1.25rem] py-4 flex justify-center items-center shadow-lg mb-8 transform group-hover:-translate-y-1 transition-all duration-300">
                                        <span className="text-nyaya-text text-[15px] font-semibold tracking-wide">+ New chat</span>
                                    </div>

                                    {/* Section Header */}
                                    <div className="text-[13px] font-medium text-nyaya-muted mb-4 pb-2 border-b border-nyaya-border/50">Pinned chats</div>

                                    {/* Chat Items */}
                                    <div className="space-y-3">
                                        <div className="bg-nyaya-surface border border-nyaya-border w-full rounded-2xl p-4 flex justify-between items-center cursor-pointer shadow-sm group-hover:bg-nyaya-border/30 transition-colors duration-300">
                                            <div className="flex items-center gap-3">
                                                <FileText size={16} className="text-nyaya-text" />
                                                <span className="text-[15px] font-medium text-nyaya-text">Work</span>
                                            </div>
                                            <ChevronRight size={14} className="text-nyaya-muted" />
                                        </div>
                                        <div className="bg-nyaya-surface border border-nyaya-border w-full rounded-2xl p-4 flex justify-between items-center cursor-pointer shadow-sm">
                                            <div className="flex items-center gap-3">
                                                <FileText size={16} className="text-nyaya-text" />
                                                <span className="text-[15px] font-medium text-nyaya-text">Work</span>
                                            </div>
                                            <ChevronRight size={14} className="text-nyaya-muted" />
                                        </div>
                                        <div className="w-full rounded-2xl py-3 px-2 flex justify-between items-center cursor-pointer opacity-70">
                                            <div className="flex items-center gap-3">
                                                <span className="text-[15px] font-medium text-nyaya-text">Chat about Tax Law</span>
                                            </div>
                                        </div>
                                        <div className="w-full rounded-2xl py-2 px-2 flex justify-between items-center cursor-pointer opacity-70">
                                            <div className="flex items-center gap-3">
                                                <FileText size={16} className="text-nyaya-muted" />
                                                <span className="text-[15px] font-medium text-nyaya-muted truncate max-w-[180px]">Tax Law Agreements com...</span>
                                            </div>
                                            <ChevronRight size={14} className="text-nyaya-muted/50" />
                                        </div>
                                    </div>

                                    {/* Fade Out Gradient at bottom of phone */}
                                    <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-nyaya-bg via-nyaya-bg/80 to-transparent pointer-events-none"></div>
                                </div>
                            </div>
                        </div>

                        {/* Right Side: Copy & App Store Badges */}
                        <div className="flex-1 w-full p-12 md:p-20 lg:pl-0 z-10 flex flex-col items-center md:items-start text-center md:text-left">

                            {/* Mobile Badge */}
                            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-nyaya-bg border border-nyaya-border text-nyaya-muted text-[11px] font-semibold uppercase tracking-widest mb-8 backdrop-blur-sm">
                                <Hexagon size={12} className="text-nyaya-text" />
                                Mobile App
                            </div>

                            <h2 className="text-5xl md:text-6xl lg:text-7xl font-medium text-nyaya-text mb-6 tracking-tight leading-[1.05]">
                                Lumina<br />mobile app
                            </h2>
                            <p className="text-lg text-nyaya-muted mb-12 leading-relaxed max-w-lg text-balance opacity-90">
                                Stay connected with your legal guide on iOS and Android. Handle briefs, track precedent, and review similarity analytics on the go. Currently in active development.
                            </p>

                            {/* Faux Store Buttons */}
                            <div className="flex flex-col sm:flex-row items-center gap-4 opacity-70">
                                <button className="flex items-center gap-3 px-5 py-3 bg-nyaya-bg border border-nyaya-border rounded-2xl hover:bg-nyaya-surface transition-colors cursor-not-allowed">
                                    <span className="text-nyaya-text">
                                        <svg viewBox="0 0 384 512" width="24" height="24" fill="currentColor">
                                            <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z" />
                                        </svg>
                                    </span>
                                    <div className="text-left">
                                        <div className="text-[9px] text-nyaya-muted uppercase tracking-wider font-semibold">Coming Soon on the</div>
                                        <div className="text-[15px] font-medium text-nyaya-text leading-tight">App Store</div>
                                    </div>
                                </button>
                                <button className="flex items-center gap-3 px-5 py-3 bg-nyaya-bg border border-nyaya-border rounded-2xl hover:bg-nyaya-surface transition-colors cursor-not-allowed">
                                    <Play className="w-6 h-6 text-nyaya-text" fill="currentColor" />
                                    <div className="text-left">
                                        <div className="text-[9px] text-nyaya-muted uppercase tracking-wider font-semibold">In Development for</div>
                                        <div className="text-[15px] font-medium text-nyaya-text leading-tight">Google Play</div>
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Final Master CTA Banner */}
                <section id="pricing" className="py-24 px-6 lg:px-12 max-w-[88rem] mx-auto relative overflow-hidden">
                    <div className="absolute inset-0 bg-nyaya-accent/5 blur-[150px] -z-10 rounded-full object-cover" />

                    <div className="rounded-[2.5rem] border border-nyaya-border bg-nyaya-surface/90 backdrop-blur-xl p-12 md:p-24 text-center relative overflow-hidden shadow-2xl">
                        {/* Internal Glows */}
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-[100px] bg-gradient-to-b from-nyaya-accent/10 to-transparent blur-[50px]"></div>
                        <div className="absolute right-0 bottom-0 w-[300px] h-[300px] bg-purple-500/5 blur-[100px] rounded-full"></div>

                        <div className="relative z-10">
                            <h2 className="text-4xl md:text-7xl font-black text-nyaya-text mb-8 tracking-tighter max-w-4xl mx-auto leading-tight">
                                Ready to scale your cognitive capacity?
                            </h2>
                            <p className="text-xl md:text-2xl text-nyaya-muted mb-12 max-w-2xl mx-auto font-medium">
                                Join thousands of elite professionals already operating years in the future.
                            </p>

                            <div className="flex flex-col sm:flex-row justify-center items-center gap-6">
                                {/* Mega Button with animated border */}
                                <div className="relative group">
                                    <button
                                        onClick={onGetStarted}
                                        className="relative px-12 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xl font-bold rounded-full transition-all flex items-center gap-3 hover:scale-[1.02] active:scale-95 shadow-lg hover:shadow-2xl hover:from-blue-500 hover:to-indigo-500"
                                    >
                                        Deploy Lumina Free <ArrowRight className="group-hover:translate-x-1 transition-transform" />
                                    </button>
                                </div>
                                <span className="text-nyaya-muted text-sm font-bold tracking-wide uppercase">No credit card required</span>
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            {/* Elite Minimal Footer */}
            <footer className="border-t border-nyaya-border bg-nyaya-bg pt-24 pb-12">
                <div className="max-w-[88rem] mx-auto px-6 lg:px-12 grid grid-cols-2 md:grid-cols-5 gap-12">
                    <div className="col-span-2">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-100 to-purple-100 border border-indigo-200 flex items-center justify-center shadow-sm">
                                <Sparkles size={18} className="text-nyaya-primary" />
                            </div>
                            <span className="text-2xl font-bold tracking-tight text-nyaya-text">Lumina<span className="text-nyaya-muted">.ai</span></span>
                        </div>
                        <p className="text-nyaya-muted text-base leading-relaxed max-w-sm font-medium">
                            The definitive research engine for modern law. High-performance semantic precedent matching and outcome prediction for the legal enterprise.
                        </p>
                    </div>

                    {/* Columns */}
                    {[
                        { title: "Platform", links: ["Prediction Engine", "Similarity Search", "RAG Workflows", "Pricing"] },
                        { title: "Resources", links: ["Documentation", "Legal Sources", "Blog", "Support"] },
                        { title: "Company", links: ["About Us", "Legal Scholars", "Security", "Terms of Service"] }
                    ].map((col, i) => (
                        <div key={i}>
                            <h4 className="text-nyaya-text font-bold mb-6 tracking-wide text-sm uppercase">{col.title}</h4>
                            <ul className="space-y-4 text-nyaya-muted font-medium">
                                {col.links.map(link => (
                                    <li key={link}><button onClick={onGetStarted} className="hover:text-nyaya-primary transition-colors text-left">{link}</button></li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="max-w-[88rem] mx-auto px-6 lg:px-12 mt-24 pt-8 border-t border-nyaya-border flex flex-col md:flex-row items-center justify-between text-sm text-nyaya-muted font-semibold">
                    <p>© {new Date().getFullYear()} Lumina Legal Technologies. All rights reserved.</p>
                    <div className="flex gap-6 mt-4 md:mt-0">
                        <button onClick={onGetStarted} className="hover:text-nyaya-primary transition-colors">X (Twitter)</button>
                        <button onClick={onGetStarted} className="hover:text-nyaya-primary transition-colors">LinkedIn</button>
                        <button onClick={onGetStarted} className="hover:text-nyaya-primary transition-colors">GitHub</button>
                    </div>
                </div>
            </footer>
        </div >
    );
}

// -------------------------------------------------------------
// Interactive Elite Components (Light Theme adapted)
// -------------------------------------------------------------

function InteractiveBentoCard({ className = "", children }) {
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    function handleMouseMove({ currentTarget, clientX, clientY }) {
        const { left, top } = currentTarget.getBoundingClientRect();
        mouseX.set(clientX - left);
        mouseY.set(clientY - top);
    }

    return (
        <div
            className={`relative rounded-[2rem] overflow-hidden group ${className}`}
            onMouseMove={handleMouseMove}
        >
            {/* Spotlight Hover Effect - adapted for dark mode */}
            <motion.div
                className="pointer-events-none absolute -inset-px rounded-[2rem] opacity-0 transition duration-300 group-hover:opacity-100 z-50"
                style={{
                    background: useMotionTemplate`
                        radial-gradient(
                            500px circle at ${mouseX}px ${mouseY}px,
                            rgba(0,0,0,0.03),
                            transparent 40%
                        )
                    `
                }}
            />
            {children}
        </div>
    );
}
