// @ts-nocheck
import { useState, useRef, DragEvent } from 'react';
import { Navigation } from '../components/Navigation';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import {
  Upload,
  FileText,
  AlertCircle,
  CheckCircle2,
  X,
  Download,
  FileSpreadsheet,
  ArrowRight,
  AlertTriangle,
  Check,
} from 'lucide-react';

interface ParsedLead {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  job_title?: string;
  notes?: string;
  _rowNumber?: number;
  _isValid?: boolean;
  _errors?: string[];
}

interface ImportProgress {
  total: number;
  processed: number;
  successful: number;
  failed: number;
}

export function LeadImport() {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [parsedLeads, setParsedLeads] = useState<ParsedLead[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [importProgress, setImportProgress] = useState<ImportProgress | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [consentGiven, setConsentGiven] = useState(true);

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const sanitizeString = (input: string | undefined): string => {
    if (!input) return '';

    // Strip HTML tags to prevent XSS
    const withoutHtml = input.replace(/<[^>]*>/g, '');

    // Remove potentially dangerous characters
    const sanitized = withoutHtml
      .replace(/[<>'"`;]/g, '') // Remove dangerous characters
      .trim();

    // Limit length to prevent DoS via large inputs
    return sanitized.slice(0, 500);
  };

  const validateLead = (lead: ParsedLead, rowNumber: number): ParsedLead => {
    const leadErrors: string[] = [];

    // Sanitize all string inputs
    const sanitizedLead: ParsedLead = {
      first_name: sanitizeString(lead.first_name),
      last_name: sanitizeString(lead.last_name),
      email: sanitizeString(lead.email),
      phone: sanitizeString(lead.phone),
      company: sanitizeString(lead.company),
      job_title: sanitizeString(lead.job_title),
      notes: sanitizeString(lead.notes),
    };

    // Validate required fields
    if (!sanitizedLead.first_name || sanitizedLead.first_name.trim() === '') {
      leadErrors.push('First name is required');
    }
    if (!sanitizedLead.last_name || sanitizedLead.last_name.trim() === '') {
      leadErrors.push('Last name is required');
    }
    if (!sanitizedLead.email || sanitizedLead.email.trim() === '') {
      leadErrors.push('Email is required');
    } else if (!validateEmail(sanitizedLead.email)) {
      leadErrors.push('Invalid email format');
    }

    // Validate phone format if provided
    if (sanitizedLead.phone && sanitizedLead.phone.length > 0) {
      const phoneRegex = /^[\d\s\-\+\(\)]+$/;
      if (!phoneRegex.test(sanitizedLead.phone)) {
        leadErrors.push('Invalid phone format');
      }
    }

    return {
      ...sanitizedLead,
      _rowNumber: rowNumber,
      _isValid: leadErrors.length === 0,
      _errors: leadErrors,
    };
  };

  const parseCSV = (text: string): ParsedLead[] => {
    const lines = text.split('\n').filter(line => line.trim());

    if (lines.length === 0) {
      throw new Error('CSV file is empty');
    }

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());

    const requiredFields = ['first_name', 'last_name', 'email'];
    const missingFields = requiredFields.filter(field => !headers.includes(field));

    if (missingFields.length > 0) {
      throw new Error(`Missing required columns: ${missingFields.join(', ')}`);
    }

    const leads: ParsedLead[] = [];

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));

      if (values.length !== headers.length) {
        continue;
      }

      const lead: any = {};
      headers.forEach((header, index) => {
        lead[header] = values[index] || '';
      });

      const validatedLead = validateLead(
        {
          first_name: lead.first_name || '',
          last_name: lead.last_name || '',
          email: lead.email || '',
          phone: lead.phone,
          company: lead.company,
          job_title: lead.job_title,
          notes: lead.notes,
        },
        i
      );

      leads.push(validatedLead);
    }

    return leads;
  };

  const handleFileSelect = async (file: File) => {
    if (!file) return;

    setFileName(file.name);
    setErrors([]);
    setSuccess(false);
    setParsing(true);

    try {
      // Read file with error handling
      let text: string;
      try {
        text = await file.text();
      } catch (readError) {
        throw new Error('Failed to read file. The file may be corrupted or too large.');
      }

      // Parse CSV with error handling
      const leads = parseCSV(text);

      if (leads.length === 0) {
        setErrors(['No valid leads found in CSV file']);
        setParsedLeads([]);
      } else {
        setParsedLeads(leads);
        const invalidCount = leads.filter(l => !l._isValid).length;
        if (invalidCount > 0) {
          setErrors([`${invalidCount} row(s) have validation errors and will be skipped`]);
        }
      }
    } catch (error: any) {
      console.error('Error parsing CSV:', error);
      setErrors([error.message || 'Failed to parse CSV file. Please ensure it is properly formatted.']);
      setParsedLeads([]);
    } finally {
      setParsing(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      await handleFileSelect(file);
    }
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file && file.type === 'text/csv') {
      await handleFileSelect(file);
    } else {
      setErrors(['Please upload a valid CSV file']);
    }
  };

  const handleImport = async () => {
    if (!user || parsedLeads.length === 0) return;

    const validLeads = parsedLeads.filter(lead => lead._isValid);
    if (validLeads.length === 0) {
      setErrors(['No valid leads to import']);
      return;
    }

    setUploading(true);
    setErrors([]);

    const progress: ImportProgress = {
      total: validLeads.length,
      processed: 0,
      successful: 0,
      failed: 0,
    };

    setImportProgress(progress);

    try {
      const batchSize = 50;
      const errorDetails: string[] = [];

      for (let i = 0; i < validLeads.length; i += batchSize) {
        const batch = validLeads.slice(i, i + batchSize);

        try {
          const leadsToInsert = batch.map(lead => {
            const { _rowNumber, _isValid, _errors, ...cleanLead } = lead;
            return {
              ...cleanLead,
              user_id: user.id,
              status: 'new',
              lead_score: 50,
              source: 'csv_import',
            };
          });

          const { error, data } = await supabase
            .from('leads')
            .insert(leadsToInsert)
            .select();

          if (error) {
            progress.failed += batch.length;
            console.error('Batch import error:', error);
            console.error('Error details:', {
              code: error.code,
              message: error.message,
              details: error.details,
              hint: error.hint
            });
            console.error('Sample lead data:', leadsToInsert[0]);

            // Collect error for display
            errorDetails.push(`Batch ${Math.floor(i / batchSize) + 1}: ${error.message}`);
          } else {
            progress.successful += data?.length || batch.length;
          }
        } catch (batchError: any) {
          // Handle unexpected errors during batch processing
          progress.failed += batch.length;
          console.error('Unexpected batch error:', batchError);
          errorDetails.push(`Batch ${Math.floor(i / batchSize) + 1}: ${batchError.message || 'Unknown error'}`);
        }

        progress.processed += batch.length;
        setImportProgress({ ...progress });
      }

      // Show results to user
      if (progress.successful > 0) {
        setSuccess(true);
        setParsedLeads([]);
        setFileName('');

        // If there were partial failures, show them
        if (errorDetails.length > 0) {
          setErrors([
            `Successfully imported ${progress.successful} leads, but ${progress.failed} failed:`,
            ...errorDetails.slice(0, 5) // Show first 5 errors only
          ]);
        }

        setTimeout(() => {
          navigate('/leads');
        }, 2000);
      } else {
        // Complete failure
        setErrors([
          'Failed to import any leads. Common issues:',
          '- Database connection problem',
          '- Invalid data format',
          '- Duplicate email addresses',
          ...errorDetails.slice(0, 3)
        ]);
      }
    } catch (error: any) {
      // Handle catastrophic errors
      console.error('Critical error importing leads:', error);
      setErrors([
        'Critical import error occurred.',
        error.message || 'Unknown error. Please try again or contact support.'
      ]);
    } finally {
      setUploading(false);
      setTimeout(() => setImportProgress(null), 3000);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const downloadTemplate = () => {
    const template =
      'first_name,last_name,email,phone,company,job_title,notes\nJohn,Doe,john.doe@example.com,555-0100,Acme Corp,CEO,Important lead from Q4 conference\nJane,Smith,jane.smith@techstart.com,555-0101,TechStart Inc,CTO,Met at AWS Summit 2024';
    const blob = new Blob([template], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rekindle_leads_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const validLeadsCount = parsedLeads.filter(l => l._isValid).length;
  const invalidLeadsCount = parsedLeads.filter(l => !l._isValid).length;

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden animate-fade-in">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[800px] h-[800px] bg-blue-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
        <div className="absolute bottom-1/4 left-1/3 w-[700px] h-[700px] bg-green-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '7s' }} />
      </div>

      <Navigation currentPage="leads" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        {/* Header */}
        <div className="mb-10">
          <button
            onClick={() => navigate('/leads')}
            className="inline-flex items-center gap-2 text-[#FF6B35] hover:text-[#F7931E] mb-4 transition-all duration-200 font-semibold hover:gap-3"
          >
            <ArrowRight className="w-5 h-5 rotate-180" />
            <span className="font-bold">Back to Leads</span>
          </button>

          <h1 className="text-5xl font-bold text-white mb-3">Import Leads</h1>
          <p className="text-xl text-gray-400 mb-6">
            Upload your CSV file or sync with your CRM to import leads
          </p>

          {/* Import Method Tabs */}
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => {}}
              className="px-6 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold rounded-xl shadow-lg"
            >
              📄 Upload CSV
            </button>
            <button
              onClick={() => alert('CRM sync coming soon! Connect your Salesforce, HubSpot, or Pipedrive account.')}
              className="px-6 py-3 glass-card glass-card-hover text-white font-bold rounded-xl border border-white/10 hover:border-orange-500/50 transition-all"
            >
              🔗 Sync CRM
            </button>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div className="glass-card p-8 mb-8 border-2 border-green-500/30 bg-green-500/10 animate-slide-up">
            <div className="flex items-start gap-4">
              <div className="p-4 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl shadow-2xl">
                <CheckCircle2 className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="font-black text-white text-2xl mb-2">Import Successful!</h3>
                <p className="text-green-300 text-lg font-medium">
                  {importProgress?.successful || 0} leads have been imported successfully. Redirecting...
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error Messages */}
        {errors.length > 0 && (
          <div className="glass-card p-8 mb-8 border-2 border-red-500/30 bg-red-500/10 animate-slide-up">
            <div className="flex items-start gap-4">
              <div className="p-4 bg-gradient-to-br from-red-500 to-pink-500 rounded-2xl shadow-2xl">
                <AlertCircle className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="font-black text-white text-2xl mb-3">Import Errors</h3>
                <ul className="text-red-300 space-y-2">
                  {errors.map((error, index) => (
                    <li key={index} className="flex items-start gap-3 font-medium">
                      <span className="text-red-400 font-bold text-lg">\u2022</span>
                      <span>{error}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <button
                onClick={() => setErrors([])}
                className="p-3 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-xl transition-all duration-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        )}

        {/* Import Progress */}
        {importProgress && (
          <div className="glass-card p-10 mb-8 border-2 border-[#FF6B35]/30 animate-scale-in">
            <div className="mb-8">
              <div className="flex justify-between items-center mb-4">
                <span className="text-2xl font-black text-white">Importing Leads...</span>
                <span className="text-2xl font-black text-[#FF6B35]">
                  {importProgress.processed} / {importProgress.total}
                </span>
              </div>
              <div className="w-full h-4 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[#FF6B35] to-[#F7931E] rounded-full transition-all duration-500 shadow-lg"
                  style={{ width: `${(importProgress.processed / importProgress.total) * 100}%` }}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <div className="flex items-center gap-4 p-6 bg-green-500/20 border border-green-500/30 rounded-2xl backdrop-blur-sm">
                <CheckCircle2 className="w-8 h-8 text-green-400" />
                <div>
                  <p className="text-xs font-bold text-green-400 uppercase tracking-wider">Successful</p>
                  <p className="text-4xl font-black text-white">{importProgress.successful}</p>
                </div>
              </div>
              <div className="flex items-center gap-4 p-6 bg-red-500/20 border border-red-500/30 rounded-2xl backdrop-blur-sm">
                <AlertCircle className="w-8 h-8 text-red-400" />
                <div>
                  <p className="text-xs font-bold text-red-400 uppercase tracking-wider">Failed</p>
                  <p className="text-4xl font-black text-white">{importProgress.failed}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Instructions Panel */}
          <div className="lg:col-span-1">
            <div className="glass-card p-8 sticky top-24">
              <div className="flex items-center gap-4 mb-8">
                <div className="p-4 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-2xl shadow-lg">
                  <FileSpreadsheet className="w-7 h-7 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">CSV Format</h2>
              </div>

              <div className="space-y-8">
                <div>
                  <h3 className="text-sm font-black text-gray-300 uppercase tracking-wider mb-4">
                    Required Columns
                  </h3>
                  <div className="space-y-3">
                    {['first_name', 'last_name', 'email'].map(field => (
                      <div key={field} className="flex items-center gap-3 text-sm">
                        <Check className="w-5 h-5 text-green-400" />
                        <code className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg font-mono text-sm text-white font-bold">
                          {field}
                        </code>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-black text-gray-300 uppercase tracking-wider mb-4">
                    Optional Columns
                  </h3>
                  <div className="space-y-3">
                    {['phone', 'company', 'job_title', 'notes'].map(field => (
                      <div key={field} className="flex items-center gap-3 text-sm text-gray-400">
                        <span className="w-5 h-5 flex items-center justify-center text-gray-500">\u2022</span>
                        <code className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg font-mono text-sm text-gray-300">
                          {field}
                        </code>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  onClick={downloadTemplate}
                  className="w-full inline-flex items-center justify-center gap-3 px-6 py-4 text-sm font-bold text-white bg-gradient-to-r from-[#FF6B35] to-[#F7931E] rounded-xl hover:shadow-2xl hover:shadow-[#FF6B35]/40 hover:scale-105 active:scale-95 transition-all duration-300 btn-shimmer"
                >
                  <Download className="w-5 h-5" />
                  Download Template
                </button>
              </div>
            </div>
          </div>

          {/* Upload Panel */}
          <div className="lg:col-span-2">
            {parsedLeads.length === 0 ? (
              <div className="glass-card p-10">
                <div
                  className={`relative border-4 border-dashed rounded-3xl p-20 text-center transition-all duration-300 ${
                    dragActive
                      ? 'border-[#FF6B35] bg-[#FF6B35]/10'
                      : 'border-white/20 hover:border-[#FF6B35]/50 hover:bg-white/5'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="csv-upload"
                    disabled={uploading || parsing}
                  />

                  {parsing ? (
                    <LoadingSpinner size="lg" text="Parsing CSV file..." />
                  ) : (
                    <>
                      <div className="mb-8">
                        <div className="inline-flex p-8 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-3xl mb-6 shadow-2xl animate-bounce-slow">
                          <Upload className="w-20 h-20 text-white" />
                        </div>
                      </div>

                      <h3 className="text-4xl font-bold text-white mb-4">
                        {dragActive ? 'Drop your file here' : 'Upload CSV File'}
                      </h3>

                      <p className="text-lg text-gray-400 mb-10 max-w-lg mx-auto">
                        Drag and drop your CSV file here, or click the button below to browse
                      </p>

                      <label
                        htmlFor="csv-upload"
                        className="inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white font-bold text-xl rounded-2xl shadow-2xl shadow-[#FF6B35]/40 hover:scale-110 active:scale-95 transition-all duration-300 cursor-pointer btn-shimmer"
                      >
                        <FileText className="w-7 h-7" />
                        Choose File
                      </label>

                      <p className="text-sm text-gray-500 mt-8">
                        Supported format: CSV (comma-separated values)
                      </p>
                    </>
                  )}
                </div>
              </div>
            ) : (
              <div className="glass-card overflow-hidden animate-slide-up">
                {/* Preview Header */}
                <div className="bg-gradient-to-r from-[#FF6B35] to-[#F7931E] px-10 py-8">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-3xl font-bold mb-2 text-white">Preview & Validate</h2>
                      <p className="text-white/80 text-lg">
                        Review your data before importing
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-5xl font-black text-white">{parsedLeads.length}</div>
                      <div className="text-sm text-white/70 font-semibold">Total Rows</div>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 p-6 bg-gray-50 border-b-2 border-gray-200">
                  <div className="flex items-center gap-3 p-4 bg-success-50 rounded-lg border-2 border-success-200">
                    <CheckCircle2 className="w-8 h-8 text-success-600 flex-shrink-0" />
                    <div>
                      <p className="text-xs font-bold text-success-600 uppercase tracking-wide">Valid Leads</p>
                      <p className="text-3xl font-bold text-success-700">{validLeadsCount}</p>
                    </div>
                  </div>

                  {invalidLeadsCount > 0 && (
                    <div className="flex items-center gap-3 p-4 bg-warning-50 rounded-lg border-2 border-warning-200">
                      <AlertTriangle className="w-8 h-8 text-warning-600 flex-shrink-0" />
                      <div>
                        <p className="text-xs font-bold text-warning-600 uppercase tracking-wide">Invalid Rows</p>
                        <p className="text-3xl font-bold text-warning-700">{invalidLeadsCount}</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Data Table */}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-100 border-b-2 border-gray-300">
                      <tr>
                        <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                          #
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                          Name
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                          Email
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                          Company
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {parsedLeads.slice(0, 20).map((lead, index) => (
                        <tr
                          key={index}
                          className={`transition-colors duration-150 ${
                            !lead._isValid ? 'bg-error-50' : 'hover:bg-gray-50'
                          }`}
                        >
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {lead._rowNumber}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-semibold text-gray-900">
                              {lead.first_name} {lead.last_name}
                            </div>
                            <div className="text-xs text-gray-500">{lead.job_title || 'N/A'}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                            {lead.email}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {lead.company || 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {lead._isValid ? (
                              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-success-100 text-success-700 text-xs font-bold rounded-full border border-success-200">
                                <Check className="w-3 h-3" />
                                Valid
                              </span>
                            ) : (
                              <div className="space-y-1">
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-error-100 text-error-700 text-xs font-bold rounded-full border border-error-200">
                                  <AlertCircle className="w-3 h-3" />
                                  Invalid
                                </span>
                                {lead._errors && lead._errors.length > 0 && (
                                  <div className="text-xs text-error-600">
                                    {lead._errors.join(', ')}
                                  </div>
                                )}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {parsedLeads.length > 20 && (
                  <div className="px-8 py-4 bg-gray-50 border-t-2 border-gray-200 text-center">
                    <p className="text-sm text-gray-600">
                      Showing first 20 of {parsedLeads.length} rows
                    </p>
                  </div>
                )}

                {/* Consent & Actions */}
                <div className="p-8 bg-gray-50 border-t-2 border-gray-200 space-y-6">
                  {/* GDPR Consent */}
                  <div className="p-6 bg-blue-50 border-2 border-blue-200 rounded-xl">
                    <label className="flex items-start gap-4 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={consentGiven}
                        onChange={(e) => setConsentGiven(e.target.checked)}
                        className="w-5 h-5 text-primary-500 focus:ring-primary-500 rounded mt-1"
                      />
                      <div>
                        <div className="text-gray-900 font-bold mb-2">
                          ✓ Marketing Consent Obtained
                        </div>
                        <div className="text-sm text-gray-700 leading-relaxed">
                          I confirm that all leads in this file have given explicit consent to receive marketing communications, 
                          or I have a legitimate business interest to contact them. This is required for GDPR/CAN-SPAM compliance.
                        </div>
                        <div className="text-xs text-gray-600 mt-2">
                          <strong>Note:</strong> Importing without consent may violate privacy laws. 
                          Learn more in our{' '}
                          <button 
                            onClick={(e) => {
                              e.preventDefault();
                              navigate('/privacy');
                            }}
                            className="text-primary-600 hover:text-primary-700 underline"
                          >
                            Privacy Policy
                          </button>.
                        </div>
                      </div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between gap-4">
                    <button
                      onClick={() => {
                        setParsedLeads([]);
                        setErrors([]);
                        setFileName('');
                        if (fileInputRef.current) {
                          fileInputRef.current.value = '';
                        }
                      }}
                      className="px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold text-base rounded-xl hover:bg-gray-100 hover:border-gray-400 active:scale-95 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-4 focus:ring-gray-100"
                      disabled={uploading}
                    >
                      Cancel
                    </button>

                    <button
                      onClick={handleImport}
                      className="flex items-center gap-3 px-10 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-brand hover:scale-105 active:scale-95 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-4 focus:ring-primary-100"
                      disabled={uploading || validLeadsCount === 0 || !consentGiven}
                    >
                      {uploading ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          Importing...
                        </>
                      ) : (
                        <>
                          <Upload className="w-5 h-5" />
                          Import {validLeadsCount} {validLeadsCount === 1 ? 'Lead' : 'Leads'}
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
