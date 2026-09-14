import asyncio
from enum import Enum

import discord


class ApprovalDecision(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    RETRY = "retry"


class PostApprovalView(discord.ui.View):
    def __init__(self, *, timeout: float = 3600) -> None:
        super().__init__(timeout=timeout)
        self.decision: ApprovalDecision | None = None
        self.message: discord.Message | None = None
        self._resolved = asyncio.Event()

    async def wait_for_decision(self) -> ApprovalDecision:
        await self._resolved.wait()
        assert self.decision is not None
        return self.decision

    async def _resolve(self, interaction: discord.Interaction, decision: ApprovalDecision, label: str) -> None:
        self.decision = decision

        for child in self.children:
            child.disabled = True   # type: ignore[attr-defined]

        await interaction.response.edit_message(content=f"**{label}**", view=self)
        self._resolved.set()
        self.stop()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._resolve(interaction, ApprovalDecision.ACCEPTED, "Accepted ✅")

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._resolve(interaction, ApprovalDecision.REJECTED, "Rejected ❌")

    @discord.ui.button(label="Re-try", style=discord.ButtonStyle.secondary)
    async def retry(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._resolve(interaction, ApprovalDecision.RETRY, "Retry 🔄")

    async def on_timeout(self) -> None:
        """
        No response within the timeout window - treat it as a rejection.
        """

        self.decision = ApprovalDecision.REJECTED

        for child in self.children:
            child.disabled = True   # type: ignore[attr-defined]

        if self.message is not None:
            await self.message.edit(content="**Timed out - treated as rejected.**")

        self._resolved.set()  
