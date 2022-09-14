import qrcode
import os.path
import uuid

import config
from src.dbHelper import insert_new_uuid, get_timestamp


def get_qrcode(text: str, result_file_path: str):
    qr = qrcode.QRCode(version=None, box_size=config.QRCODES_BOX_SIZE, border=config.QRCODES_BORDER_SIZE)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=config.QRCODES_FILL_COLOR, back_color=config.QRCODES_BG_COLOR)
    img.save(result_file_path)


def generate_qr_files(count: int, file_path: str, file_prefix: str = ''):
    for _ in range(0, count):
        ticket_uuid = str(uuid.uuid4())
        filename = f'{file_prefix}{get_timestamp()}.png'
        text = f'{config.QRCODES_TEXT_TEMPLATE}%27{ticket_uuid}%27'
        get_qrcode(text, os.path.join(file_path, filename))
        insert_new_uuid(ticket_uuid)
