from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import sys
sys.path.append("./transcoder")

from transcoder.translate import Translator

app = Flask(__name__)
translator1 = Translator(
                            model_path="transcoder/models/model_1.pth", 
                            BPE_path="transcoder/models/BPE_with_comments_codes"
                        )
translator2 = Translator(
                            model_path="transcoder/models/model_2.pth", 
                            BPE_path="transcoder/models/BPE_with_comments_codes"
                        )
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
    result = json.loads(response.text)['output']
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


def run_transform(source, source_language, target_language):
    assert source_language in {'python', 'java', 'cpp'}, source_language
    assert target_language in {'python', 'java', 'cpp'}, target_language
    if (source_language == 'cpp' and target_language == 'java') or source_language == 'java':
        output = translator1.translate(source, source_language, target_language)
    else:
        output = translator2.translate(source, source_language, target_language)
    return output
