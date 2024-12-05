# -*- coding:utf-8 -*-
from flask import Flask, render_template, request, jsonify
import urllib3
import json
import urllib.parse
import os

app = Flask(__name__)

# API 설정
legalQAUrl = "http://aiopen.etri.re.kr:8000/LegalQA"
wikiQAUrl = "http://aiopen.etri.re.kr:8000/WikiQA"
newsUrl = "https://openapi.naver.com/v1/search/news.json"  # JSON 형식으로 뉴스 검색
accessKey = "c2dde7e3-836a-4236-aef9-d0d73c46bfd8"  # 실제 Access Key
client_id = "3e5ajOZ55f2Jhd2uSyDy"  # 네이버 클라이언트 ID
client_secret = "4vqb2tXTec"  # 네이버 클라이언트 시크릿

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.form['question']

    # 법률 QA API 요청
    legal_request_json = {
        "access_key": accessKey,
        "argument": {
            "question": user_question,
        }
    }

    # 위키 QA API 요청
    wiki_request_json = {
        "argument": {
            "question": user_question,
            "type": "ENGINE_TYPE"
        }
    }

    # 뉴스 API 요청
    encText = urllib.parse.quote(user_question)
    news_request_url = f"{newsUrl}?query={encText}&display=10&sort=sim"

    # HTTP 요청
    http = urllib3.PoolManager()

    # 법률 QA API 호출
    legal_response = http.request(
        "POST",
        legalQAUrl,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": accessKey},
        body=json.dumps(legal_request_json)
    )
    legal_response_data = json.loads(legal_response.data.decode('utf-8'))

    # 위키 QA API 호출
    wiki_response = http.request(
        "POST",
        wikiQAUrl,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": accessKey},
        body=json.dumps(wiki_request_json)
    )
    wiki_response_data = json.loads(wiki_response.data.decode('utf-8'))

    # 뉴스 API 호출
    news_request = urllib.request.Request(news_request_url)
    news_request.add_header("X-Naver-Client-Id", client_id)
    news_request.add_header("X-Naver-Client-Secret", client_secret)
    news_response = urllib.request.urlopen(news_request)
    news_rescode = news_response.getcode()
    if news_rescode == 200:
        news_response_data = json.loads(news_response.read().decode('utf-8'))
    else:
        news_response_data = {"error": "뉴스 API 호출 실패"}

    # 응답 결과 정리
    results = {
        "legal": legal_response_data,
        "wiki": wiki_response_data,
        "news": news_response_data,
    }

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
