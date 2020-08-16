"""
Test for website without the influence of the transcompile model
"""

from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import difflib
from bs4 import BeautifulSoup
import sys

app = Flask(__name__)

source = ''
result = ''
source2 = ''
result2 = ''


def compile_run(source_code, language, url='https://api.jdoodle.com/v1/execute'):
    # 先假设是python code
    if language == 'python':
        lang = 'python3'
        version = 3
    elif language == 'c++':
        lang = 'cpp17'
        version = 0
    elif language == 'java':
        lang = 'java'
        version = 3
    else:
        raise NotImplementedError('{} is not supported now!'.format(language))

    data = {
        'clientId': '5889da6be5def525ee4d6c2b7a6b2535',
        'clientSecret': '412423fa76d979ed782e12fb0d9f5852a61c8792d1390460696d2abc3d8d8717',
        'script': source_code,
        'stdin': '',
        'language': lang,
        'versionIndex': version
    }

    response = requests.post(url=url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    w = json.loads(response.text)
    if 'output' in w:
        result = w['output']
    else:
        result = w['error']
    return result


@app.route('/')
def index():
    # return 'hello world'
    return render_template('index.html')


@app.route('/compile/', methods=('POST', 'GET'))
def compile():
    if request.method == 'POST':
        global source, result
        # print(request.form['code'])
        # axios请求
        data = request.get_json(silent=True)
        source = data['code']
        language = data['language']
        if language == 'cpp':
            language = 'c++'

        result = compile_run(source, language)
        print(source, result)
        return {'source': source, 'result': result}
    return redirect(url_for('index'))


@app.route('/transform/', methods=('POST', 'GET'))
def transform():
    if request.method == 'POST':
        global source, source2
        # print(request.form['code'])
        # axios请求
        data = request.get_json(silent=True)
        source = data['code']
        source_language = data['source_language']
        target_language = data['target_language']
        source2 = run_transform(source, source_language, target_language)
        print(source, source2)
        return {'source': source, 'result': source2}
    return redirect(url_for('index'))


@app.route('/diff/', methods=('POST', 'GET'))
def get_diff():
    if request.method == 'POST':
        # axios请求
        data = request.get_json(silent=True)
        source = data['text1']
        translated = data['text2']
        d = difflib.HtmlDiff()
        html = d.make_file(source.split('\n'), translated.split('\n'))
        print(source)
        print(translated)
        # print(html)
        # print(type(html))
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        t0 = tables[0]
        t0['style'] = "margin:auto;" + t0.get('style', '')
        t1 = tables[1]
        t1['style'] = "margin:auto;" + t1.get('style', '')
        result = str(t0) + '\n' + str(t1)
        # print(result)
        return {'result': result}
    return redirect(url_for('index'))


def run_transform(source, source_language, target_language):
    return 'testing'
