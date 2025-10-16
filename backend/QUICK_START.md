# 🚀 Quick Start - Person Detection WebSocket Streaming

## ✅ All Issues Fixed!

Both import and OpenGL library issues have been resolved. The system is ready to use!

## Start in 3 Steps

### 1. Install Dependencies (if not done)
```bash
cd backend
uv sync
```

### 2. Start Backend Server
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 3. Start Frontend
```bash
cd ui
streamlit run app/pages/camera.py
```

## Use the System

1. **Get JWT Token**:
   - Go to `http://localhost:8000/docs`
   - Use `/api/v1/login/access-token` endpoint
   - Login with your credentials
   - Copy the `access_token` from response

2. **Connect Frontend**:
   - Open Streamlit frontend (opens automatically)
   - Paste JWT token in the "JWT Access Token" field
   - Click "Connect"
   - Should see: "Connected" ✅

3. **Start Streaming**:
   - Click "Start Camera" (grant browser permission)
   - Click "Start Streaming"
   - **Watch for green bounding boxes around detected persons!** 🎥

## What You'll See

When persons are in frame:
- ✅ Green bounding boxes around each person
- ✅ Confidence scores (e.g., "Person 0.87")
- ✅ Statistics overlay (person count, frames processed)
- ✅ Real-time detection metadata

## Configure Detection

Adjust settings via WebSocket:
```javascript
ws.send(JSON.stringify({
    action: 'configure',
    confidence: 0.6,  // 60% minimum confidence
    enable_qr: false  // Enable/disable QR codes
}));
```

## Test Without Frontend

```bash
cd backend
uv run python test_person_detection_integration.py
```

## Troubleshooting

### Import Error
```bash
# Verify __init__.py exists
ls app/cv_model/__init__.py
# Should exist ✅
```

### libGL.so.1 Error
```bash
# Check you're using headless version
grep opencv pyproject.toml
# Should show: opencv-python-headless ✅
```

### Server Error
```bash
# Use correct app path
uv run uvicorn app.main:app --reload
# NOT app.api.main:app
```

## What's Different from Original?

| Original `person_tracker.py` | New `frame_processor.py` |
|------------------------------|-------------------------|
| Requires camera initialization | Works with any frame bytes |
| Uses cv2.imshow() for display | No GUI needed |
| Standalone application | WebSocket integration |
| opencv-python (with GUI) | opencv-python-headless |

## Architecture

```
camera.py (Frontend)
    ↓ sends frame
streaming.py (WebSocket)
    ↓ processes
frame_processor.py (YOLOv8)
    ↓ returns
Annotated frame with bounding boxes!
```

## Documentation

- 📘 `FIXED_ALL_ISSUES.md` - Complete summary of fixes
- 📖 `PERSON_DETECTION_INTEGRATION.md` - Detailed integration guide
- 🔧 `IMPORT_FIX.md` - Import issue details
- 🖼️ `OPENCV_LIBGL_FIX.md` - OpenCV library fix

## Status

✅ **All Fixed and Working!**

- ✅ Import errors resolved
- ✅ OpenGL library errors resolved
- ✅ Person detection integrated
- ✅ WebSocket streaming functional
- ✅ Tests passing
- ✅ Server starts without errors

**Ready for use! 🎉**

