# 会议记录小助手

版本：5.0.1

软件著作权登记号：2023SR1804554 (v4.2)

#### Git lfs clone and unpack files

```shell
# lfs clone
git lfs clone https://github.com/wzifan/StreamingASRWebsocketClient.git
# unpack LLM files
unzip Qwen1.5-0.5B-Chat.zip
```

#### python环境依赖

`requirements.txt`

```
samplerate==0.1.0
pyside6==6.1.3
pyaudio==0.2.13
websocket-client==1.6.4
paddlepaddle==2.5.1
paddlenlp==2.6.1
termcolor==2.3.0
transformers==4.39.2
modelscope==1.13.3
accelerate==0.28.0
pyinstaller==6.5.0

torch==2.0.1+cpu
torchvision==0.15.2 
torchaudio==2.0.2 
tensorboard==2.14.0
```

```shell
# 创建和激活环境, 注意python版本为3.8以兼容windows7
conda create -n env_name python=3.8
conda activate env_name
```

使用`pip install -r requirements.txt`安装环境

------

#### 可执行文件导出步骤

```shell
cd [项目根目录]

pip install -r requirements.txt

# 修改main_ui.py中的:
# server related
self.server_addr = 'your sherpa-1.2 server address'
self.server_port = 8888

pyinstaller main_ui.py -Dw --name="meeting_record_assistant" --icon="./icons/icon.png"  --additional-hooks-dir="./hooks"
```

------

#### 标点符号模型引用说明

###### 模型代码

标点符号模型参考github项目[PunctuationModel](https://github.com/yeyupiaoling/PunctuationModel)

`PunctuationModel/utils`与`[项目根目录]/paddle_punctuation`基本一致

###### 模型文件

其模型下载链接为https://download.csdn.net/download/qq_33200967/75664996

下载完后将解压后的模型文件夹命名为`pun_models`并放于`[项目根目录]`下，文件目录结构如下所示：

```
[项目根目录]
--pun_models
----info.json
----model.pdiparams
----model.pdiparams.info
----model.pdmodel
----vocab.txt
```

###### 依赖文件

运行`punctuation_infer.py`，将自动下载得到的`ernie-3.0-medium-zh`文件夹放于`[项目根目录]`下，文件目录结构如下所示：

```
[项目根目录]
--ernie-3.0-medium-zh
----ernie_3.0_medium_zh_vocab.txt
----special_tokens_map.json
----tokenizer_config.json
----vocab.txt
```

(`ernie-3.0-medium-zh`一般被默认下载于`[用户目录]/.paddlenlp/models/`，如`C:\Users\xxx\.paddlenlp\models\ernie-3.0-medium-zh`)

#### 服务端说明

本项目使用新一代[kaldi作为服务端](https://github.com/k2-fsa)，服务的部署方式如下：

1. 安装1.2版本的sherpa，安装方式参照https://k2-fsa.github.io/sherpa/sherpa/install/from_source.html，sherpa-1.2的下载地址为https://github.com/k2-fsa/sherpa/archive/refs/tags/v1.2.tar.gz

2. 更改sherpa-1.2的语音切分代码文件

   **为了使得语音分割更符合实际环境，我们对sherpa-1.2中的`sherpa-1.2\sherpa\python\sherpa\online_endpoint.py`与环境文件夹中的`[env_dir]/lib/python3.9/site-packages/sherpa/online_endpoint.py`进行了修改，修改好的文件在`server_related/online_endpoint.py`中，需自行替换**

3. 下载模型

   ```shell
   git lfs install
   git clone https://huggingface.co/PingfengLuo/icefall-asr-conv-emformer-transducer-stateless2-zh
   ```

   更多模型参见：https://k2-fsa.github.io/sherpa/pretrained-models.html

4. 产生秘钥文件

   ```shell
   cd [sherpa根目录]/sherpa/bin/web
   conda activate [安装了sherpa的python环境]
   pip install pyopenssl
   python generate-certificate.py
   ```

   得到的`cert.pem`即为所需秘钥文件

   为了安全，将产生的`cert.pem`、`selfsigned.crt`、`private.key`放入`[key文件夹]`

5. 运行服务启动脚本

   ```shell
   conda activate [安装了sherpa的python环境]
   bash server_related/main_wss.sh
   ```


#### 图标说明

本软件图标下载于[IconPark](https://iconpark.oceanengine.com/home)

具体图标为其官方图标库中的“编辑”

#### 开放代码许可

本软件使用了包括[LGPL](https://www.gnu.org/licenses/lgpl-3.0.html)、[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.html)、[MIT](https://mitsloan.mit.edu/licensing)等协议的内容，具体如下：

1. [pyside6](https://pypi.org/project/PySide6/6.5.3/)遵循[LGPL License](https://www.gnu.org/licenses/lgpl-3.0.html)

2. [websocket-client](https://pypi.org/project/websocket-client/)、[paddlepaddle](https://pypi.org/project/paddlepaddle/)、[paddlenlp](https://pypi.org/project/paddlenlp/)遵循[Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0.html)
3. [samplerate](https://pypi.org/project/samplerate/)、[pyaudio](https://pypi.org/project/PyAudio/)、[termcolor](https://pypi.org/project/termcolor/)遵循[MIT License](https://mitsloan.mit.edu/licensing)
4. 标点符号添加使用的代码[PunctuationModel](https://github.com/yeyupiaoling/PunctuationModel)和[模型](https://download.csdn.net/download/qq_33200967/75664996)遵循[Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0.html)
5. [pyinstaller](https://pyinstaller.org/en/stable/index.html)遵循双重协议，详见https://pyinstaller.org/en/stable/license.html
6. 服务端使用的[新一代kaldi](https://github.com/k2-fsa/k2)、[sherpa](https://github.com/k2-fsa/sherpa)遵循[Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0.html)
7. 服务端使用的语音识别模型[conv_emformer](https://huggingface.co/PingfengLuo/icefall-asr-conv-emformer-transducer-stateless2-zh)遵循[Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0.html)

如有未列出的，请联系邮箱2447424163@qq.com

由于使用了pyside6，本软件遵循[LGPL License](https://www.gnu.org/licenses/lgpl-3.0.html)

#### 其他

软件使用说明和用户使用协议见[软件使用说明.md](./软件使用说明.md)和[用户使用协议.md](./用户使用协议.md)
