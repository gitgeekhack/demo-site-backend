class OCRConfig:
    class DrivingLicense:
        NAME = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ ,\n" load_system_dawg=false load_freq_dawg=false'
        LICENSE_NO = '-l eng --oem 1 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*- " load_system_dawg=false load_freq_dawg=false'
        ADDRESS = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,\n-" load_system_dawg=false load_freq_dawg=false'
        DATE = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="0123456789/- " load_system_dawg=false load_freq_dawg=false'
        GENDER = '-l eng --oem 1 --psm 7 -c tessedit_char_whitelist="MF" load_system_dawg=false load_freq_dawg=false'
        HEIGHT = '''-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="0123456789H'\\"" load_system_dawg=false load_freq_dawg=false '''
        WEIGHT = '''-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="0123456789WGTLBlbwgt " load_system_dawg=false load_freq_dawg=false'''
        HAIR_COLOR = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ " load_system_dawg=false load_freq_dawg=false'
        EYE_COLOR = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ " load_system_dawg=false load_freq_dawg=false'
        LICENSE_CLASS = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890   " load_system_dawg=false load_freq_dawg=false'
