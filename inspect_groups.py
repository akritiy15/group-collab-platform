from app import create_app
from app.models import Group, User

app = create_app()

with app.app_context():
    groups = Group.query.all()
    print(f"Total groups: {len(groups)}")
    for group in groups:
        creator = User.query.get(group.created_by)
        print(f"Group: {group.name}, ID: {group.id}, Created by: {creator.username if creator else 'Unknown'} (ID: {group.created_by})")

    # Check all users
    users = User.query.all()
    print(f"\nTotal users: {len(users)}")
    for user in users:
        print(f"User: {user.username}, ID: {user.id}")