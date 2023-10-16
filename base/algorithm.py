


def filter(rooms, user_preferred_topics):
    # Step 2: Calculate popularity scores for rooms
    rooms_with_scores = []
    for room in rooms:
        popularity_score = room.total_participants + 0.5 * room.total_messages
        rooms_with_scores.append({'room': room, 'popularity_score': popularity_score})

    # Step 3: Sort rooms by popularity (in descending order)
    rooms_with_scores.sort(key=lambda x: x['popularity_score'], reverse=True)

    # Step 4: Filter rooms based on user's preferred topics
    matching_rooms = [room['room'] for room in rooms_with_scores if room['room'].topic in user_preferred_topics]
    non_matching_rooms = [room['room'] for room in rooms_with_scores if room['room'].topic not in user_preferred_topics]

    # Combine the matching and non-matching rooms to rearrange the list
    rearranged_rooms = matching_rooms + non_matching_rooms

    # Step 5: Return filtered rooms
    return rearranged_rooms
