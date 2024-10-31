from preferences_demo import recommend_video, update_preferences, display_preferences

def simulate_demo():
    user_id = 1
    print(f"Starting simulation for User {user_id}:")
    display_preferences(user_id)
    
    while True:
        video = recommend_video(user_id)
        print(f"\nRecommended video: {video['title']} (Tags: {video['tags']})")

        reaction = input("Do you like the video? (1 for Like, -1 for Dislike, q to quit): ")
        
        if reaction == 'q':
            print("Exiting simulation.")
            break
        
        if reaction in ['1', '-1']:
            category = video['tags']
            update_preferences(user_id, category, int(reaction))
            print("\nUpdated preferences:")
            display_preferences(user_id)
        else:
            print("Invalid input. Please enter 1, -1, or q.")

if __name__ == "__main__":
    simulate_demo()