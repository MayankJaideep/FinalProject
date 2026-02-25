import React, { useState } from 'react';
import { LayoutDashboard, MessageSquare, BookOpen, Upload, Clock, Scale } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatInterface from './components/ChatInterface';
import Dashboard from './components/Dashboard';
import PDFUploader from './components/PDFUploader';
import Chronology from './components/Chronology';
import LandingPage from './components/LandingPage';

function App() {
  const [activeTab, setActiveTab] = useState('landing');

  const tabs = [
    { id: 'chat', label: 'Research Assistant', icon: MessageSquare },
    { id: 'dashboard', label: 'Prediction Dashboard', icon: LayoutDashboard },
    { id: 'chronology', label: 'Case Timeline', icon: Clock },
    { id: 'upload', label: 'Knowledge Base', icon: Upload },
  ];

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
              <span className="flex items-center gap-1.5 text-emerald-600 font-bold text-[10px] uppercase tracking-widest bg-emerald-50 px-2 py-1 rounded-md border border-emerald-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
                Active
              </span>
            </div>
            <div className="flex items-center justify-between text-[12px]">
              <span className="text-nyaya-muted/70">Vector DB</span>
              <span className="text-nyaya-text">Connected</span>
            </div>
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
              {activeTab === 'chat' && <ChatInterface />}
              {activeTab === 'dashboard' && <Dashboard />}
              {activeTab === 'chronology' && <Chronology />}
              {activeTab === 'upload' && <PDFUploader />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

export default App;
