import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  handleReload = () => {
    this.setState({ hasError: false, error: null });
    // In many cases, it's safer to reload the window for a clean state
    // window.location.reload(); 
    // But since this is tab-based, we'll try just clearing the error state first
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full min-h-[400px] w-full bg-nyaya-bg/50 rounded-2xl border border-rose-100/50 p-8 text-center animate-in fade-in zoom-in duration-300">
          <div className="w-16 h-16 bg-rose-50 text-rose-500 rounded-full flex items-center justify-center mb-6 shadow-sm border border-rose-100">
            <AlertTriangle size={32} />
          </div>
          <h2 className="text-xl font-bold text-slate-800 mb-2">Something went wrong</h2>
          <p className="text-slate-500 mb-8 max-w-md">
            This component encountered an unexpected error. Please try reloading this tab to continue your work.
          </p>
          <button
            onClick={this.handleReload}
            className="flex items-center gap-2 px-6 py-3 bg-nyaya-primary text-white rounded-xl font-medium hover:bg-nyaya-primary/90 transition-colors shadow-sm"
          >
            <RefreshCw size={18} />
            <span>Reload this tab</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
