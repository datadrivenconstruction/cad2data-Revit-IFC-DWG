interface Env {
  ANALYTICS_DB: D1Database;
  API_TOKEN: string;
}

export const onRequest: PagesFunction<Env> = async (context) => {
  // CORS headers for the dashboard SPA
  if (context.request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
      },
    });
  }

  const authHeader = context.request.headers.get('Authorization');

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return Response.json(
      { error: 'Missing or invalid Authorization header' },
      { status: 401 }
    );
  }

  const token = authHeader.slice(7);
  if (token !== context.env.API_TOKEN) {
    return Response.json({ error: 'Invalid API token' }, { status: 403 });
  }

  const response = await context.next();

  // Add CORS headers to all responses
  const newResponse = new Response(response.body, response);
  newResponse.headers.set('Access-Control-Allow-Origin', '*');
  return newResponse;
};
