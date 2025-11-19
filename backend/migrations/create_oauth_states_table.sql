-- =====================================================
-- OAUTH STATE TOKENS TABLE
-- Stores cryptographically secure state tokens for OAuth CSRF protection
-- =====================================================

-- Create oauth_states table
CREATE TABLE IF NOT EXISTS public.oauth_states (
  -- Primary key
  state_token TEXT PRIMARY KEY,

  -- Associated user
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Provider (google, microsoft)
  provider TEXT NOT NULL CHECK (provider IN ('google', 'microsoft')),

  -- Expiration (10 minutes from creation)
  expires_at TIMESTAMPTZ NOT NULL,

  -- Metadata
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_oauth_states_user_id ON public.oauth_states(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth_states_expires_at ON public.oauth_states(expires_at);

-- Enable Row Level Security
ALTER TABLE public.oauth_states ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own OAuth states
CREATE POLICY "Users can view their own OAuth states"
  ON public.oauth_states
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own OAuth states"
  ON public.oauth_states
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own OAuth states"
  ON public.oauth_states
  FOR DELETE
  USING (auth.uid() = user_id);

-- Automatic cleanup of expired tokens (runs every 5 minutes)
CREATE OR REPLACE FUNCTION public.cleanup_expired_oauth_states()
RETURNS void AS $$
BEGIN
  DELETE FROM public.oauth_states
  WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule cleanup (using pg_cron extension if available)
-- SELECT cron.schedule('cleanup-oauth-states', '*/5 * * * *', 'SELECT public.cleanup_expired_oauth_states()');

-- Add comments
COMMENT ON TABLE public.oauth_states IS 'Stores cryptographically secure state tokens for OAuth CSRF protection';
COMMENT ON COLUMN public.oauth_states.state_token IS 'Cryptographically random token (32 bytes, URL-safe)';
COMMENT ON COLUMN public.oauth_states.expires_at IS 'Expiration timestamp (10 minutes from creation)';

-- Grant permissions
-- GRANT SELECT, INSERT, DELETE ON public.oauth_states TO authenticated;
-- GRANT USAGE ON SCHEMA public TO authenticated;
