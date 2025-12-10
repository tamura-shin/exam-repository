import os
import streamlit as st
import requests
import mimetypes
from google import genai
from google.genai import types

# ページ設定
st.title("曲紹介アプリ")
st.write("音楽ファイル又はURLをアップロードすると、AIが似た曲を紹介してくれます")

# サンプル音声のダウンロードボタン
if os.path.exists("sample.mp3"):
    with open("sample.mp3", "rb") as f:
        sample_audio_bytes = f.read()
    st.download_button(
        label="サンプル音声をダウンロード",
        data=sample_audio_bytes,
        file_name="sample.mp3",
        mime="audio/mp3",
    )

# 音声アップロード
uploaded_file = st.file_uploader("音声ファイルを選択してください", type=["mp3", "wav", "m4a"])
if uploaded_file is not None:
    # アップロードされた音声を再生
    st.audio(uploaded_file, format=uploaded_file.type)

    # 説明ボタン
    if st.button("似た曲をspotify検索"):
        with st.spinner("分析中..."):
            # 音声データを読み込む
            audio_bytes = uploaded_file.read()

            # Gemini APIクライアント初期化
            api_key = os.environ.get("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)

            # リクエスト作成
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type=uploaded_file.type,
                        ),
                        types.Part.from_text(text="何の曲なのかを特定し、この曲に似た曲をSpotifyから紹介してください。曲が特定できない場合はまず最初に特定できなかったと答えて下さい。そこから似た曲の紹介を。"),
                    ],
                ),
            ]

            # APIを呼び出して説明を生成
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=contents,
                config=types.GenerateContentConfig(),
            )

            # 結果を表示
            st.success("説明:")
            st.write(response.text)
    
    if st.button("似た曲をYouTube検索"):
        with st.spinner("分析中..."):
            # 音声データを読み込む
            audio_bytes = uploaded_file.read()

            # Gemini APIクライアント初期化
            api_key = os.environ.get("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)

            # リクエスト作成
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type=uploaded_file.type,
                        ),
                        types.Part.from_text(text="何の曲なのか、そしてこの曲に似た曲をYouTube musicから紹介してください。曲が特定できない場合は、まず最初に特定できなかったと答えて下さい。そこから似た曲の紹介を。"),
                    ],
                ),
            ]

            # APIを呼び出して説明を生成
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=contents,
                config=types.GenerateContentConfig(),
            )

            # 結果を表示
            st.success("説明:")
            st.write(response.text)

st.markdown("<div style='height:75px;'></div>", unsafe_allow_html=True)

# URLで検索
url = st.text_input("曲のURLを入力してください（例: https://www.youtube.com/watch?v=...）")
music_name = st.text_input("曲名を入力してください")
detailed_information = st.text_area("精度を高める場合にはこちらに詳細情報（アーティスト名は？曲のジャンルは？）を入力してください（任意）")
if url and music_name:
    if st.button("似た曲を探す(URLベース)"):
        with st.spinner("検索中..."):
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                st.error("環境変数 `GEMINI_API_KEY` を設定してください。")
            else:
                client = genai.Client(api_key=api_key)

                prompt = (
                    "以下のURLと曲名が指す曲について、アーティストを特定して書き出してください。"
                    "その後、この曲に似た曲をYouTube Music上から3曲ピックアップして、"
                    "曲名・アーティストを併記してください。"
                    f"\n\nURL: {url}\n\n"
                    f"曲名: {music_name}\n\n"
                    f"詳細情報: {detailed_information}\n\n"
                    "YouTube上で似た曲のタイトルとアーティスト、可能ならリンクを提示してください。"
                )

                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    ),
                ]

                try:
                    response = client.models.generate_content(
                        model = "gemini-flash-lite-latest",
                        contents = contents,
                        config = types.GenerateContentConfig(),
                    )
                    st.subheader("結果（URLベース）")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"問い合わせ中にエラーが発生しました: {e}")
                    
