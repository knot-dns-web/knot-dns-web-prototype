from datetime import datetime

def generate_serial():
    return datetime.now().strftime("%Y%m%d01")


import re

# Константы для правил
MAX_LENGTH = 253
MAX_LABEL_LENGTH = 63
MIN_TLD_LENGTH = 2
LABEL_PATTERN = r'^(?!-)[A-Za-z0-9-]{1,%d}(?<!-)$' % MAX_LABEL_LENGTH
TLD_PATTERN = r'^[A-Za-z]{%d,%d}$' % (MIN_TLD_LENGTH, MAX_LABEL_LENGTH)

def validate_zone_name(zone):
    # Убираем точку в конце
    zone = zone.rstrip('.')
    
    # Проверка общей длины
    if len(zone) > MAX_LENGTH:
        raise ValueError("Invalid zone name")
    
    labels = zone.split('.')
    for label in labels:
        if not re.match(LABEL_PATTERN, label):
           raise ValueError("Invalid zone name")
    
    # Для многоуровневых зон проверяем TLD
    if len(labels) > 1 and not re.match(TLD_PATTERN, labels[-1]):
        raise ValueError("Invalid zone name")
