# Installation Notes

## Windows Installation Fix for dlib

On Windows, `dlib` requires Visual Studio C++ build tools to compile from source, which can be problematic.

### Solution: Use dlib-bin

Instead of installing `dlib` (which requires compilation), we use `dlib-bin` which provides pre-built binaries for Windows.

**Installation:**
```bash
pip install dlib-bin
pip install face-recognition
```

The `dlib-bin` package provides the `dlib` module, so `face-recognition` works correctly without needing to compile `dlib` from source.

### Updated requirements.txt

The `requirements.txt` file has been updated to use `dlib-bin>=19.24.0` instead of `dlib>=19.24.0`.

### Verification

To verify the installation works:
```bash
python -c "import face_recognition; import dlib; print('Success!')"
```

---

**Note:** If you encounter any issues with face recognition, ensure that `dlib-bin` is installed and not the source version of `dlib`.

