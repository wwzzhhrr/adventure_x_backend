import asyncio
import os
import argparse
from decimal import Decimal
from dotenv import load_dotenv
from app.services.blockchain import CommuCoinService

async def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Fund a wallet with CommuCoin.")
    parser.add_argument("recipient_address", type=str, help="The address of the wallet to fund.")
    parser.add_argument("amount", type=Decimal, help="The amount of CommuCoin to send.")
    args = parser.parse_args()

    funder_private_key = os.getenv("FUNDER_PRIVATE_KEY")
    if not funder_private_key:
        print("Error: FUNDER_PRIVATE_KEY environment variable not set.")
        print("Please set it in your .env file.")
        return

    service = CommuCoinService()
    
    # The 'from_address' in transfer_comu is derived from the private key, so we don't need to pass it.
    # We can just pass an empty string or any placeholder.
    print(f"Attempting to transfer {args.amount} COMU to {args.recipient_address}...")

    try:
        tx_hash = await service.transfer_comu(
            from_address="", # This is derived from the private key inside the method
            to_address=args.recipient_address,
            amount=args.amount,
            private_key=funder_private_key
        )
        print(f"Successfully transferred {args.amount} COMU.")
        print(f"Transaction Hash: {tx_hash}")
    except Exception as e:
        print(f"An error occurred during the transfer: {e}")

if __name__ == "__main__":
    asyncio.run(main())