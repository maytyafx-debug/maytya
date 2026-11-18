// METATYA Agents — isolated staging Worker for TIA and MAHNOOSH MVP.
// This Worker is intentionally separate from the production Telegram sales-bot Worker.
const MODEL = '@cf/meta/llama-3.3-70b-instruct-fp8-fast';
const hits = new Map();
const ALLOWED_ORIGINS = new Set(['https://maytyafx-debug.github.io']);
const PERSONAS = {
  tia: {
    name: 'تیا',
    identity: 'جنتلمن دیجیتال؛ متین، صادق، محترمانه، دقیق و راه‌حل‌محور.',
    mission: 'نیاز کاربر را روشن کن، مسئله را ساختار بده، گزینه‌های عملی و گام بعدی پیشنهاد بده.'
  },
  mahnoosh: {
    name: 'ماه‌نوش',
    identity: 'بانوی دانا و الهام‌بخش با ریشه و زیبایی‌شناسی ایرانی؛ آرام، خلاق و خردمند.',
    mission: 'با نگاه خلاق و آموزشی به مسئله نگاه کن و ایده‌های تازه اما قابل‌اجرا پیشنهاد بده.'
  }
};

function cors(origin) {
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.has(origin) ? origin : 'null',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin'
  };
}
function json(data, status, origin) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...cors(origin), 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }
  });
}
async function generate(env, persona, messages, sharedContext = '') {
  const p = PERSONAS[persona];
  const system = [
    'تو یکی از عامل‌های هوشمند اکوسیستم METATYA هستی.',
    'هویت تو: ' + p.name + '. ' + p.identity,
    'ماموریت: ' + p.mission,
    'به فارسی روان پاسخ بده مگر کاربر زبان دیگری بخواهد.',
    'شفاف باش؛ هرگز ادعا نکن کاری را انجام داده‌ای یا داده‌ای را بررسی کرده‌ای مگر واقعاً انجام شده باشد.',
    'اگر اطلاعات کافی نداری سؤال روشن‌کننده بپرس. ایده‌ها را به مراحل کوچک و قابل‌آزمایش تبدیل کن.',
    'رمز، کلید API، اطلاعات بانکی یا داده خصوصی مشتری را درخواست نکن.',
    'در موضوعات مالی، پزشکی و حقوقی فقط اطلاعات عمومی و محتاطانه بده و از توصیه قطعی تخصصی خودداری کن.',
    sharedContext ? 'زمینه همکاری: ' + sharedContext : ''
  ].filter(Boolean).join('\n');
  const safeMessages = messages.slice(-12).map(m => ({
    role: m.role,
    content: String(m.content || '').slice(0, 1800)
  }));
  const result = await env.AI.run(MODEL, {
    messages: [{ role: 'system', content: system }, ...safeMessages],
    max_tokens: 650,
    temperature: 0.55
  });
  return String((result && (result.response || result.result)) || '').trim();
}
async function chat(req, env) {
  const origin = req.headers.get('Origin') || '';
  if (!ALLOWED_ORIGINS.has(origin)) return json({ error: 'origin_not_allowed' }, 403, origin);
  let body;
  try { body = await req.json(); }
  catch (_) { return json({ error: 'invalid_json' }, 400, origin); }

  const persona = String(body.persona || '');
  if (!['tia', 'mahnoosh', 'duo'].includes(persona)) return json({ error: 'invalid_persona' }, 400, origin);
  if (!Array.isArray(body.messages) || !body.messages.length || body.messages.length > 12) {
    return json({ error: 'messages_required_or_limit_exceeded' }, 400, origin);
  }
  const messages = body.messages.map(m => ({
    role: m.role,
    content: String(m.content || '').slice(0, 1800)
  }));
  const total = messages.reduce((n, m) => n + m.content.length, 0);
  if (total > 9000 || messages.some(m => !['user', 'assistant'].includes(m.role) || !m.content.trim())) {
    return json({ error: 'message_limit_exceeded' }, 413, origin);
  }

  // Basic prototype throttle. Production rollout must add Cloudflare rate limiting / abuse protection.
  const ip = req.headers.get('CF-Connecting-IP') || 'unknown';
  const key = 'agent:' + ip;
  const now = Date.now();
  const recent = (hits.get(key) || []).filter(t => now - t < 60000);
  if (recent.length >= 8) return json({ error: 'rate_limited', message: 'کمی مکث کن و یک دقیقه دیگر دوباره تلاش کن.' }, 429, origin);
  recent.push(now);
  hits.set(key, recent);

  try {
    if (persona === 'duo') {
      const tia = await generate(env, 'tia', messages);
      const mahnoosh = await generate(
        env,
        'mahnoosh',
        [...messages, { role: 'assistant', content: 'دیدگاه تیا برای بررسی: ' + tia }],
        'تیا این دیدگاه را ارائه کرده است: ' + tia + ' ماه‌نوش باید آن را تکمیل یا نقد سازنده کند.'
      );
      return json({ ok: true, replies: [{ persona: 'tia', text: tia }, { persona: 'mahnoosh', text: mahnoosh }] }, 200, origin);
    }
    const answer = await generate(env, persona, messages);
    if (!answer) throw new Error('empty model response');
    return json({ ok: true, persona, text: answer }, 200, origin);
  } catch (error) {
    console.log('agent_error', String(error).slice(0, 180));
    return json({ error: 'agent_unavailable', message: 'فعلاً پاسخ‌گویی در دسترس نیست. کمی بعد دوباره تلاش کن.' }, 503, origin);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'GET' && url.pathname === '/health') {
      return Response.json({ ok: true, service: 'metatya-agents-staging', personas: ['tia', 'mahnoosh', 'duo'] });
    }
    if (url.pathname !== '/api/agents/chat') return new Response('Not found', { status: 404 });
    const origin = request.headers.get('Origin') || '';
    if (request.method === 'OPTIONS') {
      if (!ALLOWED_ORIGINS.has(origin)) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: cors(origin) });
    }
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405 });
    return chat(request, env);
  }
};
