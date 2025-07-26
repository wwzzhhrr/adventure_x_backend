import asyncio
import os
from dotenv import load_dotenv
from pyinjective.async_client import AsyncClient
from pyinjective.core.network import Network
from pyinjective.wallet import PrivateKey
from pyinjective.composer import Composer
from decimal import Decimal
import ecdsa

async def main():
    """This script creates a new wallet, creates a new token factory token, and mints it."""
    load_dotenv()

    # 1. Configure network and client
    network = Network.testnet()
    client = AsyncClient(network)
    composer = Composer(network=network.string())

    # 2. Generate a new wallet (this will be the creator and funder)
    print("--- Step 1: Generating a new wallet ---")
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    priv_key_bytes = sk.to_string()
    private_key_hex = priv_key_bytes.hex()
    private_key = PrivateKey.from_hex(private_key_hex)
    pub_key = private_key.to_public_key()
    address = pub_key.to_address().to_acc_bech32()
    print(f"New Wallet Address (Creator/Funder): {address}")
    print(f"New Wallet Private Key: {private_key_hex}")
    print("IMPORTANT: Save this private key securely! Add it to your .env file as FUNDER_PRIVATE_KEY.")

    # 3. Fund the new wallet with some INJ from the faucet
    print("\n--- Step 2: Funding the new wallet ---")
    print(f"Please go to an Injective faucet (e.g., https://testnet.faucet.injective.network/) and request some INJ for the address: {address}")
    input("Press Enter after you have funded the wallet and the transaction is confirmed...")

    # 4. Create a new token
    print("\n--- Step 3: Creating a new token ---")
    subdenom = "commucoin" # You can change this to your desired token name
    token_denom = f"factory/{address}/{subdenom}"
    print(f"The new token's subdenom will be: {subdenom}")

    try:
        account = await client.get_account(address)
        msg = composer.MsgCreateDenom(
            sender=address,
            subdenom=subdenom
        )

        tx = (
            await client.prepare_tx(
                msgs=[msg],
                address=address,
                chain_id=network.chain_id,
                gas_price=500000000,
                gas_limit=200000
            )
        )

        print("Signing transaction to create token...")
        signed_tx = private_key.sign_tx(tx)

        print("Broadcasting transaction...")
        result = await client.broadcast_tx_sync_mode(signed_tx)
        print(f"Token creation transaction successful. Tx Hash: {result.tx_hash}")
        print(f"Your new token denom is: {token_denom}")
        print("IMPORTANT: Update the 'comu_token_denom' in your blockchain.py with this new value.")

    except Exception as e:
        print(f"Error creating token: {e}")
        print("Please ensure the wallet is funded with INJ to pay for gas fees.")
        return

    # 5. Mint the new token
    print("\n--- Step 4: Minting new tokens ---")
    mint_amount = Decimal("1000000") # Minting 1,000,000 tokens
    amount_in_wei = int(mint_amount * (10**18)) # Assuming 18 decimals

    try:
        # We need to fetch the account details again to get the new sequence number
        await asyncio.sleep(5) # Wait a bit for the chain to update
        account = await client.get_account(address)

        msg = composer.MsgMint(
            sender=address,
            coin=composer.Coin(
                amount=amount_in_wei,
                denom=token_denom
            )
        )

        tx = (
            await client.prepare_tx(
                msgs=[msg],
                address=address,
                chain_id=network.chain_id,
                gas_price=500000000,
                gas_limit=200000
            )
        )

        print("Signing transaction to mint tokens...")
        signed_tx = private_key.sign_tx(tx)

        print("Broadcasting transaction...")
        result = await client.broadcast_tx_sync_mode(signed_tx)
        print(f"Token minting transaction successful. Tx Hash: {result.tx_hash}")
        print(f"Successfully minted {mint_amount} of {token_denom} to your wallet {address}.")

    except Exception as e:
        print(f"Error minting tokens: {e}")

if __name__ == "__main__":
    asyncio.run(main())