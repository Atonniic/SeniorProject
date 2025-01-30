'use client';

import { useState, useEffect, useRef } from 'react';
import { FiRefreshCcw } from 'react-icons/fi';
import { FaGlobe, FaFolderOpen } from 'react-icons/fa';
import { uploadEmail, analyzeEmail, checkBackend } from './api/action';  // Import Server Actions

export default function Page() {
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [fileName, setFileName] = useState('');
    const [sender, setSender] = useState('');
    const [datetime, setDatetime] = useState('');
    const [subject, setSubject] = useState('');
    const [body, setBody] = useState('');
    const [result, setResult] = useState<{ result?: boolean } | null>(null);
    const [isManualMode, setIsManualMode] = useState(false);
    const [backendStatus, setBackendStatus] = useState<'connected' | 'pending' | 'disconnected'>('pending');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    // 🔄 Reset Form
    const resetForm = () => {
        setFileName('');
        setSender('');
        setDatetime('');
        setSubject('');
        setBody('');
        setResult(null);
        setErrorMessage(null);

        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    // 📂 Handle File Upload
    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (!selectedFile) return;

        resetForm();
        setFileName(selectedFile.name);

        const reader = new FileReader();
        reader.onload = async (event) => {
            if (!event.target?.result) return;
            const content = event.target.result as string;
            try {
                const response = await uploadEmail(selectedFile.name, content);  // ใช้ Server Action
                setSender(response.sender);
                setDatetime(response.datetime);
                setSubject(response.subject);
                setBody(response.body);
            } catch (error) {
                console.error("❌ Error uploading file:", error);
            }
        };
        reader.readAsText(selectedFile);
    };

    // 🌐 Check Backend Connection (Runs Every 10s)
    useEffect(() => {
        const checkConnection = async () => {
            const status = await checkBackend();
            setBackendStatus(status);
        };

        checkConnection();
        const interval = setInterval(checkConnection, 10000);
        return () => clearInterval(interval);
    }, []);

    // 🔍 Analyze Email
    const handleAnalyze = async () => {
        setErrorMessage(null);
        try {
            setBackendStatus('pending');
            const response = await analyzeEmail(sender, datetime, subject, body); // ใช้ Server Action
            setResult(response);
            setBackendStatus('connected');
        } catch (error) {
            console.error('❌ Error analyzing email:', error);
            setBackendStatus('disconnected');
            setErrorMessage("⚠️ Unable to connect to the backend. Please try again.");
        }
    };

    // 🎨 Set Globe Icon Color
    const globeColor =
        backendStatus === 'connected' ? 'text-green-500' :
        backendStatus === 'pending' ? 'text-gray-400 animate-spin' :
        'text-gray-500';

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100 px-10">
            <div className="bg-white shadow-lg rounded-lg p-10 w-full max-w-4xl">
                <h1 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
                    <span>📩 Upload and Analyze EML File</span>
                </h1>

                {/* 📂 File Upload */}
                {!isManualMode && (
                    <div className="mb-4 flex items-center gap-2">
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="bg-yellow-600 text-white px-4 py-3 rounded-md flex items-center gap-2 hover:bg-yellow-500"
                        >
                            <FaFolderOpen size={18} />
                        </button>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".eml"
                            onChange={handleFileChange}
                            className="hidden"
                        />
                        <input
                            type="text"
                            value={fileName || 'No file selected'}
                            readOnly
                            className="border rounded p-2 w-full bg-gray-100"
                        />
                    </div>
                )}

                {/* 🔥 Toggle Mode */}
                <div className="flex items-center justify-center mb-6">
                    <span className="mr-3 text-gray-600 text-sm">File Upload</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                        <input
                            type="checkbox"
                            checked={isManualMode}
                            onChange={() => {
                                resetForm();
                                setIsManualMode(!isManualMode);
                            }}
                            className="sr-only peer"
                        />
                        <div className="w-14 h-7 bg-gray-300 peer-focus:outline-none rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-7 peer-checked:after:border-white after:content-[''] after:absolute after:top-1 after:left-1 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
                    </label>
                    <span className="ml-3 text-gray-600 text-sm">Manual Mode</span>
                </div>

                {/* 📝 Input Fields */}
                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium">Sender:</label>
                        <input
                            type="text"
                            value={sender}
                            onChange={(e) => isManualMode ? setSender(e.target.value) : null}
                            readOnly={!isManualMode ? true : false}
                            className={`w-full border rounded p-3 ${isManualMode ? "bg-white" : "bg-gray-100"}`}
                        />                    
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Datetime:</label>
                        <input
                            type="datetime-local"
                            value={datetime}
                            onChange={(e) => isManualMode ? setDatetime(e.target.value) : null}
                            readOnly={!isManualMode ? true : false}
                            className={`w-full border rounded p-3 ${isManualMode ? "bg-white" : "bg-gray-100"}`}
                        />                    
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Subject:</label>
                        <input
                            type="text"
                            value={subject}
                            onChange={(e) => isManualMode ? setSubject(e.target.value) : null}
                            readOnly={!isManualMode}
                            className={`w-full border rounded p-3 ${isManualMode ? "bg-white" : "bg-gray-100"}`}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Body:</label>
                        <textarea
                            value={body}
                            onChange={(e) => isManualMode ? setBody(e.target.value) : null}
                            readOnly={!isManualMode}
                            className={`w-full border rounded p-3 h-40 ${isManualMode ? "bg-white" : "bg-gray-100"}`}
                        />
                    </div>
                </div>

                {/* 🔍 Analyze Button */}
                <div className="flex items-center justify-between mt-6">
                    <FaGlobe className={`mr-2 text-6xl ${globeColor}`} />
                    <button onClick={handleAnalyze} className="bg-blue-500 text-white w-full py-3 rounded text-lg hover:bg-blue-600">
                        Analyze
                    </button>
                    <button onClick={() => window.location.reload()} className="bg-gray-500 text-white ml-2 p-3 rounded-full hover:bg-gray-600">
                        <FiRefreshCcw size={24} />
                    </button>
                </div>

                {/* 🛑 Display Backend Connection Error */}
                {errorMessage && (
                    <div className="mt-4 p-4 rounded bg-yellow-300 text-gray-800 text-center font-semibold">
                        {errorMessage}
                    </div>
                )}
                
                {/* ✅ Display Analysis Result */}
                {result !== null && (
                    <div className={`mt-4 p-4 rounded text-center font-bold text-lg ${result.result ? 'bg-red-500 text-white' : 'bg-green-500 text-white'}`}>
                        {result.result ? '🚨 Phishing Email Detected! 🚨' : '✅ Good Email ✅'}
                    </div>
                )}
            </div>
        </div>
    );
}
