const V='metatya-v2';
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(['./','index.html','manifest.json','icon-192.png']).catch(()=>{})).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
// صفحه‌ها و json: اول شبکه (همیشه تازه)، اگر آفلاین بود کش. فایل‌های ثابت (آیکن و فونت): اول کش.
self.addEventListener('fetch',e=>{
  const r=e.request; if(r.method!=='GET'||!r.url.startsWith(self.location.origin)) return;
  const net=r.mode==='navigate'||/\.(json|html|js)(\?|$)/.test(r.url);
  const put=x=>{const c=x.clone();caches.open(V).then(k=>k.put(r,c));return x};
  e.respondWith(net?fetch(r).then(put).catch(()=>caches.match(r)):caches.match(r).then(m=>m||fetch(r).then(put)));
});
