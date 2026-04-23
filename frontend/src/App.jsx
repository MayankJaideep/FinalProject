import React, { useState, useEffect } from 'react';
import { MessageSquare, Upload, Clock, Gavel, Scale } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import ChatInterface from './components/ChatInterface';
import PDFUploader from './components/PDFUploader';
import Chronology from './components/Chronology';
import LandingPage from './components/LandingPage';
import ArgumentBuilder from './components/ArgumentBuilder';
import ErrorBoundary from './components/ErrorBoundary';

// Global Axios Configuration for Authentication
const API_KEY = 'development'; // This should ideally come from env, but matches backend default
axios.defaults.headers.common['Authorization'] = `Bearer ${API_KEY}`;
axios.defaults.headers.common['X-API-Key'] = API_KEY;

function App() {
  const [activeTab, setActiveTab] = useState('landing');

  const tabs = [
    { id: 'chat', label: 'Research Assistant', icon: MessageSquare },
    { id: 'chronology', label: 'Case Timeline', icon: Clock },
    { id: 'upload', label: 'Knowledge Base', icon: Upload },
    { id: 'argument', label: 'Argument Builder', icon: Gavel },
  ];

  const [health, setHealth] = useState({
    status: 'checking',
    vector_db: 'checking',
    bm25_loaded: false,
    ml_model_loaded: false,
    docs_indexed: 0,
    llm: 'checking'
  });

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const base = import.meta.env.VITE_API_BASE_URL || '/api';
        const res = await axios.get(`${base}/health`);
        setHealth(res.data);
      } catch (err) {
        setHealth(prev => ({ ...prev, status: 'error' }));
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (activeTab === 'landing') {
    return <LandingPage onGetStarted={() => setActiveTab('chat')} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50/80 via-white to-purple-50/80 text-nyaya-text font-sans selection:bg-nyaya-accent/30 selection:text-white">
      {/* Sidebar / Navigation */}
      <div className="fixed top-0 left-0 h-full w-72 bg-gradient-to-b from-nyaya-surface to-indigo-50/50 border-r border-nyaya-border shadow-[4px_0_24px_rgba(0,0,0,0.5)] z-30 flex flex-col">
        <div className="p-8 border-b border-nyaya-border/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-nyaya-text flex items-center justify-center shadow-glow">
              <Scale size={18} className="text-nyaya-bg" />
            </div>
            <h1 className="text-xl font-black tracking-tight text-nyaya-text">
              Lumina<span className="text-nyaya-muted">.ai</span>
            </h1>
          </div>
          <p className="text-[11px] font-bold uppercase tracking-widest text-nyaya-muted/70 mt-3">Copilot Engine</p>
        </div>

        <nav className="flex-1 p-5 space-y-2.5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all duration-300 relative group
                  ${isActive
                    ? 'bg-nyaya-bg border border-nyaya-border/50 text-nyaya-text shadow-sm'
                    : 'text-nyaya-muted hover:bg-nyaya-bg hover:text-nyaya-text border border-transparent hover:border-nyaya-border/30'
                  }`}
              >
                <Icon size={20} className={isActive ? 'text-nyaya-primary' : 'text-nyaya-muted group-hover:text-nyaya-primary transition-colors'} />
                <span className={`text-[15px] ${isActive ? 'font-bold' : 'font-medium'}`}>{tab.label}</span>
                {isActive && (
                  <motion.div layoutId="activeTabIndicator" className="absolute left-0 w-1 h-8 bg-nyaya-primary rounded-r-full shadow-glow" />
                )}
              </button>
            );
          })}
        </nav>

        <div className="p-5 border-t border-nyaya-border/50">
          <div className="bg-nyaya-bg rounded-2xl p-4 text-[13px] text-nyaya-muted font-medium border border-nyaya-border/50 shadow-inner">
            <div className="flex items-center justify-between mb-3">
              <span className="text-nyaya-muted/80">System Status</span>
              <span className={`flex items-center gap-1.5 font-bold text-[10px] uppercase tracking-widest px-2 py-1 rounded-md border ${health.status === 'ok' ? 'text-emerald-600 bg-emerald-50 border-emerald-200' : (health.status === 'checking' ? 'text-amber-600 bg-amber-50 border-amber-200' : 'text-rose-600 bg-rose-50 border-rose-200')}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${health.status === 'ok' ? 'bg-emerald-500 animate-pulse' : (health.status === 'checking' ? 'bg-amber-500 animate-pulse' : 'bg-rose-500')} shadow-sm`}></span>
                {health.status === 'ok' ? 'Active' : (health.status === 'checking' ? 'Connecting...' : 'Offline')}
              </span>
            </div>
            
            <AnimatePresence mode="popLayout">
              <motion.div className="space-y-2 mt-2" layout>
                {[
                  { label: "Vector DB", val: health.vector_db, isGood: health.vector_db === 'milvus_lite' || health.vector_db === 'connected' },
                  { label: "LLM Provider", val: health.llm, isGood: health.llm !== 'checking' && health.llm !== 'unavailable' && health.llm !== 'error' },
                  { label: "BM25 Index", val: health.bm25_loaded ? 'Loaded' : 'Waiting', isGood: health.bm25_loaded },
                  { label: "Predictive Model", val: health.ml_model_loaded ? 'Ready' : 'Offline', isGood: health.ml_model_loaded }
                ].map(item => (
                  <motion.div key={item.label} initial={{opacity:0}} animate={{opacity:1}} className="flex items-center justify-between text-[11px]">
                    <span className="text-nyaya-muted/70 flex items-center gap-1.5">
                      <div className={`w-1.5 h-1.5 rounded-full ${health.status === 'checking' ? 'bg-amber-400' : (item.isGood ? 'bg-emerald-400' : 'bg-rose-400')}`}></div>
                      {item.label}
                    </span>
                    <span className="text-nyaya-text capitalize">{item.val}</span>
                  </motion.div>
                ))}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="pl-72 min-h-screen relative flex flex-col bg-transparent">
        <header className="sticky top-0 bg-white/60 backdrop-blur-xl border-b border-nyaya-border h-20 flex items-center px-10 z-20">
          <h2 className="text-xl font-bold text-nyaya-text tracking-tight">
            {tabs.find(t => t.id === activeTab)?.label}
          </h2>
        </header>

        <main className={`flex-1 max-w-[90rem] mx-auto w-full relative ${activeTab === 'chat' ? 'p-4 lg:p-6' : 'p-8 lg:p-10'}`}>
          <div className="absolute top-[-10%] right-[-5%] w-[40vw] h-[40vw] rounded-full bg-nyaya-accent/10 blur-[120px] mix-blend-multiply pointer-events-none" />
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, scale: 0.98, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.98, y: -10 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            >
              <ErrorBoundary>
                {activeTab === 'chat' && <ChatInterface />}
                {activeTab === 'chronology' && <Chronology />}
                {activeTab === 'upload' && <PDFUploader />}
                {activeTab === 'argument' && <ArgumentBuilder />}
              </ErrorBoundary>
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

export default App;
