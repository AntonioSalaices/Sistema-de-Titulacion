#coding: utf-8
from django import forms
from models import Profile
from django.contrib.auth import authenticate,get_user_model,login,logout
from django.contrib.auth.models import User
from models import Profile, Egresados, Minuta
from django.core import validators


class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario",widget=forms.TextInput(attrs={'class':'form-control col-lg-9 col-md-12'}))
    password = forms.CharField(label="Contraseña",widget=forms.PasswordInput(attrs={'class':'form-control col-lg-9 col-md-12'}))
    def clean(self,*args,**kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username,password=password)
        if not user:
            raise forms.ValidationError("El usuario no existe")
        if not user.check_password(password):
            raise forms.ValidationError("El usuario o la contraseña son incorrectos")
        return super(LoginForm,self).clean(*args,**kwargs)

class FormularioContacto(forms.Form):
    correo = forms.EmailField()
    mensaje = forms.CharField()
    


class FormularioGrafica(forms.Form):
    grafica = forms.CharField()

class RegistrarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [

        ]
        exclude = [
            'username',
            'email',
            'password',
        ]

class RegistrarAgenteForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            
        ]
        exclude = [
            'nombre',
            'apellidoPaterno',
            'apellidoMaterno',
            'sexo',
            'telefono',
            'telefono2',
            'tipo',
            'user',
        ]


class RegistrarEgresados(forms.ModelForm):
    class Meta:
        model = Egresados
        fields = [
            'nombre', 
            'apellidoPaterno',
            'apellidoMaterno',
            'generacion',
            'genero',
            'carrera',
            'medio',
        ]
        labels = {
            'nombre': 'Nombre',
            'apellidoPaterno':'Apellido Paterno',
            'apellidoMaterno':'Apellido Materno',
            'generacion': 'Generación',
            'genero': 'Genero',
            'carrera': 'Carrera',
            'medio': 'Medio de Titulación',
        }
     
class RegistrarMinuta(forms.ModelForm):
    class Meta:
        model =Minuta
        fields = [
            'tiporeunion', 
            'titulo',
            'lista_asistencia',
            'puntos',
        ]
        labels = {
            'tiporeunion': 'Tipo de Reunion', 
            'titulo': 'Titulo',
            'lista_asistencia': 'Lista de Asistencia',
            'puntos': 'Puntos',
        }