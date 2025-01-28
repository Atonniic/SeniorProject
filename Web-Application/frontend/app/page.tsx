'use client';

import { useState } from 'react';
import axios from 'axios';
import { FiRefreshCcw } from "react-icons/fi"; // 🔄 Import ไอคอน Reset

export default function Page() {
    const [sender, setSender] = useState('');
    const [subject, setSubject] = useState('');
    const [body, setBody] = useState('');
    const [result, setResult] = useState<{ result?: boolean } | null>(null);
    const [isManualMode, setIsManualMode] = useState(false);

    // 🔄 รีเซ็ตค่าทั้งหมด
    const resetForm = () => {
        setSender('');
        setSubject('');
        setBody('');
        setResult(null);
    };

    // 📂 ฟังก์ชันอ่านไฟล์ EML
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            resetForm(); // ✅ รีเซ็ตค่าเมื่อเลือกไฟล์ใหม่
            const selectedFile = e.target.files[0];
            setFile(selectedFile);

            const reader = new FileReader();
            reader.onload = async (event) => {
                if (event.target && event.target.result) {
                    const content = event.target.result as string;

                    try {
                        const response = await axios.post('http://localhost:8000/upload-email/', {
                            fileName: selectedFile.name,
                            content: content
                        });

                        setSender(response.data.sender);
                        setSubject(response.data.subject);
                        setBody(response.data.body);
                    } catch (error) {
                        console.error("Error uploading file:", error);
                    }
                }
            };
            reader.readAsText(selectedFile);
        }
    };

    // 🛠️ ฟังก์ชันเปิด/ปิด Manual Mode
    const toggleManualMode = () => {
        resetForm();
        setIsManualMode(!isManualMode);
    };

    // 🟢 ฟังก์ชัน Analyze Email
    const handleAnalyze = async () => {
        try {
            const response = await axios.post('http://localhost:8000/analyze-email', { sender, subject, body });
            setResult(response.data);
        } catch (error) {
            console.error('Error:', error);
            setResult({ result: false });
        }
    };

    // 🎨 กำหนดสีพื้นหลังของผลลัพธ์
    const resultBgColor = result
        ? result.result
            ? 'bg-red-500 text-white' // 🔴 Phishing Email
            : 'bg-green-500 text-white' // 🟢 Good Email
        : 'bg-gray-100';

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100 px-6">
            <div className="bg-white shadow-lg rounded-lg p-10 w-full max-w-3xl">
                <h1 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
                    <span>📩 Upload and Analyze EML File</span>
                </h1>

                {/* 📂 อัปโหลดไฟล์ (ซ่อนเมื่อเปิด Manual Mode) */}
                {!isManualMode && (
                    <div className="mb-4">
                        <input
                            type="file"
                            accept=".eml"
                            onChange={handleFileChange}
                            className="border rounded p-2 w-full"
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
                            onChange={toggleManualMode}
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

                {/* 🔍 ปุ่ม Analyze และ Reset */}
                <div className="flex justify-between items-center mt-6">
                    <button
                        onClick={handleAnalyze}
                        disabled={!sender || !subject || !body} // ✅ ปิดปุ่มถ้าข้อมูลไม่ครบ
                        className={`flex-1 text-white py-3 rounded text-lg mr-2
                            ${!sender || !subject || !body ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"}`}
                    >
                        Analyze
                    </button>

                    {/* 🔄 ปุ่ม Reset Form */}
                    {result !== null && (
                        <button
                            onClick={resetForm}
                            className="bg-gray-500 text-white p-3 rounded-full hover:bg-gray-600"
                        >
                            <FiRefreshCcw size={24} />
                        </button>
                    )}
                </div>

                {/* ✅ แสดงผลลัพธ์ของการตรวจสอบ */}
                {result !== null && (
                    <div className={`mt-4 p-4 rounded text-center font-bold text-lg ${resultBgColor}`}>
                        {result.result ? '🚨 Phishing Email Detected! 🚨' : '✅ Good Email ✅'}
                    </div>
                )}

                {/* 📊 ลิงก์ไปยัง Dashboard */}
                <div className="flex items-center justify-center mt-10">
                    <h1 className="text-2xl font-bold text-center flex items-center gap-2">
                        <span>📊</span>
                        <a
                            href="http://34.41.68.246:3000/public-dashboards/9b2ad83572b04d25a41d6217f6037673"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-500 hover:underline"
                        >
                            Dashboard
                        </a>
                    </h1>
                </div>
            </div>
        </div>
    );
}
