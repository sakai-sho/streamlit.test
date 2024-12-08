import streamlit as st # フロントエンドを扱うstreamlitの機能をインポート
import pandas as pd # データフレームを扱う機能をインポート
import yfinance as yf # yahoo financeから株価情報を取得するための機能をインポート
import altair as alt # チャート可視化機能をインポート

#取得する銘柄の名前とキーを変換する一覧を設定
#東証などのシンボルはhttps://support.yahoo-net.jp/PccFinance/s/article/H000006603で検索できる
tickers = {
    'apple': 'AAPL',
    'facebook': 'META',
    'google': 'GOOGL',
    'microsoft': 'MSFT',
    'netflix': 'NFLX',
    'amazon': 'AMZN',
    'TOTO': '5332.T',
    'TOYOTA': '7203.T',
}

print('株価可視化アプリ')
print("こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。")# サイドバーに表示
print("表示日数選択") # サイドバーに表示

days = 10 # 取得するための日数daysに代入

print(f"過去 {days}日間 の株価") # 取得する日数を表示


def get_data(days, tickers):
    df = pd.DataFrame() # 株価を代入するための空箱を用意

    # 選択した株価の数だけ yf.Tickerでリクエストしてデータを取得する
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company]) # 設定した銘柄一覧でリクエストの為の7203.Tなどに変換をして、それをyf.Tickerで株価リクエスト

        #日数をyfinanceが対応する期間に変換
        if days <= 5:
            period = '1d'  # 5日以内は1日ごとのデータ
        elif days <= 30:
            period = '1mo'  # 30日以内は1ヶ月
        elif days <= 90:
            period = '3mo'  # 3ヶ月以内
        elif days <= 180:
            period = '6mo'  # 6ヶ月以内
        elif days <= 365:
            period = '1y'  # 1年以内
        else:
            period = '2y'  # 2年以内

        hist = tkr.history(period=period) # スライドバーで指定した日数で取得した情報を絞る
        hist.index = pd.to_datetime(hist.index) # DatetimeIndexに変換
        hist.index = hist.index.strftime('%d %B %Y') # indexを日付のフォーマットに変更
        hist = hist[['Close']] # データを終値だけ抽出
        hist.columns = [company] # データのカラムをyf.Tickerのリクエストした企業名に設定
        hist = hist.T # 欲しい情報が逆なので、転置する
        hist.index.name = 'Name' # indexの名前をNameにする
        df = pd.concat([df, hist]) # 用意した空のデータフレームに設定したhistのデータを結合する
    return df # 返り値としてdfを返す

df = get_data(days, tickers) # リクエストする企業一覧すべてと変換するtickersを引数に株価取得





# 企業名の配列を生成し、companiesに代入
companies = ['google', 'apple','TOYOTA']

data = df.loc[companies] # 取得したデータから抽出するための配列で絞ってdataに代入
print("株価 ", data.sort_index()) # dataにあるindexを表示
data = data.T.reset_index() # dataを抽出して転置

# 企業ごとの別々のカラムにデータを表示する必要ないので企業を１つのカラムに統一
data = pd.melt(data, id_vars=['Date']).rename(
    columns={'value': 'Stock Prices'}
)


# チャートに表示する範囲、それぞれをymin, ymaxに代入
print("株価の範囲指定") # サイドバーに表示
ymin = 0
ymax = 3000

# dataとスライドバーで設定した最大最小値を元にalt.Chartを使って株価チャートを作成
chart = (
    alt.Chart(data)
    .mark_line(opacity=0.8, clip=True)
    .encode(
        x="Date:T",
        y=alt.Y("Stock Prices:Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
        color='Name:N'
    )
)

# 作成したチャートをstreamlitで表示
