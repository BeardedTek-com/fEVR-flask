from flask import request
class menuState:
    def get():
        if request.cookies.get('menu'):
            menu = request.cookies.get('menu')
            print(menu)
            return menu