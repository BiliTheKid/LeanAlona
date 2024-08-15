# prisma_client.py
from prisma import Prisma

# Create a single instance of the Prisma client
prisma_client = Prisma()

async def init_prisma_client():
    """Initialize and connect the Prisma client."""
    await prisma_client.connect()

async def disconnect_prisma_client():
    """Disconnect the Prisma client."""
    await prisma_client.disconnect()
