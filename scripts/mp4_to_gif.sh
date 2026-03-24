#!/usr/bin/env bash
# Convert an MP4 video to a high-quality GIF using a two-pass palette approach.
# Usage: ./scripts/mp4_to_gif.sh <input.mp4> [output.gif] [width]

set -euo pipefail

INPUT="${1:?Usage: $0 <input.mp4> [output.gif] [width]}"
OUTPUT="${2:-${INPUT%.mp4}.gif}"
WIDTH="${3:-600}"

if ! command -v ffmpeg &>/dev/null; then
    echo "Error: ffmpeg is required but not found." >&2
    exit 1
fi

ffmpeg -i "$INPUT" \
    -vf "fps=10,scale=${WIDTH}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
    -loop 0 \
    "$OUTPUT"

echo "Created: $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
