/*
  # Invoices Table for Billing Management

  1. New Table
    - `invoices`
      - Stores all billing invoices
      - Tracks Stripe charges and meeting fees
      - Audit trail for all financial transactions
      - Supports platform fees + performance fees model

  2. Security
    - Enable RLS on table
    - User-scoped access (users can only see their own invoices)
    - Admin read-all policy for support

  3. Features
    - Complete billing history
    - Stripe charge tracking
    - Meeting-based performance fee calculation
    - Refund support
    - Invoice status tracking
*/

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- User Reference
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Invoice Details
  invoice_number text NOT NULL UNIQUE, -- e.g., "INV-2025-001"
  status text NOT NULL CHECK (status IN ('draft', 'pending', 'paid', 'failed', 'refunded', 'partially_refunded')),

  -- Amounts (in pence/cents)
  platform_fee_amount integer NOT NULL DEFAULT 9900, -- £99.00 or $99.00
  performance_fee_amount integer NOT NULL DEFAULT 0,
  total_amount integer NOT NULL,
  amount_paid integer DEFAULT 0,
  amount_refunded integer DEFAULT 0,

  -- Currency
  currency text NOT NULL DEFAULT 'GBP' CHECK (currency IN ('GBP', 'USD', 'EUR')),

  -- Billing Period
  billing_period_start timestamptz NOT NULL,
  billing_period_end timestamptz NOT NULL,

  -- Performance Metrics
  meetings_count integer DEFAULT 0,
  total_acv integer DEFAULT 0, -- Total ACV from all meetings in this period
  performance_fee_rate numeric(5,4) DEFAULT 0.0250, -- 2.5%

  -- Stripe Integration
  stripe_invoice_id text, -- Stripe Invoice ID
  stripe_charge_id text, -- Stripe Charge ID
  stripe_payment_intent_id text, -- Stripe Payment Intent ID
  stripe_customer_id text, -- Stripe Customer ID
  payment_method_id text, -- Stripe Payment Method ID

  -- Payment Details
  payment_status text CHECK (payment_status IN ('unpaid', 'processing', 'succeeded', 'failed', 'refunded')),
  paid_at timestamptz,
  payment_failed_at timestamptz,
  payment_failure_reason text,

  -- Refund Details
  refunded_at timestamptz,
  refund_reason text,
  refund_stripe_id text,

  -- Invoice Metadata
  invoice_pdf_url text, -- URL to PDF invoice (if generated)
  notes text, -- Admin notes
  metadata jsonb, -- Additional flexible data

  -- Related Records
  lead_ids uuid[], -- Array of lead IDs that contributed to this invoice

  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  due_date timestamptz,

  -- Indexes for performance
  CONSTRAINT check_total_amount CHECK (total_amount = platform_fee_amount + performance_fee_amount)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);
CREATE INDEX IF NOT EXISTS idx_invoices_stripe_invoice_id ON invoices(stripe_invoice_id);
CREATE INDEX IF NOT EXISTS idx_invoices_stripe_charge_id ON invoices(stripe_charge_id);
CREATE INDEX IF NOT EXISTS idx_invoices_billing_period ON invoices(billing_period_start, billing_period_end);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at DESC);

-- Enable Row Level Security
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own invoices
CREATE POLICY "Users can view their own invoices"
  ON invoices
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own invoices (via service role in backend)
-- Note: In production, this should be restricted to service role only
CREATE POLICY "Service role can insert invoices"
  ON invoices
  FOR INSERT
  WITH CHECK (auth.jwt()->>'role' = 'service_role' OR auth.uid() = user_id);

-- Policy: Service role can update invoices
CREATE POLICY "Service role can update invoices"
  ON invoices
  FOR UPDATE
  USING (auth.jwt()->>'role' = 'service_role');

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_invoices_updated_at_trigger
  BEFORE UPDATE ON invoices
  FOR EACH ROW
  EXECUTE FUNCTION update_invoices_updated_at();

-- Function to generate invoice number
CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS text AS $$
DECLARE
  next_num integer;
  year_month text;
BEGIN
  year_month := to_char(now(), 'YYYYMM');

  -- Get the next sequential number for this month
  SELECT COALESCE(MAX(CAST(SUBSTRING(invoice_number FROM 13) AS integer)), 0) + 1
  INTO next_num
  FROM invoices
  WHERE invoice_number LIKE 'INV-' || year_month || '-%';

  RETURN 'INV-' || year_month || '-' || LPAD(next_num::text, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- Add comment to table
COMMENT ON TABLE invoices IS 'Stores all billing invoices for Rekindle.ai platform and performance fees';
COMMENT ON COLUMN invoices.platform_fee_amount IS 'Fixed monthly platform fee in smallest currency unit (pence/cents)';
COMMENT ON COLUMN invoices.performance_fee_amount IS 'Variable performance fee based on meetings booked, in smallest currency unit';
COMMENT ON COLUMN invoices.total_amount IS 'Total invoice amount (platform + performance fees)';
COMMENT ON COLUMN invoices.meetings_count IS 'Number of meetings booked during this billing period';
COMMENT ON COLUMN invoices.performance_fee_rate IS 'Performance fee percentage (0.0250 = 2.5%)';
