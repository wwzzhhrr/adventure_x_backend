import asyncio
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.user import User
from app.services.blockchain import CommuCoinService

async def migrate():
    service = CommuCoinService()
    with Session(engine) as session:
        users = session.query(User).all()
        for user in users:
            if user.wallet_address:  # Only migrate if exists
                wallet = await service.create_wallet()
                user.wallet_address = wallet["address"]
                user.wallet_public_key = wallet["public_key"]
                user.wallet_private_key = wallet["encrypted_private_key"]
        session.commit()

if __name__ == "__main__":
    asyncio.run(migrate())