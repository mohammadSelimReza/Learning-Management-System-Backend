import random
import string
def generate_transaction_id(length=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choices(chars, k=length))
