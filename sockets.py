from flask_socketio import emit, join_room
from models import db, Message, User

def generate_room(user1, user2):
    return "_".join(sorted([user1, user2]))

def register_socket_events(socketio):
    @socketio.on('join')
    def on_join(data):
        username = data.get('username')
        partner = data.get('partner')
        join_room(username) 
        if partner and partner != "global":
            room = generate_room(username, partner)
            join_room(room)

    @socketio.on('send_message')
    def handle_message(data):
        sender_name = data.get('sender')
        receiver_name = data.get('receiver')
        message_content = data.get('message')
        room = generate_room(sender_name, receiver_name)
        
        sender = db.session.execute(db.select(User).filter_by(username=sender_name)).scalar()
        receiver = db.session.execute(db.select(User).filter_by(username=receiver_name)).scalar()
        
        if sender and receiver:
            new_msg = Message(sender_id=sender.id, receiver_id=receiver.id, content=message_content, room=room)
            db.session.add(new_msg)
            db.session.commit()

        emit('receive_message', data, to=room)
        emit('new_notification', data, to=receiver_name)