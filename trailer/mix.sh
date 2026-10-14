#!/usr/bin/env bash
# usage: trailer/mix.sh <product_dir> <duration>
# Places each voice-over line (vo_segments.txt: src_start src_end place_at) and ducks music under the voice.
set -euo pipefail
cd "$1"; DUR=$2
i=0; F=""; L=""
while read s e p; do
  [ -z "$s" ] && continue
  d=$(python3 -c "print(int($p*1000))"); fo=$(python3 -c "print(round($e-$s-0.06,3))")
  F+="[0:a]atrim=$s:$e,asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st=$fo:d=0.06,adelay=$d|$d[v$i];"
  L+="[v$i]"; i=$((i+1))
done < vo_segments.txt
ffmpeg -y -loglevel error -i vo_raw.mp3 -i music.wav -filter_complex \
"${F}${L}amix=inputs=$i:normalize=0,aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur=$DUR,volume=1.6,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120[vo];
[vo]asplit=2[vo1][vo2];
[1:a][vo1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];
[duck][vo2]amix=inputs=2:normalize=0,alimiter=limit=0.95,atrim=0:$DUR[out]" -map "[out]" -ar 44100 final_audio.wav
echo "mixed $1"
