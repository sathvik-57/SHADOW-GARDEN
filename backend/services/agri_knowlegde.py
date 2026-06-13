# backend/services/agri_knowledge.py

disease_prevention_guide = {
    "Tomato___Early_blight": {
        "prevention": [
            "Remove infected leaves immediately.",
            "Use fungicides like chlorothalonil or copper-based sprays.",
            "Practice crop rotation and avoid overhead watering."
        ],
        "recommend_crop": "Tomato",
    },
    "Tomato___Late_blight": {
        "prevention": [
            "Apply fungicides before rainy seasons.",
            "Remove and destroy infected plants.",
            "Plant resistant tomato varieties."
        ],
        "recommend_crop": "Tomato",
    },
    "Potato___Early_blight": {
        "prevention": [
            "Avoid overhead irrigation.",
            "Apply appropriate fungicides.",
            "Keep the garden clean and free of debris."
        ],
        "recommend_crop": "Potato",
    },
    # Add more diseases as needed
}

crop_lifecycle_steps = {
    "Tomato": [
        "Seed selection and nursery preparation",
        "Sowing in nursery beds (Week 1–2)",
        "Transplantation to main field (Week 3–4)",
        "Regular irrigation and weeding (Week 5–8)",
        "Flowering and pest control (Week 6–10)",
        "Harvesting ripe fruits (Week 10–14)"
    ],
    "Potato": [
        "Tuber selection and sprouting",
        "Planting sprouted tubers (Week 1–2)",
        "Soil mounding and irrigation (Week 3–6)",
        "Fertilizer and pest management (Week 6–10)",
        "Leaf drying and harvesting (Week 12–16)"
    ],
    # Add more crops as needed
}
