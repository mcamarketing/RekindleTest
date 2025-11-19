-- =====================================================
-- CONVERSATION HISTORY TABLE
-- Stores Rex AI chat history for context-aware conversations
-- =====================================================

-- Create chat_history table
CREATE TABLE IF NOT EXISTS public.chat_history (
  -- Primary key
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Conversation data (max 6 turns)
  history JSONB NOT NULL DEFAULT '[]'::jsonb,

  -- Metadata
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Constraints
  CONSTRAINT history_max_turns CHECK (jsonb_array_length(history) <= 12) -- 6 turns = 12 messages (user + assistant)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON public.chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_updated_at ON public.chat_history(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own chat history
CREATE POLICY "Users can view their own chat history"
  ON public.chat_history
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chat history"
  ON public.chat_history
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own chat history"
  ON public.chat_history
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own chat history"
  ON public.chat_history
  FOR DELETE
  USING (auth.uid() = user_id);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION public.update_chat_history_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chat_history_updated_at
  BEFORE UPDATE ON public.chat_history
  FOR EACH ROW
  EXECUTE FUNCTION public.update_chat_history_updated_at();

-- Add comments
COMMENT ON TABLE public.chat_history IS 'Stores conversation history for Rex AI chat (max 6 turns per user)';
COMMENT ON COLUMN public.chat_history.history IS 'Array of conversation messages (max 12 items = 6 turns)';
COMMENT ON COLUMN public.chat_history.user_id IS 'Foreign key to auth.users';

-- Example data structure for history JSONB field:
-- [
--   {"role": "user", "content": "Hello", "timestamp": "2025-11-12T00:00:00Z"},
--   {"role": "assistant", "content": "Hi! How can I help?", "timestamp": "2025-11-12T00:00:01Z"},
--   ...
-- ]

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.chat_history TO authenticated;
-- GRANT USAGE ON SCHEMA public TO authenticated;
