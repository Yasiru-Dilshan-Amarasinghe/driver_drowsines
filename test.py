try:
    import mediapipe as mp  # type: ignore[import]
    print("✅ MediaPipe is installed correctly!")
except ImportError as e:
    print(f"❌ MediaPipe is NOT installed or not detected.")
    print(f"Error: {e}")
    print("Install with: pip install mediapipe")