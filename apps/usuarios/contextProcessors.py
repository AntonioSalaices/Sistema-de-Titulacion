from forms import LoginForm
def add_variable_context(request):
    return{
        'login':LoginForm
    }
