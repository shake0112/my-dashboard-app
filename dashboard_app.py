import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import streamlit as st
import pandas as pd
from google import genai

# 1. 隠し部屋から自動で鍵を読み込んでAIを起動！
client = genai.Client()

st.title("📊 ファイトキャンプ・データダッシュボードAI")

# 初期データ（5日分）を session_state に保持
if "training_df" not in st.session_state:
    st.session_state.training_df = pd.DataFrame(
        {
            "日付": ["1日目", "2日目", "3日目", "4日目", "5日目"],
            "体重(kg)": [72.5, 72.2, 71.8, 71.5, 71.3],
            "睡眠時間(h)": [7.5, 6.5, 7.0, 5.5, 6.0],
            "疲労度(5段階)": [2, 3, 3, 4, 4],
        }
    )

st.subheader("📝 週間トレーニング記録（セル編集・行追加OK）")
st.caption("Excelのように数字を直接書き換えたり、行を追加して記録を更新できます。")

edited_df = st.data_editor(
    st.session_state.training_df,
    num_rows="dynamic",
    use_container_width=True,
    key="training_data_editor",
)

st.session_state.training_df = edited_df

st.markdown("---")
st.subheader("📈 推移グラフ")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**体重の推移**")
    if not edited_df.empty and "体重(kg)" in edited_df.columns:
        chart_weight = edited_df.set_index("日付")[["体重(kg)"]]
        st.line_chart(chart_weight)
    else:
        st.info("体重データがありません。")

with col2:
    st.markdown("**睡眠時間の推移**")
    if not edited_df.empty and "睡眠時間(h)" in edited_df.columns:
        chart_sleep = edited_df.set_index("日付")[["睡眠時間(h)"]]
        st.line_chart(chart_sleep)
    else:
        st.info("睡眠時間データがありません。")

st.markdown("---")

if st.button("🔥 ヘッドコーチの週間データ分析"):
    with st.spinner("名門ジムの鬼ヘッドコーチがデータを精査中..."):
        try:
            data_text = edited_df.to_string()

            prompt = f"""
            あなたは名門格闘技ジムの鬼ヘッドコーチです。
            以下の週間トレーニングデータを読み、選手に向けて厳しくも的確な分析を行ってください。

            【週間トレーニングデータ】
            {data_text}

            【口調のルール】
            ・名門ジムの鬼ヘッドコーチ口調。厳しく、熱く、具体的。
            ・選手に直接語りかける「お前は〜だ！」というトーン。
            ・データに基づいた根拠のある分析をすること。数字を引用して説明すること。

            【出力構成（厳守）】

            ## 【今週のスタミナ・肉体評価】
            体重の推移と睡眠時間の相関を分析すること。
            例：睡眠が足りない日に体重が落ちすぎていないか、減量とリカバリーのバランスは適切か、
            疲労度の推移と睡眠時間の関係など、データから読み取れる肉体・スタミナの状態を評価すること。

            ## 【オーバートレーニングの兆候チェック】
            疲労度の上昇、睡眠時間の不足、体重の異常な減少など、
            データから見えるオーバートレーニングや burnout の兆候がないかチェックすること。
            危険信号があれば具体的に指摘し、なければ現状維持の根拠を述べること。

            ## 【次週への強化指令】
            今週のデータ分析を踏まえ、来週に向けた具体的な強化・調整指令を出すこと。
            睡眠時間の確保、就寝リズムの改善、減量ペースの調整、リカバリーの取り方など、実行可能な指示にすること。
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            st.session_state["coach_analysis"] = response.text
            st.success("分析完了！ヘッドコーチからの指令を確認しろ！")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if "coach_analysis" in st.session_state:
    st.markdown("---")
    st.subheader("🥊 鬼ヘッドコーチからの週間分析")
    st.markdown(st.session_state["coach_analysis"])
