# In deepface_patch/basemodels/FbDeepFace.py
from tensorflow import keras
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Convolution2D, Activation, MaxPooling2D, Flatten, Dense, Dropout

# Instead of LocallyConnected2D, use Convolution2D with appropriate parameters
# (Original function would need to be modified accordingly)

def loadModel(url="https://github.com/swghosh/DeepFace/releases/download/weights-vggface-2d-aligned/VGGFace2_DeepFace_weights_val-0.9034.h5"):
    # Modified model definition that uses Conv2D instead of LocallyConnected2D
    # ...
