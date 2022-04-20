from random import randint,choice
import string

class randpwd:
    def generate(count=None):
        if count == None:
            count = randint(10,24)
        elif count > 24:
            count = 24
        elif count == 0:
            count = randint(10,24)
        password = ""
        for x in range(count):
            num = randint(0,2)
            print(f"{type(num)}: {num}")
            if num == 0:
                password += choice(string.ascii_lowercase)
            elif num == 1:
                password += choice(string.ascii_uppercase)
            elif num == 2:
                password += choice(string.digits)
        return password

if __name__ == '__main__':
    print(randpwd.generate(500))