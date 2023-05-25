from datetime import datetime


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def getcurrentformatteddatetime():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validPassword(password):
    if len(password)>=8 and len(password)<=16:
        cap_test, small_test, num_test, sp_char_test = False, False, False, False
        for ele in password:
            if cap_test==False and ele.isupper():
                cap_test = True
            if small_test == False and ele.islower():
                small_test = True
            if num_test == False and ele.isnumeric():
                num_test = True
            if sp_char_test == False and ele in "!@#$%_":
                sp_char_test = True
            if cap_test and small_test and num_test and sp_char_test:
                return True
    return False