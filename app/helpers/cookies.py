from flask import request, make_response
class cookies:
    def getCookie(cookie):
        if request.cookies.get(cookie):
            return request.cookies.get('menu')
        else:
            return None
        
    def getCookies(jar):
        cookies = {}
        for cookie in jar:
            if cookie in request.cookies:
                cookies[cookie] = request.cookies.get(cookie)
            else:
                cookies[cookie] = None
        return cookies
        
    def setCookies(jar,resp):
        Response = make_response(resp)
        for cookie in jar:
            Response.set_cookie(cookie,jar[cookie])
            return Response