'use client';

import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  Zap, 
  Layers, 
  Bot, 
  RotateCw, 
  AlertTriangle, 
  Send, 
  Trash2, 
  Sparkles,
  Server
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ClusterStatus {
  health: {
    score: number;
    rating: string;
    badge_color: string;
    deductions: string[];
  };
  power_watts: number;
  pods_summary: {
    total: number;
    running: number;
    terminating: number;
  };
  anomaly_count: number;
}

interface Anomaly {
  id: string;
  level: string;
  title: string;
  description: string;
  suggested_action: string;
}

interface NodeInfo {
  name: string;
  ready: boolean;
  roles: string[];
  internal_ip: string;
}

export default function DashboardPage() {
  const [status, setStatus] = useState<ClusterStatus | null>(null);
  const [nodes, setNodes] = useState<NodeInfo[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [analysis, setAnalysis] = useState<string>('');
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([
    {
      role: 'assistant',
      content: 'Xin chào! Tôi là AIOps SRE Copilot chạy trên mô hình **GPT-5.6 Sol**. Tôi đã kết nối dữ liệu K3s, Prometheus và log của cụm onprem. Bạn cần tôi hỗ trợ phân tích sự cố nào?'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [resStatus, resNodes, resAnom] = await Promise.all([
        fetch('/api/cluster/status'),
        fetch('/api/cluster/nodes'),
        fetch('/api/cluster/anomalies')
      ]);
      const dataStatus = await resStatus.json();
      const dataNodes = await resNodes.json();
      const dataAnom = await resAnom.json();

      setStatus(dataStatus);
      setNodes(dataNodes.nodes || []);
      setAnomalies(dataAnom.anomalies || []);
    } catch (err) {
      console.error('Lỗi tải dữ liệu:', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const runIncidentAnalysis = async () => {
    setAnalyzing(true);
    setAnalysis('');
    try {
      const res = await fetch('/api/aiops/analyze', { method: 'POST' });
      const data = await res.json();
      if (data.success && data.analysis) {
        setAnalysis(data.analysis);
      } else {
        setAnalysis('⚠️ Lỗi: ' + (data.analysis || 'Không thể tạo phân tích'));
      }
    } catch (err: any) {
      setAnalysis('⚠️ Lỗi kết nối: ' + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const sendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || chatLoading) return;

    const newMessages = [...messages, { role: 'user', content: inputMessage }];
    setMessages(newMessages);
    setInputMessage('');
    setChatLoading(true);

    try {
      const res = await fetch('/api/aiops/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages })
      });
      const data = await res.json();
      if (data.success && data.content) {
        setMessages([...newMessages, { role: 'assistant', content: data.content }]);
      } else {
        setMessages([...newMessages, { role: 'assistant', content: '⚠️ Lỗi: ' + (data.content || 'AI không phản hồi.') }]);
      }
    } catch (err: any) {
      setMessages([...newMessages, { role: 'assistant', content: '⚠️ Lỗi kết nối: ' + err.message }]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Top Bar */}
      <header className="glass sticky top-0 z-50 px-6 py-4 flex flex-wrap items-center justify-between gap-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight">K3s AIOps Platform</h1>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                GPT-5.6 Sol
              </span>
            </div>
            <p className="text-xs text-slate-400">On-Premises Homelab Autonomous SRE & Observability</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>9Router LLM</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>K3s Core</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>Prometheus</span>
          </div>
          <button 
            onClick={fetchData} 
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-1 p-6 max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* 3 Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Health Score */}
            <div className="glass p-5 rounded-2xl flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Health Score</span>
                <ShieldCheck className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="my-3 flex items-baseline gap-2">
                <span className="text-4xl font-extrabold text-white">{status?.health?.score ?? '--'}</span>
                <span className="text-sm text-slate-400">/ 100</span>
              </div>
              <div className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-indigo-300 w-fit">
                {status?.health?.rating ?? 'Đang tải...'}
              </div>
            </div>

            {/* Power Draw */}
            <div className="glass p-5 rounded-2xl flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Công Suất Tiêu Thụ</span>
                <Zap className="w-5 h-5 text-amber-400" />
              </div>
              <div className="my-3 flex items-baseline gap-2">
                <span className="text-4xl font-extrabold text-amber-300">{status?.power_watts ?? '--'}</span>
                <span className="text-sm text-slate-400">Watts</span>
              </div>
              <div className="text-xs text-slate-400">
                RAPL + Wall estimate (~140W idle)
              </div>
            </div>

            {/* Workloads */}
            <div className="glass p-5 rounded-2xl flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Workload Pods</span>
                <Layers className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="my-3 flex items-baseline gap-2">
                <span className="text-4xl font-extrabold text-emerald-400">{status?.pods_summary?.running ?? '--'}</span>
                <span className="text-sm text-slate-400">/ {status?.pods_summary?.total ?? '--'}</span>
              </div>
              <div className="text-xs text-slate-400">
                {status?.pods_summary?.terminating ?? 0} pod terminating
              </div>
            </div>
          </div>

          {/* AI Incident Analysis Box */}
          <div className="glass p-6 rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-slate-900/90 to-indigo-950/20">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-800">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  AI Incident & Root Cause Analysis
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Sử dụng mô hình <strong>gpt-5.6-sol</strong> tổng hợp telemetry cluster để chẩn đoán sự cố tự động
                </p>
              </div>
              <button 
                onClick={runIncidentAnalysis} 
                disabled={analyzing}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all active:scale-95 disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                {analyzing ? 'Đang Chẩn Đoán...' : 'Chạy Phân Tích AI'}
              </button>
            </div>

            <div className="min-h-[140px] text-xs leading-relaxed text-slate-300">
              {analysis ? (
                <div className="prose prose-invert max-w-none prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800">
                  <ReactMarkdown>{analysis}</ReactMarkdown>
                </div>
              ) : (
                <div className="py-8 text-center text-slate-500 text-xs">
                  Nhấn <strong>"Chạy Phân Tích AI"</strong> để yêu cầu GPT-5.6 Sol chẩn đoán toàn diện nguyên nhân gốc rễ và kế hoạch khắc phục.
                </div>
              )}
            </div>
          </div>

          {/* Anomalies & Nodes */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Anomalies List */}
            <div className="glass p-5 rounded-2xl">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center justify-between">
                <span>Bất Thường Tự Động Phát Hiện</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">{anomalies.length}</span>
              </h3>
              <div className="space-y-3 max-h-72 overflow-y-auto pr-1 text-xs">
                {anomalies.length === 0 ? (
                  <div className="text-slate-400 py-4 text-center">Không phát hiện bất thường nào. Cụm vận hành hoàn hảo!</div>
                ) : (
                  anomalies.map(a => (
                    <div key={a.id} className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-slate-200">{a.title}</span>
                        <span className="text-[9px] uppercase px-1.5 py-0.5 rounded font-bold bg-amber-500/20 text-amber-400">{a.level}</span>
                      </div>
                      <p className="text-slate-400 mb-1.5">{a.description}</p>
                      <div className="p-1.5 rounded bg-slate-950 font-mono text-[10px] text-indigo-300">{a.suggested_action}</div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Nodes */}
            <div className="glass p-5 rounded-2xl">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center justify-between">
                <span>Trạng Thái Cụm Node</span>
                <Server className="w-4 h-4 text-slate-400" />
              </h3>
              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1 text-xs">
                {nodes.map(n => (
                  <div key={n.name} className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${n.ready ? 'bg-emerald-400' : 'bg-rose-500'}`} />
                      <div>
                        <div className="font-medium text-slate-200">{n.name}</div>
                        <div className="text-[10px] text-slate-400">{n.internal_ip || 'No IP'} • {n.roles?.join(', ')}</div>
                      </div>
                    </div>
                    <span className={`text-[10px] px-2 py-0.5 rounded font-medium ${n.ready ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                      {n.ready ? 'Ready' : 'NotReady'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: AI Chatbot (1 col) */}
        <div className="glass rounded-2xl p-5 flex flex-col h-[750px] border border-slate-800">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-white">AI SRE Chatbot</h2>
                <p className="text-[11px] text-emerald-400">● Live Cluster Context Infused</p>
              </div>
            </div>
            <button 
              onClick={() => setMessages([{ role: 'assistant', content: 'Đã xóa hội thoại. Bạn có thể hỏi tôi câu mới.' }])}
              className="text-xs text-slate-500 hover:text-slate-300"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-3.5 pr-1 text-xs">
            {messages.map((m, idx) => (
              <div key={idx} className={`flex gap-2.5 items-start ${m.role === 'user' ? 'justify-end' : ''}`}>
                {m.role !== 'user' && (
                  <div className="w-6 h-6 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center text-[10px] text-white">AI</div>
                )}
                <div className={`p-3 rounded-2xl max-w-[85%] leading-relaxed ${
                  m.role === 'user' 
                    ? 'bg-indigo-600 text-white rounded-tr-sm' 
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-sm prose prose-invert'
                }`}>
                  {m.role === 'user' ? m.content : <ReactMarkdown>{m.content}</ReactMarkdown>}
                </div>
                {m.role === 'user' && (
                  <div className="w-6 h-6 rounded-full bg-slate-700 flex-shrink-0 flex items-center justify-center text-[10px] text-white">Bạn</div>
                )}
              </div>
            ))}
            {chatLoading && (
              <div className="flex gap-2.5 items-start">
                <div className="w-6 h-6 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center text-[10px] text-white">AI</div>
                <div className="bg-slate-900 px-3.5 py-2.5 rounded-2xl text-slate-400 border border-slate-800 text-xs flex items-center gap-2">
                  <RotateCw className="w-3.5 h-3.5 animate-spin" /> GPT-5.6 Sol đang suy nghĩ...
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="mt-4 pt-3 border-t border-slate-800">
            <form onSubmit={sendChat} className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={e => setInputMessage(e.target.value)}
                placeholder="Hỏi về pod kẹt, node tang1, RAM, CPU..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 transition-colors"
              />
              <button
                type="submit"
                disabled={chatLoading}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors flex items-center justify-center disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>

      </main>

      <footer className="text-center py-4 text-xs text-slate-500 border-t border-slate-900">
        K3s AIOps Platform • Powered by 9Router GPT-5.6 Sol • On-Premises Homelab
      </footer>
    </div>
  );
}

