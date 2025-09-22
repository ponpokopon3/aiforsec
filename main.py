import streamlit as st
import json
from langchain.llms import OpenAI
import os

# 再帰的にtitleキーを持つ値を抽出
def find_titles(data):
	results = []
	if isinstance(data, dict):
		if 'title' in data:
			results.append(data)
		for v in data.values():
			results.extend(find_titles(v))
	elif isinstance(data, list):
		for item in data:
			results.extend(find_titles(item))
	return results

def show_recursive(data, level=0):
	indent = '&nbsp;' * 4 * level
	if isinstance(data, dict):
		for k, v in data.items():
			if isinstance(v, (dict, list)):
				st.markdown(f'{indent}**{k}**:')
				show_recursive(v, level+1)
			else:
				st.markdown(f'{indent}**{k}**: {v}')
	elif isinstance(data, list):
		for i, item in enumerate(data):
			st.markdown(f'{indent}-')
			show_recursive(item, level+1)

# JSONファイルの読み込み
with open('kijyunr7.json', encoding='utf-8') as f:
	data = json.load(f)

# titleキーを持つ値を抽出
title_items = find_titles(data)
titles = [item['title'] for item in title_items]

st.title('title選択＆コンテキスト階層表示＋Langchain')
selected_title = st.selectbox('タイトルを選択してください', titles)
api_key = st.text_input('OpenAI APIキーを入力してください', type='password')

if st.button('実行'):
	context = next((item for item in title_items if item['title'] == selected_title), None)
	if context:
		st.subheader('コンテキスト（階層表示）')
		show_recursive(context)
		st.subheader('コンテキスト（JSON表示）')
		st.json(context)
		# LangchainでOpenAI APIに送信
		if api_key:
			os.environ['OPENAI_API_KEY'] = api_key
			llm = OpenAI(temperature=0.2)
			prompt = f"以下の内容についてそのまま出力してください:\n{json.dumps(context, ensure_ascii=False, indent=2)}"
			with st.spinner('OpenAI APIに問い合わせ中...'):
				try:
					response = llm(prompt)
					st.subheader('OpenAI APIの応答')
					st.write(response)
				except Exception as e:
					st.error(f'APIエラー: {e}')
		else:
			st.info('OpenAI APIキーを入力してください。')
	else:
		st.warning('該当するコンテキストが見つかりませんでした。')