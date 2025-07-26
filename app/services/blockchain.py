from pyinjective.async_client import AsyncClient
from pyinjective.core.network import Network
from pyinjective.composer import Composer
from pyinjective.wallet import PrivateKey, PublicKey
from web3 import Web3
from cryptography.fernet import Fernet
import os
from decimal import Decimal
from typing import Dict
import asyncio
import base64
import ecdsa

class CommuCoinService:
    def __init__(self):
        # 初始化 Injective 网络连接
        self.network = Network.testnet()
        self.client = AsyncClient(self.network)
        self.composer = Composer(network=self.network.string())
        
        # 钱包加密相关
        self.encryption_key = os.getenv('WALLET_ENCRYPTION_KEY', 'test_key_32_chars_long_for_demo').encode()[:32]
        if len(self.encryption_key) < 32:
            self.encryption_key = self.encryption_key.ljust(32, b'0')
        key = base64.urlsafe_b64encode(self.encryption_key)
        self.fernet = Fernet(key)
        
        # CommuCoin 代币配置
        self.comu_token_denom = "inj1q2440s4800s9w0c37h7tjn3u4"  # 实际 denom 从截图获取
        self.comu_decimals = 18
    
    async def create_wallet(self) -> Dict[str, str]:
        """创建新的钱包地址"""
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        priv_key_bytes = sk.to_string()
        priv_key_hex = priv_key_bytes.hex()
        priv_key = PrivateKey.from_hex(priv_key_hex)
        pub_key = priv_key.to_public_key()
        address = pub_key.to_address().to_acc_bech32()
        public_key_hex = pub_key.to_hex()
        encrypted_private_key = self.fernet.encrypt(priv_key_hex.encode()).decode()
        return {
            "address": address,
            "public_key": public_key_hex,
            "encrypted_private_key": encrypted_private_key
        }
    
    def decrypt_private_key(self, encrypted_private_key: str) -> str:
        return self.fernet.decrypt(encrypted_private_key.encode()).decode()
    
    async def get_comu_balance(self, address: str) -> Decimal:
        """获取 COMU 代币余额"""
        address = address.lower()
        balances = await self.client.fetch_bank_balances(address=address)
        for coin in balances["balances"]:
            if coin["denom"] == self.comu_token_denom:
                return Decimal(coin["amount"]) / Decimal(10 ** self.comu_decimals)
        return Decimal(0)
    
    async def transfer_comu(self, from_address: str, to_address: str, amount: Decimal, private_key: str) -> str:
        """转移 COMU 代币"""
        priv_key = PrivateKey.from_hex(private_key)
        pub_key = priv_key.to_public_key()
        from_acc = await self.client.get_account(pub_key.acc_address())
        
        amount_in_wei = int(amount * Decimal(10 ** self.comu_decimals))
        msg = self.composer.MsgSend(
            from_address=from_acc.address,
            to_address=to_address,
            amount=amount_in_wei,
            denom=self.comu_token_denom
        )
        
        tx = await self.client.create_transaction(
            msgs=[msg],
            priv_key=priv_key,
            account_num=from_acc.account_number,
            sequence=from_acc.sequence,
            chain_id=self.network.chain_id
        )
        
        result = await self.client.broadcast_tx_wait(tx.tx_hash)
        return result.txhash

# 依赖注入
def get_blockchain_service() -> CommuCoinService:
    return CommuCoinService()