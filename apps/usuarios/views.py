from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest    
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate, get_user_model
from forms import LoginForm,RegistrarAgenteForm,RegistrarForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from models import Profile, Egresados, Minuta
from forms import *
from django.views.generic.list import ListView
from django.core.mail import EmailMessage
from django.utils import timezone
from django.views.generic import View
from django.db.models import  *
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Table
from io import StringIO, BytesIO
import time
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core import serializers
# Create your views here.


def index(request):
    return render(request,'index.html')

def contacto_mail(request):
    
    if request.method=='POST':
        form = FormularioContacto(request.POST)
        if form.is_valid():
            asunto= 'Convocatoria a Reunion del Comite de Titulacion'
            mensaje= form.cleaned_data['mensaje']
            correo = form.cleaned_data['correo']
            mail = EmailMessage(asunto,mensaje, to= [correo])
            mail.send()
        return HttpResponseRedirect('convocar')    
    else:
        form= FormularioContacto()

    return render(request,'usuarios/convocar_reunion.html',{'form': form, 'users': User.objects.all()})  


def vista_lista_minutas(request):
    minuta = Minuta.objects.all().order_by('id')
    contexto = {'minutas': minuta}
    return render(request,'usuarios/minuta_list.html', contexto)


@login_required(login_url='/login/')
def vista_logout(request):
    logout(request)
    return redirect('index')

def vista_login(request):
    form  = LoginForm(request.POST or None)
    context = {"form":form}
    if request.user.is_authenticated():
        return redirect('index')
    if form.is_valid():
        username= form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username,password=password)
        login(request,user)
        return redirect('index')
    return render(request,"usuarios/login.html",context)

def vista_registrar(request):
    
    if request.user.is_authenticated():
        return redirect('index')
    if request.method == 'POST':
        form = RegistrarForm(request.POST or None)
        user  = form.save(commit=False)
        user.email = request.POST.get('correo')
        user.username = request.POST.get('correo')
        password = request.POST.get('contrasena')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=request.POST.get('correo'),password=password)
        login(request,new_user)
        profile_form = Profile.objects.get(user=request.user)
        profile_form.nombre = request.POST.get('nombre')
        profile_form.apellidoPaterno =  request.POST.get('apellido_paterno')
        profile_form.apellidoMaterno = request.POST.get('apellido_materno')
        profile_form.telefono =  request.POST.get('telefono1')
        profile_form.telefono2 = request.POST.get('telefono2')
        profile_form.save()
        return redirect('index')
    else:
        form = RegistrarForm()
        profile_form = RegistrarAgenteForm()
    context = {
    "form":form,
    "profile_form": profile_form
    }
    return render(request, "usuarios/registrar.html", context)

def vista_json_correoDisponible(request):
    correo = request.GET.get('correo',None)
    if User.objects.filter(email=correo):
        return HttpResponse("False")
    return HttpResponse("True")


def EgresadoViewSet(request):
    matchs = Egresados.objects.all()
    if request.method== 'POST':
        srch = request.POST['srh']
        src2 = request.POST['sel1']
        src3 = request.POST['sel2']
        src4 = request.POST['sel3']
        
        if (srch or src2 or src3 or src4):
            match = Egresados.objects.filter(Q(carrera__icontains=srch) |
                                             Q(generacion__icontains=srch) |
                                              Q(genero__icontains=srch) |
                                                Q(medio__icontains=srch )                        )

            match = match.filter(Q(generacion__icontains=src2))  
            match = match.filter(Q(genero__icontains=src3))
            match = match.filter(Q(medio__icontains=src4))
            contador = match.count()
            if match: 
                return render(request, 'usuarios/egresado_list.html', {'egresado':match, 'contador': contador })
            else:
                messages.error(request,'Resultados no encontrados')    
        else:
            return HttpResponseRedirect('/usuarios/listado')    
    return render(request, 'usuarios/egresado_list.html',{'egresado':matchs})


def vista_registraregre(request):
    if request.method=='POST':
        form = RegistrarEgresados(request.POST)
        if form.is_valid():
            messages.success(request,"Registro con exito")
            form.save()
        return redirect("index")
    else:
        form = RegistrarEgresados()
    return render(request,'usuarios/registrar_egresado.html',{'form': form})

def registrarminuta(request):
    hour = timezone.localtime(timezone.now())
    formatedHour = hour.strftime("%H:%M:%S")
    formatedDay  = hour.strftime("%d/%m/%Y")
    if request.method=='POST':
        form = RegistrarMinuta(request.POST)
        if form.is_valid():
            form.save()
        return redirect("index")
    else:
        form = RegistrarMinuta()
    return render(request,'usuarios/registrar_minuta.html',{'form': form, 'horas':formatedHour, 'fechas':formatedDay} )

class GraficaView(View):
    def get(self,request, *args, **kwargs):
        return render(request, 'usuarios/graficas_egresados.html', { })


def get_data(request, *args, **kwargs):
    data ={
        "salas":10,
        "clientes": 100,
    }
    return JsonResponse(data) #http response

def report(request):
    #Software
    g2012= Egresados.objects.filter(Q(carrera='Software') & Q(generacion='2012-2017')).count()
    g2013= Egresados.objects.filter(Q(carrera='Software') & Q(generacion='2013-2018')).count()
    g2014= Egresados.objects.filter(Q(carrera='Software') & Q(generacion='2014-2019')).count()
    g2015= Egresados.objects.filter(Q(carrera='Software') & Q(generacion='2015-2020')).count()
    #Civil
    gc2012= Egresados.objects.filter(Q(carrera='Civil') & Q(generacion='2012-2017')).count()
    gc2013= Egresados.objects.filter(Q(carrera='Civil') & Q(generacion='2013-2018')).count()
    gc2014= Egresados.objects.filter(Q(carrera='Civil') & Q(generacion='2014-2019')).count()
    gc2015= Egresados.objects.filter(Q(carrera='Civil') & Q(generacion='2015-2020')).count()
    #Geodesia
    gg2012= Egresados.objects.filter(Q(carrera='Geodesia') & Q(generacion='2012-2017')).count()
    gg2013= Egresados.objects.filter(Q(carrera='Geodesia') & Q(generacion='2013-2018')).count()
    gg2014= Egresados.objects.filter(Q(carrera='Geodesia') & Q(generacion='2014-2019')).count()
    gg2015= Egresados.objects.filter(Q(carrera='Geodesia') & Q(generacion='2015-2020')).count()
    #Proc. Industriales
    gi2012= Egresados.objects.filter(Q(carrera='Proc. Industriales') & Q(generacion='2012-2017')).count()
    gi2013= Egresados.objects.filter(Q(carrera='Proc. Industriales') & Q(generacion='2013-2018')).count()
    gi2014= Egresados.objects.filter(Q(carrera='Proc. Industriales') & Q(generacion='2014-2019')).count()
    gi2015= Egresados.objects.filter(Q(carrera='Proc. Industriales') & Q(generacion='2015-2020')).count()
    #-------------------------    
    numsoft = Egresados.objects.filter(carrera='Software').count()
    numciv = Egresados.objects.filter(carrera='Civil').count()
    numgeod = Egresados.objects.filter(carrera='Geodesia').count()
    numind = Egresados.objects.filter(carrera='Proc. Industriales').count()
    #--------------------------Genero
    numegreF = Egresados.objects.filter(genero='F').count()
    numegreM = Egresados.objects.filter(genero='M').count()
    hour = timezone.localtime(timezone.now())
    formatedHour = hour.strftime("%H:%M:%S")
    formatedDay  = hour.strftime("%d/%m/%Y")
    time.sleep(1)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename = Egresados-report.pdf'
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    #Header
    c.setLineWidth(.3)
    c.drawImage("UAS.png",30,770,width=50,height=66)
    c.setFont('Helvetica',14)
    c.drawString(30,750,'Facultad de Ingenieria Mochis - Comision Academica de Titulacion')
    c.setFont('Helvetica',12)
    c.drawString(30,735,'Reporte')
    c.setFont('Helvetica',12)
    c.drawString(30,710,'1.-Total de egresados por carrera')
    c.setFont('Helvetica',12)
    c.drawString(30,580,'2.-Total de egresados por genero')
    c.setFont('Helvetica',12)
    c.drawString(30,490,'3.-Total de egresados por generacion en Ingenieria Civil')
    c.setFont('Helvetica',12)
    c.drawString(30,370,'4.-Total de egresados por generacion en Ingenieria Geodesica')
    c.setFont('Helvetica',12)
    c.drawString(30,245,'5.-Total de egresados por generacion en Ingenieria de Procesos Industriales')
    c.setFont('Helvetica',12)
    c.drawString(30,115,'6.-Total de egresados por generacion en Ingenieria de Software')

    c.setFont('Helvetica-Bold',12)
    c.drawString(480,780, formatedHour)
    c.line(460,777,560,777)
    c.drawString(480,765, formatedDay)
    #/Header
    egresados = [{'carrera':'Software','egresados': numsoft},
                 {'carrera':'Civil','egresados':numciv},
                 {'carrera':'Geodesia','egresados':numgeod},
                 {'carrera':'Industriales','egresados':numind}]
    #Generaci             
    generaciones = [{'generacion':'2012-2017','cont':g2012},
                 {'generacion':'2013-2018','cont':g2013},
                 {'generacion':'2014-2019','cont':g2014},
                 {'generacion':'2015-2020','cont':g2015}]
    #GeneraciCiv             
    generacionesc = [{'generacion':'2012-2017','cont2':gc2012},
                 {'generacion':'2013-2018','cont2':gc2013},
                 {'generacion':'2014-2019','cont2':gc2014},
                 {'generacion':'2015-2020','cont2':gc2015}]
    #GeneraciGeodesia         
    generacionesg = [{'generacion':'2012-2017','cont3':gg2012},
                 {'generacion':'2013-2018','cont3':gg2013},
                 {'generacion':'2014-2019','cont3':gg2014},
                 {'generacion':'2015-2020','cont3':gg2015}]
    #GeneraciIndustr        
    generacionesi = [{'generacion':'2012-2017','cont4':gi2012},
                 {'generacion':'2013-2018','cont4':gi2013},
                 {'generacion':'2014-2019','cont4':gi2014},
                 {'generacion':'2015-2020','cont4':gi2015}]       
    #Genero      
    generos = [{'genero':'Hombres','g1':numegreM},
                 {'genero':'Mujeres','g1':numegreF}]                   
    #TableHeader
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize=10
    #Tabla1
    carrer = Paragraph('''Carrera''', styleBH)
    egrer = Paragraph('''# Egresados''', styleBH)
    data=[]
    data.append([carrer, egrer])
    #Tabla2
    gene = Paragraph('''Generacion''', styleBH)
    egrersof = Paragraph('''# Egresados - Software''', styleBH)
    data2=[]
    data2.append([gene, egrersof])
    #Tabla3
    genec = Paragraph('''Generacion''', styleBH)
    egrerciv = Paragraph('''# Egresados - Civil''', styleBH)
    data3=[]
    data3.append([genec, egrerciv])
    #Tabla4
    geneg = Paragraph('''Generacion''', styleBH)
    egrerg = Paragraph('''# Egresados - Geodesia''', styleBH)
    data4=[]
    data4.append([geneg, egrerg])
    #Tabla5
    genei = Paragraph('''Generacion''', styleBH)
    egreri = Paragraph('''# Egresados - Industriales''', styleBH)
    data5=[]
    data5.append([genei, egreri])
    #Tabla6
    gen = Paragraph('''Genero''', styleBH)
    genenum = Paragraph('''# Egresados''', styleBH)
    data6=[]
    data6.append([gen, genenum])
    #Table 
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize=7

    #T1
    high = 650
    for egresado in egresados:
        this_egresado = [egresado['carrera'], egresado['egresados']]
        data.append(this_egresado)
        high = high - 10


    width, height = A4
    table = Table(data, colWidths=[2.5* cm, 3.1*cm ])
    table.setStyle(TableStyle([#Estilos de tabla
        ('INNERGRID',(0,0),(-1,-1), 0.25, colors.blue),
        ('BOX',(0,0),(-1,-1), 0.25, colors.blue),]))    
    #T2

    high2 = 60
    for generacion in generaciones:
        this_generacions = [generacion['generacion'], generacion['cont']]
        data2.append(this_generacions)
        high2 = high2 - 10


    width, height = A4
    table2 = Table(data2, colWidths=[3.5* cm, 5.1*cm ])
    table2.setStyle(TableStyle([#Estilos de tabla
        ('INNERGRID',(0,0),(-1,-1), 0.25, colors.blue),
        ('BOX',(0,0),(-1,-1), 0.25, colors.blue),]))     
    #T3

    high3 = 435
    for generacion in generacionesc:
        this_generacionsc = [generacion['generacion'], generacion['cont2']]
        data3.append(this_generacionsc)
        high3 = high3 - 10


    width, height = A4
    table3 = Table(data3, colWidths=[3.5* cm, 5.1*cm ])
    table3.setStyle(TableStyle([#Estilos de tabla
        ('INNERGRID',(0,0),(-1,-1), 0.25, colors.blue),
        ('BOX',(0,0),(-1,-1), 0.25, colors.blue),]))
    


    #T4

    high4 = 315
    for generacion in generacionesg:
        this_generacionsg = [generacion['generacion'], generacion['cont3']]
        data4.append(this_generacionsg)
        high4 = high4 - 10


    width, height = A4
    table4 = Table(data4, colWidths=[3.5* cm, 5.1*cm ])
    table4.setStyle(TableStyle([#Estilos de tabla
        ('INNERGRID',(0,0),(-1,-1), 0.25, colors.blue),
        ('BOX',(0,0),(-1,-1), 0.25, colors.blue),]))


    #T5

    high5 = 190
    for generacion in generacionesi:
        this_generacionsi = [generacion['generacion'], generacion['cont4']]
        data5.append(this_generacionsi)
        high5 = high5 - 10


    width, height = A4
    table5 = Table(data5, colWidths=[3.5* cm, 5.1*cm ])
    table5.setStyle(TableStyle([#Estilos de tabla
        ('INNERGRID',(0,0),(-1,-1), 0.25, colors.blue),
        ('BOX',(0,0),(-1,-1), 0.25, colors.blue),]))

    #T6

    high6 = 540
    for genero in generos:
        this_genero = [genero['genero'], genero['g1']]
        data6.append(this_genero)
        high6 = high6 - 10


    width, height = A4
    table6 = Table(data6, colWidths=[3.5* cm, 5.1*cm ])
    table6.setStyle(TableStyle([#Estilos de tabla
        ('INNERGRID',(0,0),(-1,-1), 0.25, colors.blue),
        ('BOX',(0,0),(-1,-1), 0.25, colors.blue),]))

    #pdf save
    table.wrapOn(c, width, height)    
    table.drawOn(c,30,high)
    table6.wrapOn(c, width, height)    
    table6.drawOn(c,30,high6)
    table2.wrapOn(c, width, height)    
    table2.drawOn(c,30,high2)
    table3.wrapOn(c, width, height)    
    table3.drawOn(c,30,high3)
    table4.wrapOn(c, width, height)    
    table4.drawOn(c,30,high4)
    table5.wrapOn(c, width, height)    
    table5.drawOn(c,30,high5)
    c.showPage()
    

    c.save()
    pdf= buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


class CharData(APIView):
    authentication_classes = []
    permission_classes =[]

    def get(self, request, format=None):
        #Software
        g2012= Egresados.objects.filter(Q(carrera='Software') & Q(generacion='2012-2017')).count()
        g2013= Egresados.objects.filter(Q(carrera='Software') & Q(generacion='2013-2018')).count()
        g2014= Egresados.objects.filter(Q(carrera='Software') & Q(generacion='2014-2019')).count()
        g2015= Egresados.objects.filter(Q(carrera='Software') & Q(generacion='2015-2020')).count()
        #Civil
        gc2012= Egresados.objects.filter(Q(carrera='Civil') & Q(generacion='2012-2017')).count()
        gc2013= Egresados.objects.filter(Q(carrera='Civil') & Q(generacion='2013-2018')).count()
        gc2014= Egresados.objects.filter(Q(carrera='Civil') & Q(generacion='2014-2019')).count()
        gc2015= Egresados.objects.filter(Q(carrera='Civil') & Q(generacion='2015-2020')).count()
        #Geodesia
        gg2012= Egresados.objects.filter(Q(carrera='Geodesia') & Q(generacion='2012-2017')).count()
        gg2013= Egresados.objects.filter(Q(carrera='Geodesia') & Q(generacion='2013-2018')).count()
        gg2014= Egresados.objects.filter(Q(carrera='Geodesia') & Q(generacion='2014-2019')).count()
        gg2015= Egresados.objects.filter(Q(carrera='Geodesia') & Q(generacion='2015-2020')).count()
        #Proc. Industriales
        gi2012= Egresados.objects.filter(Q(carrera='Proc. Industriales') & Q(generacion='2012-2017')).count()
        gi2013= Egresados.objects.filter(Q(carrera='Proc. Industriales') & Q(generacion='2013-2018')).count()
        gi2014= Egresados.objects.filter(Q(carrera='Proc. Industriales') & Q(generacion='2014-2019')).count()
        gi2015= Egresados.objects.filter(Q(carrera='Proc. Industriales') & Q(generacion='2015-2020')).count()
        #--------------------------Genero
        numegreF = Egresados.objects.filter(genero='F').count()
        numegreM = Egresados.objects.filter(genero='M').count()
        #Carreras
        numsoft = Egresados.objects.filter(carrera='Software').count()
        numciv = Egresados.objects.filter(carrera='Civil').count()
        numgeod = Egresados.objects.filter(carrera='Geodesia').count()
        numind = Egresados.objects.filter(carrera='Proc. Industriales').count()
        #Variables a enviar por Json
        glabels = ['2012-2017','2013-2018','2014-2019','2015-2020']
        gitems = [g2012,g2013,g2014,g2015]
        gcitems = [gc2012,gc2013,gc2014,gc2015]
        ggitems = [gg2012,gg2013,gg2014,gg2015]
        giitems = [gi2012,gi2013,gi2014,gi2015]
        labels2 = ['Software','Civil', 'Geodesia', 'Proc. Industriales']
        items2 = [numsoft,numciv, numgeod, numind]
        labels = ['Mujeres', 'Hombres']
        default_items = [numegreF, numegreM]
        data ={
        "labels": labels,
        "default": default_items,
        "labels2": labels2,
        "items": items2,
        "glabels": glabels,
        "gitems": gitems,
        "gcitems":gcitems,
        "ggitems": ggitems,
        "giitems": giitems,
        }
        return Response(data)
