from fastapi import HTTPException
from crud.crud import create_user_answer
from models.user_answer import UserAnswerCreate


async def create_user_answer_endpoint(user_answer: UserAnswerCreate):
    try:
        # Call the service function to create a new user answer record
        new_user_answer = await create_user_answer(user_answer)
        return {"message": "User answer created successfully", "data": new_user_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))