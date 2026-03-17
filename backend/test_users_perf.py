import time
import asyncio
from app.core.database import SessionLocal, engine, Base
from app.data.models.user import User
from app.data.models.role import Role, user_roles
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.v1.endpoints.users import get_users

def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # clean up
    db.query(user_roles).delete()
    db.query(User).delete()
    db.query(Role).delete()
    db.commit()

    # create roles
    role1 = Role(name="role1", display_name="Role 1", description="desc 1")
    role2 = Role(name="role2", display_name="Role 2", description="desc 2")
    db.add_all([role1, role2])
    db.commit()

    # create users
    users = []
    for i in range(100):
        u = User(
            email=f"user{i}@example.com",
            full_name=f"User {i}",
            phone=f"+25191100{i:04d}",
            password_hash="hash",
            municipality="Addis",
            license_number=f"LIC{i:04d}",
            is_active=True,
            is_verified=True,
            is_admin=False,
            is_valuer=True
        )
        users.append(u)
    db.add_all(users)
    db.commit()

    # assign roles
    for u in users:
        u.roles.append(role1)
        if u.id % 2 == 0:
            u.roles.append(role2)
    db.commit()
    db.close()

async def measure():
    setup_db()
    db = SessionLocal()
    # Dummy current user
    current_user = db.query(User).first()

    start_time = time.time()
    # Call the endpoint function
    await get_users(skip=0, limit=100, db=db, current_user=current_user)
    end_time = time.time()

    print(f"Time taken: {(end_time - start_time) * 1000:.2f} ms")
    db.close()

if __name__ == "__main__":
    asyncio.run(measure())
