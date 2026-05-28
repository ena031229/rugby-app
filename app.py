import pandas as pd
import streamlit as st
import plotly.express as px

# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="ラグビー部 InBody",
    layout="centered"
)

# =========================
# データ読み込み
# =========================
df = pd.read_csv("players.csv")
df.columns = df.columns.str.strip()
df["date"] = pd.to_datetime(df["date"])

# =========================
# サイドバー（選手だけ）
# =========================
st.sidebar.title("⚙️ 設定")

players = df["name"].unique()
selected_player = st.sidebar.selectbox("👤 選手を選択", players)

# =========================
# データ抽出
# =========================
player_df = df[df["name"] == selected_player].sort_values("date")
latest = player_df.iloc[-1]

# =========================
# タイトル
# =========================
st.title("🏉 TUS InBody")

# =========================
# 最新データ（カードUI）
# =========================
st.header("📊 最新データ")

weight_diff = latest['goal_weight'] - latest['weight']
muscle_diff = latest['goal_muscle'] - latest['muscle']
fat_diff = latest['fat'] - latest['goal_fat']

weight_color = "green" if weight_diff >= 0 else "red"
muscle_color = "green" if muscle_diff >= 0 else "red"
fat_color = "green" if fat_diff <= 0 else "red"

# 体重
st.markdown(f"""
<div style="padding:15px; border-radius:15px; background-color:#f0f2f6; margin-bottom:10px;">
<h3>🏋️ 体重</h3>
<h1>{latest['weight']} kg</h1>
<p style="color:{weight_color}; font-size:18px;">
目標まで {abs(weight_diff):.1f} kg
</p>
</div>
""", unsafe_allow_html=True)

# 筋肉量
st.markdown(f"""
<div style="padding:15px; border-radius:15px; background-color:#f0f2f6; margin-bottom:10px;">
<h3>💪 筋肉量</h3>
<h1>{latest['muscle']} kg</h1>
<p style="color:{muscle_color}; font-size:18px;">
目標まで {abs(muscle_diff):.1f} kg
</p>
</div>
""", unsafe_allow_html=True)

# 体脂肪
st.markdown(f"""
<div style="padding:15px; border-radius:15px; background-color:#f0f2f6;">
<h3>🔥 体脂肪率</h3>
<h1>{latest['fat']} %</h1>
<p style="color:{fat_color}; font-size:18px;">
{abs(fat_diff):.1f} %オーバー
</p>
</div>
""", unsafe_allow_html=True)

# =========================
# グラフ（←ここに選択を配置）
# =========================
st.header("📈 推移グラフ")

metric_map = {
    "体重": "weight",
    "筋肉量": "muscle",
    "体脂肪率": "fat"
}

# 👇 グラフのすぐ上に配置
metric_label = st.selectbox("表示したい項目", list(metric_map.keys()))
metric = metric_map[metric_label]

fig = px.line(
    player_df,
    x="date",
    y=metric,
    markers=True,
    title=f"{selected_player} の {metric_label} 推移"
)

# 目標ライン
if metric == "weight":
    fig.add_hline(y=latest["goal_weight"], line_dash="dash")
elif metric == "muscle":
    fig.add_hline(y=latest["goal_muscle"], line_dash="dash")
elif metric == "fat":
    fig.add_hline(y=latest["goal_fat"], line_dash="dash")

fig.update_layout(height=350)

st.plotly_chart(fig, use_container_width=True)

# =========================
# チームランキング
# =========================
st.header("🏆 チームランキング")

latest_df = df.sort_values("date").groupby("name").tail(1)
ranking = latest_df.sort_values("weight", ascending=False).reset_index(drop=True)

for i, row in ranking.iterrows():
    st.markdown(f"""
    <div style="padding:10px; margin-bottom:8px; background-color:#ffffff; border-radius:10px;">
    <b>{i+1}位 {row['name']}</b><br>
    体重: {row['weight']} kg | 筋肉: {row['muscle']} kg | 脂肪: {row['fat']}%
    </div>
    """, unsafe_allow_html=True)

# =========================
# 目標達成ランキング
# =========================
st.header("🎯 目標達成ランキング")

latest_df["score"] = (
    (latest_df["goal_weight"] - latest_df["weight"]).abs()
    + (latest_df["goal_muscle"] - latest_df["muscle"]).abs()
    + (latest_df["fat"] - latest_df["goal_fat"]).abs()
)

goal_ranking = latest_df.sort_values("score").reset_index(drop=True)

for i, row in goal_ranking.iterrows():
    st.markdown(f"""
    <div style="padding:10px; margin-bottom:8px; background-color:#e8f5e9; border-radius:10px;">
    <b>{i+1}位 {row['name']}</b><br>
    スコア: {row['score']:.2f}
    </div>
    """, unsafe_allow_html=True)