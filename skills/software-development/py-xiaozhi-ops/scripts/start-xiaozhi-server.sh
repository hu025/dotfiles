#!/bin/bash
# xiaozhi-server 启动脚本（修复 libten_vad.so 缺失）
XD="/home/saber/xiaozhi-server/xiaozhi_server-linux-amd64-v0.6.4/xiaozhi_server-linux-amd64"
VAD="$XD/ten-vad/lib/Linux/x64"
export LD_LIBRARY_PATH="$VAD:$LD_LIBRARY_PATH"
cd "$XD" && ./xiaozhi_server -c "$XD/main_config.yaml"
