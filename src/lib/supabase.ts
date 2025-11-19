import { createClient } from '@supabase/supabase-js';

// Production-ready: Use environment variables only
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Strict validation - fail fast if missing
if (!supabaseUrl || !supabaseAnonKey) {
  const error = 'Missing required Supabase environment variables. ' +
    'Ensure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are set in .env.local';
  console.error('❌ SUPABASE CONFIG ERROR:', error);
  throw new Error(error);
}

// Validate URL format
if (!supabaseUrl.startsWith('https://') || !supabaseUrl.includes('.supabase.co')) {
  const error = `Invalid Supabase URL format: ${supabaseUrl}. Expected: https://xxx.supabase.co`;
  console.error('❌ SUPABASE URL ERROR:', error);
  throw new Error(error);
}

// Validate anon key format (JWT should start with 'eyJ')
if (!supabaseAnonKey.startsWith('eyJ')) {
  const error = 'Invalid Supabase anon key format. Expected JWT starting with "eyJ"';
  console.error('❌ SUPABASE KEY ERROR:', error);
  throw new Error(error);
}

// Development-only logging
if (import.meta.env.DEV) {
  console.log('✅ Supabase client initialized:', supabaseUrl);
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
