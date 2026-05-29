from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.models import Tenant, User, UserRole
from app.db.session import SessionLocal


def seed_initial_data() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == settings.seed_admin_email))
        if existing:
            return

        tenant = Tenant(name="Default Tenant", domain_name="default.local")
        db.add(tenant)
        db.flush()

        admin = User(
            tenant_id=None,
            email=settings.seed_admin_email,
            name="System Admin",
            password_hash=hash_password(settings.seed_admin_password),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()

