// server.js
const express = require('express');
const fetch = require('node-fetch');
const app = express();
const PORT = process.env.PORT || 3000;

// Proxy endpoint to fetch stock data
app.get('/proxy', async (req, res) => {
  const { ticker, period1, period2, interval } = req.query;
  const apiUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?period1=${period1}&period2=${period2}&interval=${interval}`;

  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch data for ${ticker}`);
    }
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).send({ error: error.message });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
