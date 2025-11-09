import time

import paddlehub as hub

model = hub.Module(
    name='auto_punc',
    version='1.0.0')

texts = [
    'NICE!近几年不但我用书给女儿压岁也劝说亲朋不要给女儿压岁钱而改送压岁书今天天气真好啊nice'
]
print("start")
for i in range(10):
    t1 = time.time()
    punc_texts = model.add_puncs(texts)
    print(time.time() - t1)
    print(punc_texts)