import { createClient } from '@supabase/supabase-js';

// These read from the environment variables you just saved in Netlify's
// dashboard. They are never written directly in this file.
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SECRET_KEY
);

export default async (req) => {
  if (req.method !== 'GET') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const { count, error } = await supabase
      .from('subscribers')
      .select('*', { count: 'exact', head: true });

    if (error) {
      console.error('Supabase count error (full object):', error);
      return new Response(JSON.stringify({ error: 'Something went wrong' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({ count }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    console.error('Unexpected error thrown:', err);
    return new Response(JSON.stringify({ error: 'Unexpected error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
