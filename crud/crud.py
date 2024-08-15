from Config.prisma_client import prisma_client
from typing import Dict, Any

async def create_user_answer(user_answer: Dict[str, Any]):
    try:
        # Create a new user answer record
        new_user_answer = await prisma_client.useranswer.create(
            data={
                "idNumber": user_answer.get('idNumber', ''),
                "fullName": user_answer.get('fullName', ''),
                "settlementCode": user_answer.get('settlementCode', 0),
                "accessibility": user_answer.get('accessibility', False),
                "pets": user_answer.get('pets', False),
                "numberOfPeople": user_answer.get('numberOfPeople', 0),
                "hotelOption1": user_answer.get('hotelOption1', ''),
                "hotelOption2": user_answer.get('hotelOption2', ''),
                "hotelOption3": user_answer.get('hotelOption3', ''),
                "selectedHotel": user_answer.get('selectedHotel', ''),
            }
        )
        return new_user_answer
    except Exception as e:
        print(f"Error creating user answer: {e}")
        raise
