const API = "https://api.binance.com/api/v3/klines";

async function getCandles(symbol, interval) {
  const response = await fetch(
    `${API}?symbol=${symbol}&interval=${interval}&limit=50`
  );

  if (!response.ok) {
    throw new Error("خطا در دریافت داده");
  }

  return await response.json();
}

function analyze(candles) {

  const closes = candles.map(c => Number(c[4]));
  const highs = candles.map(c => Number(c[2]));
  const lows = candles.map(c => Number(c[3]));

  const price = closes[closes.length - 1];

  const short = closes.slice(-10);
  const long = closes.slice(-30);

  const shortAvg =
    short.reduce((a,b) => a + b, 0) / short.length;

  const longAvg =
    long.reduce((a,b) => a + b, 0) / long.length;

  let trend;

  if (shortAvg > longAvg) {
    trend = "🟢 صعودی";
  } else if (shortAvg < longAvg) {
    trend = "🔴 نزولی";
  } else {
    trend = "🟡 خنثی";
  }

  const resistance = Math.max(...highs.slice(-20));
  const support = Math.min(...lows.slice(-20));

  return {
    price,
    trend,
    support,
    resistance
  };
}


async function getAnalysis(symbol, interval) {

  try {

    const candles = await getCandles(symbol, interval);

    const result = analyze(candles);

    return `
💰 قیمت: $${result.price.toLocaleString(undefined,{
      maximumFractionDigits:2
    })}

📈 روند: ${result.trend}

🟢 حمایت: $${result.support.toLocaleString(undefined,{
      maximumFractionDigits:2
    })}

🔴 مقاومت: $${result.resistance.toLocaleString(undefined,{
      maximumFractionDigits:2
    })}

⏱ تایم‌فریم: ${interval}

⚠️ تحلیل خودکار و آموزشی است.
`;

  } catch (error) {

    console.error(error);

    return "⚠️ دریافت اطلاعات بازار با مشکل مواجه شد.";
  }
}


async function showTimeframe(timeframe) {

  const btc = await getAnalysis("BTCUSDT", timeframe);

  alert(
    "₿ تحلیل بیت‌کوین\n\n" +
    btc
  );
}


async function updateMarket() {

  try {

    const btc = await getCryptoPrice("BTCUSDT");
    const eth = await getCryptoPrice("ETHUSDT");

    const btcElement = document.getElementById("btcPrice");
    const ethElement = document.getElementById("ethPrice");

    if (btc) {
      btcElement.innerText =
        "$" + btc.toLocaleString(undefined,{
          maximumFractionDigits:2
        });
      btcElement.classList.remove("loading");
    }

    if (eth) {
      ethElement.innerText =
        "$" + eth.toLocaleString(undefined,{
          maximumFractionDigits:2
        });
      ethElement.classList.remove("loading");
    }

  } catch(error) {

    console.error(error);

  }
}


async function getCryptoPrice(symbol) {

  const response = await fetch(
    `https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`
  );

  if (!response.ok) {
    throw new Error("API error");
  }

  const data = await response.json();

  return Number(data.price);
}


updateMarket();

setInterval(updateMarket, 30000);
