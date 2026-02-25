import React, { useState } from 'react';
import { Clock, Calendar, FileText, Loader2, AlertCircle, CheckCircle2, ChevronRight } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function Chronology() {
    const [caseText, setCaseText] = useState('');
    const [loading, setLoading] = useState(false);
    const [timeline, setTimeline] = useState([]);
    const [message, setMessage] = useState('');
    const [error, setError] = useState(null);
    const [selectedEvent, setSelectedEvent] = useState(null);

    const handleGenerateTimeline = async () => {
        if (!caseText || caseText.trim().length < 50) {
            setError('Please enter at least 50 characters of case text');
            return;
        }

        setLoading(true);
        setError(null);
        setTimeline([]);
        setMessage('');

        try {
            const response = await axios.post(`${API_URL}/visualize/timeline`, {
                text: caseText
            });

            setTimeline(response.data.events || []);
            setMessage(response.data.message || '');

            if (response.data.events && response.data.events.length > 0) {
                setSelectedEvent(response.data.events[0]);
            }
        } catch (err) {
            console.error('Timeline generation error:', err);
            setError(err.response?.data?.detail || 'Failed to generate timeline. Please check your API connection.');
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setCaseText('');
        setTimeline([]);
        setMessage('');
        setError(null);
        setSelectedEvent(null);
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative z-10 w-full max-w-7xl mx-auto py-12 px-6">
            {/* Left Panel: Input */}
            <div className="lg:col-span-1 space-y-6">
                <div className="bg-nyaya-surface border border-nyaya-border rounded-3xl p-8 relative overflow-hidden shadow-2xl">
                    <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-nyaya-accent/50 to-nyaya-primary/50"></div>

                    <h3 className="text-xl font-medium text-nyaya-text mb-8 flex items-center gap-3 relative z-10">
                        <div className="p-2 bg-nyaya-bg border border-nyaya-border rounded-xl">
                            <FileText className="text-nyaya-text" size={20} />
                        </div>
                        Case Document
                    </h3>

                    <textarea
                        value={caseText}
                        onChange={(e) => setCaseText(e.target.value)}
                        rows={16}
                        className="w-full px-5 py-4 rounded-2xl bg-nyaya-bg border border-nyaya-border text-nyaya-text placeholder-nyaya-muted/50 focus:outline-none focus:border-nyaya-primary/50 focus:ring-1 focus:ring-nyaya-primary/30 transition-all resize-none text-[15px] leading-relaxed shadow-inner relative z-10 custom-scrollbar"
                        placeholder="Paste your FIR, Judgment, or any legal document containing dates and events...

Example:
'On 15th January 2023, the complainant filed FIR No. 234/2023 at City Police Station alleging theft. The incident occurred on 14th January 2023 at 3:00 PM...'"
                    />

                    {error && (
                        <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-xl flex items-center gap-3 border border-red-200 backdrop-blur-sm relative z-10">
                            <AlertCircle size={18} className="shrink-0" />
                            <span className="text-sm font-medium">{error}</span>
                        </div>
                    )}

                    {message && !error && timeline.length > 0 && (
                        <div className="mt-4 p-4 bg-green-50 text-green-700 rounded-xl flex items-center gap-3 border border-green-200 backdrop-blur-sm relative z-10">
                            <CheckCircle2 size={18} className="shrink-0" />
                            <span className="text-sm font-medium">{message}</span>
                        </div>
                    )}

                    <div className="mt-8 flex gap-4 relative z-10">
                        <button
                            onClick={handleGenerateTimeline}
                            disabled={loading || !caseText}
                            className="flex-1 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-500 hover:to-indigo-500 rounded-2xl font-bold transition-all disabled:opacity-50 disabled:shadow-none disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-lg hover:shadow-xl active:scale-[0.98]"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="animate-spin" size={20} />
                                    Extracting Events...
                                </>
                            ) : (
                                <>
                                    <Calendar size={20} />
                                    Generate Timeline
                                </>
                            )}
                        </button>

                        {timeline.length > 0 && (
                            <button
                                onClick={handleClear}
                                className="px-6 py-4 bg-nyaya-bg text-nyaya-text rounded-2xl font-bold hover:bg-nyaya-surface transition-all border border-nyaya-border"
                            >
                                Clear
                            </button>
                        )}
                    </div>

                    <div className="mt-8 p-6 bg-nyaya-bg rounded-2xl border border-nyaya-border relative z-10 shadow-inner">
                        <p className="font-bold text-xs text-nyaya-muted uppercase tracking-widest mb-3">💡 Extraction Tips:</p>
                        <ul className="space-y-2 ml-1 text-[13px] text-nyaya-muted font-medium">
                            <li className="flex gap-2 items-start"><span className="text-nyaya-primary mt-0.5">•</span> Include specific dates (DD/MM/YYYY)</li>
                            <li className="flex gap-2 items-start"><span className="text-nyaya-primary mt-0.5">•</span> Paste complete paragraphs</li>
                            <li className="flex gap-2 items-start"><span className="text-nyaya-primary mt-0.5">•</span> Works with FIRs & Judgments</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Right Panel: Timeline Visualization */}
            <div className="lg:col-span-2 h-[850px]">
                {!loading && timeline.length === 0 ? (
                    <div className="h-full bg-nyaya-surface border border-nyaya-border rounded-3xl p-12 flex flex-col items-center justify-center relative overflow-hidden text-center shadow-2xl">
                        <div className="w-24 h-24 bg-nyaya-bg rounded-full border border-nyaya-border flex items-center justify-center mb-8 shadow-inner">
                            <Clock size={32} className="text-nyaya-muted/50" />
                        </div>
                        <h3 className="text-2xl font-medium text-nyaya-text mb-4">Ready to Visualize</h3>
                        <p className="text-base text-nyaya-muted max-w-sm text-balance leading-relaxed">
                            Paste your case text and click "Generate Timeline" to extract and visualize chronological events.
                        </p>
                    </div>
                ) : loading ? (
                    <div className="h-full bg-nyaya-surface border border-nyaya-border rounded-3xl p-12 flex flex-col items-center justify-center relative overflow-hidden text-center shadow-2xl">
                        <div className="text-center relative z-10 flex flex-col items-center">
                            <Loader2 className="animate-spin text-nyaya-primary mb-6" size={48} />
                            <h3 className="text-xl font-medium text-nyaya-text mb-2">Analyzing case chronology...</h3>
                            <p className="text-[15px] text-nyaya-muted">Using AI to extract dates and conceptual events</p>
                        </div>
                    </div>
                ) : (
                    <div className="bg-nyaya-surface border border-nyaya-border rounded-3xl p-8 h-full flex flex-col relative overflow-hidden shadow-2xl">
                        <h3 className="text-2xl font-medium text-nyaya-text mb-8 flex items-center gap-3 relative z-10">
                            <div className="w-10 h-10 rounded-xl bg-nyaya-bg border border-nyaya-border flex items-center justify-center">
                                <Calendar className="text-nyaya-primary" size={20} />
                            </div>
                            Case Chronology
                            <span className="text-[11px] font-bold bg-nyaya-bg text-nyaya-muted px-3 py-1.5 rounded-full border border-nyaya-border tracking-widest uppercase ml-2">{timeline.length} Events</span>
                        </h3>

                        <div className="flex-1 overflow-y-auto relative z-10 pr-4 custom-scrollbar">
                            {/* Custom Vertical Timeline */}
                            <div className="relative pt-4">
                                {/* Vertical Line*/}
                                <div className="absolute left-8 top-4 bottom-4 w-px bg-gradient-to-b from-nyaya-primary/50 via-nyaya-border to-transparent"></div>

                                {timeline.map((event, index) => (
                                    <div key={index} className="relative mb-10 pl-24 group">
                                        {/* Date Circle */}
                                        <div className="absolute left-0 flex flex-col items-center h-full">
                                            <div
                                                className={`w-[4.5rem] h-[4.5rem] rounded-2xl flex items-center justify-center relative z-10 cursor-pointer transition-all duration-300
                                                ${selectedEvent === event
                                                        ? 'bg-nyaya-text text-nyaya-bg shadow-glow scale-[1.05]'
                                                        : 'bg-nyaya-bg border border-nyaya-border text-nyaya-muted hover:border-nyaya-primary/50 hover:text-nyaya-text group-hover:bg-nyaya-surface'
                                                    }`}
                                                onClick={() => setSelectedEvent(event)}
                                            >
                                                <div className="text-center">
                                                    <div className="text-lg font-black tracking-tighter">
                                                        {event.date !== 'Unknown' ? event.date.split('-')[2] : '?'}
                                                    </div>
                                                    <div className="text-[9px] font-bold uppercase tracking-[0.2em] mt-0.5 opacity-80">
                                                        {event.date !== 'Unknown'
                                                            ? new Date(event.date).toLocaleDateString('en-US', { month: 'short' })
                                                            : 'UNK'
                                                        }
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Event Card */}
                                        <div
                                            className={`bg-nyaya-bg border rounded-2xl p-6 cursor-pointer transition-all duration-300 relative overflow-hidden
                                                ${selectedEvent === event
                                                    ? 'border-nyaya-primary/50 shadow-lg shadow-nyaya-primary/5 bg-nyaya-primary/5'
                                                    : 'border-nyaya-border hover:border-nyaya-muted/30 hover:bg-nyaya-surface group-hover:-translate-y-1'
                                                }`}
                                            onClick={() => setSelectedEvent(event)}
                                        >
                                            {selectedEvent === event && (
                                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-nyaya-primary rounded-l-2xl"></div>
                                            )}
                                            <div className="flex items-start justify-between mb-3">
                                                <h4 className={`font-medium text-base md:text-lg flex-1 pr-4 leading-snug 
                                                    ${selectedEvent === event ? 'text-nyaya-primary' : 'text-nyaya-text'}`}>
                                                    {event.title}
                                                </h4>
                                                {selectedEvent === event && (
                                                    <ChevronRight className="text-nyaya-primary flex-shrink-0 mt-1" size={20} />
                                                )}
                                            </div>
                                            <div className="text-[10px] font-bold uppercase tracking-widest text-nyaya-muted mb-4 flex items-center gap-2">
                                                <Calendar size={12} className={selectedEvent === event ? 'text-nyaya-primary/70' : ''} />
                                                {event.date !== 'Unknown'
                                                    ? new Date(event.date).toLocaleDateString('en-US', {
                                                        weekday: 'long',
                                                        year: 'numeric',
                                                        month: 'long',
                                                        day: 'numeric'
                                                    })
                                                    : 'Date Unknown'
                                                }
                                            </div>
                                            <p className={`text-[14px] line-clamp-2 leading-relaxed font-medium 
                                                ${selectedEvent === event ? 'text-nyaya-text/90' : 'text-nyaya-muted'}`}>
                                                {event.description}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Selected Event Detail (Bottom) */}
                        {selectedEvent && (
                            <div className="mt-6 pt-6 border-t border-nyaya-border relative z-10">
                                <div className="bg-nyaya-bg rounded-2xl p-8 border border-nyaya-border relative overflow-hidden text-left shadow-inner">
                                    <div className="absolute top-0 right-0 w-32 h-32 bg-nyaya-primary/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

                                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-6 relative z-10 mb-6 border-b border-nyaya-border/50 pb-6">
                                        <h4 className="font-medium text-nyaya-text text-xl max-w-xl leading-tight">{selectedEvent.title}</h4>
                                        <span className="text-[10px] font-black bg-nyaya-text text-nyaya-bg px-4 py-2 rounded-lg tracking-widest uppercase whitespace-nowrap self-start shadow-glow">
                                            {selectedEvent.date !== 'Unknown'
                                                ? selectedEvent.date
                                                : 'Date Unknown'
                                            }
                                        </span>
                                    </div>
                                    <p className="text-[15px] text-nyaya-muted leading-loose relative z-10 font-medium">{selectedEvent.description}</p>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
