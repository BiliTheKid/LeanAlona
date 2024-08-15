from Config.prisma_client import prisma_client
from models.user_answer import UserAnswerCreate

async def create_user_answer(user_answer: UserAnswerCreate):
    try:
        # Validate if settlement code exists
        settlement = await prisma_client.settlement.find_unique(
            where={"code": user_answer.settlementCode}
        )
        
        if not settlement:
            raise ValueError(f"Settlement with code {user_answer.settlementCode} does not exist.")

        print(f"Creating UserAnswer with data: {user_answer}")

        # Create a new user answer record
        new_user_answer = await prisma_client.useranswer.create(
            data={
                "idNumber": user_answer.idNumber,
                "fullName": user_answer.fullName,
                "settlementCode": user_answer.settlementCode,
                "accessibility": user_answer.accessibility,
                "pets": user_answer.pets,
                "numberOfPeople": user_answer.numberOfPeople,
                "hotelOption1": user_answer.hotelOption1,
                "hotelOption2": user_answer.hotelOption2,
                "hotelOption3": user_answer.hotelOption3,
                "selectedHotel": user_answer.selectedHotel,
            }
        )
        return new_user_answer

    except Exception as e:
        print(f"Error creating user answer: {e}")
        raise
