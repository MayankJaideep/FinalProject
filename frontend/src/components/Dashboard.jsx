import React, { useState, useEffect } from 'react';
import { Scale, FileText, Activity, AlertTriangle, Loader2, ChevronRight, Gavel, Search, ArrowUpRight, ShieldCheck, Zap, TrendingUp, History, Section } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const MOCK_RESULTS = {
    analytics: {
        winRate: 65,
        avgDuration: "14 months",
        judgeTendency: "Strict",
        outcomes: [
            { name: 'Allowance', value: 65, color: '#4F46E5' }, // Indigo
            { name: 'Dismissal', value: 25, color: '#E11D48' }, // Rose
            { name: 'Settlement', value: 10, color: '#94A3B8' }, // Slate
        ]
    },
    cases: [
        {
            id: 1,
            name: "Mehta v. Union of India",
            year: 2024,
            court: "Delhi High Court",
            match: 94,
            outcome: "Allowance",
            factSimilarity: "High",
            legalSimilarity: "High",
            tags: ["Bail", "Medical Grounds", "PMLA"],
            reason: "The court heavily weighed the medical documentation provided by the defense, establishing a strong precedent that age and specific medical conditions override standard PMLA bail restrictions."
        },
        {
            id: 2,
            name: "Suresh Trading vs State of Maharashtra",
            year: 2023,
            court: "Supreme Court",
            match: 88,
            outcome: "Dismissal",
            factSimilarity: "Medium",
            legalSimilarity: "High",
            tags: ["Bail", "Economic Offense", "Flight Risk"],
            reason: "While the medical grounds were similar, the court dismissed the application due to a lack of corroborating chronologies and the applicant being deemed a severe flight risk."
        }
    ]
};

const LEGAL_SECTIONS = [
    "Section 138 NI Act",
    "Section 420 IPC",
    "IBC 2016",
    "Contract Act",
    "PMLA",
    "Arbitration Act"
];

// Layout sections
const SECTIONS = {
    INPUT: 'input',
    LOADING: 'loading',
    RESULTS: 'results'
};

export default function Dashboard() {
    const [formData, setFormData] = useState({
        description: '',
        court: 'Delhi High Court',
        judge: '',
        sections: []
    });

    const [currentStep, setCurrentStep] = useState(SECTIONS.INPUT);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    // Auto-scroll to top when step changes
    useEffect(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, [currentStep]);

    const toggleSection = (sec) => {
        setFormData(prev => ({
            ...prev,
            sections: prev.sections.includes(sec)
                ? prev.sections.filter(s => s !== sec)
                : [...prev.sections, sec]
        }));
    };

    const handleAnalyze = async () => {
        if (!formData.description) return;
        setCurrentStep(SECTIONS.LOADING);
        setError(null);

        try {
            // Using the new /predict endpoint which consolidates ML scores, SHAP, and LLM explanation
            const response = await axios.post(`/api/predict`, {
                description: formData.description,
                court: formData.court,
                judge: formData.judge,
                case_type: formData.sections[0] || "Commercial"
            });

            // The consolidated response is in response.data.result
            setResults(response.data.result);
            setCurrentStep(SECTIONS.RESULTS);
        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.response?.data?.detail || 'Failed to analyze cases. Make sure the backend is running.');
            setCurrentStep(SECTIONS.INPUT);
        }
    };

    const handleReset = () => {
        setCurrentStep(SECTIONS.INPUT);
        setResults(null);
        setError(null);
        setFormData({
            description: '',
            court: 'Delhi High Court',
            judge: '',
            sections: []
        });
    };

    return (
        <div className="w-full max-w-5xl mx-auto py-12 px-6 lg:px-8 min-h-screen relative z-10 pb-32">

            {/* Header Area */}
            <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-nyaya-border pb-8">
                <div>
                    <h1 className="text-4xl font-black text-nyaya-text tracking-tight mb-3">Precedent Engine</h1>
                    <p className="text-nyaya-muted font-medium max-w-2xl text-[16px] leading-relaxed">Input your case parameters below to semantically search across millions of records. The engine will identify the most comparable historical cases and extract empirical strategies.</p>
                </div>
                {currentStep === SECTIONS.RESULTS && (
                    <button
                        onClick={handleReset}
                        className="px-6 py-3 bg-nyaya-surface border border-nyaya-border rounded-xl text-nyaya-text font-bold text-sm shadow-sm hover:bg-nyaya-bg transition-colors whitespace-nowrap"
                    >
                        New Analysis
                    </button>
                )}
            </div>

            <AnimatePresence mode="wait">

                {/* ------------------------------------------------------------------------- */}
                {/* STEP 1: INPUT FORM (Clean, Single Column) */}
                {/* ------------------------------------------------------------------------- */}
                {currentStep === SECTIONS.INPUT && (
                    <motion.div
                        key="input"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="space-y-10"
                    >
                        {!formData.description && !error && (
                            <div className="flex flex-col items-center justify-center text-center py-12 animate-in fade-in">
                                <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-6 shadow-sm border border-indigo-100">
                                    <Scale size={32} />
                                </div>
                                <h2 className="text-xl font-bold text-nyaya-text mb-2">Prediction Dashboard</h2>
                                <p className="text-nyaya-muted max-w-sm">Enter a case description to predict its likely outcome</p>
                            </div>
                        )}
                        {error && (
                            <div className="bg-rose-50 border border-rose-200 text-rose-700 px-6 py-4 rounded-2xl flex items-center justify-between shadow-sm">
                                <div className="flex items-center gap-3">
                                    <AlertTriangle size={20} className="text-rose-600" />
                                    <span className="font-bold text-[14px]">{error}</span>
                                </div>
                                <button onClick={() => setError(null)} className="text-rose-400 hover:text-rose-600">
                                    &times;
                                </button>
                            </div>
                        )}

                        {/* Primary Input Container */}
                        <div className="bg-nyaya-surface border border-nyaya-border rounded-[2rem] p-10 shadow-sm relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50/50 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>

                            <h2 className="text-xl font-bold text-nyaya-text mb-8 flex items-center gap-3">
                                <FileText size={24} className="text-indigo-600" />
                                1. Describe the Facts
                            </h2>

                            <div className="space-y-4 relative z-10">
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    rows={8}
                                    className="w-full p-6 rounded-2xl bg-nyaya-bg/50 border border-nyaya-border text-[16px] text-nyaya-text focus:outline-none focus:border-indigo-400 focus:ring-[4px] focus:ring-indigo-500/10 resize-none transition-all placeholder:text-nyaya-muted/60 custom-scrollbar leading-relaxed"
                                    placeholder="Detail the chronological events, key arguments, and context of the dispute here..."
                                />
                                <div className="flex justify-end text-[13px] font-semibold text-nyaya-muted">
                                    {formData.description.length} characters (minimum 50 recommended)
                                </div>
                            </div>
                        </div>

                        {/* Secondary Parameters Container */}
                        <div className="bg-nyaya-surface border border-nyaya-border rounded-[2rem] p-10 shadow-sm">
                            <h2 className="text-xl font-bold text-nyaya-text mb-8 flex items-center gap-3">
                                <Scale size={24} className="text-indigo-600" />
                                2. Jurisdiction & Context
                            </h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-3">
                                    <label className="text-[14px] font-bold text-nyaya-text tracking-wide">Forum</label>
                                    <div className="relative">
                                        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-nyaya-muted" />
                                        <select
                                            value={formData.court}
                                            onChange={(e) => setFormData({ ...formData, court: e.target.value })}
                                            className="w-full py-4 pl-12 pr-4 rounded-2xl bg-nyaya-bg/50 border border-nyaya-border text-[15px] font-medium text-nyaya-text focus:outline-none focus:border-indigo-400 focus:ring-[4px] focus:ring-indigo-500/10 transition-all appearance-none cursor-pointer"
                                        >
                                            <option value="Supreme Court">Supreme Court of India</option>
                                            <option value="Delhi High Court">Delhi High Court</option>
                                            <option value="Bombay High Court">Bombay High Court</option>
                                            <option value="NCLT">National Company Law Tribunal</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <label className="text-[14px] font-bold text-nyaya-text tracking-wide">Presiding Coram (Optional)</label>
                                    <input
                                        type="text"
                                        value={formData.judge}
                                        onChange={(e) => setFormData({ ...formData, judge: e.target.value })}
                                        placeholder="e.g. Hon'ble Justice D.Y. Chandrachud"
                                        className="w-full p-4 rounded-2xl bg-nyaya-bg/50 border border-nyaya-border text-[15px] font-medium text-nyaya-text focus:outline-none focus:border-indigo-400 focus:ring-[4px] focus:ring-indigo-500/10 transition-all placeholder:text-nyaya-muted/60"
                                    />
                                </div>
                            </div>

                            <div className="mt-10 space-y-4 border-t border-nyaya-border/50 pt-8">
                                <label className="text-[14px] font-bold text-nyaya-text tracking-wide flex items-center gap-2">
                                    Relevant Acts & Sections
                                    <span className="text-[11px] font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-full">{formData.sections.length} Selected</span>
                                </label>
                                <div className="flex flex-wrap gap-3">
                                    {LEGAL_SECTIONS.map(sec => (
                                        <button
                                            key={sec}
                                            onClick={() => toggleSection(sec)}
                                            className={`px-5 py-3 rounded-xl text-[14px] font-bold transition-all border ${formData.sections.includes(sec)
                                                ? 'bg-nyaya-text text-nyaya-surface border-nyaya-text shadow-md hover:-translate-y-0.5'
                                                : 'bg-nyaya-surface text-nyaya-muted border-nyaya-border hover:border-indigo-300 hover:text-indigo-600'
                                                }`}
                                        >
                                            {sec}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Action Bar */}
                        <div className="flex justify-end pt-4">
                            <button
                                onClick={handleAnalyze}
                                disabled={!formData.description || formData.description.length < 10}
                                className="px-10 py-5 bg-[#4F46E5] hover:bg-[#4338CA] text-white rounded-2xl font-black text-[16px] transition-all shadow-xl hover:shadow-2xl hover:-translate-y-1 active:scale-95 disabled:opacity-50 disabled:shadow-none disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-3 w-full md:w-auto min-w-[300px]"
                            >
                                <Zap size={20} />
                                <span>Run Engine Analysis</span>
                                <ChevronRight size={20} className="ml-2 opacity-50" />
                            </button>
                        </div>
                    </motion.div>
                )}


                {/* ------------------------------------------------------------------------- */}
                {currentStep === SECTIONS.LOADING && (
                    <motion.div
                        key="loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="space-y-6"
                    >
                        {/* Skeleton Header */}
                        <div className="bg-nyaya-surface border border-nyaya-border rounded-[2rem] p-10 shadow-sm space-y-4 animate-pulse">
                            <div className="h-4 w-32 bg-nyaya-border rounded-full" />
                            <div className="h-8 w-56 bg-nyaya-border rounded-full" />
                            <div className="h-4 w-full bg-nyaya-border rounded-full" />
                            <div className="h-4 w-4/5 bg-nyaya-border rounded-full" />
                        </div>
                        {/* Skeleton Stats Row */}
                        <div className="grid grid-cols-3 gap-6">
                            {[...Array(3)].map((_, i) => (
                                <div key={i} className="bg-nyaya-surface border border-nyaya-border rounded-2xl p-6 animate-pulse space-y-4">
                                    <div className="h-4 w-24 bg-nyaya-border rounded-full" />
                                    <div className="h-8 w-16 bg-nyaya-border rounded-full" />
                                </div>
                            ))}
                        </div>
                        {/* Skeleton Case Cards */}
                        {[...Array(2)].map((_, i) => (
                            <div key={i} className="bg-nyaya-surface border border-nyaya-border rounded-2xl p-8 animate-pulse space-y-4">
                                <div className="flex items-center justify-between">
                                    <div className="h-5 w-48 bg-nyaya-border rounded-full" />
                                    <div className="h-6 w-16 bg-nyaya-border rounded-full" />
                                </div>
                                <div className="h-4 w-full bg-nyaya-border rounded-full" />
                                <div className="h-4 w-3/4 bg-nyaya-border rounded-full" />
                                <div className="h-4 w-1/2 bg-nyaya-border rounded-full" />
                            </div>
                        ))}
                    </motion.div>
                )}


                {/* ------------------------------------------------------------------------- */}
                {/* STEP 3: FULL RESULTS (Scrolling Stack) */}
                {/* ------------------------------------------------------------------------- */}
                {currentStep === SECTIONS.RESULTS && (
                    <motion.div
                        key="results"
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-12"
                    >
                        {/* Summary Bar */}
                        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 flex items-center justify-between shadow-sm">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center">
                                    <ShieldCheck size={24} className="text-emerald-600" />
                                </div>
                                <div>
                                    <h3 className="text-[16px] font-black text-emerald-900 leading-tight">Analysis Complete</h3>
                                    <p className="text-[14px] font-semibold text-emerald-700/80">Computed against High Court and Supreme Court registries.</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <span className="block text-3xl font-black text-emerald-600 leading-none">{results.cases.length}</span>
                                <span className="text-[12px] font-bold text-emerald-700/60 uppercase tracking-widest">Precedents Found</span>
                            </div>
                        </div>

                        {/* ROW 1: MACRO INTELLIGENCE */}
                        <section className="space-y-6">
                            <h2 className="text-2xl font-black text-nyaya-text flex items-center gap-3">
                                <TrendingUp size={24} className="text-indigo-600" />
                                1. Macro Intelligence & Environment
                            </h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {/* Widget A: Donut */}
                                <div className="bg-nyaya-surface border border-nyaya-border rounded-[2rem] p-10 shadow-sm flex flex-col items-center">
                                    <h3 className="text-[16px] font-bold text-nyaya-text mb-8 w-full">Historical Outcome Distribution</h3>
                                    <div style={{ width: '100%', height: 300 }} className="relative flex items-center justify-center mb-8">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <PieChart>
                                                <Pie
                                                    data={results.analytics.outcomes}
                                                    cx="50%"
                                                    cy="50%"
                                                    innerRadius={80}
                                                    outerRadius={110}
                                                    paddingAngle={4}
                                                    dataKey="value"
                                                    stroke="none"
                                                    cornerRadius={8}
                                                >
                                                    {results.analytics.outcomes.map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                                    ))}
                                                </Pie>
                                                <Tooltip
                                                    formatter={(value) => `${value}%`}
                                                    contentStyle={{ borderRadius: '12px', border: '1px solid #E0E7FF', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', padding: '16px', fontWeight: 'bold' }}
                                                    itemStyle={{ fontWeight: 'bold', color: '#1E1B4B' }}
                                                />
                                            </PieChart>
                                        </ResponsiveContainer>
                                        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                                            <span className="text-5xl font-black text-nyaya-text mb-2">{results.analytics.winRate}%</span>
                                            <span className="text-[12px] uppercase tracking-widest font-bold text-nyaya-muted">Allowance Rate</span>
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap items-center justify-center gap-6 w-full pt-6 border-t border-nyaya-border/50">
                                        {results.analytics.outcomes.map(item => (
                                            <div key={item.name} className="flex items-center gap-2">
                                                <div className="w-4 h-4 rounded-full shadow-sm" style={{ backgroundColor: item.color }}></div>
                                                <span className="text-[14px] font-bold text-nyaya-text">{item.name}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Widget B: Environmental Analytics */}
                                <div className="bg-nyaya-surface border border-nyaya-border rounded-[2rem] p-10 shadow-sm flex flex-col justify-between">
                                    <div>
                                        <h3 className="text-[16px] font-bold text-nyaya-text mb-8">Forum Analytics (Delhi High Court)</h3>

                                        <div className="mb-10 p-6 bg-nyaya-bg/50 rounded-2xl border border-nyaya-border/50">
                                            <div className="flex justify-between items-end mb-4">
                                                <span className="text-[13px] font-bold text-nyaya-muted uppercase tracking-wider">Average Resolution Time</span>
                                                <span className="text-3xl font-black text-nyaya-text">{results.analytics.avgDuration}</span>
                                            </div>
                                            <div className="w-full bg-nyaya-surface rounded-full h-4 mb-3 border border-nyaya-border overflow-hidden shadow-inner">
                                                <div className="bg-slate-400 h-full rounded-full" style={{ width: '60%' }}></div>
                                            </div>
                                            <p className="text-[13px] font-medium text-nyaya-muted">Based on analogous filings in the past 5 years.</p>
                                        </div>

                                        <div className="p-6 bg-nyaya-bg/50 rounded-2xl border border-nyaya-border/50">
                                            <div className="flex justify-between items-end mb-4">
                                                <span className="text-[13px] font-bold text-nyaya-muted uppercase tracking-wider flex items-center gap-2">
                                                    Coram Tendency
                                                    {formData.judge && <span className="bg-nyaya-surface text-nyaya-text px-2 py-0.5 rounded-md border border-nyaya-border">for {formData.judge}</span>}
                                                </span>
                                                <span className="text-3xl font-black text-nyaya-text">32%</span>
                                            </div>
                                            <div className="w-full bg-nyaya-surface rounded-full h-4 mb-4 border border-nyaya-border overflow-hidden shadow-inner flex">
                                                <div className="bg-[#4F46E5] h-full transition-all" style={{ width: '32%' }}></div>
                                                <div className="bg-[#E11D48] h-full transition-all" style={{ width: '68%' }}></div>
                                            </div>
                                            <div className="flex justify-between text-[12px] font-bold tracking-wider uppercase">
                                                <span className="text-indigo-600">Pro-Allowance (32%)</span>
                                                <span className="text-rose-600">Strict (68%)</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* ROW 1.5: AI STRATEGIC INTELLIGENCE */}
                        {results.llm_explanation && (
                            <section className="space-y-6">
                                <h2 className="text-2xl font-black text-nyaya-text flex items-center gap-3">
                                    <ShieldCheck size={24} className="text-indigo-600" />
                                    AI Strategic Intelligence
                                </h2>
                                <div className="bg-[#1E1B4B] text-white rounded-[2rem] p-10 shadow-xl relative overflow-hidden group">
                                    <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
                                    <div className="flex items-start gap-6 relative z-10">
                                        <div className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center shrink-0 shadow-lg border border-indigo-400/30">
                                            <Activity size={28} className="text-white" />
                                        </div>
                                        <div className="space-y-4">
                                            <div className="flex items-center gap-3">
                                                <span className="text-[12px] font-black uppercase tracking-[0.2em] text-indigo-300">Strategic Brief</span>
                                                <div className="h-px w-12 bg-indigo-500/30"></div>
                                                <span className="text-[11px] font-bold text-indigo-400 bg-indigo-900/50 px-2 py-0.5 rounded border border-indigo-800">Powered by {results.model}</span>
                                            </div>
                                            <p className="text-[17px] leading-relaxed font-medium text-indigo-50 italic">
                                                {results.llm_explanation}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </section>
                        )}

                        {/* SHAP EXPLAINABILITY PANEL */}
                        {results.explanation && results.explanation.top_features && (
                            <>
                            <div className="w-full h-px bg-nyaya-border my-8"></div>
                            <section className="space-y-6">
                                <h2 className="text-2xl font-black text-nyaya-text flex items-center gap-3">
                                    <Activity size={24} className="text-indigo-600" />
                                    Why this prediction? (XAI)
                                </h2>
                                
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    {/* Feature Importance (SHAP) */}
                                    <div className="bg-nyaya-surface border border-nyaya-border rounded-[2rem] p-10 shadow-sm flex flex-col">
                                        <h3 className="text-[16px] font-bold text-nyaya-text mb-2">SHAP Feature Contributions</h3>
                                        <p className="text-sm text-nyaya-muted mb-6">Factors driving the stacking model's outcome prediction</p>
                                        
                                        <div className="flex-1 min-h-[250px]">
                                            <ResponsiveContainer width="100%" height={250}>
                                                <BarChart data={results.explanation.top_features} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                                    <XAxis type="number" />
                                                    <YAxis dataKey="feature" type="category" width={120} tick={{ fontSize: 12 }} />
                                                    <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{ borderRadius: '8px' }} />
                                                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                                        {results.explanation.top_features.map((entry, index) => (
                                                            <Cell key={`cell-${index}`} fill={entry.direction === 'positive' ? '#4F46E5' : '#E11D48'} />
                                                        ))}
                                                    </Bar>
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </div>
                                    </div>
                                    
                                    {/* Confidence Band */}
                                    <div className="bg-nyaya-surface border border-nyaya-border rounded-[2rem] p-10 shadow-sm flex flex-col justify-center">
                                         <h3 className="text-[16px] font-bold text-nyaya-text mb-2">Confidence Band</h3>
                                         <p className="text-sm text-nyaya-muted mb-8">Empirical probability range</p>
                                         
                                         <div className="relative pt-6 pb-2">
                                            <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden">
                                                <div 
                                                    className="h-full bg-indigo-500/30 absolute rounded-full border border-indigo-500/50"
                                                    style={{ 
                                                        left: `${results.explanation.confidence_band.low * 100}%`,
                                                        width: `${(results.explanation.confidence_band.high - results.explanation.confidence_band.low) * 100}%` 
                                                    }}
                                                />
                                            </div>
                                            
                                            <div className="absolute top-0 flex flex-col items-center" style={{ left: `${results.explanation.confidence_band.low * 100}%`, transform: 'translateX(-50%)' }}>
                                                <span className="text-xs font-bold text-slate-500 mb-1">Low</span>
                                                <div className="h-4 w-px bg-slate-400" />
                                            </div>
                                            
                                            <div className="absolute top-0 flex flex-col items-center" style={{ left: `${results.explanation.confidence_band.high * 100}%`, transform: 'translateX(-50%)' }}>
                                                <span className="text-xs font-bold text-slate-500 mb-1">High</span>
                                                <div className="h-4 w-px bg-slate-400" />
                                            </div>
                                            
                                            <div className="flex justify-between mt-4 text-sm font-bold text-nyaya-text">
                                                <span>{Math.round(results.explanation.confidence_band.low * 100)}%</span>
                                                <span>{Math.round(results.explanation.confidence_band.high * 100)}%</span>
                                            </div>
                                         </div>
                                    </div>
                                </div>
                            </section>
                            </>
                        )}
                        
                        <div className="w-full h-px bg-nyaya-border my-8"></div>

                        {/* ROW 2: COMPARABLE PRECEDENTS */}
                        <section className="space-y-6">
                            <h2 className="text-2xl font-black text-nyaya-text flex items-center justify-between">
                                <span className="flex items-center gap-3">
                                    <History size={24} className="text-indigo-600" />
                                    2. Applicable Precedents
                                </span>
                            </h2>

                            <div className="space-y-6">
                                {results.cases.slice(0, 3).map(item => (
                                    <div key={item.id} className="bg-nyaya-surface border border-nyaya-border rounded-[2rem] p-8 shadow-sm hover:shadow-lg transition-all duration-300 relative group overflow-hidden">

                                        {/* Top Header */}
                                        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8 border-b border-nyaya-border pb-6">
                                            <div className="space-y-2">
                                                <h3 className="text-xl font-black text-nyaya-text leading-tight group-hover:text-indigo-600 transition-colors cursor-pointer">
                                                    {typeof item.name === 'object' ? `${item.name.petitioner} vs ${item.name.respondent}` : item.name}
                                                </h3>
                                                <div className="flex flex-wrap items-center gap-4 text-[14px] font-bold text-nyaya-muted">
                                                    <span className="flex items-center gap-1.5"><Gavel size={16} /> {item.court}</span>
                                                    <span className="opacity-50">•</span>
                                                    <span>{item.year}</span>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-4 md:flex-col md:items-end md:gap-3 shrink-0">
                                                <div className="bg-indigo-50 border border-indigo-100 px-4 py-2 rounded-xl flex items-center gap-2">
                                                    <Zap size={16} className="text-indigo-700" />
                                                    <span className="text-[14px] font-black text-indigo-800">{item.match}% Semantic Match</span>
                                                </div>
                                                <span className={`px-4 py-2 rounded-xl text-[13px] font-black uppercase tracking-widest border
                                                    ${item.outcome === 'Allowance' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                                                        item.outcome === 'Dismissal' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                                                            'bg-slate-100 text-slate-700 border-slate-300'}`}>
                                                    {item.outcome}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 mb-8">
                                            {/* Left: Metrics & Tags */}
                                            <div className="md:col-span-4 space-y-6 border-r border-nyaya-border/50 pr-6">
                                                <div className="space-y-4">
                                                    <div className="bg-nyaya-bg rounded-xl p-4 border border-nyaya-border/50">
                                                        <div className="text-[12px] font-bold text-nyaya-muted uppercase tracking-wider mb-2">Factual Alignment</div>
                                                        <div className="text-[16px] font-black text-nyaya-text">{item.factSimilarity}</div>
                                                    </div>
                                                    <div className="bg-nyaya-bg rounded-xl p-4 border border-nyaya-border/50">
                                                        <div className="text-[12px] font-bold text-nyaya-muted uppercase tracking-wider mb-2">Legal Principle</div>
                                                        <div className="text-[16px] font-black text-nyaya-text">{item.legalSimilarity}</div>
                                                    </div>
                                                </div>

                                                <div className="space-y-3 pt-2">
                                                    <div className="text-[12px] font-bold text-nyaya-muted uppercase tracking-wider">Identified Clusters</div>
                                                    <div className="flex flex-wrap gap-2">
                                                        {item.tags.map(tag => (
                                                            <span key={tag} className="text-[12px] font-bold text-nyaya-text bg-white border border-nyaya-border px-3 py-1.5 rounded-lg shadow-sm">
                                                                {tag}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Right: Synthesis */}
                                            <div className="md:col-span-8 flex flex-col justify-center">
                                                <div className="flex items-center gap-2 mb-4">
                                                    <Activity size={18} className="text-indigo-600" />
                                                    <h4 className="text-[14px] font-black text-nyaya-text tracking-wide uppercase">AI Extracted Ratio Decidendi</h4>
                                                </div>
                                                <p className="text-[16px] text-nyaya-text leading-relaxed font-medium bg-indigo-50/30 p-6 rounded-2xl border border-indigo-100 italic">
                                                    "{item.reason}"
                                                </p>

                                                <div className="mt-8 flex justify-end">
                                                    <button className="h-12 px-6 rounded-xl text-[14px] font-black text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-100 flex items-center gap-2 transition-all hover:shadow-md">
                                                        Open Full Source <ArrowUpRight size={18} />
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
