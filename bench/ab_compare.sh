#!/usr/bin/env bash
# Vídeo lado a lado: A (Opus, videos/03-tunel-terra) | B (Fable, videos/03b-tunel-terra-fable)
# Uso: bash bench/ab_compare.sh   -> bench/ab_03.mp4 (1080x960, áudio do B)
set -e
A=videos/03-tunel-terra/out/video.mp4; B=videos/03b-tunel-terra-fable/out/video.mp4
ffmpeg -v error -y -i "$A" -i "$B" -filter_complex \
 "[0:v]scale=540:960,drawtext=text='A  OPUS 5.5':x=20:y=20:fontsize=34:fontcolor=white:box=1:boxcolor=black@0.6[a];\
  [1:v]scale=540:960,drawtext=text='B  FABLE':x=20:y=20:fontsize=34:fontcolor=white:box=1:boxcolor=black@0.6[b];\
  [a][b]hstack=inputs=2[v]" -map "[v]" -map 1:a -c:v libx264 -preset veryfast -crf 20 -c:a aac -shortest bench/ab_03.mp4
echo bench/ab_03.mp4
