# ================================
#   QUESTIONS BANK FOR HCI PROJECT
# ================================

# --------------------------------
# 1. HAND-GESTURE QUESTIONS
# (LEFT / RIGHT HAND ANSWERS)
# --------------------------------

hand_gesture_questions = [
    # Very Simple Identification
    {
        "id": 1,
        "question": "Which one is a fruit?",
        "left": "Apple",
        "right": "Cat",
        "answer": "left"
    },
    {
        "id": 2,
        "question": "Which animal is bigger?",
        "left": "Dog",
        "right": "Elephant",
        "answer": "right"
    },
    {
        "id": 3,
        "question": "Which shape has three sides?",
        "left": "Triangle",
        "right": "Circle",
        "answer": "left"
    },
    {
        "id": 4,
        "question": "Which one is yellow?",
        "left": "Banana",
        "right": "Rectangle",
        "answer": "left"
    },
    {
        "id": 5,
        "question": "Which one can bark?",
        "left": "Dog",
        "right": "Apple",
        "answer": "left"
    },

    # Recognition & Understanding
    {
        "id": 6,
        "question": "Which is the round shape?",
        "left": "Circle",
        "right": "Rectangle",
        "answer": "left"
    },
    {
        "id": 7,
        "question": "Which one is an animal?",
        "left": "Cat",
        "right": "Orange",
        "answer": "left"
    },
    {
        "id": 8,
        "question": "Which fruit is orange in color?",
        "left": "Orange",
        "right": "Banana",
        "answer": "left"
    },
    {
        "id": 9,
        "question": "Which one has four sides?",
        "left": "Rectangle",
        "right": "Triangle",
        "answer": "left"
    },
    {
        "id": 10,
        "question": "Which one is the heavier animal?",
        "left": "Elephant",
        "right": "Dog",
        "answer": "left"
    },

    # Bonus Mixed-Difficulty
    {
        "id": 11,
        "question": "Which fruit starts with the letter A?",
        "left": "Apple",
        "right": "Banana",
        "answer": "left"
    },
    {
        "id": 12,
        "question": "Which one is NOT a fruit?",
        "left": "Dog",
        "right": "Orange",
        "answer": "left"
    },
    {
        "id": 13,
        "question": "Which shape has 4 sides?",
        "left": "Rectangle",
        "right": "Circle",
        "answer": "left"
    },
    {
        "id": 14,
        "question": "Which animal is smaller?",
        "left": "Cat",
        "right": "Elephant",
        "answer": "left"
    },
    {
        "id": 15,
        "question": "Which one is round?",
        "left": "Circle",
        "right": "Apple",
        "answer": "left"
    },
]



# --------------------------------
# 2. LASER-MATCHING QUESTIONS
# --------------------------------

laser_matching_type_A = [
    {
        "id": 1,
        "groups": ["Fruit", "Animal"],
        "items": {
            "apple": "Fruit",
            "cat": "Animal",
            "orange": "Fruit",
            "elephant": "Animal"
        }
    },
    {
        "id": 2,
        "groups": ["Shapes", "Fruits"],
        "items": {
            "circle": "Shapes",
            "rectangle": "Shapes",
            "banana": "Fruits"
        }
    }
]


laser_matching_type_B = {
    "description": "Match picture to correct word",
    "pairs": {
        "banana": "banana",
        "dog": "dog"
    },
    "wrong_words": ["circle"]
}


laser_matching_type_C = {
    "description": "Match shape to real-world object",
    "shapes": ["circle", "triangle"],
    "objects": {
        "orange": "circle",
        "pizza slice": "triangle"
    }
}


# --------------------------------
# EXPORT ALL FOR EASY IMPORT
# --------------------------------

__all__ = [
    "hand_gesture_questions",
    "laser_matching_type_A",
    "laser_matching_type_B",
    "laser_matching_type_C"
]
