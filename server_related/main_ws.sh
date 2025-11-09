export SHERPA_PATH="[sherpa1_path]"
# export PATH=$SHERPA_PATH/build/bin:$PATH
# export PYTHONPATH=$PWD/build/lib:$SHERPA_PATH/sherpa/python/sherpa:$PYTHONPATH

exp_dir="[root_path]/k2_model/icefall-asr-conv-emformer-transducer-stateless2-zh"
decoding_method="modified_beam_search"
num_workers=4

model_path="$exp_dir/exp/cpu_jit.pt"
token_path="$exp_dir/data/lang_char_bpe/tokens.txt"
lm_path="$exp_dir/data/lang_char_bpe/L.pt"

wav_path1="$exp_dir/test_wavs/0.wav"
wav_path2="$exp_dir/test_wavs/1.wav"

log_path="./log.txt"
server_port=8888
sherpa-online-websocket-server \
    --doc-root="$SHERPA_PATH/sherpa/bin/web" \
    --decoding-method=$decoding_method \
    --nn-model=$model_path \
    --tokens=$token_path \
    --use-gpu=false \
    --num-work-threads=$num_workers \
    --port=$server_port \
    --log-file=$log_path

# --lg=$lm_path \
