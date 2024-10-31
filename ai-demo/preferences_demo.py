import csv
import random

PREFERENCES_FILE = "users.csv"
VIDEOS_FILE = "videos.csv"

def get_user_preferences(user_id):
    """Fetch user preferences from CSV."""
    with open(PREFERENCES_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['user_id']) == user_id:
                return [float(row['math']), float(row['science']), float(row['english']), float(row['history'])]

def recommend_video(user_id):
    """Recommend a video based on user preferences."""
    preferences = get_user_preferences(user_id)
    categories = ['math', 'science', 'english', 'history']
    chosen_category = random.choices(categories, weights=preferences, k=1)[0]

    with open(VIDEOS_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if chosen_category in row['tags']:
                return row

def update_preferences(user_id, category, reaction):
    """Update user preferences in CSV based on their feedback."""
    updated_rows = []
    with open(PREFERENCES_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['user_id']) == user_id:
                row[category] = str(float(row[category]) + (0.05 if reaction == 1 else -0.1))
                total = sum([float(row[c]) for c in ['math', 'science', 'english', 'history']])
                for c in ['math', 'science', 'english', 'history']:
                    row[c] = str(float(row[c]) / total)
            updated_rows.append(row)

    with open(PREFERENCES_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['user_id', 'math', 'science', 'english', 'history'])
        writer.writeheader()
        writer.writerows(updated_rows)

def display_preferences(user_id):
    """Display current preferences."""
    preferences = get_user_preferences(user_id)
    categories = ['math', 'science', 'english', 'history']
    print(f"Current preferences for User {user_id}:")
    for i, category in enumerate(categories):
        print(f"{category.capitalize()}: {preferences[i]:.2f}")