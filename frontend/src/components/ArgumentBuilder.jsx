import React, { useState } from 'react';
import { Gavel, AlertTriangle, Loader2, Copy, MessageSquarePlus } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

export default function ArgumentBuilder() {
    const [formData, setFormData] = useState({ issue: '', side: 'petitioner', case_ids: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);

    const handleSubmit = async () => {
        setLoading(true); setError(null); setResult(null);
        try {
            const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL || '/api'}/argument-builder`, {
                issue: formData.issue,
                side: formData.side,
                relevant_case_ids: formData.case_ids.split(',').map(s => s.trim()).filter(x => x)
            });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
        setLoading(false);
    };

    const copyText = (text) => navigator.clipboard.writeText(text);

    const sendToChat = (text) => {
        window.dispatchEvent(new CustomEvent('sendToChat', { detail: text }));
        alert("Sent to Chat! Switch to the Research Assistant tab to view.");
    };

    return (
        <div className="max-w-6xl mx-auto py-12 px-6">
            <h1 className="text-3xl font-black mb-8 flex items-center gap-3"><Gavel className="text-indigo-600" /> Argument Builder</h1>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Form */}
                <div className="bg-white rounded-2xl p-6 border shadow-sm space-y-5 h-fit">
                    <div>
                        <label className="block text-sm font-bold mb-2">Legal Issue / Dispute Summary</label>
                        <textarea 
                            className="w-full p-4 border rounded-xl resize-none ring-indigo-500 max-h-64" 
                            rows={8}
                            value={formData.issue}
                            onChange={e => setFormData({...formData, issue: e.target.value})}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-bold mb-2">Representation Side</label>
                        <select className="w-full p-3 border rounded-xl" value={formData.side} onChange={e => setFormData({...formData, side: e.target.value})}>
                            <option value="petitioner">Petitioner / Plaintiff</option>
                            <option value="respondent">Respondent / Defendant</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-bold mb-2">Relevant Case IDs (Optional)</label>
                        <input type="text" placeholder="e.g. 2024-DHC-123, SC-44" className="w-full p-3 border rounded-xl" value={formData.case_ids} onChange={e => setFormData({...formData, case_ids: e.target.value})} />
                    </div>
                    <button onClick={handleSubmit} disabled={loading || !formData.issue} className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition disabled:opacity-50">
                        {loading ? <Loader2 className="animate-spin" /> : <Gavel />} Generate Arguments
                    </button>
                    {error && <div className="text-rose-600 text-sm bg-rose-50 p-4 rounded-xl flex items-center gap-2"><AlertTriangle/>{error}</div>}
                </div>

                {/* Results Panels */}
                <div className="lg:col-span-2 space-y-6">
                    <AnimatePresence mode="wait">
                        {loading ? (
                            <div className="space-y-6">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className="bg-white border border-nyaya-border rounded-2xl p-6 shadow-sm animate-pulse space-y-4">
                                        <div className="flex justify-between items-center mb-4">
                                            <div className="h-6 w-32 bg-slate-100 rounded-full" />
                                            <div className="h-8 w-8 bg-slate-100 rounded-lg" />
                                        </div>
                                        <div className="h-4 w-full bg-slate-50 rounded-full" />
                                        <div className="h-4 w-5/6 bg-slate-50 rounded-full" />
                                        <div className="h-4 w-4/6 bg-slate-50 rounded-full" />
                                    </div>
                                ))}
                            </div>
                        ) : result ? (
                            <motion.div key="result-wrapper" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                                {Object.entries(result).map(([section, text]) => (
                                    <motion.div key={section} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-white border rounded-2xl p-6 shadow-sm">
                                        <div className="flex items-center justify-between mb-4 border-b pb-2">
                                            <h3 className="text-lg font-black uppercase tracking-wide text-indigo-900">{section}</h3>
                                            <div className="flex gap-2">
                                                <button onClick={() => copyText(text)} className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg" title="Copy"><Copy size={16} /></button>
                                                {section === 'arguments' && (
                                                    <button onClick={() => sendToChat(text)} className="p-2 bg-indigo-100 text-indigo-700 hover:bg-indigo-200 rounded-lg flex items-center gap-1" title="Send to Chat">
                                                        <MessageSquarePlus size={16} /><span className="text-xs font-bold">Send to Chat</span>
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                        <div className="text-slate-700 whitespace-pre-wrap leading-relaxed">{text}</div>
                                    </motion.div>
                                ))}
                            </motion.div>
                        ) : (
                            <div className="h-full min-h-[500px] flex flex-col items-center justify-center bg-nyaya-surface/50 border-2 border-dashed border-nyaya-border rounded-[2rem] text-center p-12">
                                <div className="w-16 h-16 bg-white border border-nyaya-border rounded-2xl flex items-center justify-center mb-6 shadow-sm text-nyaya-muted/40">
                                    <Gavel size={32} />
                                </div>
                                <h3 className="text-xl font-bold text-nyaya-text mb-2">Argument Builder</h3>
                                <p className="text-nyaya-muted max-w-sm leading-relaxed">
                                    Input your legal issue on the left to generate structured points, counter-arguments, and legal strategies.
                                </p>
                            </div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
