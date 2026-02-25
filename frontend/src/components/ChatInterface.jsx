import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Book, Loader2, Paperclip, FileText, CheckCircle2, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = 'http://localhost:8000';

export default function ChatInterface() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am Lumina Copilot. How can I help you with your legal research today?', isSystem: false }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [uploadingPdf, setUploadingPdf] = useState(false);
    const [language, setLanguage] = useState('en');
    const [jurisdiction, setJurisdiction] = useState('All');
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const textareaRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input, isSystem: false };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
        setLoading(true);

        try {
            // Format history for API (exclude system upload messages)
            const history = messages
                .filter(m => !m.isSystem)
                .map(m => ({ role: m.role, content: m.content }));

            const response = await axios.post(`${API_URL}/chat`, {
                message: userMessage.content,
                history: history,
                language: language,
                jurisdiction: jurisdiction
            });

            const aiMessage = {
                role: 'assistant',
                content: response.data.response,
                sources: response.data.sources,
                isSystem: false
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error extracting information.', isSystem: false }]);
            console.error('Chat error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handlePdfUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploadingPdf(true);
        const formData = new FormData();
        formData.append('files', file);

        try {
            await axios.post(`${API_URL}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            // Add system message to chat
            const sysMessage = {
                role: 'system',
                content: `Processed document: ${file.name}. It is now in my knowledge base. You can ask me questions about it.`,
                isSystem: true
            };
            setMessages(prev => [...prev, sysMessage]);
        } catch (error) {
            console.error('PDF upload inside chat failed:', error);
            const errMessage = {
                role: 'system',
                content: `Failed to upload ${file.name}. Please try again.`,
                isSystem: true,
                isError: true
            };
            setMessages(prev => [...prev, errMessage]);
        } finally {
            setUploadingPdf(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-7.5rem)] bg-nyaya-bg border border-nyaya-border overflow-hidden relative shadow-2xl rounded-2xl">
            {/* Ambient Background Effect */}
            <div className="absolute inset-0 bg-nyaya-accent/5 blur-[100px] pointer-events-none rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1/2 h-1/2 mix-blend-multiply opacity-20"></div>

            {/* Context & Settings Bar (Redesigned) */}
            <div className="bg-nyaya-bg/90 backdrop-blur-md border-b border-nyaya-border p-4 px-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 z-10 relative">
                <div className="flex flex-wrap items-center gap-4">
                    <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-nyaya-muted uppercase tracking-widest pl-1">Language</label>
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="bg-nyaya-surface border border-nyaya-border text-nyaya-text text-sm font-medium rounded-xl focus:ring-1 focus:ring-nyaya-primary/30 focus:border-nyaya-primary/50 block px-4 py-2 outline-none shadow-sm transition-all appearance-none pr-8 cursor-pointer"
                            style={{ backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23A1A1AA' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.5rem center', backgroundSize: '1em' }}
                        >
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="ta">Tamil</option>
                            <option value="te">Telugu</option>
                            <option value="mr">Marathi</option>
                            <option value="bn">Bengali</option>
                        </select>
                    </div>

                    <div className="hidden sm:block h-8 w-px bg-nyaya-border/50 self-end mb-1"></div>

                    <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-nyaya-muted uppercase tracking-widest pl-1">Jurisdiction Context</label>
                        <select
                            value={jurisdiction}
                            onChange={(e) => setJurisdiction(e.target.value)}
                            className="bg-nyaya-surface border border-nyaya-border text-nyaya-text text-sm font-medium rounded-xl focus:ring-1 focus:ring-nyaya-primary/30 focus:border-nyaya-primary/50 block px-4 py-2 outline-none shadow-sm transition-all appearance-none pr-8 cursor-pointer max-w-[200px] truncate"
                            style={{ backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23A1A1AA' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.5rem center', backgroundSize: '1em' }}
                        >
                            <option value="All">All Courts</option>
                            <option value="Supreme Court of India">Supreme Court</option>
                            <option value="Delhi High Court">Delhi High Court</option>
                            <option value="Bombay High Court">Bombay High Court</option>
                            <option value="Madras High Court">Madras High Court</option>
                            <option value="Calcutta High Court">Calcutta High Court</option>
                        </select>
                    </div>
                </div>

                <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-nyaya-primary/10 border border-nyaya-primary/20 text-nyaya-primary text-xs font-semibold">
                    <Bot size={14} />
                    Lumina Active
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 relative z-10 custom-scrollbar scroll-smooth">
                {messages.map((msg, idx) => (
                    <motion.div
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={idx}
                        className={`flex gap-4 w-full max-w-[95%] mx-auto ${msg.role === 'user' ? 'flex-row-reverse' : ''} ${msg.isSystem ? 'justify-center mx-auto max-w-full pt-4' : ''}`}
                    >
                        {/* System Message (Upload Confirmation) */}
                        {msg.isSystem ? (
                            <div className={`px-4 py-2.5 rounded-xl text-xs font-medium flex items-center gap-2 border shadow-sm backdrop-blur-sm ${msg.isError ? 'bg-red-50 text-red-600 border-red-200' : 'bg-green-50 text-green-700 border-green-200'}`}>
                                {msg.isError ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                                {msg.content}
                            </div>
                        ) : (
                            <>
                                {/* Avatar */}
                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm border
                                  ${msg.role === 'user'
                                        ? 'bg-nyaya-text text-nyaya-bg border-nyaya-text'
                                        : 'bg-nyaya-surface text-nyaya-primary border-nyaya-border'}`}>
                                    {msg.role === 'user' ? <User size={18} strokeWidth={2.5} /> : <Bot size={18} />}
                                </div>

                                {/* Bubble */}
                                <div className={`flex-1 min-w-0 space-y-3`}>
                                    <div className={`p-5 text-[15px] leading-relaxed shadow-sm
                                        ${msg.role === 'user'
                                            ? 'bg-nyaya-surface text-nyaya-text rounded-2xl rounded-tr-sm border border-nyaya-border/50'
                                            : 'bg-nyaya-bg text-nyaya-text border-l-2 border-l-nyaya-primary/50  pl-6 py-2' // Minimalist list view style for AI
                                        }`}>

                                        {/* Name Label for AI */}
                                        {msg.role === 'assistant' && (
                                            <div className="text-[10px] font-bold text-nyaya-primary uppercase tracking-widest mb-3 flex items-center gap-2">
                                                Lumina Copilot
                                            </div>
                                        )}

                                        {msg.role === 'assistant' ? (
                                            <div className="prose prose-sm max-w-none 
                                                prose-p:my-2 prose-p:text-nyaya-muted prose-p:leading-7
                                                prose-headings:text-nyaya-text prose-headings:font-medium prose-headings:mt-6 prose-headings:mb-3
                                                prose-strong:text-nyaya-text
                                                prose-ul:my-3 prose-li:text-nyaya-muted
                                                prose-a:text-nyaya-primary prose-a:no-underline hover:prose-a:underline
                                                prose-code:bg-nyaya-surface prose-code:text-nyaya-primary prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:border prose-code:border-nyaya-border/50">
                                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                                            </div>
                                        ) : (
                                            <p className="whitespace-pre-wrap font-medium">{msg.content}</p>
                                        )}
                                    </div>

                                    {/* Sources */}
                                    {msg.sources && msg.sources.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mt-3 p-3 bg-nyaya-surface/50 rounded-xl border border-nyaya-border/30">
                                            <div className="w-full text-[10px] font-bold text-nyaya-muted uppercase tracking-widest mb-1 pl-1">Sources Cited</div>
                                            {msg.sources.map((src, i) => (
                                                <span key={i} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-nyaya-bg border border-nyaya-border rounded-lg text-[11px] font-semibold tracking-wide text-nyaya-muted shadow-sm hover:border-nyaya-primary/30 transition-colors cursor-default">
                                                    <Book size={12} className="text-nyaya-primary" />
                                                    {src.type}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </>
                        )}
                    </motion.div>
                ))}

                {loading && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 w-full max-w-[95%] mx-auto">
                        <div className="w-10 h-10 rounded-xl bg-nyaya-surface text-nyaya-primary flex items-center justify-center shrink-0 border border-nyaya-border shadow-sm">
                            <Bot size={18} />
                        </div>
                        <div className="border-l-2 border-l-nyaya-primary/30 pl-6 py-4 flex items-center min-w-[100px]">
                            <div className="flex gap-2">
                                <motion.div className="w-2 h-2 rounded-full bg-nyaya-primary/60" animate={{ y: [0, -5, 0], opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1, delay: 0 }} />
                                <motion.div className="w-2 h-2 rounded-full bg-nyaya-primary/60" animate={{ y: [0, -5, 0], opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} />
                                <motion.div className="w-2 h-2 rounded-full bg-nyaya-primary/60" animate={{ y: [0, -5, 0], opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} />
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} className="h-4" />
            </div>

            {/* Input Handling (Redesigned) */}
            <div className="p-2 md:p-3 border-t border-nyaya-border bg-nyaya-bg/95 backdrop-blur-xl relative z-10">
                <div className="w-full max-w-[98%] mx-auto flex gap-2 items-end relative bg-nyaya-surface border border-nyaya-border rounded-2xl p-1.5 focus-within:ring-1 focus-within:ring-nyaya-primary/50 focus-within:border-nyaya-primary/50 transition-all shadow-inner">

                    {/* Inline PDF Upload */}
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handlePdfUpload}
                        accept=".pdf"
                        className="hidden"
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={uploadingPdf}
                        className="bg-nyaya-bg text-nyaya-muted p-2.5 rounded-xl hover:bg-nyaya-border hover:text-nyaya-text disabled:opacity-50 disabled:cursor-not-allowed transition-colors border border-nyaya-border mb-0.5 shrink-0"
                        title="Upload PDF to Knowledge Base"
                    >
                        {uploadingPdf ? <Loader2 size={18} className="animate-spin" /> : <Paperclip size={18} />}
                    </button>

                    <textarea
                        ref={textareaRef}
                        rows="1"
                        value={input}
                        onChange={(e) => {
                            setInput(e.target.value);
                            e.target.style.height = 'auto';
                            e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
                        }}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                        placeholder="Draft a legal memo, search precedent, or query a document..."
                        className="flex-1 px-3 py-2.5 bg-transparent focus:outline-none resize-none text-[14px] text-nyaya-text placeholder-nyaya-muted/60 max-h-[150px] overflow-y-auto custom-scrollbar leading-relaxed"
                        style={{ minHeight: '42px' }}
                    />

                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md p-2.5 rounded-xl font-bold hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:from-nyaya-border disabled:to-nyaya-border disabled:text-nyaya-muted transition-all mb-0.5 shrink-0 flex items-center justify-center group"
                    >
                        <Send size={18} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                    </button>
                </div>

                <div className="text-center mt-3 flex items-center justify-center gap-2">
                    <AlertTriangle size={12} className="text-nyaya-muted/70" />
                    <span className="text-[11px] text-nyaya-muted/70 font-medium tracking-wide">
                        Lumina is an AI assistant. May produce inaccurate information. Verify all legal citations.
                    </span>
                </div>
            </div>
        </div>
    );
}
