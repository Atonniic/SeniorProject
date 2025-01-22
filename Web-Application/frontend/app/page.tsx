'use client';

import { useState } from 'react';
import axios from 'axios';

export default function Page() {
    const [formData, setFormData] = useState({
        sender: '',
        recipient: '',
        subject: '',
        body: '',
    });

    const [result, setResult] = useState<{ error?: string; data?: object } | null>(null);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/analyze-email', formData);
            setResult(response.data);
        } catch (error) {
            console.error('Error:', error);
            setResult({ error: 'Unable to process the request.' });
        }
    };

    return (
        <div className="bg-white shadow-lg rounded-lg p-8 w-full max-w-2xl mt-10">
            <h1 className="text-2xl font-bold mb-4">Phishing email Detection system and Analyze using Natural Language Processing</h1>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium" htmlFor="sender">Sender:</label>
                    <input
                        id="sender"
                        name="sender"
                        type="text"
                        value={formData.sender}
                        onChange={handleChange}
                        className="w-full border rounded p-2"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium" htmlFor="subject">Subject:</label>
                    <input
                        id="subject"
                        name="subject"
                        type="text"
                        value={formData.subject}
                        onChange={handleChange}
                        className="w-full border rounded p-2"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium" htmlFor="body">Body:</label>
                    <textarea
                        id="body"
                        name="body"
                        value={formData.body}
                        onChange={handleChange}
                        className="w-full border rounded p-2"
                        required
                    />
                </div>
                <button type="submit" className="w-full bg-blue-500 text-white py-2 rounded">Analyze</button>
            </form>
            {result && (
                <div className="mt-4 p-4 bg-gray-100 rounded">
                    <h2 className="text-lg font-semibold">Result:</h2>
                    <pre className="text-sm mt-2">{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
            <div className="flex items-center justify-center mt-8">
                <h1 className="text-2xl font-bold text-center">
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
    );
}
