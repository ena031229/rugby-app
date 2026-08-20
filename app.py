import pandas as pd
import streamlit as st
import plotly.express as px


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="TUS InBody",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS
# =========================================================
st.html("""
<style>

body {
    font-family: "Noto Sans JP", sans-serif;
}

/* メインタイトル */
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #252936;
    margin-bottom: 3px;
}

.sub-title {
    font-size: 16px;
    color: #777777;
    margin-bottom: 25px;
}

/* 選手情報 */
.player-header {
    background: linear-gradient(135deg, #202a38, #344154);
    border-radius: 18px;
    padding: 25px 30px;
    margin: 10px 0 30px 0;
    color: white;
}

.player-name {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 8px;
}

.measurement-date {
    font-size: 15px;
    color: #d8dee8;
}

/* セクション */
.section-title {
    font-size: 27px;
    font-weight: 800;
    color: #252936;
    margin: 25px 0 15px 0;
}

/* データカード */
.metric-card {
    background: white;
    border: 1px solid #e9ebef;
    border-radius: 18px;
    padding: 24px;
    min-height: 220px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}

.metric-title {
    font-size: 17px;
    font-weight: 700;
    color: #555b66;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 36px;
    font-weight: 800;
    color: #252936;
    margin-bottom: 8px;
}

.metric-goal {
    font-size: 14px;
    color: #777777;
    margin-bottom: 12px;
}

.metric-diff {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 8px;
}

.positive {
    color: #16a34a;
}

.negative {
    color: #dc2626;
}

.neutral {
    color: #6b7280;
}

.previous-data {
    font-size: 13px;
    color: #888888;
}

/* ランキング */
.ranking-card {
    background: white;
    border: 1px solid #e9ebef;
    border-radius: 14px;
    padding: 15px 20px;
    margin-bottom: 8px;
    box-shadow: 0 2px 7px rgba(0,0,0,0.04);
}

.ranking-name {
    font-size: 17px;
    font-weight: 700;
    color: #252936;
}

.ranking-data {
    font-size: 14px;
    color: #666666;
}

/* サイドバー */
.sidebar-title {
    font-size: 22px;
    font-weight: 800;
}

.sidebar-description {
    font-size: 14px;
    color: #666666;
}

</style>
""")


# =========================================================
# データ読み込み
# =========================================================
@st.cache_data
def load_data():

    data = pd.read_csv("players.csv")

    data.columns = data.columns.str.strip()

    data["date"] = pd.to_datetime(data["date"])

    return data


df = load_data()


# =========================================================
# サイドバー
# =========================================================
st.sidebar.html("""
<div class="sidebar-title">
    🏉 TUS InBody
</div>

<br>

<div class="sidebar-description">
    選手の身体データを管理・分析するダッシュボード
</div>
""")

st.sidebar.markdown("---")

st.sidebar.subheader("👤 選手選択")

players = df["name"].unique()

selected_player = st.sidebar.selectbox(
    "選手を選択してください",
    players
)

st.sidebar.markdown("---")

st.sidebar.subheader("📊 表示内容")

st.sidebar.markdown("""
- 最新身体データ
- 目標達成度
- 前回測定との比較
- 身体データの推移
- チームランキング
""")


# =========================================================
# 選手データ
# =========================================================
player_df = (
    df[df["name"] == selected_player]
    .sort_values("date")
    .copy()
)

latest = player_df.iloc[-1]

latest_date = latest["date"].strftime("%Y/%m/%d")


# =========================================================
# 前回データ
# =========================================================
if len(player_df) >= 2:

    previous = player_df.iloc[-2]

    weight_change = latest["weight"] - previous["weight"]
    muscle_change = latest["muscle"] - previous["muscle"]
    fat_change = latest["fat"] - previous["fat"]

else:

    previous = None

    weight_change = None
    muscle_change = None
    fat_change = None


# =========================================================
# 目標との差
# =========================================================

# 体重
weight_diff = latest["goal_weight"] - latest["weight"]

# 筋肉
muscle_diff = latest["goal_muscle"] - latest["muscle"]

# 体脂肪
fat_diff = latest["fat"] - latest["goal_fat"]


# =========================================================
# 目標達成度
# =========================================================
def calculate_progress(current, goal, mode):

    if mode == "increase":

        if goal == 0:
            return 100

        progress = current / goal * 100

    else:

        if current == 0:
            return 100

        progress = goal / current * 100

    return max(0, min(progress, 100))


weight_progress = calculate_progress(
    latest["weight"],
    latest["goal_weight"],
    "increase"
)

muscle_progress = calculate_progress(
    latest["muscle"],
    latest["goal_muscle"],
    "increase"
)

fat_progress = calculate_progress(
    latest["fat"],
    latest["goal_fat"],
    "decrease"
)


# =========================================================
# タイトル
# =========================================================
st.html("""
<div class="main-title">
    🏉 TUS InBody
</div>

""")


# =========================================================
# 選手情報
# =========================================================
st.html(f"""
<div class="player-header">

    <div class="player-name">
        👤 {selected_player}
    </div>

    <div class="measurement-date">
        📅 最新測定日：{latest_date}
    </div>

</div>
""")


# =========================================================
# 最新コンディション
# =========================================================
st.html("""
<div class="section-title">
    📊 最新コンディション
</div>
""")


col1, col2, col3 = st.columns(3)


# =========================================================
# 体重
# =========================================================
with col1:

    if weight_diff > 0:

        diff_text = f"あと {weight_diff:.1f} kg"
        diff_class = "positive"

    elif weight_diff < 0:

        diff_text = f"{abs(weight_diff):.1f} kg オーバー"
        diff_class = "negative"

    else:

        diff_text = "🎯 目標達成"
        diff_class = "positive"


    if weight_change is not None:

        if weight_change > 0:
            change_text = f"↑ 前回より +{weight_change:.1f} kg"

        elif weight_change < 0:
            change_text = f"↓ 前回より {weight_change:.1f} kg"

        else:
            change_text = "→ 前回から変化なし"

    else:

        change_text = "初回測定"


    st.html(f"""
    <div class="metric-card">

        <div class="metric-title">
            🏋️ 体重
        </div>

        <div class="metric-value">
            {latest["weight"]:.1f} kg
        </div>

        <div class="metric-goal">
            目標：{latest["goal_weight"]:.1f} kg
        </div>

        <div class="metric-diff {diff_class}">
            {diff_text}
        </div>

        <div class="previous-data">
            {change_text}
        </div>

    </div>
    """)

    st.progress(
        int(weight_progress),
        text=f"目標達成度 {weight_progress:.0f}%"
    )


# =========================================================
# 筋肉量
# =========================================================
with col2:

    if muscle_diff > 0:

        diff_text = f"あと {muscle_diff:.1f} kg"
        diff_class = "positive"

    elif muscle_diff < 0:

        diff_text = f"{abs(muscle_diff):.1f} kg オーバー"
        diff_class = "positive"

    else:

        diff_text = "🎯 目標達成"
        diff_class = "positive"


    if muscle_change is not None:

        if muscle_change > 0:
            change_text = f"↑ 前回より +{muscle_change:.1f} kg"

        elif muscle_change < 0:
            change_text = f"↓ 前回より {muscle_change:.1f} kg"

        else:
            change_text = "→ 前回から変化なし"

    else:

        change_text = "初回測定"


    st.html(f"""
    <div class="metric-card">

        <div class="metric-title">
            💪 筋肉量
        </div>

        <div class="metric-value">
            {latest["muscle"]:.1f} kg
        </div>

        <div class="metric-goal">
            目標：{latest["goal_muscle"]:.1f} kg
        </div>

        <div class="metric-diff {diff_class}">
            {diff_text}
        </div>

        <div class="previous-data">
            {change_text}
        </div>

    </div>
    """)

    st.progress(
        int(muscle_progress),
        text=f"目標達成度 {muscle_progress:.0f}%"
    )


# =========================================================
# 体脂肪率
# =========================================================
with col3:

    if fat_diff > 0:

        diff_text = f"{fat_diff:.1f}% オーバー"
        diff_class = "negative"

    elif fat_diff < 0:

        diff_text = f"目標より {abs(fat_diff):.1f}% 少ない"
        diff_class = "positive"

    else:

        diff_text = "🎯 目標達成"
        diff_class = "positive"


    if fat_change is not None:

        if fat_change > 0:
            change_text = f"↑ 前回より +{fat_change:.1f}%"

        elif fat_change < 0:
            change_text = f"↓ 前回より {fat_change:.1f}%"

        else:
            change_text = "→ 前回から変化なし"

    else:

        change_text = "初回測定"


    st.html(f"""
    <div class="metric-card">

        <div class="metric-title">
            🔥 体脂肪率
        </div>

        <div class="metric-value">
            {latest["fat"]:.1f}%
        </div>

        <div class="metric-goal">
            目標：{latest["goal_fat"]:.1f}%
        </div>

        <div class="metric-diff {diff_class}">
            {diff_text}
        </div>

        <div class="previous-data">
            {change_text}
        </div>

    </div>
    """)

    st.progress(
        int(fat_progress),
        text=f"目標達成度 {fat_progress:.0f}%"
    )


# =========================================================
# 推移グラフ
# =========================================================
st.html("""
<div class="section-title">
    📈 身体データの推移
</div>
""")


metric_map = {
    "体重": "weight",
    "筋肉量": "muscle",
    "体脂肪率": "fat"
}


metric_label = st.selectbox(
    "表示する項目",
    list(metric_map.keys())
)

metric = metric_map[metric_label]


# =========================================================
# グラフ
# =========================================================
fig = px.line(
    player_df,
    x="date",
    y=metric,
    markers=True,
    labels={
        "date": "測定日",
        metric: metric_label
    }
)


# 目標値
if metric == "weight":

    goal = latest["goal_weight"]

elif metric == "muscle":

    goal = latest["goal_muscle"]

else:

    goal = latest["goal_fat"]


fig.add_hline(
    y=goal,
    line_dash="dash",
    annotation_text=f"目標 {goal:.1f}",
    annotation_position="top right"
)


fig.update_layout(
    height=420,
    margin=dict(
        l=20,
        r=20,
        t=30,
        b=20
    ),
    hovermode="x unified",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

fig.update_xaxes(
    showgrid=True
)

fig.update_yaxes(
    showgrid=True
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# チームランキング
# =========================================================
st.html("""
<div class="section-title">
    🏆 チームランキング
</div>
""")


latest_df = (
    df.sort_values("date")
    .groupby("name")
    .tail(1)
    .copy()
)


ranking = (
    latest_df
    .sort_values("weight", ascending=False)
    .reset_index(drop=True)
)


for i, row in ranking.iterrows():

    if i == 0:
        medal = "🥇"

    elif i == 1:
        medal = "🥈"

    elif i == 2:
        medal = "🥉"

    else:
        medal = f"{i + 1}位"


    st.html(f"""
    <div class="ranking-card">

        <div class="ranking-name">
            {medal} {row["name"]}
        </div>

        <div class="ranking-data">
            体重：{row["weight"]:.1f} kg
            &nbsp;｜&nbsp;
            筋肉：{row["muscle"]:.1f} kg
            &nbsp;｜&nbsp;
            体脂肪：{row["fat"]:.1f}%
            &nbsp;｜&nbsp;
            測定日：{row["date"].strftime("%Y/%m/%d")}
        </div>

    </div>
    """)


# =========================================================
# フッター
# =========================================================
st.markdown("---")

st.caption(
    "🏉 TUS InBody | 選手の身体データ管理・分析システム"
)