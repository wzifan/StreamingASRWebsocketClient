from PyInstaller.utils.hooks import collect_data_files, collect_all, collect_dynamic_libs

hiddenimports = ["samplerate", "paddle", "paddlenlp", "datasets"]
datas = collect_data_files("samplerate")
datas = datas + collect_dynamic_libs("paddle")
datas = datas + collect_all('paddlenlp.transformers')[0]
datas = datas + collect_all('datasets')[0]
datas = datas + [('./ernie-3.0-medium-zh', 'ernie-3.0-medium-zh'), ('./pun_models', 'pun_models'),
                 ('./icons', 'icons'), ('./images', 'images')]
