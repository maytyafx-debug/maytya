/* Metatya CTA: فرم ایمیل، پیشنهادهای درآمدی، دکمه‌های مثلث طلایی، اشتراک‌گذاری. بدون وابستگی. */
(function(){
  var CFG={url:'https://megbqtoihsuouiaxpifl.supabase.co',
    key:'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZ2JxdG9paHN1b3VpYXhwaWZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA3ODYzNDEsImV4cCI6MjEwNjM2MjM0MX0.x7aDRiSPd6F6XkjdZ7EIQUf5bU8Qf6PKrZUECzNEZzU',
    links:[['✈️','تلگرام','https://t.me/maytya'],['▶️','یوتیوب','https://www.youtube.com/@maytyaFx'],['📸','اینستاگرام','https://instagram.com/maytyafx']]};
  // منبع ورود (اولین لمس): utm_source/ref یا دامنه‌ی ارجاع‌دهنده؛ در localStorage می‌ماند تا به لید وصل شود. هیچ داده‌ی شخصی ذخیره نمی‌شود.
  function detect(){
    try{
      var q=new URLSearchParams(location.search),src=(q.get('utm_source')||q.get('ref')||'').toLowerCase(),camp=(q.get('utm_campaign')||'').toLowerCase();
      src=({t:'telegram',y:'youtube',i:'instagram',g:'google',w:'whatsapp'})[src]||src;
      if(!src&&document.referrer){var h=new URL(document.referrer).hostname.replace(/^www\./,'');
        if(h===location.hostname)return null;
        src=/youtube\.com|youtu\.be/.test(h)?'youtube':/instagram\.com/.test(h)?'instagram':/(^|\.)t\.me$|telegram\.(org|me)/.test(h)?'telegram':/google\./.test(h)?'google':/bing\.com/.test(h)?'bing':/(^|\.)(twitter|x)\.com$/.test(h)?'x':h.slice(0,24)}
      if(!src)return null;return{src:src.slice(0,20),camp:camp.slice(0,20)}
    }catch(e){return null}}
  function touch(){var d=detect(),st=null;
    try{st=JSON.parse(localStorage.getItem('mt_src')||'null')}catch(e){}
    if(d&&!st){st={src:d.src,camp:d.camp,ts:Date.now()};try{localStorage.setItem('mt_src',JSON.stringify(st))}catch(e){}}
    return{now:d,first:st}}
  var TOUCH=touch();
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function safe(u){return /^https?:\/\//i.test(u||'')?esc(u):'#'}
  function rel(u){return /^[a-z0-9_\-\/]+\.html(#[\w\-]*)?(\?.*)?$/i.test(u||'')}
  function utm(u,src){if(rel(u))return u;try{var x=new URL(u);if(!/t\.me$/.test(x.hostname)){x.searchParams.set('utm_source','metatya');x.searchParams.set('utm_medium',src||'site')}return x.href}catch(e){return u}}
  var CSS='.mt-box{background:var(--card,#fff);border:1px solid var(--line,#dce6e2);border-radius:14px;padding:14px 16px;margin:14px 0;font-family:inherit;color:var(--ink,#0f241f)}.mt-box h3{font-size:14.5px;margin-bottom:6px}.mt-box p{font-size:12.5px;line-height:1.9;color:var(--sub,#4c635d)}.mt-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.mt-btn{flex:1 1 90px;text-align:center;text-decoration:none;font-size:12.5px;padding:9px 8px;border-radius:10px;border:1px solid var(--line,#dce6e2);color:var(--ink,#0f241f);background:var(--card,#fff);font-family:inherit;cursor:pointer}.mt-btn.pri{background:var(--teal,#1f6f63);color:#fff;border-color:var(--teal,#1f6f63)}.mt-form input[type=email]{width:100%;border:1px solid var(--line,#dce6e2);border-radius:10px;padding:10px 12px;font-family:inherit;font-size:13px;margin-top:8px;direction:ltr;text-align:left;background:var(--bg,#fff);color:var(--ink,#0f241f)}.mt-form label{display:flex;gap:8px;font-size:11.5px;color:var(--sub,#4c635d);margin-top:8px;line-height:1.7}.mt-msg{font-size:12px;margin-top:8px}.mt-off{border-top:1px dashed var(--line,#dce6e2);padding-top:10px;margin-top:10px}.mt-off b{font-size:13.5px}.mt-tag{font-size:10.5px;color:var(--gold,#c08a2e);margin-right:6px}.mt-disc{font-size:10.5px;color:var(--sub,#4c635d);margin-top:8px;line-height:1.8}';
  function css(){if(document.getElementById('mt-css'))return;var s=document.createElement('style');s.id='mt-css';s.textContent=CSS;document.head.appendChild(s)}
  function social(el,src){css();var h='<div class="mt-box"><h3>همراه Metatya باشید</h3><p>تحلیل کوتاه و اعلان محتوای جدید را در کانال‌ها دنبال کنید.</p><div class="mt-row">';
    CFG.links.forEach(function(l,i){h+='<a class="mt-btn'+(i===0?' pri':'')+'" target="_blank" rel="noopener" href="'+safe(utm(l[2],src))+'">'+l[0]+' '+l[1]+'</a>'});
    el.insertAdjacentHTML('beforeend',h+'</div></div>')}
  function lead(el,src){css();var id='mtf'+Math.random().toString(36).slice(2,7);
    el.insertAdjacentHTML('beforeend','<div class="mt-box mt-form" id="'+id+'"><h3>خبرنامه Metatya</h3><p>هفته‌ای یک‌بار خلاصه‌ی تحلیل‌ها و آموزش‌های تازه، بدون اسپم.</p><input type="email" placeholder="you@example.com" autocomplete="email" aria-label="ایمیل"><label><input type="checkbox"> با دریافت ایمیل از Metatya موافقم و می‌دانم هر زمان می‌توانم لغو کنم.</label><div class="mt-row"><button class="mt-btn pri" type="button">عضویت</button></div><div class="mt-msg" role="status"></div></div>');
    var box=document.getElementById(id),inp=box.querySelector('input[type=email]'),ck=box.querySelector('input[type=checkbox]'),msg=box.querySelector('.mt-msg');
    box.querySelector('button').onclick=function(){
      var e=(inp.value||'').trim();
      if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(e)){msg.textContent='ایمیل معتبر وارد کنید.';return}
      if(!ck.checked){msg.textContent='برای عضویت، تیک موافقت را بزنید.';return}
      msg.textContent='در حال ثبت...';
      fetch(CFG.url+'/rest/v1/leads',{method:'POST',headers:{apikey:CFG.key,Authorization:'Bearer '+CFG.key,'Content-Type':'application/json',Prefer:'return=minimal'},body:JSON.stringify({email:e,source:((TOUCH.first?TOUCH.first.src+(TOUCH.first.camp?'/'+TOUCH.first.camp:''):'direct')+'|'+String(src||'site')).slice(0,60),consent:true})})
        .then(function(r){msg.textContent=r.ok?'ثبت شد ✅ ممنون!':(r.status===409?'این ایمیل قبلاً ثبت شده است.':'ثبت نشد؛ کمی بعد دوباره امتحان کنید.')})
        .catch(function(){msg.textContent='خطای اتصال؛ دوباره امتحان کنید.'})}}
  function local(u){return rel(u)||/^downloads\/[\w.\-]+$/.test(u||'')}
  function offers(el,section,base){css();
    fetch((base||'')+'monetization.json',{cache:'no-cache'}).then(function(r){return r.ok?r.json():null}).then(function(d){
      if(!d||!d.items)return;
      var L=d.items.filter(function(i){return i&&i.active!==false&&i.url&&(local(i.url)||/^https?:\/\//i.test(i.url))&&(!i.sections||i.sections.indexOf('all')>-1||i.sections.indexOf(section)>-1)}).slice(0,3);
      if(!L.length)return;
      var T={free:'هدیه رایگان',affiliate:'لینک معرفی',product:'محصول Metatya',service:'خدمت Metatya'};
      var h='<div class="mt-box"><h3>پیشنهادهای Metatya</h3>';
      L.forEach(function(i){
        var href=local(i.url)?esc((base||'')+i.url):safe(utm(i.url,'offer'));
        var rl=(i.type==='affiliate'?'sponsored ':'')+'noopener';
        var im=(i.image&&/^downloads\/[\w.\-]+$/.test(i.image))?'<img alt="'+esc(i.title)+'" loading="lazy" src="'+esc((base||'')+i.image)+'" style="width:100%;border-radius:12px;margin:6px 0">':'';
        h+='<div class="mt-off">'+im+'<span class="mt-tag">'+esc(T[i.type]||'پیشنهاد')+'</span><b>'+esc(i.title)+'</b><p>'+esc(i.description||'')+'</p><div class="mt-row"><a class="mt-btn pri"'+(i.type==='free'?' download':'')+' target="_blank" rel="'+rl+'" href="'+href+'">'+esc(i.cta||'مشاهده')+'</a></div></div>';
      });
      h+='<div class="mt-disc">'+esc(d.disclosure||'برخی لینک‌ها معرفی هستند و ممکن است برای Metatya کمیسیون داشته باشند؛ هزینه‌ی شما تغییر نمی‌کند. این‌ها توصیه‌ی سرمایه‌گذاری نیستند.')+'</div></div>';
      el.insertAdjacentHTML('beforeend',h)}).catch(function(){})}
  function share(btn,title){btn.onclick=function(){var u=location.href;if(navigator.share){navigator.share({title:title||document.title,url:u}).catch(function(){})}else if(navigator.clipboard){navigator.clipboard.writeText(u);btn.textContent='لینک کپی شد ✅'}}}
  window.MetatyaCTA={touch:TOUCH,social:social,lead:lead,offers:offers,share:share,esc:esc,safe:safe};
})();
