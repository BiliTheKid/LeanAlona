-- CreateTable
CREATE TABLE "UserAnswer" (
    "id" SERIAL NOT NULL,
    "idNumber" TEXT NOT NULL,
    "fullName" TEXT NOT NULL,
    "settlementCode" INTEGER NOT NULL,
    "accessibility" BOOLEAN NOT NULL,
    "pets" BOOLEAN NOT NULL,
    "numberOfPeople" INTEGER NOT NULL,
    "hotelOption1" TEXT,
    "hotelOption2" TEXT,
    "hotelOption3" TEXT,
    "selectedHotel" TEXT,

    CONSTRAINT "UserAnswer_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Settlement" (
    "id" SERIAL NOT NULL,
    "code" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "alias1" TEXT,
    "alias2" TEXT,
    "alias3" TEXT,

    CONSTRAINT "Settlement_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "UserAnswer_idNumber_key" ON "UserAnswer"("idNumber");

-- CreateIndex
CREATE UNIQUE INDEX "Settlement_code_key" ON "Settlement"("code");

-- AddForeignKey
ALTER TABLE "UserAnswer" ADD CONSTRAINT "UserAnswer_settlementCode_fkey" FOREIGN KEY ("settlementCode") REFERENCES "Settlement"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
