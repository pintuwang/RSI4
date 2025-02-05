from flask import Flask, request, render_template, send_file
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pytz import timezone
import io

app = Flask(__name__)

def calculate_rsi(price_series, period):
    if period <= 0:
        return pd.Series(index=price_series.index)
    
    delta = price_series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)
    return 100.0 - (100.0 / (1.0 + rs))

def weighted_rsi(data, periods):
    valid_periods = [p for p in periods if p > 0]
    rsi_df = pd.DataFrame(index=data.index)
    
    for period in valid_periods:
        rsi_values = calculate_rsi(data['Close'], period)
        volume = data['Volume'].squeeze()
        
        numerator = (rsi_values * volume).rolling(window=period, min_periods=1).sum()
        denominator = volume.rolling(window=period, min_periods=1).sum().replace(0, np.finfo(float).eps)
        volume_weighted_rsi = numerator / denominator
        
        rsi_df[f'RSI_{period}'] = rsi_values
        rsi_df[f'Weighted_RSI_{period}'] = volume_weighted_rsi
    
    return rsi_df

def generate_charts(stock_ticker, periods):
    try:
        valid_periods = [int(p.strip()) for p in periods.split(',') if int(p.strip()) > 0][:3]
        
        if not valid_periods:
            return None, "Please enter up to 3 positive RSI periods"
        
        stock_data = yf.download(stock_ticker, period='1y')
        
        if stock_data.empty:
            return None, f"No data available for {stock_ticker}"
        
        stock_data['Volume'] = stock_data['Volume'].astype(float).fillna(0)
        
        rsi_data = weighted_rsi(stock_data, valid_periods)
        
        singapore_timezone = timezone('Asia/Singapore')
        now = datetime.now(singapore_timezone)
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        fig, axs = plt.subplots(3, 1, sharex=True, figsize=(12, 15))
        fig.suptitle(f'{stock_ticker} - Price, Volume, RSI Analysis - Generated(SG Time): {formatted_time}', fontsize=16)
        
        # Price and Volume plot
        axs[0].plot(stock_data.index, stock_data['Close'], color='blue', label='Close Price')
        axs[0].set_ylabel('Price')
        axs[0].legend(loc='upper left')
        
        volume_ax = axs[0].twinx()
        volume_ax.set_yscale('linear')
        volume_ax.plot(stock_data.index, stock_data['Volume'], 'r-', alpha=0.5, label='Volume')
        volume_ax.fill_between(stock_data.index, stock_data['Volume'], 0, color='red', alpha=0.3)
        volume_ax.set_ylabel('Volume')
        volume_ax.legend(loc='upper right')
        
        # RSI plots
        line_colors = plt.cm.viridis(np.linspace(0, 1, len(valid_periods)))
        
        for i, period in enumerate(valid_periods):
            color = line_colors[i]
            axs[1].plot(rsi_data.index, rsi_data[f'Weighted_RSI_{period}'], 
                       label=f'Weighted RSI ({period})', color=color)
            axs[2].plot(rsi_data.index, rsi_data[f'RSI_{period}'], 
                       label=f'RSI ({period})', color=color)
        
        for ax in axs[1:]:
            ax.axhline(70, linestyle='--', color='r', alpha=0.5)
            ax.axhline(30, linestyle='--', color='g', alpha=0.5)
            ax.legend(loc='upper left')
        
        axs[1].set_ylabel('Weighted RSI')
        axs[2].set_ylabel('RSI')
        
        plt.xlabel('Date')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    stock_ticker = request.form.get('stock_ticker', '')
    rsi_periods = request.form.get('rsi_periods', '')
    
    buf, error = generate_charts(stock_ticker, rsi_periods)
    
    if error:
        return {'error': error}, 400
        
    return send_file(
        buf,
        mimetype='image/png',
        as_attachment=False
    )

if __name__ == '__main__':
    app.run(debug=True)
Last edited 12 minutes ago


