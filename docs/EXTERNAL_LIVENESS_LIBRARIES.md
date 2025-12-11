# External Liveness Detection Libraries Integration

## Overview

The system now supports integration with external liveness detection libraries to enhance anti-spoofing capabilities. These libraries use pre-trained deep learning models that are specifically designed to detect fake faces (photos, videos, masks).

## Supported Libraries

### 1. face-live-detection-sdk
- **Package**: `face-live-detection-sdk`
- **Type**: Pre-trained deep learning model
- **Installation**: `pip install face-live-detection-sdk`
- **Advantages**: 
  - Uses TensorFlow-based models
  - Fast inference
  - Good accuracy for photo detection

### 2. liveness-detector
- **Package**: `liveness-detector`
- **Type**: Gesture-based liveness detection
- **Installation**: `pip install liveness-detector`
- **Advantages**:
  - Challenge-response mechanism
  - Prompts users for gestures (blink, smile, etc.)
  - Good for preventing video replay attacks

## How It Works

The system uses a **hybrid approach**:

1. **Primary Detection**: MediaPipe Face Mesh (always active)
   - Depth analysis
   - Movement detection
   - Blink detection

2. **Secondary Detection**: External library (if available)
   - Pre-trained deep learning models
   - Texture analysis
   - Advanced pattern recognition

3. **Decision Logic**:
   - If external library detects FAKE → **Immediate rejection**
   - If external library confirms LIVE → **Can override MediaPipe** (if 2+ indicators present)
   - If external library unavailable → **Falls back to MediaPipe only**

## Installation

To enable external liveness detection, install one of the supported libraries:

```bash
# Option 1: face-live-detection-sdk (recommended)
pip install face-live-detection-sdk

# Option 2: liveness-detector
pip install liveness-detector
```

The system will automatically detect and use the first available library.

## Configuration

The external detector is enabled by default. To disable it:

```python
# In kiosk_app.py, when creating LivenessDetector:
detector = LivenessDetector(use_external=False)
```

## Benefits

1. **Better Photo Detection**: External libraries use specialized models trained on spoofing datasets
2. **Defense in Depth**: Multiple detection methods increase security
3. **Fallback Support**: System works even if external library is unavailable
4. **Easy Integration**: No code changes needed - just install the library

## Current Status

- ✅ Code integration complete
- ✅ Automatic library detection
- ✅ Fallback to MediaPipe if unavailable
- ⚠️ Libraries need to be installed separately (optional)

## Testing

After installing an external library:

1. Start the kiosk application
2. Check console output for: `✓ External liveness detector initialized`
3. Test with a photo - should be rejected immediately
4. Test with a real face - should work normally

## Troubleshooting

**Library not detected?**
- Check installation: `pip list | grep -i liveness`
- Check console output for import errors
- System will fall back to MediaPipe-only mode

**Performance issues?**
- External libraries may add ~50-200ms per frame
- Consider disabling if performance is critical
- MediaPipe-only mode is faster but less accurate for photos

## Future Enhancements

- Support for more libraries (kbyai, image-liveness)
- Configurable library priority
- Performance benchmarking
- Accuracy comparison reports





