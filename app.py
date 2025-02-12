import os
import json
from PIL import Image
import tempfile

import numpy as np
import tensorflow as tf
import streamlit as st
from groq_api import generate_text_from_image, generate_text_from_prediction

# Set page configuration
st.set_page_config(
    page_title="Plant Disease Classifier",
    page_icon="🌿",
    layout="wide"
)

working_dir = os.path.dirname(os.path.abspath(__file__))
model_path = f"{working_dir}/plant_disease_prediction_model.h5"
# Load the pre-trained model
model = tf.keras.models.load_model(model_path)

# loading the class names
class_indices = json.load(open(f"{working_dir}/class_indices.json"))

# Function to Load and Preprocess the Image using Pillow
def load_and_preprocess_image(image_path, target_size=(224, 224)):
    # Load the image
    img = Image.open(image_path)
    # Resize the image
    img = img.resize(target_size)
    # Convert the image to a numpy array
    img_array = np.array(img)
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    # Scale the image values to [0, 1]
    img_array = img_array.astype('float32') / 255.
    return img_array

# Function to Predict the Class of an Image
def predict_image_class(model, image_path, class_indices):
    preprocessed_img = load_and_preprocess_image(image_path)
    predictions = model.predict(preprocessed_img)
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    predicted_class_name = class_indices[str(predicted_class_index)]
    confidence = np.max(predictions) * 100
    return predicted_class_name, confidence

# Streamlit App
st.title('🌿 Plant Disease Classifier')
st.write("Upload an image of a plant leaf to detect diseases")

# Add text indicating the leaves for which the model works perfectly

uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(image, caption='Uploaded Image', use_container_width=True)

    with col2:
        # Preprocess the uploaded image and predict the class
        prediction, confidence = predict_image_class(model, uploaded_image, class_indices)
        if confidence < 80:
            st.error('Sorry, not able to detect the disease with high confidence.')
            # Save the uploaded image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(uploaded_image.getbuffer())
                temp_file_path = temp_file.name

            # Generate text using Groq API for low confidence
            generated_text = generate_text_from_prediction(prediction, confidence, temp_file_path)
        else:
            st.success(f'Prediction: {prediction}')
            st.info(f'Confidence: {confidence:.2f}%')

            # Generate text using Groq API for high confidence
            generated_text = generate_text_from_prediction(prediction, confidence)

        # Display additional information
        st.write("### Additional Information")
        st.write(f"**Class:** {prediction}")
        st.write(f"**Confidence:** {confidence:.2f}%")

        # Display generated text
        st.write("### Generated Text")
        st.write(generated_text)

st.write("""
### This model works perfectly for the following leaves:
- Apple
- Blueberry
- Cherry (including sour)
- Corn (Maize)
- Grape
- Orange
- Peach
- Pepper (Bell Pepper)
- Potato
- Raspberry
- Soybean
- Squash
- Strawberry
- Tomato
""")

