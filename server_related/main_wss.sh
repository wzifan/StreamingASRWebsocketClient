export SHERPA_PATH="[sherpa1_path]"
# export PATH=$SHERPA_PATH/build/bin:$PATH
# export PYTHONPATH=$PWD/build/lib:$SHERPA_PATH/sherpa/python/sherpa:$PYTHONPATH

exp_dir="[root_path]/k2_model/icefall-asr-conv-emformer-transducer-stateless2-zh"
decoding_method="modified_beam_search"
num_workers=4

model_path="$exp_dir/exp/cpu_jit.pt"
bpe_model_path="$exp_dir/data/lang_char_bpe/bpe.model"
token_path="$exp_dir/data/lang_char_bpe/tokens.txt"
lm_path="$exp_dir/data/lang_char_bpe/L.pt"

certificate_path="$SHERPA_PATH/mykey/cert.pem"

wav_path1="$exp_dir/test_wavs/0.wav"
wav_path2="$exp_dir/test_wavs/1.wav"

log_path="./log.txt"
server_port=8888
python  $SHERPA_PATH/sherpa/bin/conv_emformer_transducer_stateless2/streaming_server.py \
    --doc-root "$SHERPA_PATH/sherpa/bin/web" \
    --decoding-method=$decoding_method \
    --nn-model-filename $model_path \
    --token-filename $token_path \
    --nn-pool-size $num_workers \
    --max-batch-size 50 \
    --port $server_port \
    --certificate $certificate_path \
    --endpoint.rule1.contain-nonsilence 0 \
    --endpoint.rule1.min-trailing-silence 4.0 \
    --endpoint.rule1.min-utterance-length 0.0 \
    --endpoint.rule2.contain-nonsilence 1 \
    --endpoint.rule2.min-trailing-silence 30.0 \
    --endpoint.rule2.min-utterance-length 0.0 \
    --endpoint.rule3.contain-nonsilence 1 \
    --endpoint.rule3.min-trailing-silence 30.0 \
    --endpoint.rule3.min-utterance-length 0.0

# --lg=$lm_path \
# --bpe-model-filename=$bpe_model_path \
# --token-filename $token_path \

# endpoint path:[env_dir]/lib/python3.9/site-packages/sherpa/online_endpoint.py
