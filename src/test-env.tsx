// Temporary debug component to check environment variables
export function TestEnv() {
  return (
    <div style={{ padding: '20px', fontFamily: 'monospace', background: '#f0f0f0' }}>
      <h2>Environment Variables Debug</h2>
      <p><strong>VITE_SUPABASE_URL:</strong> {import.meta.env.VITE_SUPABASE_URL || 'NOT SET'}</p>
      <p><strong>VITE_SUPABASE_ANON_KEY:</strong> {import.meta.env.VITE_SUPABASE_ANON_KEY ? `${String(import.meta.env.VITE_SUPABASE_ANON_KEY).substring(0, 50)}...` : 'NOT SET'}</p>
      <p><strong>VITE_API_URL:</strong> {import.meta.env.VITE_API_URL || 'NOT SET'}</p>
      <hr />
      <p><strong>Mode:</strong> {import.meta.env.MODE}</p>
      <p><strong>DEV:</strong> {String(import.meta.env.DEV)}</p>
      <p><strong>PROD:</strong> {String(import.meta.env.PROD)}</p>
    </div>
  );
}
