import asyncio
from typing import Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
from prisma import Prisma
from Config.prisma_client import prisma_client
from models.user_answer import UserAnswerCreate
from services.services import create_user_answer_endpoint






# Test function to run the script standalone
async def main():
    # Example user answer data
    test_data = UserAnswerCreate(
        idNumber="3023242222222348",
        fullName="יפונחכחכ",
        settlementCode=1,
        accessibility=True,
        pets=False,
        numberOfPeople=5,
        hotelOption1="Option 1",
        hotelOption2="Option 2",
        hotelOption3="Option 3",
        selectedHotel="Option 1"
    )

    # Initialize Prisma client
    await prisma_client.connect()

    try:
        # Create user answer and print result
        result = await create_user_answer_endpoint(test_data)
        print(f"User answer created: {result}")
    finally:
        # Disconnect Prisma client
        await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
