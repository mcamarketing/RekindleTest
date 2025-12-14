import { useState } from 'react';
import { Upload, Send, MessageSquare, Calendar, FileText } from 'lucide-react';

interface BatchReport {
  batch_id: string;
  report: {
    leads_contacted: number;
    replies_received: number;
    interested_count: number;
    qualified_count: number;
    meetings_booked: number;
    revival_fee_gbp: number;
    booking_fee_gbp: number;
    total_fee_gbp: number;
  };
  export_data: any[];
}

export function MVPConsole() {
  const [batchId, setBatchId] = useState('');
  const [businessType, setBusinessType] = useState('generic');
  const [senderName, setSenderName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [report, setReport] = useState<BatchReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/mvp/leads/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();

      if (data.success) {
        setBatchId(data.batch_id);
        alert(`Uploaded ${data.accepted_count} leads. Batch ID: ${data.batch_id}`);
      } else {
        setError(data.error || 'Upload failed');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartRevival = async () => {
    if (!batchId || !senderName || !companyName) {
      alert('Fill in all fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/mvp/revival/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          batch_id: batchId,
          business_type: businessType,
          sender_name: senderName,
          company_name: companyName,
        }),
      });

      const data = await res.json();

      if (data.success) {
        setMessages(data.sample_messages || []);
        alert(`Generated ${data.messages_generated} messages (showing first 3)`);
      } else {
        setError('Revival start failed');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleIngestReply = async (leadEmail: string, messageText: string) => {
    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/mvp/replies/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead_email: leadEmail,
          message_text: messageText,
          batch_id: batchId,
        }),
      });

      const data = await res.json();

      if (data.success) {
        alert(`Classified as ${data.classification}. Next: ${data.next_action}`);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!batchId) {
      alert('No batch ID');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`/api/mvp/batches/${batchId}/report`);
      const data = await res.json();

      if (data.success) {
        setReport(data);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Rekindle MVP Console</h1>
        <p className="text-gray-600 mb-8">Performance pricing: £25/meeting, £0.10/revived lead</p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <div className="grid gap-6">
          {/* 1. Upload CSV */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-4">
              <Upload className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-semibold">1. Upload Leads CSV</h2>
            </div>
            <input
              type="file"
              accept=".csv"
              onChange={handleUpload}
              className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {batchId && (
              <p className="mt-2 text-sm text-green-600">Batch ID: <code className="bg-gray-100 px-2 py-1 rounded">{batchId}</code></p>
            )}
          </div>

          {/* 2. Start Revival */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-4">
              <Send className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-semibold">2. Generate Revival Messages</h2>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <input
                type="text"
                placeholder="Batch ID"
                value={batchId}
                onChange={(e) => setBatchId(e.target.value)}
                className="px-3 py-2 border rounded"
              />
              <select
                value={businessType}
                onChange={(e) => setBusinessType(e.target.value)}
                className="px-3 py-2 border rounded"
              >
                <option value="generic">Generic</option>
                <option value="agency">Agency</option>
                <option value="real_estate">Real Estate</option>
                <option value="saas">SaaS</option>
              </select>
              <input
                type="text"
                placeholder="Your Name"
                value={senderName}
                onChange={(e) => setSenderName(e.target.value)}
                className="px-3 py-2 border rounded"
              />
              <input
                type="text"
                placeholder="Company Name"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="px-3 py-2 border rounded"
              />
            </div>
            <button
              onClick={handleStartRevival}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Messages'}
            </button>

            {messages.length > 0 && (
              <div className="mt-4 space-y-3">
                <p className="text-sm font-medium">Sample Messages (copy and send manually):</p>
                {messages.map((msg, i) => (
                  <div key={i} className="bg-gray-50 p-3 rounded text-sm">
                    <p className="font-medium">{msg.lead_name} ({msg.lead_email})</p>
                    <p className="text-gray-600 mt-1">Subject: {msg.subject}</p>
                    <p className="mt-2">{msg.body}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 3. Ingest Reply */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="w-5 h-5 text-green-600" />
              <h2 className="text-xl font-semibold">3. Paste Reply (Manual)</h2>
            </div>
            <ReplyForm onSubmit={handleIngestReply} loading={loading} />
          </div>

          {/* 4. Generate Report */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-4">
              <FileText className="w-5 h-5 text-orange-600" />
              <h2 className="text-xl font-semibold">4. Generate Report</h2>
            </div>
            <button
              onClick={handleGenerateReport}
              disabled={loading}
              className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50"
            >
              Generate Report
            </button>

            {report && (
              <div className="mt-4 grid grid-cols-3 gap-4">
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm text-gray-600">Leads Contacted</p>
                  <p className="text-2xl font-bold">{report.report.leads_contacted}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm text-gray-600">Replies</p>
                  <p className="text-2xl font-bold">{report.report.replies_received}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm text-gray-600">Interested</p>
                  <p className="text-2xl font-bold text-green-600">{report.report.interested_count}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm text-gray-600">Qualified</p>
                  <p className="text-2xl font-bold text-blue-600">{report.report.qualified_count}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm text-gray-600">Meetings</p>
                  <p className="text-2xl font-bold text-purple-600">{report.report.meetings_booked}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm text-gray-600">Total Fee</p>
                  <p className="text-2xl font-bold text-orange-600">£{report.report.total_fee_gbp}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ReplyForm({ onSubmit, loading }: { onSubmit: (email: string, text: string) => void; loading: boolean }) {
  const [email, setEmail] = useState('');
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email && text) {
      onSubmit(email, text);
      setText('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input
        type="email"
        placeholder="Lead Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full px-3 py-2 border rounded"
      />
      <textarea
        placeholder="Paste reply message here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        className="w-full px-3 py-2 border rounded"
      />
      <button
        type="submit"
        disabled={loading}
        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
      >
        Classify Reply
      </button>
    </form>
  );
}
