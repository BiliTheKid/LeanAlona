from pydantic import BaseModel
## UserAnswer models -- not completet yet
class UserAnswerCreate(BaseModel):
    idNumber: str
    fullName: str
    settlementCode: int
    accessibility: bool
    pets: bool
    numberOfPeople: int
    hotelOption1: str = None
    hotelOption2: str = None
    hotelOption3: str = None
    selectedHotel: str = None

class UserAnswerResponse(BaseModel):
    id: int
    idNumber: str
    fullName: str
    settlementCode: int
    accessibility: bool
    pets: bool
    numberOfPeople: int
    hotelOption1: str = None
    hotelOption2: str = None
    hotelOption3: str = None
    selectedHotel: str = None
