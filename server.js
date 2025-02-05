const express = require('express');
const cors = require('cors'); // Import the cors middleware
const fetch = require('node-fetch');
const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

app.get('/proxy', async (req, res) => {
  const { ticker, period1, period2, interval } = req.query;
  const apiUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?period1=${period1}&period2=${period2}&interval=${interval}`;

  try {
    console.log('Fetching data from:', apiUrl); // Log the constructed URL
    const response = await fetch(apiUrl);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Yahoo Finance API error:', errorData); // Log the API error
      throw new Error(`Yahoo Finance API error: ${errorData.message || response.statusText}`);
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