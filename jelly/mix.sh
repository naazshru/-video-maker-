#!/usr/bin/env bash
# Places each voice-over line on its scene and ducks the music under the voice.
set -euo pipefail
cd "$(dirname "$0")"
# segment: start end place_at   (seconds in vo_raw.mp3 -> seconds in trailer)
SEGS="0.00 2.50 0.40
3.05 6.08 3.70
6.62 9.00 7.50
9.52 11.32 13.30
11.38 12.52 15.80
12.66 14.11 18.30
14.11 16.08 20.60
16.42 19.15 23.20
19.52 22.44 26.90"
i=0; F=""; L=""
while read s e p; do
  d=$(python3 -c "print(int($p*1000))")
  F+="[0:a]atrim=$s:$e,asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st=$(python3 -c "print(round($e-$s-0.06,3))"):d=0.06,adelay=$d|$d[v$i];"
  L+="[v$i]"; i=$((i+1))
done <<< "$SEGS"
ffmpeg -y -loglevel error -i vo_raw.mp3 -i music.wav -filter_complex \
"${F}${L}amix=inputs=$i:normalize=0,aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur=30,volume=1.6,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120[vo];
[vo]asplit=2[vo1][vo2];
[1:a][vo1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];
[duck][vo2]amix=inputs=2:normalize=0,alimiter=limit=0.95,atrim=0:30[out]" -map "[out]" -ar 44100 final_audio.wav
echo ok
