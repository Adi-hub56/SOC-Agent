'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: 'Hi! I\'m your SOC Assistant. Ask me anything about your incidents.',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, null, {
        params: { message: input }
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-8 right-8 w-16 h-16 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 z-40 hover:scale-110 hover:shadow-3xl"
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }}
      >
        <svg
          className="w-10 h-10"
          viewBox="0 0 200 200"
          fill="none"
        >
          <defs>
            <linearGradient id="pandaGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
              <stop offset="100%" stopColor="#f0f0f0" stopOpacity="1" />
            </linearGradient>
            <linearGradient id="eyeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1a1a1a" stopOpacity="1" />
              <stop offset="100%" stopColor="#000000" stopOpacity="1" />
            </linearGradient>
          </defs>

          <circle cx="100" cy="100" r="85" fill="url(#pandaGrad)" stroke="#e0e0e0" strokeWidth="2" />
          <circle cx="100" cy="105" r="85" fill="rgba(0,0,0,0.1)" />

          <circle cx="45" cy="35" r="18" fill="#1a1a1a" stroke="#000" strokeWidth="1.5" />
          <circle cx="45" cy="35" r="12" fill="#333" />

          <circle cx="155" cy="35" r="18" fill="#1a1a1a" stroke="#000" strokeWidth="1.5" />
          <circle cx="155" cy="35" r="12" fill="#333" />

          <ellipse cx="65" cy="85" rx="20" ry="28" fill="#1a1a1a" stroke="#000" strokeWidth="1" />
          <ellipse cx="135" cy="85" rx="20" ry="28" fill="#1a1a1a" stroke="#000" strokeWidth="1" />

          <circle cx="65" cy="85" r="11" fill="white" />
          <circle cx="135" cy="85" r="11" fill="white" />

          <circle cx="63" cy="88" r="6" fill="url(#eyeGrad)" />
          <circle cx="61" cy="86" r="2" fill="white" opacity="0.8" />
          
          <circle cx="133" cy="88" r="6" fill="url(#eyeGrad)" />
          <circle cx="131" cy="86" r="2" fill="white" opacity="0.8" />

          <ellipse cx="100" cy="130" rx="8" ry="10" fill="#1a1a1a" stroke="#000" strokeWidth="1" />
          
          <circle cx="97" cy="130" r="2" fill="#000" />
          <circle cx="103" cy="130" r="2" fill="#000" />

          <path d="M 100 130 L 100 150" stroke="#1a1a1a" strokeWidth="3" fill="none" strokeLinecap="round" />
          <path d="M 85 145 Q 100 160 115 145" stroke="#1a1a1a" strokeWidth="2.5" fill="none" strokeLinecap="round" />

          <ellipse cx="75" cy="170" rx="12" ry="18" fill="#1a1a1a" stroke="#000" strokeWidth="1" />
          <ellipse cx="125" cy="170" rx="12" ry="18" fill="#1a1a1a" stroke="#000" strokeWidth="1" />

          <ellipse cx="75" cy="180" rx="6" ry="8" fill="#333" />
          <ellipse cx="125" cy="180" rx="6" ry="8" fill="#333" />
        </svg>
      </button>

      {isOpen && (
        <div className="fixed bottom-24 right-8 w-96 h-96 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl flex flex-col z-50 animate-in slide-in-from-bottom-4">
          <div className="bg-slate-800 border-b border-slate-700 p-4 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-white">SOC Assistant</h2>
              <p className="text-xs text-gray-400">AI-powered incident analyst</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white text-2xl"
            >
              ✕
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map(msg => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-slate-700 text-gray-100 rounded-bl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  <p className="text-xs mt-1 opacity-70">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-700 px-4 py-2 rounded-lg rounded-bl-none text-sm text-gray-300">
                  Thinking...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-slate-700 p-4 space-y-2">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              className="w-full bg-slate-800 text-white border border-slate-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500 resize-none"
              rows={2}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded font-bold text-sm"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
