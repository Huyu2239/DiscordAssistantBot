import io

import discord
from discord import app_commands
from discord.ext import commands

from libs.file2img import get_images_from_attachment


class FileViewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supported_extensions = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ]
        self.ctx_menu = app_commands.ContextMenu(
            name="ファイルを閲覧",
            callback=self.file_viewer,
        )
        self.bot.tree.add_command(self.ctx_menu)

    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def file_viewer(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        is_sent = False
        await interaction.response.defer(ephemeral=True, thinking=True)
        attachments = [
            attachment
            for attachment in message.attachments
            if attachment.content_type in self.supported_extensions
        ]
        for attachment in attachments:
            images = await get_images_from_attachment(attachment)
            if images is None:
                continue
            is_sent = True
            await interaction.followup.send(
                embed=discord.Embed(
                    title=attachment.filename,
                    description=message.jump_url,
                    color=discord.Color.blue(),
                ),
                ephemeral=True,
            )
            images = [images[idx : idx + 10] for idx in range(0, len(images), 10)]
            count = 1
            for image_container in images:
                files = []
                for image in image_container:
                    fileio = io.BytesIO()
                    image.save(fileio, format="jpeg")
                    fileio.seek(0)
                    files.append(discord.File(fileio, filename="image.jpg"))
                    count += 1
                await interaction.followup.send(
                    content=f"{count-len(files)}~{count-1}ページ",
                    files=files,
                    ephemeral=True,
                )

        if is_sent is False:
            error_embed = discord.Embed(
                title="閲覧不可",
                description="対応しているファイルが添付ファイルに含まれていません．",
                color=discord.Color.red(),
            )
            return await interaction.followup.send(embed=error_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(FileViewer(bot))
