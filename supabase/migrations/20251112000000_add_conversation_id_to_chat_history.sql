-- =====================================================
-- ADD CONVERSATION_ID SUPPORT TO CHAT_HISTORY
-- Enables multiple conversations per user (stateful memory)
-- =====================================================

-- Drop existing primary key constraint
ALTER TABLE public.chat_history DROP CONSTRAINT IF EXISTS chat_history_pkey;

-- Add conversation_id column
ALTER TABLE public.chat_history 
ADD COLUMN IF NOT EXISTS conversation_id UUID DEFAULT gen_random_uuid();

-- Create new composite primary key
ALTER TABLE public.chat_history 
ADD PRIMARY KEY (user_id, conversation_id);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_chat_history_conversation_id ON public.chat_history(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_conversation ON public.chat_history(user_id, conversation_id);

-- Update existing records to have unique conversation_ids
UPDATE public.chat_history 
SET conversation_id = gen_random_uuid() 
WHERE conversation_id IS NULL;

-- Make conversation_id NOT NULL after updating existing records
ALTER TABLE public.chat_history 
ALTER COLUMN conversation_id SET NOT NULL;

-- Add comment
COMMENT ON COLUMN public.chat_history.conversation_id IS 'Unique conversation ID for stateful memory (allows multiple conversations per user)';

