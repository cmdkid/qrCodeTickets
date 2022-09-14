def ticket_status_to_text(status: str):
    if status == 'generated':
        return 'statusGrey', 'WAS NOT SOLD'
    elif status == 'active':
        return 'statusGreen', 'VALID'
    elif status == 'used':
        return 'statusRed', 'ALREADY USED'
    elif status == 'revoked':
        return 'statusRed', 'REVOKED'
    else:
        return 'statusRed', 'NOT VALID'
