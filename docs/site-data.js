/* بارگذاری داده‌ی حوزه‌ها و پک‌ها.
   اولویت با نسخه‌ای است که از پنل ادمین در Supabase ذخیره شده (جدول site_content).
   اگر آن نبود، یا Supabase در دسترس نبود، همان فایل GitHub (topics.json / packs.json) خوانده می‌شود. */
(function () {
  var DB = window.METATYA_DB || {};
  function fromFile(url) {
    return fetch(url, { cache: 'no-cache' }).then(function (r) { return r.json(); });
  }
  window.MetatyaData = {
    load: function (key, fileUrl) {
      if (!DB.url || !DB.anon) return fromFile(fileUrl);
      var base = DB.url.replace(/\/$/, '');
      var url = base + '/rest/v1/site_content?select=value&key=eq.' + encodeURIComponent(key);
      return fetch(url, { headers: { apikey: DB.anon, Authorization: 'Bearer ' + DB.anon } })
        .then(function (r) { return r.ok ? r.json() : []; })
        .then(function (rows) {
          if (rows && rows[0] && rows[0].value) return rows[0].value;
          return fromFile(fileUrl);
        })
        .catch(function () { return fromFile(fileUrl); });
    }
  };
})();
