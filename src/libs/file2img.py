import glob
import logging
import os
from PIL import Image
import io
import discord

import pdf2image
import asyncio


BASE_COMMAND = 'libreoffice --headless --language=ja --infilter=",,64" --convert-to pdf:writer_pdf_Export --outdir . -env:UserInstallation=file://{user_profile} {office_file_path}'
USER_PROFILE = os.getenv("HOME") + "/.config/libreoffice/4/user"


async def get_images_from_attachment(
    attachment: discord.Attachment,
) -> list[Image.Image]:
    images = []
    loop = asyncio.get_running_loop()
    if attachment.content_type == "application/pdf":
        pdf_io = io.BytesIO()
        await attachment.save(pdf_io)
        images = await loop.run_in_executor(
            None, pdf2image.convert_from_bytes, pdf_io.read()
        )
    else:
        await attachment.save(attachment.filename)
        await generate_pdf_from(attachment.filename)
        pdf_file_name = ".".join(attachment.filename.split(".")[:-1]) + ".pdf"
        images = await loop.run_in_executor(
            None,
            pdf2image.convert_from_path,
            pdf_file_name,
        )
        os.remove(attachment.filename)
        os.remove(pdf_file_name)
    return images


async def generate_pdf_from(office_file_path: str):
    proc = await asyncio.create_subprocess_shell(
        BASE_COMMAND.format(
            user_profile=USER_PROFILE, office_file_path=office_file_path
        ),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stderr:
        logger = logging.getLogger("discord")
        logger.error(f"Failed to convert {office_file_path} to pdf.")
        logger.error(stdout)
        logger.error(stderr)
    for f in glob.glob("./*.tmp"):
        os.remove(f)
