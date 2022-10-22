from typing import Optional

from discord import HTTPException, Message
from discord.ext.commands import Context


class SubContext(Context):
    async def confirm(self, message: str = None) -> Optional[Message]:
        """
        Adds a checkmark to ctx.message.
        If unable to sends <message>
        """
        try:
            await self.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        except HTTPException:
            message = message or "\N{WHITE HEAVY CHECK MARK}"
            return await self.send(message)
