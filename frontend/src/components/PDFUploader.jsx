import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function PDFUploader() {
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState(null); // success | error
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFiles(Array.from(e.target.files));
            setStatus(null);
        }
    };

    const handleUpload = async () => {
        if (files.length === 0) return;

        setUploading(true);
        setStatus(null);

        const formData = new FormData();
        files.forEach((file) => {
            formData.append('files', file);
        });

        try {
            const response = await axios.post(`${API_URL}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            console.log(response.data);
            setStatus('success');
            setFiles([]);
        } catch (error) {
            console.error('Upload failed:', error);
            setStatus('error');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6 relative z-10 py-12 px-6">
            <div className="bg-nyaya-surface border border-nyaya-border rounded-4xl p-10 md:p-14 text-center relative overflow-hidden shadow-2xl">
                {/* Ambient Effects */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-nyaya-primary/5 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none"></div>
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-nyaya-accent/5 rounded-full blur-3xl -ml-32 -mb-32 pointer-events-none"></div>
                <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-nyaya-accent/30 via-nyaya-primary/50 to-nyaya-accent/30"></div>

                <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-nyaya-border rounded-[2.5rem] p-12 md:p-16 cursor-pointer hover:border-nyaya-primary/50 hover:bg-nyaya-bg/50 transition-all duration-300 group bg-nyaya-bg relative z-10 shadow-inner group"
                >
                    <div className="w-24 h-24 bg-nyaya-surface text-nyaya-primary rounded-3xl shadow-glow border border-nyaya-primary/20 flex items-center justify-center mx-auto mb-8 group-hover:-translate-y-2 group-hover:shadow-[0_0_30px_-5px_var(--nyaya-primary)] transition-all duration-500">
                        <Upload size={40} strokeWidth={1.5} className="group-hover:scale-110 transition-transform duration-500" />
                    </div>
                    <h3 className="text-2xl font-medium text-nyaya-text tracking-tight mb-3">Upload Legal Documents</h3>
                    <p className="text-[15px] font-medium text-nyaya-muted max-w-md mx-auto leading-relaxed">Drag and drop PDF files here, or click to browse your computer</p>
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        multiple
                        accept=".pdf"
                        className="hidden"
                    />
                </div>

                {/* File List */}
                {files.length > 0 && (
                    <div className="mt-10 space-y-3 relative z-10 text-left">
                        {files.map((file, idx) => (
                            <div key={idx} className="flex items-center gap-4 bg-nyaya-bg border border-nyaya-border shadow-sm p-4 rounded-2xl text-[14px] text-nyaya-text font-medium hover:border-nyaya-primary/30 transition-colors">
                                <div className="w-12 h-12 rounded-xl bg-nyaya-surface border border-nyaya-border flex items-center justify-center flex-shrink-0 shadow-inner">
                                    <FileText size={20} className="text-nyaya-primary" />
                                </div>
                                <span className="flex-1 truncate">{file.name}</span>
                                <span className="text-[10px] font-bold uppercase tracking-widest text-nyaya-muted bg-nyaya-surface px-3 py-1.5 rounded-lg border border-nyaya-border shadow-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Action Button */}
                <div className="mt-10 relative z-10">
                    <button
                        onClick={handleUpload}
                        disabled={uploading || files.length === 0}
                        className={`w-full py-5 px-8 rounded-2xl font-bold flex items-center justify-center gap-3 transition-all duration-300
                            ${files.length === 0
                                ? 'bg-nyaya-bg text-nyaya-muted border border-nyaya-border cursor-not-allowed'
                                : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-500 hover:to-indigo-500 shadow-lg hover:shadow-xl hover:-translate-y-1 active:scale-[0.98]'
                            }`}
                    >
                        {uploading ? (
                            <>
                                <Loader className="animate-spin" size={20} />
                                Processing and Indexing...
                            </>
                        ) : status === 'success' ? (
                            <>
                                <CheckCircle size={20} className="text-green-500" />
                                Upload Complete
                            </>
                        ) : status === 'error' ? (
                            <>
                                <AlertCircle size={20} className="text-red-500" />
                                Upload Failed
                            </>
                        ) : (
                            'Add to Knowledge Base'
                        )}
                    </button>
                </div>
            </div>

            <div className="text-center text-[13px] font-medium text-nyaya-muted/70 flex items-center justify-center gap-2">
                <FileText size={14} className="opacity-50" />
                <p>Supports multiple PDF files. Documents are indexed locally for maximum privacy.</p>
            </div>
        </div>
    );
}
