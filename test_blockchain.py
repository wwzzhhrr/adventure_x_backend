import asyncio
from app.services.blockchain import CommuCoinService

async def test_create_wallet():
    service = CommuCoinService()
    wallet = await service.create_wallet()
    print(wallet)

if __name__ == '__main__':
    asyncio.run(test_create_wallet())