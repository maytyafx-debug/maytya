async function getCryptoPrice(symbol) {
  try {
    const response = await fetch(
      `https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`
    );

    if (!response.ok) {
      throw new Error("API error");
    }

    const data = await response.json();
    return Number(data.price);
  } catch (error) {
    console.error(error);
    return null;
  }
}

async function updateMarket() {
  const btc = await getCryptoPrice("BTCUSDT");
  const eth = await getCryptoPrice("ETHUSDT");

  console.log("BTC:", btc);
  console.log("ETH:", eth);
}

updateMarket();
