import subprocess
import os
import asyncio
from cvat.constant import PDF_PATH


async def convert_pdf_image(src_file):
    """
    Note: In order to run this function you need ImageMagic library installed in your machine if not already installed
          run below command.
          --> 'sudo apt install imagemagick'
    """
    target_dir = os.path.splitext(src_file)[0]
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, os.path.split(target_dir)[1] + '.jpg')

    subprocess.run([
        'convert',
        '-alpha', 'remove',
        '-colorspace', 'Gray',
        '-quality', '75',
        '-density', '150',
        src_file, target_file],
        stdout=subprocess.PIPE,
        timeout=120,
        text=True)


loop = asyncio.get_event_loop()
loop.run_until_complete(convert_pdf_image(PDF_PATH))
