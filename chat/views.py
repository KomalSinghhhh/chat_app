from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Message

@login_required
def chat_room(request, room_name):
    # Get search query if provided
    search_query = request.GET.get('search', '') 
    
    # Exclude the current user from the user list
    users = User.objects.exclude(id=request.user.id) 
    
    # Fetch chat messages between the current user and the selected user
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )
    
    # Apply search query if it exists
    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))  
    
    # Order chats by timestamp
    chats = chats.order_by('timestamp') 
    
    # Prepare a list for storing the last messages with each user
    user_last_messages = []

    for user in users:
        # Fetch the most recent message between the current user and the user
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        # Append the user and their last message to the list
        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Ensure datetime.min is timezone-aware
    aware_min = make_aware(datetime.min)  

    # Sort user_last_messages by the timestamp of the last_message in descending order
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else aware_min,
        reverse=True
    )

    # Render the chat.html template with the required context
    return render(request, 'chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query 
    })
