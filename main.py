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


def split_by_indent(source_code):
    # 根据缩进分割python代码
    # 无法处理函数前有修饰语的情况

    lines = source_code.split("\n")
    fragment = []
    result = []
    first = True

    for line in lines:
        if (len(line) == 0):
            continue
        if (line.split(' ')[0] == "def"):
            if (first == False and len(fragment) > 0):
                result.append("".join(fragment))
                fragment = []
            first = False
        fragment.append(line)
    if (len(fragment) != 0):
        result.append("".join(fragment))
    
    return result


def split_by_brace(source_code):
    # 根据大括号分割java/cpp代码中的多个函数
    # 无法处理一个class内定义了多个函数的情况

    result = []
    stack = []
    start_point = 0

    for i, char in enumerate(source_code):
        if char == "{":
            stack.append(char)
        elif char == "}":
            assert len(stack) > 0, "Unmatched right brace"
            stack.pop()
            if (len(stack) == 0):
                result.append(source_code[start_point:i + 1])
                start_point = i + 1

    assert len(stack) == 0, "Unmatched left brace"
    return result


def split_code(source_code, source_language):
    if (source_language == "python"):
        return split_by_indent(source_code)
    else:
        return split_by_brace(source_code)


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

        split_source_code = split_code(source, source_language)
        split_target_code = []
        for fragment in split_source_code:
            source2 = run_transform(fragment, source_language, target_language)
            print(fragment, source2)
            split_target_code.append(source2[0])
        source2 = "".join(split_target_code)
        print("results:\n", source2)
        return {'source': source, 'result': source2}
    return redirect(url_for('index'))


def run_transform(source, source_language, target_language):
    assert source_language in {'python', 'java', 'cpp'}, source_language
    assert target_language in {'python', 'java', 'cpp'}, target_language
    assert source_language != target_language, "Source language is same as target language!"
    
    if (source_language == 'cpp' and target_language == 'java') or source_language == 'java':
        output = translator1.translate(source, source_language, target_language)
    else:
        output = translator2.translate(source, source_language, target_language)
    return output
