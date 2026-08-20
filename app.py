import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="🏉 TUS InBody",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

    /* 全体 */
    .main {
        background-color: #f7f8fa;
    }

    /* タイトル */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .sub-title {
        color: #777;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* 選手ヘッダー */
    .player-header {
        background: linear-gradient(135deg, #1f2937, #374151);
        color: white;
        padding: 25px;
        border-radius: 18px;
        margin-bottom: 25px;
    }

    .player-name {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .measurement-date {
        font-size: 15px;
        color: #d1d5db;
    }

    /* カード */
    .metric-card {
        background-color: white;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.07);
        border: 1px solid #eeeeee;
        min-height: 220px;
    }

    .metric-title {
        font-size: 18px;
        font-weight: 700;
        color: #555;
    }

    .metric-value {
        font-size: 38px;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 5px;
    }

    .metric-goal {
        color: #777;
        font-size: 14px;
    }

    .metric-diff {
        font-size: 16px;
        font-weight: 700;
        margin-top: 12px;
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

    /* セクションタイトル */
    .section-title {
        font-size: 26px;
        font-weight: 800;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    /* ランキング */
    .ranking-card {
        background-color: white;
        padding: 15px 20px;
        border-radius: 14px;
        margin-bottom: 8px;
        border: 1px solid #eeeeee;
        box-shadow: 0 2px 7px rgba(0,0,0,0.05);
    }

    .ranking-name {
        font-size: 18px;
        font-weight: 700;
    }

    .ranking-data {
        color: #666;
        font-size: 14px;
    }

    /* 目標達成 */
    .goal-ranking-card {
        background-color: white;
        padding: 15px 20px;
        border-radius: 14px;
        margin-bottom: 8px;
        border-left: 5px solid #22c55e;
        box-shadow: 0 2px 7px rgba(0,0,0,0.05);
    }

    /* サイドバー */
    [data-testid="stSidebar"] {
        background-color: #f1f3f6;
    }

</style>
""", unsafe_allow_html=True)


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
st.sidebar.title("🏉 TUS InBody")

st.sidebar.markdown("---")

st.sidebar.subheader("👤 選手選択")

players = df["name"].unique()

selected_player = st.sidebar.selectbox(
    "選手を選択してください",
    players
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
### 📊 表示内容

- 最新身体データ
- 目標達成度
- 前回測定との比較
- 身体データの推移
- チームランキング
- 目標達成ランキング
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
# 目標達成率
# =========================================================

def calculate_progress(current, goal, metric_type):

    if metric_type == "increase":

        if goal == 0:
            return 100

        progress = current / goal * 100

    else:

        # 脂肪など「減らす」項目
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

st.markdown(
    '<div class="main-title">🏉 TUS InBody</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">選手の身体データを管理・分析するダッシュボード</div>',
    unsafe_allow_html=True
)


# =========================================================
# 選手情報
# =========================================================

st.markdown(f"""
<div class="player-header">

    <div class="player-name">
        👤 {selected_player}
    </div>

    <div class="measurement-date">
        📅 最新測定日：{latest_date}
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# 最新データ
# =========================================================

st.markdown(
    '<div class="section-title">📊 最新コンディション</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)


# ---------------------------------------------------------
# 体重
# ---------------------------------------------------------

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


    st.markdown(f"""
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

        <div class="metric-goal">
            {change_text}
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.progress(
        int(weight_progress),
        text=f"目標達成度 {weight_progress:.0f}%"
    )


# ---------------------------------------------------------
# 筋肉量
# ---------------------------------------------------------

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


    st.markdown(f"""
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

        <div class="metric-goal">
            {change_text}
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.progress(
        int(muscle_progress),
        text=f"目標達成度 {muscle_progress:.0f}%"
    )


# ---------------------------------------------------------
# 体脂肪
# ---------------------------------------------------------

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


    st.markdown(f"""
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

        <div class="metric-goal">
            {change_text}
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.progress(
        int(fat_progress),
        text=f"目標達成度 {fat_progress:.0f}%"
    )


# =========================================================
# 推移グラフ
# =========================================================

st.markdown(
    '<div class="section-title">📈 身体データの推移</div>',
    unsafe_allow_html=True
)

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


# グラフ用データ
graph_df = player_df.copy()

fig = px.line(
    graph_df,
    x="date",
    y=metric,
    markers=True,
    labels={
        "date": "測定日",
        metric: metric_label
    }
)


# ---------------------------------------------------------
# 目標ライン
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# グラフデザイン
# ---------------------------------------------------------

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

st.markdown(
    '<div class="section-title">🏆 チームランキング</div>',
    unsafe_allow_html=True
)

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


ranking_display = []

for i, row in ranking.iterrows():

    if i == 0:
        rank = "🥇"
    elif i == 1:
        rank = "🥈"
    elif i == 2:
        rank = "🥉"
    else:
        rank = f"{i + 1}"

    ranking_display.append({
        "順位": rank,
        "選手": row["name"],
        "体重 (kg)": round(row["weight"], 1),
        "筋肉量 (kg)": round(row["muscle"], 1),
        "体脂肪率 (%)": round(row["fat"], 1),
        "測定日": row["date"].strftime("%Y/%m/%d")
    })


ranking_table = pd.DataFrame(ranking_display)

st.dataframe(
    ranking_table,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 目標達成ランキング
# =========================================================

st.markdown(
    '<div class="section-title">🎯 目標達成ランキング</div>',
    unsafe_allow_html=True
)

latest_df["score"] = (
    (latest_df["goal_weight"] - latest_df["weight"]).abs()
    +
    (latest_df["goal_muscle"] - latest_df["muscle"]).abs()
    +
    (latest_df["fat"] - latest_df["goal_fat"]).abs()
)

goal_ranking = (
    latest_df
    .sort_values("score")
    .reset_index(drop=True)
)


for i, row in goal_ranking.iterrows():

    if i == 0:
        medal = "🥇"
    elif i == 1:
        medal = "🥈"
    elif i == 2:
        medal = "🥉"
    else:
        medal = f"{i + 1}位"

    st.markdown(f"""
    <div class="goal-ranking-card">

        <span class="ranking-name">
            {medal} {row["name"]}
        </span>

        <br>

        <span class="ranking-data">
            目標との差：{row["score"]:.2f}
        </span>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# フッター
# =========================================================

st.markdown("---")

st.caption(
    "🏉 TUS InBody | 選手の身体データ管理・分析システム"
)