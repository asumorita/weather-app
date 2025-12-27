import streamlit as st
import requests
from datetime import datetime


# ページ設定
st.set_page_config(
    page_title="ASU 天気予報アプリ",
    page_icon="🌤️",
    layout="centered"
)


# ヘッダー
st.markdown("### 🏢 ASU")
st.title("🌤️ 天気予報アプリ")
st.write("今日と明日の天気をチェックしましょう！")


st.markdown("---")


# 位置情報入力
st.subheader("📍 場所を入力してください")


col1, col2 = st.columns(2)


with col1:
    city = st.text_input(
        "都市名",
        value="Tokyo",
        help="英語で入力してください（例：Tokyo, Osaka, Yokohama）"
    )


with col2:
    # よく使う都市のクイック選択
    quick_city = st.selectbox(
        "クイック選択",
        ["選択してください", "Tokyo", "Osaka", "Nagoya", "Fukuoka", "Sapporo", "Yokohama", "Kyoto"]
    )
    
    if quick_city != "選択してください":
        city = quick_city


# 天気取得ボタン
if st.button("🌤️ 天気を取得", type="primary", use_container_width=True):
    
    if not city:
        st.error("❌ 都市名を入力してください")
    else:
        try:
            # Open-Meteo API（無料、APIキー不要）を使用
            # まず位置情報を取得
            geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ja&format=json"
            
            with st.spinner("位置情報を取得中..."):
                geo_response = requests.get(geocoding_url, timeout=10)
                geo_data = geo_response.json()
            
            if "results" not in geo_data or len(geo_data["results"]) == 0:
                st.error(f"❌ 「{city}」が見つかりませんでした。英語で入力してください。")
            else:
                # 位置情報取得成功
                location = geo_data["results"][0]
                latitude = location["latitude"]
                longitude = location["longitude"]
                location_name = location.get("name", city)
                country = location.get("country", "")
                
                st.success(f"✅ {location_name}, {country} の天気を取得します")
                
                # 天気予報を取得
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia/Tokyo"
                
                with st.spinner("天気予報を取得中..."):
                    weather_response = requests.get(weather_url, timeout=10)
                    weather_data = weather_response.json()
                
                # 天気コードの日本語変換
                weather_codes = {
                    0: "☀️ 快晴",
                    1: "🌤️ 晴れ",
                    2: "⛅ 曇り時々晴れ",
                    3: "☁️ 曇り",
                    45: "🌫️ 霧",
                    48: "🌫️ 霧（霜）",
                    51: "🌧️ 小雨",
                    53: "🌧️ 雨",
                    55: "🌧️ 大雨",
                    61: "🌧️ 小雨",
                    63: "🌧️ 雨",
                    65: "🌧️ 大雨",
                    71: "🌨️ 小雪",
                    73: "🌨️ 雪",
                    75: "🌨️ 大雪",
                    80: "🌦️ にわか雨",
                    81: "🌦️ にわか雨",
                    82: "🌦️ 激しいにわか雨",
                    95: "⛈️ 雷雨",
                    96: "⛈️ 雷雨（雹）",
                    99: "⛈️ 激しい雷雨"
                }
                
                # 現在の天気
                current = weather_data["current"]
                current_temp = current["temperature_2m"]
                current_humidity = current["relative_humidity_2m"]
                current_wind = current["wind_speed_10m"]
                current_weather_code = current["weather_code"]
                current_weather = weather_codes.get(current_weather_code, "☁️ 不明")
                
                # 今日と明日の天気
                daily = weather_data["daily"]
                
                st.markdown("---")
                st.subheader(f"📍 {location_name}, {country}")
                
                # 現在の天気
                st.markdown("### 🌡️ 現在の天気")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("天気", current_weather)
                
                with col2:
                    st.metric("気温", f"{current_temp}°C")
                
                with col3:
                    st.metric("湿度", f"{current_humidity}%")
                
                with col4:
                    st.metric("風速", f"{current_wind} m/s")
                
                st.markdown("---")
                
                # 今日と明日の予報
                st.markdown("### 📅 今日・明日の予報")
                
                for i in range(2):
                    date = daily["time"][i]
                    weather_code = daily["weather_code"][i]
                    temp_max = daily["temperature_2m_max"][i]
                    temp_min = daily["temperature_2m_min"][i]
                    precipitation = daily["precipitation_sum"][i]
                    
                    weather_text = weather_codes.get(weather_code, "☁️ 不明")
                    
                    day_label = "今日" if i == 0 else "明日"
                    
                    with st.container():
                        st.markdown(f"#### {day_label} ({date})")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("天気", weather_text)
                        
                        with col2:
                            st.metric("最高気温", f"{temp_max}°C")
                        
                        with col3:
                            st.metric("最低気温", f"{temp_min}°C")
                        
                        with col4:
                            st.metric("降水量", f"{precipitation} mm")
                        
                        # アドバイス
                        if precipitation > 5:
                            st.warning("☔ 傘を持って行きましょう")
                        
                        if temp_max > 30:
                            st.warning("🌞 暑いので熱中症に注意")
                        
                        if temp_min < 5:
                            st.info("🧥 寒いので暖かい服装で")
                        
                        st.markdown("---")
                
                # データソース表示
                st.caption("📊 Data provided by Open-Meteo.com")
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 天気情報の取得に失敗しました: {str(e)}")
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")


# 説明
st.markdown("---")
st.info("""
💡 **使い方**
1. 都市名を英語で入力（Tokyo, Osaka など）
2. または「クイック選択」から選ぶ
3. 「天気を取得」ボタンをクリック
4. 現在の天気と今日・明日の予報が表示されます
""")


# フッター
st.markdown("---")
st.caption("🌤️ ASU - 天気予報アプリ")
st.caption("Created with ❤️ by ASU")
