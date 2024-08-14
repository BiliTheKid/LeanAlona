import asyncio
import csv
from prisma import Prisma
from prisma.models import Settlement
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_settlement(data):
    try:
        # Create a new settlement
        settlement = await Settlement.prisma().create(data=data)
        logger.info(f"Created Settlement with ID: {settlement.id}")
        return settlement

    except Exception as e:
        logger.error(f"Error creating Settlement: {str(e)}")
        raise

async def update_settlement(settlement_id, data):
    try:
        # Update a settlement
        updated_settlement = await Settlement.prisma().update(
            where={"id": settlement_id},
            data=data
        )
        logger.info(f"Updated Settlement with ID: {updated_settlement.id}")
        return updated_settlement

    except Exception as e:
        logger.error(f"Error updating Settlement: {str(e)}")
        raise

async def import_settlements_from_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Create a dictionary with the data from the CSV
                settlement_data = {
                    "code": int(row["Settlement_code"]),
                    "name": row["Settlement"],
                    "alias1": row["alias1"] if row["alias1"] else None,
                    "alias2": row["alias2"] if row["alias2"] else None,
                    "alias3": row["alias3"] if row["alias3"] else None
                }
                
                # Check if the settlement already exists
                existing_settlement = await Settlement.prisma().find_first(
                    where={"code": settlement_data["code"]}
                )
                
                if existing_settlement:
                    logger.info(f"Settlement with code {settlement_data['code']} already exists. Updating...")
                    await update_settlement(existing_settlement.id, settlement_data)
                else:
                    logger.info(f"Creating new Settlement with code {settlement_data['code']}...")
                    await create_settlement(settlement_data)

    except Exception as e:
        logger.error(f"Error importing settlements from CSV: {str(e)}")
        raise

async def main():
    try:
        db = Prisma(auto_register=True)
        await db.connect()

        file_path = 'settlements.csv'  # Path to your CSV file
        await import_settlements_from_csv(file_path)

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

    finally:
        await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
