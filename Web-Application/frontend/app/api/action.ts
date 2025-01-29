'use server';

import axios from 'axios';

const backendURL = "http://188.166.210.66";  // เชื่อมต่อ backend ตรงๆ (HTTP)

// 📂 Upload Email File
export async function uploadEmail(fileName: string, content: string) {
    try {
        const response = await axios.post(`${backendURL}/upload-email/`, {
            fileName,
            content,
        });
        return response.data;
    } catch (error) {
        console.error("❌ Error uploading file:", error);
        throw new Error("Failed to upload email file.");
    }
}

// 🔍 Analyze Email
export async function analyzeEmail(sender: string, subject: string, body: string) {
    try {
        const response = await axios.post(`${backendURL}/analyze-email`, { sender, subject, body });
        return response.data;
    } catch (error) {
        console.error("❌ Error analyzing email:", error);
        throw new Error("Failed to analyze email.");
    }
}

// 🌐 Check Backend Connection
export async function checkBackend() {
    try {
        await axios.get(`${backendURL}/`);
        return 'connected';
    } catch {
        return 'disconnected';
    }
}
