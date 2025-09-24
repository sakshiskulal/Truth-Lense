from .database import Base, engine, SessionLocal
from .models import User
from .auth import hash_password

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Ensure admin user exists
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@truthlens.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@truthlens.com",
                hashed_password=hash_password("admin123")
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created: admin@truthlens.com / admin123")
    finally:
        db.close()