# 2020 Google sps project: Transcompile

### Transcompile model usage

`run_transform(source, source_language, target_language)`  function in `main.py`  is reserved for calling transcompile model. This function offers source code, source language kind and target language kind, and expects to return target code.

- source: code text (String)
- source_language: one in the following three kinds (String):
  - 'python'
  - 'c++'
  - 'java'

- target_language: one in the following three kinds (String):
  - 'python'
  - 'c++'
  - 'java'
- return value: transformed code text (String)



You can put your model code in appropriate location and import your model to run in `run_transform` function. Two model checkpoints([model_1](https://dl.fbaipublicfiles.com/transcoder/model_1.pth), [model_2](https://dl.fbaipublicfiles.com/transcoder/model_2.pth)) should be put in `google_sps_transcompile/transcoder/models`. 

Please replace the path to `libclang.so` to the correct path in `clang.cindex.Config.set_library_path('path_to_libclang')` in `code_tokenizer.py`.