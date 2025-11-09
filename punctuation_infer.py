# -*- coding: utf-8 -*-
import time

from paddle_punctuation.predictor import PunctuationExecutor

if __name__ == '__main__':
    # tokenizer_dir = os.path.abspath('./ernie-3.0-medium-zh')
    model_dir = './pun_models'
    pun_executor = PunctuationExecutor(model_dir=model_dir, use_gpu=False)
    # pun_executor = PunctuationExecutor(model_dir='./pun_models', tokenizer_dir=tokenizer_dir, use_gpu=False)
    for i in range(5):
        t1 = time.time()
        result = pun_executor('测试文本')
        print(result, time.time() - t1)
