import aiosqlite


def get_database() -> aiosqlite.Connection:
    """
    Gets the arcanumbot database
    :return: The db context manager
    """

    def adapt_set(_set):
        return ",".join(map(str, _set))

    def convert_set(s):
        return {i.decode() for i in s.split(b",")}

    import sqlite3

    sqlite3.register_adapter(set, adapt_set)

    sqlite3.register_converter("pyset", convert_set)

    return aiosqlite.connect("arcanumbot.db", detect_types=sqlite3.PARSE_DECLTYPES)
