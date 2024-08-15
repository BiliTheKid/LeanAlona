from fastapi import HTTPException
from crud.crud import create_user_answer
from models.user_answer import UserAnswerCreate

async def create_user_answer_endpoint(user_data: dict):
    try:
        # Map your incoming dictionary to the expected UserAnswerCreate model
        user_answer = UserAnswerCreate(
            idNumber=user_data.get("id_number"),
            fullName=user_data.get("identification"),
            settlementCode=user_data.get("place"),
            accessibility=user_data.get("accessible"),
            pets=user_data.get("pet"),
            numberOfPeople=user_data.get("people"),
            hotelOption1="Option 1",  # Set default or dynamic values as needed
            hotelOption2="Option 2",
            hotelOption3="Option 3",
            selectedHotel="Option 1"
        )

        # Call the service function to create a new user answer record
        new_user_answer = await create_user_answer(user_answer)
        return {"message": "User answer created successfully", "data": new_user_answer}

    except Exception as e:
        print(f"Error creating user answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# You would typically pass `user_data` to `create_user_answer_endpoint(user_data)`
