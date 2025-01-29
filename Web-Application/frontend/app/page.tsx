'use client';

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { FiRefreshCcw } from 'react-icons/fi';
import { FaGlobe, FaFolderOpen } from 'react-icons/fa';

export default function Page() {
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [fileName, setFileName] = useState('');
    const [sender, setSender] = useState('');
    const [subject, setSubject] = useState('');
    const [body, setBody] = useState('');
    const [result, setResult] = useState<{ result?: boolean } | null>(null);
    const [isManualMode, setIsManualMode] = useState(false);
    const [backendStatus, setBackendStatus] = useState<'connected' | 'pending' | 'disconnected'>('pending');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    // 🔄 รีเซ็ตค่าทั้งหมด
    const resetForm = () => {
        setFileName('');
        setSender('');
        setSubject('');
        setBody('');
        setResult(null);
        setErrorMessage(null);

        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    // 📂 ฟังก์ชันอ่านไฟล์ EML
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (!selectedFile) return;

        resetForm();
        setFileName(selectedFile.name);

        const reader = new FileReader();
        reader.onload = async (event) => {
            if (!event.target?.result) return;
            const content = event.target.result as string;
            try {
                const response = await axios.post('http://188.166.210.66/upload-email/', {
                    fileName: selectedFile.name,
                    content: content
                });

                setSender(response.data.sender);
                setSubject(response.data.subject);
                setBody(response.data.body);
            } catch (error) {
                console.error("❌ Error uploading file:", error);
            }
        };
        reader.readAsText(selectedFile);
    };

    // 🌐 ตรวจสอบสถานะ Backend ทุก 10 วินาที
    useEffect(() => {
        const checkBackend = async () => {
            try {
                await axios.get('http://188.166.210.66/');
                setBackendStatus('connected');
            } catch {
                setBackendStatus('disconnected');
            }
        };

        checkBackend();
        const interval = setInterval(checkBackend, 10000);
        return () => clearInterval(interval);
    }, []);

    // 🔍 ฟังก์ชัน Analyze Email
    const handleAnalyze = async () => {
        setErrorMessage(null);
        try {
            setBackendStatus('pending'); // 🟡 รอผล
            const response = await axios.post('http://188.166.210.66/analyze-email', { sender, subject, body });
            setResult(response.data);
            setBackendStatus('connected'); // ✅ เชื่อมต่อสำเร็จ
        } catch (error) {
            console.error('❌ Error analyzing email:', error);
            setBackendStatus('disconnected'); // ❌ เชื่อมต่อไม่ได้
            setErrorMessage("⚠️ Unable to connect to the backend. Please try again."); // 🛑 แจ้งเตือน
        }
    };

    // 🎨 กำหนดสีไอคอนโลกตามสถานะ backend
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

                {/* 📂 ปุ่มเลือกไฟล์ */}
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
                            value={fileName || 'ไม่ได้เลือกไฟล์ใด'}
                            readOnly
                            className="border rounded p-2 w-full bg-gray-100"
                        />
                    </div>
                )}

                {/* 🔥 ปุ่มเลื่อน Toggle Mode */}
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

                {/* 📝 ช่องกรอก Sender, Subject, Body */}
                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium">Sender:</label>
                        <input
                            type="text"
                            value={sender}
                            onChange={(e) => isManualMode && setSender(e.target.value)}
                            readOnly={!isManualMode}
                            className="w-full border rounded p-3 bg-gray-100"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Subject:</label>
                        <input
                            type="text"
                            value={subject}
                            onChange={(e) => isManualMode && setSubject(e.target.value)}
                            readOnly={!isManualMode}
                            className="w-full border rounded p-3 bg-gray-100"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Body:</label>
                        <textarea
                            value={body}
                            onChange={(e) => isManualMode && setBody(e.target.value)}
                            readOnly={!isManualMode}
                            className="w-full border rounded p-3 bg-gray-100 h-40"
                        />
                    </div>
                </div>

                {/* 🔍 ปุ่ม Analyze + 🌍 ไอคอน Backend Status */}
                <div className="flex items-center justify-between mt-6">
                    <FaGlobe className={`mr-2 text-6xl ${globeColor}`} />
                    <button
                        onClick={handleAnalyze}
                        disabled={!sender || !subject || !body}
                        className={`w-full py-3 rounded text-lg 
                            ${!sender || !subject || !body ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 text-white hover:bg-blue-600"}`}
                    >
                        Analyze
                    </button>
                    <button
                        onClick={() => window.location.reload()}
                        className="bg-gray-500 text-white ml-2 p-3 rounded-full hover:bg-gray-600"
                    >
                        <FiRefreshCcw size={24} />
                    </button>
                </div>

                {/* 🛑 แสดงข้อความแจ้งเตือนเมื่อเชื่อมต่อ Backend ไม่ได้ */}
                {errorMessage && (
                    <div className="mt-4 p-4 rounded bg-yellow-300 text-gray-800 text-center font-semibold">
                        {errorMessage}
                    </div>
                )}
                
                {/* ✅ แสดงผลลัพธ์ของการตรวจสอบ */}
                {result !== null && (
                    <div className={`mt-4 p-4 rounded text-center font-bold text-lg ${result.result ? 'bg-red-500 text-white' : 'bg-green-500 text-white'}`}>
                        {result.result ? '🚨 Phishing Email Detected! 🚨' : '✅ Good Email ✅'}
                    </div>
                )}
            </div>
        </div>
    );
}
