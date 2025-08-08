from flask import request, jsonify


def logged_user(call_func=True):
    def decorator(f):
        @logged_user(f)
        def decorated_function(*args, **kwargs):
            print('in dec')
            pass
            auth_token = request.headers.get('Authorization')
            print(auth_token)
            # if call_func:
            #     # Do something before the view function is called
            #     print("Before the view function is called")
            #
            #     # Call the view function and get the response
            #     response = f(*args, **kwargs)
            #
            #     # Do something after the view function is called
            #     print("After the view function is called")
            #
            #     # Return the response
            #     return response
            # else:
            #     # Return without calling the function
            #     print("Function not called")
            return jsonify(message='Function not called')
        return decorated_function
    return decorator