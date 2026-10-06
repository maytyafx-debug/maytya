const V='metatya-v2', SHELL=['./','index.html','manifest.json','icon-192.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
// شبکه‌اول برای همه‌چیز (سایت همیشه تازه می‌ماند)؛ فقط اگر آفلاین بود از کش خوانده می‌شود.
self.addEventListener('fetch',e=>{
  const r=e.request; if(r.method!=='GET'||!r.url.startsWith(self.location.origin)) return;
  e.respondWith(fetch(r,{cache:'no-cache'}).then(x=>{ if(x.ok){const c=x.clone();caches.open(V).then(k=>k.put(r,c));} return x; })
    .catch(()=>caches.match(r).then(m=>m||caches.match('index.html'))));
});
