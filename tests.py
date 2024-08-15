# import asyncio
# from typing import Dict, Any
# from fastapi import FastAPI
# from pydantic import BaseModel
# from prisma import Prisma
# from Config.prisma_client import prisma_client
# from models.user_answer import UserAnswerCreate

# app = FastAPI()

# # Define a simple test model for demonstration
# class TestUserAnswerCreate(BaseModel):
#     idNumber: str
#     fullName: str
#     settlementCode: int
#     accessibility: bool
#     pets: bool
#     numberOfPeople: int
#     hotelOption1: str
#     hotelOption2: str
#     hotelOption3: str
#     selectedHotel: str

# # Function to create user answer record
# async def create_user_answer(user_answer: UserAnswerCreate):
#     try:
#         new_user_answer = await prisma_client.useranswer.create(
#             data={
#                 "idNumber": user_answer.idNumber,
#                 "fullName": user_answer.fullName,
#                 "settlementCode": user_answer.settlementCode,
#                 "accessibility": user_answer.accessibility,
#                 "pets": user_answer.pets,
#                 "numberOfPeople": user_answer.numberOfPeople,
#                 "hotelOption1": user_answer.hotelOption1,
#                 "hotelOption2": user_answer.hotelOption2,
#                 "hotelOption3": user_answer.hotelOption3,
#                 "selectedHotel": user_answer.selectedHotel,
#             }
#         )
#         return new_user_answer
#     except Exception as e:
#         print(f"Error creating user answer: {e}")
#         raise

# @app.post("/test-create-user-answer/")
# async def test_create_user_answer(user_answer: TestUserAnswerCreate):
#     result = await create_user_answer(user_answer)
#     return {"result": result}

# # Test function to run the script standalone
# async def main():
#     # Example user answer data
#     test_data = TestUserAnswerCreate(
#         idNumber="302324348",
#         fullName="יפונחכחכ",
#         settlementCode=1,
#         accessibility=True,
#         pets=False,
#         numberOfPeople=5,
#         hotelOption1="Option 1",
#         hotelOption2="Option 2",
#         hotelOption3="Option 3",
#         selectedHotel="Option 1"
#     )

#     # Initialize Prisma client
#     await prisma_client.connect()

#     try:
#         # Create user answer and print result
#         result = await create_user_answer(test_data)
#         print(f"User answer created: {result}")
#     finally:
#         # Disconnect Prisma client
#         await prisma_client.disconnect()

# if __name__ == "__main__":
#     asyncio.run(main())
