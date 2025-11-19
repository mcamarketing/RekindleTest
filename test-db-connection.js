// Quick script to test Supabase connection
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://jnhbmemmwtsrfhlztmyq.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpuaGJtZW1td3RzcmZobHp0bXlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3Nzc5MjYsImV4cCI6MjA3ODM1MzkyNn0.3jxVHd_wcAHFhiIW7_6ZajCfpFOVlFsZsYn_rZeB-pw';

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
  console.log('🔍 Testing Supabase connection...\n');

  try {
    // Test 1: Check auth
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError) throw authError;
    console.log('✅ Auth connection: OK');
    console.log('   Current user:', session ? session.user.email : 'Not logged in');

    // Test 2: Check tables exist
    const { data: leads, error: leadsError } = await supabase.from('leads').select('count');
    if (leadsError) throw leadsError;
    console.log('✅ Leads table: OK');

    const { data: campaigns, error: campaignsError } = await supabase.from('campaigns').select('count');
    if (campaignsError) throw campaignsError;
    console.log('✅ Campaigns table: OK');

    const { data: messages, error: messagesError } = await supabase.from('messages').select('count');
    if (messagesError) throw messagesError;
    console.log('✅ Messages table: OK');

    console.log('\n🎉 Database connection successful!');
    console.log('   Your REKINDLE application is ready to use!');

  } catch (error) {
    console.error('❌ Connection failed:', error.message);
  }
}

testConnection();
