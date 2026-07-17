#!/bin/bash
# Start backend in background, wait, then run the video generation
cd /Users/santosh/Desktop/projects/videoGen
export COQUI_TOS_AGREED=1

# Kill any existing
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1

# Start backend
/opt/homebrew/opt/python@3.11/bin/python3.11 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for startup
for i in $(seq 1 10); do
    if curl -s http://localhost:8000/api/v1/projects > /dev/null 2>&1; then
        echo "Backend ready"
        break
    fi
    sleep 1
done

# Re-import the VID01 script
echo "Importing VID01 script..."
PIPELINE_ID=$(/opt/homebrew/opt/python@3.11/bin/python3.11 scripts/import_vid01.py 2>&1 | grep "Pipeline ID" | awk '{print $3}')
echo "Pipeline ID: $PIPELINE_ID"

# Generate images
echo "Generating images..."
curl -s -X POST "http://localhost:8000/api/v1/pipeline/$PIPELINE_ID/generate-images"

# Wait for images
echo "Waiting for image generation..."
while true; do
    RESULT=$(curl -s "http://localhost:8000/api/v1/pipeline/$PIPELINE_ID/images" 2>/dev/null)
    COMPLETED=$(echo "$RESULT" | /opt/homebrew/opt/python@3.11/bin/python3.11 -c "import sys,json; d=json.load(sys.stdin); print(sum(1 for i in d['images'] if i['status']=='completed'))" 2>/dev/null || echo "0")
    echo "  Images completed: $COMPLETED/5"
    if [ "$COMPLETED" = "5" ]; then
        break
    fi
    sleep 30
done

echo "All images generated. Starting Ken Burns + TTS..."
curl -s -X POST "http://localhost:8000/api/v1/pipeline/$PIPELINE_ID/generate-ken-burns-video"

# Wait for video generation
echo "Waiting for Ken Burns + TTS generation..."
while true; do
    LOG_TAIL=$(tail -3 /tmp/uvicorn.log 2>/dev/null)
    echo "  Latest: $LOG_TAIL"
    
    # Check if final.mp4 exists
    if [ -f "output/videos/$PIPELINE_ID/final.mp4" ]; then
        echo "Final video generated!"
        break
    fi
    sleep 60
done

# Verify
echo "=== Verification ==="
ffprobe -v error -show_entries stream=codec_type,codec_name,sample_rate,duration:format=duration,size -of default=noprint_wrappers=1 "output/videos/$PIPELINE_ID/final.mp4" 2>&1

echo "=== Audio files ==="
ls -lh "output/videos/$PIPELINE_ID/audio/" 2>&1

echo "=== Final clips ==="
ls -lh "output/videos/$PIPELINE_ID/final_clips/" 2>&1

echo ""
echo "PIPELINE_ID=$PIPELINE_ID"
echo "FINAL_VIDEO=output/videos/$PIPELINE_ID/final.mp4"

# Kill backend
kill $BACKEND_PID 2>/dev/null