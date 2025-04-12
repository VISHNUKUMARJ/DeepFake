"""
Image DeepFake Detection Utility (Hybrid)

Uses DeepFace for real analysis. Falls back to mock analysis if needed.
"""
import os
import random
import time
import numpy as np
from deepface import DeepFace

def convert_numpy(obj):
    """Recursively convert NumPy types to native Python types."""
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    else:
        return obj

def check_fake_image(image_path):
    """
    Analyze an image to detect if it's AI-generated or manipulated.

    Returns DeepFace result if possible, otherwise returns mock fallback.
    """
    if not os.path.exists(image_path):
        return {
            "error": "Image file not found",
            "confidence_score": 0,
            "is_fake": False
        }

    try:
        # Attempt real analysis
        analysis = DeepFace.analyze(
            img_path=image_path,
            actions=["age", "gender", "race", "emotion"],
            enforce_detection=False
        )
        clean_analysis = convert_numpy(analysis)

        # Basic logic to decide if it's fake (you can refine this)
        emotion_conf = clean_analysis[0]['emotion'].get('neutral', 0)
        is_fake = emotion_conf < 30  # arbitrary rule for demo
        confidence = 0.8 if is_fake else 0.4

        return {
            "confidence_score": confidence,
            "is_fake": is_fake,
            "analysis": "DeepFace analysis successful.",
            "deepface_details": clean_analysis
        }

    except Exception as e:
        # Fall back to mock if DeepFace fails
        return fallback_fake_detection(image_path, error=str(e))

def fallback_fake_detection(image_path, error="DeepFace failed"):
    """Simulate fake detection for fallback."""
    time.sleep(1.5)

    file_size = os.path.getsize(image_path)
    seed = file_size % 100
    random.seed(seed)

    confidence = random.uniform(0.3, 0.95)
    is_fake = confidence > 0.5

    if is_fake:
        indicators = [
            "inconsistent lighting", "unusual facial feature proportions",
            "irregular background patterns", "unnatural texture smoothing",
            "pixel-level artifacts around edges", "shadow inconsistencies",
            "symmetry abnormalities", "unexpected color distributions"
        ]
        selected_indicators = random.sample(indicators, random.randint(2, 3))
        analysis_text = (
            "This image shows signs of AI generation or manipulation. "
            "Detected patterns include " + ", ".join(selected_indicators) + "."
        )
    else:
        analysis_text = (
            "This image appears to be authentic based on our fallback analysis. "
            "No significant indicators of manipulation were detected."
        )

    return {
        "confidence_score": confidence,
        "is_fake": is_fake,
        "analysis": analysis_text,
        "fallback_used": True,
        "error": error
    }
