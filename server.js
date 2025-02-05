const express = require('express');
const cors = require('cors'); // Import the cors middleware
const fetch = require('node-fetch');
const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

app.get('/proxy', async (req, res) => {
  const { ticker, period1, period2, interval } = req.query;

  // Validate ticker
  if (!ticker || typeof ticker !== 'string' || ticker.trim() === '') {
    return res.status(400).send({ error: 'Invalid or missing ticker symbol' });
  }

  // Validate period1 and period2
  const parsedPeriod1 = parseInt(period1, 10);
  const parsedPeriod2 = parseInt(period2, 10);
  if (isNaN(parsedPeriod1) || isNaN(parsedPeriod2)) {
    return res.status(400).send({ error: 'Invalid or missing period1/period2 (must be Unix timestamps)' });
  }

  // Validate interval
  const validIntervals = ['1d', '5d', '1wk', '1mo', '3mo'];
  if (!validIntervals.includes(interval)) {
    return res.status(400).send({ error: 'Invalid interval (must be one of: 1d, 5d, 1wk, 1mo, 3mo)' });
  }

  const apiUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?period1=${parsedPeriod1}&period2=${parsedPeriod2}&interval=${interval}`;

  try {
    console.log('Fetching data from:', apiUrl); // Log the constructed URL
    const response = await fetch(apiUrl);

    if (!response.ok) {
      const text = await response.text(); // Read the response as text
      console.error('Yahoo Finance API error:', text); // Log the raw response
      throw new Error(`Yahoo Finance API error: ${text || response.statusText}`);
    }

    const data = await response.json();
    console.log('API Response:', data); // Log the API response

    if (!data.chart || !data.chart.result || !data.chart.result[0]) {
      throw new Error(`No data available for ${ticker}`);
    }

    res.json(data);
  } catch (error) {
    console.error('Error fetching data:', error.message); // Log the error
    res.status(500).send({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});