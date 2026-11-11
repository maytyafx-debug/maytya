(() => {
  "use strict";

  const MetatyaData = {
    brand: {
      name: "Metatya",
      persianName: "مایتیا",
      slogan: "با قانون معامله کن، نه با هیجان",
      description: "پلتفرم آموزشی، تحلیلی و توسعه مهارت‌های مالی و فردی",
      telegram: "https://t.me/Maytyafx"
    },

    pillars: [
      {
        id: "forex",
        title: "بازار فارکس",
        icon: "💱",
        description: "آشنایی با ساختار بازار ارز، تحلیل و مدیریت ریسک",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "green"
      },
      {
        id: "crypto",
        title: "بازار رمزارزها",
        icon: "₿",
        description: "شناخت دارایی‌های دیجیتال، فناوری بلاکچین و بازار",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "gold"
      },
      {
        id: "stocks",
        title: "بورس و سرمایه‌گذاری",
        icon: "📈",
        description: "آموزش مفاهیم سهام، شاخص‌ها و تحلیل شرکت‌ها",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "green"
      },
      {
        id: "income",
        title: "مدیریت درآمد",
        icon: "💰",
        description: "سواد مالی، برنامه‌ریزی درآمد و شناخت جریان نقدی",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "gold"
      },
      {
        id: "business",
        title: "کسب‌وکار",
        icon: "🏢",
        description: "مدیریت کسب‌وکار، مدل درآمدی و توسعه محصول",
        tracks: ["مقدماتی", "حرفه‌ای"],
        color: "green"
      },
      {
        id: "personal-finance",
        title: "مالی شخصی",
        icon: "🧮",
        description: "بودجه‌بندی، پس‌انداز، تصمیم‌گیری و برنامه مالی",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "gold"
      },
      {
        id: "education",
        title: "آموزش و مهارت",
        icon: "🎓",
        description: "یادگیری ساختاریافته، تمرین و ارزیابی پیشرفت",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "green"
      },
      {
        id: "law",
        title: "حقوق و قوانین",
        icon: "⚖️",
        description: "آشنایی آموزشی با مقررات و مسئولیت‌های مالی",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "gold"
      },
      {
        id: "psychology",
        title: "روان‌شناسی و تصمیم‌گیری",
        icon: "🧠",
        description: "شناخت سوگیری‌ها، تمرکز و تصمیم‌گیری منطقی",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "green"
      },
      {
        id: "ai",
        title: "هوش مصنوعی",
        icon: "🤖",
        description: "کاربردهای هوش مصنوعی، اتوماسیون و ابزارهای هوشمند",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "gold"
      },
      {
        id: "privacy",
        title: "امنیت و حریم خصوصی",
        icon: "🔐",
        description: "امنیت دیجیتال، حفاظت اطلاعات و رفتار امن آنلاین",
        tracks: ["مقدماتی", "پیشرفته"],
        color: "green"
      }
    ],

    products: [
      {
        id: "lite",
        title: "دفترچه معاملات LITE",
        level: "رایگان",
        description: "شروع ثبت و مرور منظم تصمیم‌ها و یادگیری",
        features: [
          "ثبت فعالیت‌ها",
          "ساختار ساده مرور",
          "جعبه‌ابزار مقدماتی"
        ],
        action: "دریافت نسخه رایگان",
        url: "https://t.me/maytya?direct"
      },
      {
        id: "pro",
        title: "دفترچه معاملات PRO",
        level: "حرفه‌ای",
        description: "ساختار جامع ثبت، تحلیل و ارزیابی عملکرد",
        features: [
          "بیش از ۱۰۰۰ فرمول و محاسبه",
          "داشبورد آماری",
          "ابزارهای مدیریت ریسک",
          "گزارش‌های پیشرفته"
        ],
        action: "استعلام مشخصات و قیمت",
        url: "https://t.me/maytya?direct"
      },
      {
        id: "master",
        title: "بسته MASTER",
        level: "جامع",
        description: "ترکیب ابزارهای PRO و آموزش ساختاریافته",
        features: [
          "امکانات PRO",
          "محتوای آموزشی تکمیلی",
          "مسیرهای تمرین",
          "راهنمای استفاده"
        ],
        action: "استعلام مشخصات و قیمت",
        url: "https://t.me/maytya?direct"
      },
      {
        id: "consultation",
        title: "جلسه مشاوره آموزشی",
        level: "اختصاصی",
        description: "جلسه آموزشی برای بررسی مسیر یادگیری و نیازها",
        features: [
          "۳۰ دقیقه جلسه",
          "بررسی اهداف آموزشی",
          "ارائه نقشه راه یادگیری"
        ],
        action: "دریافت اطلاعات",
        url: "https://t.me/maytya?direct"
      }
    ],

    fitTracks: [
      {
        id: "fit-starter",
        title: "مسیر شروع FIT",
        audience: "تازه‌واردان",
        description: "آشنایی با اصول پایه، ایمنی و مهارت‌های حرکتی",
        modules: [
          "شناخت تجهیزات",
          "اصول ایمنی",
          "آشنایی با مهارت‌های پایه",
          "تمرین‌های متناسب با سطح"
        ]
      },
      {
        id: "fit-competitive",
        title: "مسیر رقابتی FIT",
        audience: "ورزشکاران رقابتی",
        description: "آمادگی فنی و ذهنی برای حضور در رقابت‌ها",
        modules: [
          "برنامه‌ریزی تمرین",
          "تکنیک و هماهنگی",
          "تمرکز و مدیریت فشار",
          "ارزیابی مهارت"
        ]
      },
      {
        id: "fit-elite",
        title: "مسیر قهرمانی FIT",
        audience: "ورزشکاران سطح بالا",
        description: "مسیر تخصصی توسعه عملکرد با نظارت مربی واجد صلاحیت",
        modules: [
          "تحلیل عملکرد فنی",
          "برنامه‌ریزی دوره‌ای",
          "آمادگی ذهنی",
          "بازبینی و ارزیابی تخصصی"
        ]
      }
    ],

    contentCategories: [
      "مقدماتی",
      "پیشرفته",
      "تحلیل",
      "آموزش",
      "روان‌شناسی",
      "مدیریت ریسک",
      "امنیت",
      "ابزارها"
    ],

    getPillar(id) {
      return this.pillars.find(item => item.id === id) || null;
    },

    getProduct(id) {
      return this.products.find(item => item.id === id) || null;
    },

    getFitTrack(id) {
      return this.fitTracks.find(item => item.id === id) || null;
    }
  };

  window.MetatyaData = MetatyaData;
})();
