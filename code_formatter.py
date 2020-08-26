import subprocess
from yapf.yapflib.yapf_api import FormatCode


def clang_format(code, language_arg):
    p = subprocess.Popen(['clang-format', language_arg],
          stdout = subprocess.PIPE,
          stdin = subprocess.PIPE)
    stdout, _ = p.communicate(bytes(code, encoding='utf8'))
    return stdout.decode('utf-8')


def format_cpp(code):
    return clang_format(code, "--assume-filename=.cpp")


def format_java(code):
    return clang_format(code, "--assume-filename=.java")


def format_python(code):
    code, _ = FormatCode(code)
    return code
