import aiosqlite


DBSCHEMA = """
CREATE TABLE IF NOT EXISTS "coins" (
    "user_id" INTEGER UNIQUE,
    "coins"	INTEGER,
    PRIMARY KEY("user_id")
);

CREATE TABLE IF NOT EXISTS "cooldowns" (
    "command_name" TEXT,
    "user_id" INTEGER,
    PRIMARY KEY("command_name", "user_id")
);

CREATE TABLE IF NOT EXISTS "purple_hearts" (
    "user_id" INTEGER,
    PRIMARY KEY("user_id")
);
"""


# temporary fix while migrating to postgres
tables_inited = False


async def create_tables():
    if tables_inited:
        return

    async with (await get_database()) as connection:
        await connection.executescript(DBSCHEMA.strip())
        await connection.commit()

    tables_inited = True


async def get_database() -> aiosqlite.Connection:
    await create_tables()
    return aiosqlite.connect("arcanumbot.db")
