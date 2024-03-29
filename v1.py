from datetime import timedelta
from functools import reduce, wraps
from io import StringIO
from itertools import chain
from django.db.models.functions import *
from django.db import transaction
from django.http import *
import csv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import numpy as np
import requests
from .models import *
import json
from django.http import JsonResponse
from django.core.management.base import BaseCommand
from bs4 import UnicodeDammit
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import *  # login_required
from django.views.decorators.cache import cache_control
from django.db.models import *

from django.utils import timezone
import pandas as pd
import ast

import psycopg2
import mysql.connector

from .modeltblclname import *


# def custom_token_login_required(view_func):
#     def _wrapped_view(request, *args, **kwargs):
#         token_key= request.session.get('token')
#         # print(token_key, "hi")
#         try:
#             conn = mysql.connector.connect(
#                 host="mpulse-backup.cxqifsxuei8y.ap-south-1.rds.amazonaws.com",
#                 user="mpulse",
#                 password="smile2021!",
#                 database="mpulse"
#             )
#             cursor_obj = conn.cursor()
#             # print("connection establishes")
#             sql = f"""
#             select * from users at2 where at2.token ='{token_key}'
#             """
#             cursor_obj.execute(sql)
#             result = cursor_obj.fetchall()
#             # print(result, "result____")
#             if len(result) > 0 and 'location' in request.session and 'empId' in request.session:
#                 # request.session['token'] = result[0][11]
#                 EmpID = request.session.get('empId')
#                 language = userProfile.objects.filter(id=EmpID).values('language')[0]
#                 try:
#                     request.session['language'] = ast.literal_eval(
#                         language['language'])
#                     permlist = Roles.objects.filter(
#                         userprofile_id=EmpID).values('role')
#                     request.session['permlist'] = [i['role'] for i in permlist]
#                 except Exception as er:
#                     print(er)
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return HttpResponseRedirect('https://mpulse.plus/logout')
#         except Exception as er:
#             print(er)
#             return HttpResponse({'error': str(er),'Go Login':'https://mpulse.plus/'}, status=401)
#     return _wrapped_view

# @csrf_exempt
# def home(request):
#     if request.method == 'GET':
#         token = request.GET.get('token')
#         employeeid = request.GET.get('user')
#         employeename = request.GET.get('name')
#         # print(token,"token",employeeid,'employeeid',employeename,'employeename')
#         if token and employeeid and employeename:
#             request.session['token'] = token
#             # print(request.session.get('token'),"============",token)

#             UserID, created = userProfile.objects.update_or_create(
#                     employeeID=employeeid,
#                     defaults={'employeeName': str(employeename).replace("&nbsp;", " ")})
#             request.session['empId'] = UserID.id
#             request.session['employeeID'] = employeeid

#             userrec = userProfile.objects
#             language = userrec.filter(id=UserID.id).values('language')[0]
#             location = userrec.filter(id=UserID.id).values('location')

#             # Roles.objects.update_or_create(
#             #    userprofile_id=UserID.id, role='Admin')
#             try:
#                 request.session['language'] = ast.literal_eval(language['language'])
#             except Exception as er:
#                 request.session['language'] = list('English')
#                 print(er)
#             request.session['location'] = [i['location'] for i in location]
#             permlist = Roles.objects.filter(
#                 userprofile_id__employeeID=employeeid).values('role')

#             request.session['permlist'] = [i['role'] for i in permlist]

#             return redirect('/dash/')
#         else:
#             return HttpResponseRedirect('https://mpulse.plus/')

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# # @custom_token_login_required
# def dashboardView(request):
#     if request.method == 'POST':
#         pass
#     else:
#         return render(request, 'index.html')


def loginrequired(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            session = request.session
            if 'empId' in session and 'language' in session and 'location' in session:
                EmpID = request.session.get('empId')
                language = userProfile.objects.filter(id=EmpID).values('language')[0]
                try:
                    request.session['language'] = ast.literal_eval(
                        language['language'])
                except Exception as er:
                    print(er)
                
                return view_func(request, *args, **kwargs)
            else:
                request.session.flush()
                request.session.clear()
                return redirect('/dash/')
        except Exception as er:
            print(er)
            return redirect('/dash/')
    return _wrapped_view


@csrf_exempt
@loginrequired
def home(request):
    if request.method == 'POST':
        data = request.POST.get('token')
        request.session['token'] = data
        status = 'success'
        responseData = {'status': 'successpost'}
        return JsonResponse(responseData)
    else:
        data = request.GET.get('token')
        employeeid = request.GET.get('user')
        # employeename = request.GET.get('empname')
        return redirect('/dash/')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboardView(request):
    if request.method == 'POST':
        employeeid = request.POST.get('empid')
        # employeename = request.POST.get('empname')
        password = request.POST.get('password')

        if password == 'admin123$':

            UserID, created = userProfile.objects.update_or_create(
                employeeID=employeeid)
            
            request.session['empId'] = UserID.id
            request.session['employeeID'] = employeeid

            userrec = userProfile.objects
            language = userrec.filter(id=UserID.id).values('language')[0]
            location = userrec.filter(id=UserID.id).values('location')

            Roles.objects.update_or_create(
              userprofile_id=UserID.id, role='Admin')
            
            try:
                request.session['language'] = ast.literal_eval(
                    language['language'])
            except Exception as er:
                request.session['language'] = list('English')
                print(er)
            request.session['location'] = [i['location'] for i in location]
            permlist = Roles.objects.filter(
                userprofile_id__employeeID=employeeid).values('role')

            request.session['permlist'] = [i['role'] for i in permlist]

            return render(request, 'index.html')
        else:
            return render(request, 'index.html')
    else:
        return render(request, 'index.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @custom_token_login_required
@loginrequired
def app_logOut(request):
    request.session.flush()
    request.session.clear()
    request.session.clear_expired()
    return HttpResponseRedirect('/dash/')

# @custom_token_login_required
@loginrequired
def project_management(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        key = request.POST.get('key')
        if key == 'language':
            language = request.POST.get('language')
            Languages.objects.update_or_create(
                language=language, defaults={'created_by_id': EmpID})
            return render(request, 'pages/projectmanagement.html', {'status': 200, 'message': 'success'})
        if key == 'location':
            location = request.POST.get('location')
            Location.objects.update_or_create(
                location=location, defaults={'created_by_id': EmpID})
            return render(request, 'pages/projectmanagement.html', {'status': 200, 'message': 'success'})
    else:
        return render(request, 'pages/projectmanagement.html')

# @custom_token_login_required
@loginrequired
def userTable(request):
    if request.method == "POST":
        key = request.POST.get('key')
        employeeID = request.POST.get('employeeID')
        # print(employeeID)
        if key == 'Edit':
            userdatas = userProfile.objects.filter(id=employeeID).values(
                'id', 'employeeName', 'employeeID', 'location', 'language', 'reporting', 'prodStart_date', 'created_at')
            roles = Roles.objects.filter(
                userprofile_id=employeeID).values('role')
            shift = ShiftTime.objects.filter(userprofile_id=employeeID).values(
                'starttime', 'endtime').last()
            langs = Languages.objects.values('language')
            location = Location.objects.values('location')
            return render(request, 'pages/userManagement.html', {'langs': langs, 'location': location, 'userdatas': userdatas[0], 'roles': [i['role'] for i in roles], 'shift': shift})
        elif key == 'Delete':
            try:
                userProfile_instance = userProfile.objects.get(id=employeeID)
                roles_instances = Roles.objects.filter(
                    userprofile=userProfile_instance)
                roles_instances.delete()

                userProfile_instance.delete()
                return redirect('/api/v1/userTable/')
            except Exception as er:
                print(er)
                return redirect('/api/v1/userTable/')
    else:
        userdatas = userProfile.objects.values(
            'id', 'employeeName', 'employeeID', 'location', 'language', 'reporting', 'prodStart_date', 'created_at')
        roles = Roles.objects.values('userprofile_id__employeeID', 'role')
        roles = Roles.objects.values('role', employeeID = F('userprofile_id__employeeID'))
        userdatas_df = pd.DataFrame(userdatas)
        roles_df = pd.DataFrame(roles)
        mrgd_df = pd.merge(userdatas_df,roles_df,on='employeeID',how='outer')
        mrgd_df = mrgd_df.to_dict('records')
        return render(request, 'pages/UserTable.html', {'userDatas': mrgd_df, 'roles': roles})


# @custom_token_login_required
@loginrequired
def OverAllRole(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        employeeID = request.POST.get('employeeid')
        roles = request.POST.getlist('roles')
        try:
            UseTable = userProfile.objects
            empall = [eid.strip() for eid in employeeID.split(',')]
            for EmpId in empall:
                UseTable.update_or_create(
                    employeeID=EmpId)

            UserID = UseTable.filter(
                employeeID__in=empall).values('id')
            for ids in UserID:
                for role in roles:
                    Roles.objects.create(
                        userprofile_id=ids['id'], role=role, created_by_id=EmpID)
            return JsonResponse({'status': 200, 'message': 'Success'})

        except Exception as er:
            return JsonResponse({'status': 400, 'message': str(er)})
    else:
        return redirect('/api/v1/userTable/')


# @custom_token_login_required
@loginrequired
def UserManagement(request):
    EmpID = request.session.get('empId')
    if request.method == "POST":
        key = request.POST.get('key')
        if key == 'userdata':
            employeeID = request.POST.get('employeeid')
            employeeName = request.POST.get('employeeName')
            reporting = request.POST.get('reporting')
            location = request.POST.get('location')
            language = request.POST.getlist('language')
            prodStart_date = request.POST.get('prodStart_date')
            roles = request.POST.getlist('role')

            UserID, created = userProfile.objects.update_or_create(
                employeeID=employeeID,
                defaults={'employeeName': employeeName,
                          'reporting': reporting,
                          'language': language,
                          'location': location,
                          'prodStart_date': prodStart_date})
            try:
                rolestable = Roles.objects
                for role in roles:
                    if not rolestable.filter(role=role, userprofile_id=UserID.id).exists():
                        rolestable.update_or_create(
                            userprofile_id=UserID.id, role=role, created_by_id=EmpID)
                rolestable.filter(userprofile_id=UserID.id,).exclude(
                    role__in=roles).delete()
            except Exception as er:
                return JsonResponse({'status': 400, 'message': str(er)})
            return JsonResponse({'status': 200, 'message': 'Success'})

        else:
            userprofile = request.POST.get('userprofile')
            shift_starttime = request.POST.get('shift_starttime')
            shift_endtime = request.POST.get('shift_endtime')
            ShiftTime.objects.update_or_create(
                userprofile_id=userprofile, starttime=shift_starttime, endtime=shift_endtime, created_by_id=EmpID)
            return redirect('/api/v1/userTable/')
    else:
        langs = Languages.objects.values('language')
        return render(request, 'pages/userManagement.html', {'langs': langs})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @custom_token_login_required
@loginrequired
def uploadView(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        language = request.POST.get('language', None)
        file_name = request.FILES.get('file', None)
        fileExtention = str(file_name).split('.')
        key = request.POST.get('key', None)

        if fileExtention and file_name:
            fileType = fileExtention[1]

            last_RECD = basefile.objects.order_by('-id').first()
            if last_RECD:
                last_id = int(last_RECD.batch_name[5:])
                new_id = last_id + 1
            else:
                new_id = 1
            batch_name = f'BATCH{new_id:05}'

            if fileType == 'csv':
                excel_data = pd.read_csv(
                    file_name, encoding='utf-8', encoding_errors='ignore')
                if not excel_data.empty:
                    excel_data.fillna('', inplace=True)
                to_dict = excel_data.to_dict('records')
                try:
                    baseid = basefile.objects.create(
                        batch_name=batch_name, filename=file_name, language=language, created_by_id=EmpID)
                    with transaction.atomic():
                        for i in to_dict:
                            raw_data.objects.create(
                                id_value=i.get('id_value', None),
                                question=i.get('question', None),
                                asin=i.get('asin', None),
                                title=i.get('title', None),
                                product_url=i.get('product_url', None),
                                imagepath=i.get('imagepath', None),
                                evidence=i.get('evidence', None),
                                answer_one=i.get('answer_one', None),
                                answer_two=i.get('answer_two', None),
                                baseid_id=baseid.id
                            )
                        responseData = {'status': 'success',
                                        'result': 'Data Upload Successfully'}
                        return JsonResponse(responseData)
                except Exception as er:
                    print(er)
                    responseData = {'status': 'failed',
                                    'result': ",File Already Exist"}
                    return JsonResponse(responseData)
            else:
                file_content = file_name.read()
                parsed_data = json.loads(file_content)
                # cleaned_data = remove_binary_and_newlines(
                #     parsed_data)  # Remove binary and newline characters
                # cleaned_json = json.dumps(cleaned_data, indent=4)
                try:
                    baseid = basefile.objects.create(
                        batch_name=batch_name, filename=file_name, language=language, created_by_id=EmpID)
                    with transaction.atomic():
                        for i in parsed_data:
                            raw_data.objects.create(
                                id_value=i.get('id_value', None),
                                question=i.get('question', None),
                                asin=i.get('asin', None),
                                title=i.get('title', None),
                                product_url=i.get('product_url', None),
                                imagepath=i.get('imagepath', None),
                                evidence=i.get('evidence', None),
                                answer_one=i.get('answer_one', None),
                                answer_two=i.get('answer_two', None),
                                baseid_id=baseid.id
                            )
                        responseData = {'status': 'success',
                                        'result': 'Data Upload Successfully'}
                        return JsonResponse(responseData)
                except Exception as er:
                    print(er)
                    responseData = {'status': 'failed',
                                    'result': "File Already Exist"}
                    return JsonResponse(responseData)

        elif key == 'MiniRecords':
            fromdate = request.POST.get('fromDate')
            todate = request.POST.get('toDate')
            language = request.POST.get('language')
            request.session['fromDate'] = fromdate
            request.session['toDate'] = todate

            status = request.POST.get('status', None)
            request.session['smpstatus'] = status

            conditions = Q()
            if status != 'All':
                conditions &= Q(status=status)
            if fromdate and todate:
                conditions &= Q(
                    baseid_id__created_at__range=(fromdate, todate))
            if language != 'All':
                conditions &= Q(baseid_id__language=language)

            datas = raw_data.objects.filter(conditions)
            if datas.count() > 0:
                tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename', 'baseid_id__language').annotate(
                    count=Count('status')).order_by('uploaded_at').distinct()
                content = 'show'
            else:
                tabledata = []
                content = 'hide'
            return render(request, 'pages/upload.html', {'tabledata': tabledata, 'content': content, 'status': status})
        else:
            responseData = {'status': 'failed', 'result': 'Data is Required'}
            return JsonResponse(responseData)
    else:
        datas = raw_data.objects.filter(~Q(status='deleted'))
        if datas.count() > 0:
            tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename', 'baseid_id__language').annotate(
                count=Count('status')).order_by('-uploaded_at').distinct()[:10]
            content = 'show'
        else:
            tabledata = []
            content = 'hide'
        langs = Languages.objects.values('language')
        return render(request, 'pages/upload.html', {'tabledata': tabledata, 'content': content, 'key': 'all', 'langs': langs})


# @custom_token_login_required
@loginrequired
def miniFileDownload(request):
    if request.method == "POST":
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="MiniFileDownload.csv"'

        status = request.session.get('smpstatus', None)
        fromdate = request.session['fromDate']
        todate = request.session['toDate']

        conditions = Q()
        if status:
            conditions &= Q(status=status)
        if fromdate and todate:
            conditions &= Q(baseid_id__created_at__range=(fromdate, todate))

        datas = raw_data.objects.filter(~Q(status='deleted'), conditions)
        if datas.count() > 0:
            tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename').annotate(
                count=Count('status')).order_by('uploaded_at').distinct()
            writer = csv.writer(response)
            title = [
                "BAtch ID",
                "File Name",
                "Status",
                "Uploaded By",
                "Uploaded At"]
            writer.writerow(title)
            for v in tabledata:
                record = [v["baseid_id__batch_name"],
                          v["baseid_id__filename"],
                          v["status"],
                          v["baseid_id__created_by_id__employeeID"],
                          v["uploaded_at"]]
                writer.writerow(record)
            return response


# @custom_token_login_required
@loginrequired
def fileDownload(request, batchid, filename_form):
    batchID = batchid
    filename = filename_form

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="FileDownload"' + \
        batchID+'_'+filename+'".csv"'

    records = raw_data.objects.filter(baseid_id__batch_name=batchID).values("id_value", "baseid_id__batch_name", "baseid_id__created_at", "baseid_id__created_by_id__employeeID",
                                                                            "question",
                                                                            "asin",
                                                                            "title",
                                                                            "product_url",
                                                                            "imagepath",
                                                                            "evidence",
                                                                            "answer_one",
                                                                            "answer_two", "baseid_id__filename")
    writer = csv.writer(response)
    title = [
        "batchID",
        "File Name",
        "id_value",
        "question",
        "asin",
        "title",
        "product_url",
        "imagepath",
        "evidence",
        "answer_one",
        "answer_two",
        "created_at",
        "created_by"]
    writer.writerow(title)
    for v in records:
        record = [v["baseid_id__batch_name"],
                  v["baseid_id__filename"],
                  v["id_value"],
                  v["question"],
                  v["asin"],
                  v["title"],
                  v["product_url"],
                  v["imagepath"],
                  v["evidence"],
                  v["answer_one"],
                  v["answer_two"],
                  v['baseid_id__created_at'],
                  v["baseid_id__created_by_id__employeeID"]]
        writer.writerow(record)

    if records.exists():
        return response
    else:
        return JsonResponse({'status': 400, 'message': 'No Records'})


# @custom_token_login_required
@loginrequired
def fileMamagement(request):
    if request.method == 'POST':
        key = request.POST.get('key')

        if key == 'delete':
            filename = request.POST.get('filename')
            raw_data.objects.filter(
                baseid_id__filename=filename).delete()
            basefile.objects.filter(filename=filename).delete()

            # raw_data.objects.filter(
            #     baseid_id__filename=filename).update(status='deleted')
            # basefile.objects.filter(filename=filename).update(
            #     filename=str(filename)+'Deleted')
        elif key == 'processing':  # Hold records when it is processing
            batch_name = request.POST.get('batch_name')
            selectbox = request.POST.get('selectedValue')
            if selectbox == 'ALL':
                raw_data.objects.filter(
                    baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'DA1':
                raw_data.objects.filter(Q(l1_status__isnull=True) | ~Q(
                    l1_status='completed'), baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'DA2':
                raw_data.objects.filter(Q(l2_status__isnull=True) | ~Q(
                    l2_status='completed'), baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'QC':
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status='completed')) & (Q(l2_status__isnull=True) | Q(l2_status='completed')) & (
                    Q(l3_status__isnull=True) | ~Q(l3_status='picked')), baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'QA':
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status='completed')) & (Q(l2_status__isnull=True) | Q(l2_status='completed')) & (
                    Q(l4_status__isnull=True) | ~Q(l4_status='picked')), baseid_id__batch_name=batch_name).update(status='hold')

        elif key == 'hold':  # Unhold Records when it is Hold
            batch_name = request.POST.get('batch_name')
            selectbox = request.POST.get('selectedValue')
            if selectbox == 'ALL':
                raw_data.objects.filter(
                    baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'DA1':
                raw_data.objects.filter(Q(l1_status__isnull=True) | ~Q(
                    l1_status='completed'), baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'DA2':
                raw_data.objects.filter(Q(l2_status__isnull=True) | ~Q(
                    l2_status='completed'), baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'QC':
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status='completed')) & (Q(l2_status__isnull=True) | Q(l2_status='completed')) & (
                    Q(l3_status__isnull=True) | ~Q(l3_status='picked')), baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'QA':
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status='completed')) & (Q(l2_status__isnull=True) | Q(l2_status='completed')) & (
                    Q(l4_status__isnull=True) | ~Q(l4_status='picked')), baseid_id__batch_name=batch_name).update(status='processing')

        return JsonResponse({'status': 'Success'})
    # return render(request, 'pages/upload.html')


# @custom_token_login_required
@loginrequired
def remove_binary_and_newlines(data):
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, bytes):
                del data[key]  # Remove binary value
            else:
                data[key] = remove_binary_and_newlines(value)
    elif isinstance(data, list):
        data = [remove_binary_and_newlines(item) for item in data]
    elif isinstance(data, str):
        data = data.replace('\n', '')

    return data


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @custom_token_login_required
@loginrequired
def SampleFileDownloadView(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="evaluate.csv"'
    csv_writer = csv.writer(response)
    header = ["id_value", "question", "asin", "title", "product_url",
              "imagepath", "evidence", "answer_one", "answer_two"]
    csv_writer.writerow(header)
    return response


# @custom_token_login_required
@loginrequired
def loneproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    # EmpLoc = request.session.get('empLoc') Location/area wise filter
    # ,Q(created_by_id__location = EmpLoc)

    if request.method == 'GET':
        try:
            with transaction.atomic():
                l1_count = raw_data.objects.filter(Q(l1_prod_id__end_time__date=timezone.now().date()), Q(
                    l1_status='completed') & Q(l1_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
                if l1_count is not None:
                    l1_count = l1_count
                else:
                    l1_count = 0

                query = Q()
                if language:
                    query = Q(baseid_id__language__in=language)

                instance = raw_data.objects.select_for_update(skip_locked=True).filter(query,
                                                                                       (Q(l1_status='picked') & Q(l1_emp_id=EmpID)) | (Q(l1_status='not_picked') & Q(l1_emp_id__isnull=True)) & (Q(l1_loc__isnull=True) & Q(l2_loc__isnull=True) | Q(l2_loc=location[0]))).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', 'l1_emp_id').exclude(status__in=['hold', 'deleted']).exclude(l2_emp_id=EmpID).order_by('-l1_status', 'id').first()

                if instance:
                    l1prod = l1_production.objects
                    if l1prod.filter(qid_id=instance['id']).exists():
                        l1_production.objects.filter(qid_id=instance['id']).update(
                            start_time=timezone.now())
                        raw_data.objects.filter(id=instance['id']).update(
                            l1_status='picked', l1_emp_id=EmpID, l1_loc=location[0])
                    else:
                        prodid = l1_production.objects.create(
                            qid_id=instance['id'], start_time=timezone.now())
                        raw_data.objects.filter(id=instance['id']).update(
                            l1_status='picked', l1_emp_id=EmpID, l1_loc=location[0], l1_prod_id=prodid.id)
        except Exception as er:
            print(er)
            # ,'l1count':l1count l1count = raw_data.objects.filter(Q(l1_status='completed', l1_emp_id=EmpID)).values('baseid__batch_name').annotate(l1count=Count('baseid__batch_name')).exclude(status__in=['hold', 'deleted']).order_by('-baseid__batch_name')
            instance = []
        return render(request, 'pages/l1_production.html', {'result': instance, 'l1_count': l1_count,'htmlfields':htmlfields})
    else:
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        que1 = request.POST.get('que1', None)
        que1a = request.POST.get('que1a', None)

        que2_ans1 = request.POST.get('que2_ans1', None)
        que2a_ans1 = request.POST.get('que2a_ans1', None)
        que3_ans1 = ','.join(request.POST.getlist('que3_ans1', None))
        que4_ans1 = ','.join(request.POST.getlist('que4_ans1', None))
        que4a_ans1 = request.POST.get('que4a_ans1', None)
        que4b_ans1 = request.POST.get('que4b_ans1', None)
        que4c_ans1 = request.POST.get('que4c_ans1', None)
        que4d_ans1 = request.POST.get('que4d_ans1', None)
        que4e_ans1 = request.POST.get('que4e_ans1', None)
        que4f_ans1 = request.POST.get('que4f_ans1', None)
        que5_ans1 = ','.join(request.POST.getlist('que5_ans1', None))
        que5a_ans1 = request.POST.get('que5a_ans1', None)
        que6_ans1 = request.POST.get('que6_ans1', None)
        que6a_ans1 = request.POST.get('que6a_ans1', None)
        que7_ans1 = request.POST.get('que7_ans1', None)
        que8_ans1 = request.POST.get('que8_ans1', None)
        que8a_ans1 = request.POST.get('que8a_ans1', None)
        que8b_ans1 = request.POST.get('que8b_ans1', None)
        que2_ans2 = request.POST.get('que2_ans2', None)
        que2a_ans2 = request.POST.get('que2a_ans2', None)
        que3_ans2 = ','.join(request.POST.getlist('que3_ans2', None))
        que4_ans2 = ','.join(request.POST.getlist('que4_ans2', None))
        que4a_ans2 = request.POST.get('que4a_ans2', None)
        que4b_ans2 = request.POST.get('que4b_ans2', None)
        que4c_ans2 = request.POST.get('que4c_ans2', None)
        que4d_ans2 = request.POST.get('que4d_ans2', None)
        que4e_ans2 = request.POST.get('que4e_ans2', None)
        que4f_ans2 = request.POST.get('que4f_ans2', None)
        que5_ans2 = ','.join(request.POST.getlist('que5_ans2', None))
        que5a_ans2 = request.POST.get('que5a_ans2', None)
        que6_ans2 = request.POST.get('que6_ans2', None)
        que6a_ans2 = request.POST.get('que6a_ans2', None)
        que7_ans2 = request.POST.get('que7_ans2', None)
        que8_ans2 = request.POST.get('que8_ans2', None)
        que8a_ans2 = request.POST.get('que8a_ans2', None)
        que8b_ans2 = request.POST.get('que8b_ans2', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    l1prod_values = l1prod.values_list('id', flat=True)

                    responseData = {'status': 'success',
                                    'result': "Production Completed"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l1_prod_id=l1prod_values,
                                                               l1_status='completed', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    l1prod_values = l1prod.values_list('id', flat=True)

                    redirect_url = '/dash/'
                    responseData = {'status': 'success', 'redirect_url': redirect_url,
                                    'result': "Production Completed"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l1_prod_id=l1prod_values,
                                                               l1_status='completed', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l1_prod_id=l1prod_values,
                                                           l1_status='hold', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)


# @custom_token_login_required
@loginrequired
def ltwoproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    if request.method == 'GET':
        try:
            with transaction.atomic():
                l2_count = raw_data.objects.filter(Q(l2_prod_id__end_time__date=timezone.now().date()), Q(
                    l2_status='completed') & Q(l2_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
                if l2_count is not None:
                    l2_count = l2_count
                else:
                    l2_count = 0

                query = Q()
                if language:
                    query = Q(baseid_id__language__in=language)

                instance = raw_data.objects.select_for_update(skip_locked=True).filter(query,
                                                                                       (Q(l2_status='picked') & Q(l2_emp_id=EmpID)) | (Q(l2_status='not_picked') & Q(l2_emp_id__isnull=True)) & (Q(l2_loc__isnull=True) & Q(l1_loc__isnull=True) | Q(l1_loc=location[0]))).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', 'l2_emp_id').exclude(status__in=['hold', 'deleted']).exclude(l1_emp_id=EmpID).order_by('-l2_status', 'id').first()

                if instance:
                    l2prod = l2_production.objects
                    if l2prod.filter(qid_id=instance['id']).exists():
                        l2_production.objects.filter(qid_id=instance['id']).update(
                            start_time=timezone.now())
                        raw_data.objects.filter(id=instance['id']).update(
                            l2_status='picked', l2_emp_id=EmpID, l2_loc=location[0])
                    else:
                        prodid = l2_production.objects.create(
                            qid_id=instance['id'], start_time=timezone.now())
                        raw_data.objects.filter(id=instance['id']).update(
                            l2_status='picked', l2_emp_id=EmpID, l2_loc=location[0], l2_prod_id=prodid.id)
        except Exception as er:
            print(er)
            # , 'l2count':l2count l2count = raw_data.objects.filter(Q(l2_status='completed', l2_emp_id=EmpID)).values('baseid__batch_name').annotate(l2count=Count('baseid__batch_name')).exclude(status__in=['hold', 'deleted']).order_by('-baseid__batch_name')
            instance = []
        return render(request, 'pages/l2_production.html', {'result': instance, "l2_count": l2_count,'htmlfields':htmlfields})
    else:
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        que1 = request.POST.get('que1', None)
        que1a = request.POST.get('que1a', None)

        que2_ans1 = request.POST.get('que2_ans1', None)
        que2a_ans1 = request.POST.get('que2a_ans1', None)
        que3_ans1 = ','.join(request.POST.getlist('que3_ans1', None))
        que4_ans1 = ','.join(request.POST.getlist('que4_ans1', None))
        que4a_ans1 = request.POST.get('que4a_ans1', None)
        que4b_ans1 = request.POST.get('que4b_ans1', None)
        que4c_ans1 = request.POST.get('que4c_ans1', None)
        que4d_ans1 = request.POST.get('que4d_ans1', None)
        que4e_ans1 = request.POST.get('que4e_ans1', None)
        que4f_ans1 = request.POST.get('que4f_ans1', None)
        que5_ans1 = ','.join(request.POST.getlist('que5_ans1', None))
        que5a_ans1 = request.POST.get('que5a_ans1', None)
        que6_ans1 = request.POST.get('que6_ans1', None)
        que6a_ans1 = request.POST.get('que6a_ans1', None)
        que7_ans1 = request.POST.get('que7_ans1', None)
        que8_ans1 = request.POST.get('que8_ans1', None)
        que8a_ans1 = request.POST.get('que8a_ans1', None)
        que8b_ans1 = request.POST.get('que8b_ans1', None)
        que2_ans2 = request.POST.get('que2_ans2', None)
        que2a_ans2 = request.POST.get('que2a_ans2', None)
        que3_ans2 = ','.join(request.POST.getlist('que3_ans2', None))
        que4_ans2 = ','.join(request.POST.getlist('que4_ans2', None))
        que4a_ans2 = request.POST.get('que4a_ans2', None)
        que4b_ans2 = request.POST.get('que4b_ans2', None)
        que4c_ans2 = request.POST.get('que4c_ans2', None)
        que4d_ans2 = request.POST.get('que4d_ans2', None)
        que4e_ans2 = request.POST.get('que4e_ans2', None)
        que4f_ans2 = request.POST.get('que4f_ans2', None)
        que5_ans2 = ','.join(request.POST.getlist('que5_ans2', None))
        que5a_ans2 = request.POST.get('que5a_ans2', None)
        que6_ans2 = request.POST.get('que6_ans2', None)
        que6a_ans2 = request.POST.get('que6a_ans2', None)
        que7_ans2 = request.POST.get('que7_ans2', None)
        que8_ans2 = request.POST.get('que8_ans2', None)
        que8a_ans2 = request.POST.get('que8a_ans2', None)
        que8b_ans2 = request.POST.get('que8b_ans2', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    l2prod_values = l2prod.values_list('id', flat=True)

                    responseData = {'status': 'success',
                                    'result': "Production Completed"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l2_prod_id=l2prod_values,
                                                               l2_status='completed', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    l2prod_values = l2prod.values_list('id', flat=True)

                    redirect_url = '/dash/'
                    responseData = {'status': 'success', 'redirect_url': redirect_url,
                                    'result': "Production Completed"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l2_prod_id=l2prod_values,
                                                               l2_status='completed', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l2_prod_id=l2prod_values,
                                                           l2_status='hold', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)


def queue():
    rawData = raw_data.objects.filter(Q(l1_status='completed') & Q(
        l2_status='completed') & Q(l1_l2_accuracy__isnull=True)).values('id')
    for i in rawData:
        fromqueue = l1_l2Comparison(i['id'])
        queue = fromqueue['result']
        if 'Not Matched' in queue['Comparison'].values:
            l1_l2_accuracy = 'fail'
        else:
            l1_l2_accuracy = 'pass'
        raw_data.objects.filter(id=i['id']).update(
            l1_l2_accuracy=l1_l2_accuracy)
    return


def l1_l2Comparison(id):
    l1_prod = l1_production.objects.filter(qid_id=id).values('id', 'que1', 'que1a', 'que2_ans1', 'que2a_ans1', 'que3_ans1', 'que4_ans1', 'que4a_ans1', 'que4b_ans1', 'que4c_ans1',
                                                             'que4d_ans1', 'que4e_ans1', 'que4f_ans1', 'que5_ans1', 'que5a_ans1', 'que6_ans1', 'que6a_ans1',
                                                             'que7_ans1', 'que8_ans1', 'que8a_ans1', 'que8b_ans1', 'que2_ans2', 'que2a_ans2', 'que3_ans2', 'que4_ans2',
                                                             'que4a_ans2', 'que4b_ans2', 'que4c_ans2', 'que4d_ans2', 'que4e_ans2', 'que4f_ans2', 'que5_ans2',
                                                             'que5a_ans2', 'que6_ans2', 'que6a_ans2', 'que7_ans2', 'que8_ans2', 'que8a_ans2', 'que8b_ans2')
    l2_prod = l2_production.objects.filter(qid_id=id).values('id', 'que1', 'que1a', 'que2_ans1', 'que2a_ans1', 'que3_ans1', 'que4_ans1', 'que4a_ans1', 'que4b_ans1', 'que4c_ans1',
                                                             'que4d_ans1', 'que4e_ans1', 'que4f_ans1', 'que5_ans1', 'que5a_ans1', 'que6_ans1', 'que6a_ans1',
                                                             'que7_ans1', 'que8_ans1', 'que8a_ans1', 'que8b_ans1', 'que2_ans2', 'que2a_ans2', 'que3_ans2', 'que4_ans2',
                                                             'que4a_ans2', 'que4b_ans2', 'que4c_ans2', 'que4d_ans2', 'que4e_ans2', 'que4f_ans2', 'que5_ans2',
                                                             'que5a_ans2', 'que6_ans2', 'que6a_ans2', 'que7_ans2', 'que8_ans2', 'que8a_ans2', 'que8b_ans2')

    df1 = pd.DataFrame(l1_prod).fillna('null')
    df2 = pd.DataFrame(l2_prod).fillna('null')

    if not df1.empty and not df2.empty:

        fields_to_compare = ['que1', 'que1a', 'que2_ans1', 'que2a_ans1', 'que3_ans1', 'que4_ans1', 'que4a_ans1', 'que4b_ans1', 'que4c_ans1',
                             'que4d_ans1', 'que4e_ans1', 'que4f_ans1', 'que5_ans1', 'que5a_ans1', 'que6_ans1', 'que6a_ans1',
                             'que7_ans1', 'que8_ans1', 'que8a_ans1', 'que8b_ans1', 'que2_ans2', 'que2a_ans2', 'que3_ans2', 'que4_ans2',
                             'que4a_ans2', 'que4b_ans2', 'que4c_ans2', 'que4d_ans2', 'que4e_ans2', 'que4f_ans2', 'que5_ans2',
                             'que5a_ans2', 'que6_ans2', 'que6a_ans2', 'que7_ans2', 'que8_ans2', 'que8a_ans2', 'que8b_ans2'
                             ]

        result_list = []
        for field in fields_to_compare:
            if field not in  ['que5_ans1','que5_ans2', 'que7_ans1', 'que7_ans2', 'que8b_ans1', 'que8b_ans2']:
                comparison_result = 'Matched' if (
                    df1[field] == df2[field]).all() else 'Not Matched'
            else:
                comparison_result = 'link&commands'
            
            result_list.append(
                {'Field': field, 'Comparison': comparison_result, 'DA2ans': str(df2[field].item())})

        result_df = pd.DataFrame(result_list)


        d1q5 = l1_prod.values('que5_ans1','que5_ans2').first()
        d2q5 = l2_prod.values('que5_ans1','que5_ans2').first()

        datas = {'result': result_df, 'l1_prod_link': d1q5,
                 'l2_prod_link': d2q5}
        
        return datas
    else:
        return False


# @custom_token_login_required
@loginrequired
def lthreeproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    if request.method == "POST":
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        que1 = request.POST.get('que1', None)
        que1a = request.POST.get('que1a', None)

        que2_ans1 = request.POST.get('que2_ans1', None)
        que2a_ans1 = request.POST.get('que2a_ans1', None)
        que3_ans1 = ','.join(request.POST.getlist('que3_ans1', None))
        que4_ans1 = ','.join(request.POST.getlist('que4_ans1', None))
        que4a_ans1 = request.POST.get('que4a_ans1', None)
        que4b_ans1 = request.POST.get('que4b_ans1', None)
        que4c_ans1 = request.POST.get('que4c_ans1', None)
        que4d_ans1 = request.POST.get('que4d_ans1', None)
        que4e_ans1 = request.POST.get('que4e_ans1', None)
        que4f_ans1 = request.POST.get('que4f_ans1', None)
        que5_ans1 = ','.join(request.POST.getlist('que5_ans1', None))
        que5a_ans1 = request.POST.get('que5a_ans1', None)
        que6_ans1 = request.POST.get('que6_ans1', None)
        que6a_ans1 = request.POST.get('que6a_ans1', None)
        que7_ans1 = request.POST.get('que7_ans1', None)
        que8_ans1 = request.POST.get('que8_ans1', None)
        que8a_ans1 = request.POST.get('que8a_ans1', None)
        que8b_ans1 = request.POST.get('que8b_ans1', None)
        que2_ans2 = request.POST.get('que2_ans2', None)
        que2a_ans2 = request.POST.get('que2a_ans2', None)
        que3_ans2 = ','.join(request.POST.getlist('que3_ans2', None))
        que4_ans2 = ','.join(request.POST.getlist('que4_ans2', None))
        que4a_ans2 = request.POST.get('que4a_ans2', None)
        que4b_ans2 = request.POST.get('que4b_ans2', None)
        que4c_ans2 = request.POST.get('que4c_ans2', None)
        que4d_ans2 = request.POST.get('que4d_ans2', None)
        que4e_ans2 = request.POST.get('que4e_ans2', None)
        que4f_ans2 = request.POST.get('que4f_ans2', None)
        que5_ans2 = ','.join(request.POST.getlist('que5_ans2', None))
        que5a_ans2 = request.POST.get('que5a_ans2', None)
        que6_ans2 = request.POST.get('que6_ans2', None)
        que6a_ans2 = request.POST.get('que6a_ans2', None)
        que7_ans2 = request.POST.get('que7_ans2', None)
        que8_ans2 = request.POST.get('que8_ans2', None)
        que8a_ans2 = request.POST.get('que8a_ans2', None)
        que8b_ans2 = request.POST.get('que8b_ans2', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l3prod = l3_production.objects.filter(qid_id=eid)
                    l3prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    l3prod_values = l3prod.values_list('id', flat=True)

                    responseData = {'status': 'success',
                                    'result': "Production Completed"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l3_prod_id=l3prod_values,
                                                               l3_status='completed', l3_emp_id=EmpID)
            except Exception as er:
                print(er)
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l3prod = l3_production.objects.filter(qid_id=eid)

                    l3prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    l3prod_values = l3prod.values_list('id', flat=True)

                    redirect_url = '/dash/'
                    responseData = {'status': 'success', 'redirect_url': redirect_url,
                                    'result': "Production Completed"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l3_prod_id=l3prod_values,
                                                               l3_status='completed', l3_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l3prod = l3_production.objects.filter(qid_id=eid)
                    l3prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    responseData = {'status': 'success',
                                    'result': "Production  Hold"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l3_prod_id=l3prod_values,
                                                               l3_status='hold', l3_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

    else:
        l3_count = raw_data.objects.filter(Q(l3_prod_id__end_time__date=timezone.now().date()), Q(
            l3_status='completed') & Q(l3_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l3_count is not None:
            l3_count = l3_count
        else:
            l3_count = 0
        try:
            query = Q()
            if language:
                query = Q(baseid_id__language__in=language)

            def loop():
                with transaction.atomic():
                    rawData = raw_data.objects.select_for_update(skip_locked=True).filter(Q(l1_status='completed') & Q(l2_status='completed') & query & ((Q(l3_status='not_moved') & Q(l3_emp_id__isnull=True)) | (Q(l3_status='picked') & Q(l3_emp_id=EmpID))) &
                                                                                          (Q(l1_l2_accuracy__isnull=True) | Q(l1_l2_accuracy='fail'))).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', 'l1_l2_accuracy').exclude(status__in=['hold', 'deleted']).exclude(l1_l2_accuracy='pass').exclude(l1_emp_id=EmpID).exclude(l2_emp_id=EmpID).order_by('baseid_id', 'id', '-l3_status').first()

                    if rawData and rawData is not None:
                        l3comp = l1_l2Comparison(rawData['id'])
                        if l3comp:
                            l3input = l3comp['result']
                            l3link = l3comp
                            if 'Not Matched' in l3input['Comparison'].values:
                                l1_l2_accuracy = 'fail'

                                if l3_production.objects.filter(qid_id=rawData['id']).exists():
                                    l3_production.objects.filter(qid_id=rawData['id']).update(
                                        start_time=timezone.now())
                                    raw_data.objects.filter(id=rawData['id']).update(
                                        l3_status='picked', l3_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy)
                                else:
                                    prodid = l3_production.objects.create(
                                        qid_id=rawData['id'], start_time=timezone.now(), created_by_id=EmpID)
                                    raw_data.objects.filter(id=rawData['id']).update(
                                        l3_status='picked', l3_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy, l3_prod_id=prodid.id)

                                l3dict = json.dumps(
                                    l3input.to_dict(orient='records'))
                                return {'htmlfields':htmlfields, 'l3_count': l3_count, 'result': rawData, 'status': l3dict, 'l1_prod_link': l3link['l1_prod_link'], 'l2_prod_link': l3link['l2_prod_link']}
                            else:
                                l1_l2_accuracy = 'pass'
                                raw_data.objects.filter(id=rawData['id']).update(
                                    l1_l2_accuracy=l1_l2_accuracy)
                                return loop()
                        return None
                    return None

            loop_result = loop()
            if loop_result:
                return render(request, 'pages/l3_production.html', loop_result)
            else:
                queue()
                return render(request, 'pages/l3_production.html', {'l3_count': l3_count, 'result': []})

        except Exception as er:
            print(er)
            # , 'l3count':l3count l3count = raw_data.objects.filter(Q(l3_status='completed', l3_emp_id=EmpID)).values('baseid__batch_name').annotate(l3count=Count('baseid__batch_name')).exclude(status__in=['hold', 'deleted']).order_by('-baseid__batch_name')
            rawData = []
        return render(request, 'pages/l3_production.html', {'l3_count': l3_count, 'result': rawData})


# @custom_token_login_required
@loginrequired
def lfourproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    if request.method == "POST":
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        que1 = request.POST.get('que1', None)
        que1a = request.POST.get('que1a', None)

        que2_ans1 = request.POST.get('que2_ans1', None)
        que2a_ans1 = request.POST.get('que2a_ans1', None)
        que3_ans1 = ','.join(request.POST.getlist('que3_ans1', None))
        que4_ans1 = ','.join(request.POST.getlist('que4_ans1', None))
        que4a_ans1 = request.POST.get('que4a_ans1', None)
        que4b_ans1 = request.POST.get('que4b_ans1', None)
        que4c_ans1 = request.POST.get('que4c_ans1', None)
        que4d_ans1 = request.POST.get('que4d_ans1', None)
        que4e_ans1 = request.POST.get('que4e_ans1', None)
        que4f_ans1 = request.POST.get('que4f_ans1', None)
        que5_ans1 = ','.join(request.POST.getlist('que5_ans1', None))
        que5a_ans1 = request.POST.get('que5a_ans1', None)
        que6_ans1 = request.POST.get('que6_ans1', None)
        que6a_ans1 = request.POST.get('que6a_ans1', None)
        que7_ans1 = request.POST.get('que7_ans1', None)
        que8_ans1 = request.POST.get('que8_ans1', None)
        que8a_ans1 = request.POST.get('que8a_ans1', None)
        que8b_ans1 = request.POST.get('que8b_ans1', None)
        que2_ans2 = request.POST.get('que2_ans2', None)
        que2a_ans2 = request.POST.get('que2a_ans2', None)
        que3_ans2 = ','.join(request.POST.getlist('que3_ans2', None))
        que4_ans2 = ','.join(request.POST.getlist('que4_ans2', None))
        que4a_ans2 = request.POST.get('que4a_ans2', None)
        que4b_ans2 = request.POST.get('que4b_ans2', None)
        que4c_ans2 = request.POST.get('que4c_ans2', None)
        que4d_ans2 = request.POST.get('que4d_ans2', None)
        que4e_ans2 = request.POST.get('que4e_ans2', None)
        que4f_ans2 = request.POST.get('que4f_ans2', None)
        que5_ans2 = ','.join(request.POST.getlist('que5_ans2', None))
        que5a_ans2 = request.POST.get('que5a_ans2', None)
        que6_ans2 = request.POST.get('que6_ans2', None)
        que6a_ans2 = request.POST.get('que6a_ans2', None)
        que7_ans2 = request.POST.get('que7_ans2', None)
        que8_ans2 = request.POST.get('que8_ans2', None)
        que8a_ans2 = request.POST.get('que8a_ans2', None)
        que8b_ans2 = request.POST.get('que8b_ans2', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    l4prod_values = l4prod.values_list('id', flat=True)

                    responseData = {'status': 'success',
                                    'result': "Production Completed"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l4_prod_id=l4prod_values,
                                                               l4_status='completed', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    l4prod_values = l4prod.values_list('id', flat=True)

                    redirect_url = '/dash/'
                    responseData = {'status': 'success', 'redirect_url': redirect_url,
                                    'result': "Production Completed"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l4_prod_id=l4prod_values,
                                                               l4_status='completed', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(),
                                  que1=que1,
                                  que1a=que1a,
                                  que2_ans1=que2_ans1,
                                  que2a_ans1=que2a_ans1,
                                  que3_ans1=que3_ans1,
                                  que4_ans1=que4_ans1,
                                  que4a_ans1=que4a_ans1,
                                  que4b_ans1=que4b_ans1,
                                  que4c_ans1=que4c_ans1,
                                  que4d_ans1=que4d_ans1,
                                  que4e_ans1=que4e_ans1,
                                  que4f_ans1=que4f_ans1,
                                  que5_ans1=que5_ans1,
                                  que5a_ans1=que5a_ans1,
                                  que6_ans1=que6_ans1,
                                  que6a_ans1=que6a_ans1,
                                  que7_ans1=que7_ans1,
                                  que8_ans1=que8_ans1,
                                  que8a_ans1=que8a_ans1,
                                  que8b_ans1=que8b_ans1,
                                  que2_ans2=que2_ans2,
                                  que2a_ans2=que2a_ans2,
                                  que3_ans2=que3_ans2,
                                  que4_ans2=que4_ans2,
                                  que4a_ans2=que4a_ans2,
                                  que4b_ans2=que4b_ans2,
                                  que4c_ans2=que4c_ans2,
                                  que4d_ans2=que4d_ans2,
                                  que4e_ans2=que4e_ans2,
                                  que4f_ans2=que4f_ans2,
                                  que5_ans2=que5_ans2,
                                  que5a_ans2=que5a_ans2,
                                  que6_ans2=que6_ans2,
                                  que6a_ans2=que6a_ans2,
                                  que7_ans2=que7_ans2,
                                  que8_ans2=que8_ans2,
                                  que8a_ans2=que8a_ans2,
                                  que8b_ans2=que8b_ans2,
                                  is_production_status='Completed', created_by_id=EmpID)

                    responseData = {'status': 'success',
                                    'result': "Production  Hold"}
                    if eid:
                        raw_data.objects.filter(id=eid).update(l4_prod_id=l4prod_values,
                                                               l4_status='hold', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

    else:
        filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
            status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
        l4_count = raw_data.objects.filter(Q(l4_prod_id__end_time__date=timezone.now().date()), Q(
            l4_status='completed') & Q(l4_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l4_count is not None:
            l4_count = l4_count
        else:
            l4_count = 0

        BaseID = request.GET.get('baseid', None)
        if BaseID != None and BaseID != "":
            request.session['BaseID'] = BaseID
        else:
            BaseID = request.session.get('BaseID')

        batcQueue = raw_data.objects.filter(baseid_id=BaseID).exists()
        if batcQueue:
            try:
                query = Q()
                if language:
                    query = Q(baseid_id__language__in=language)

                filecount = raw_data.objects.filter(l1_l2_accuracy='pass', baseid_id=BaseID).exclude(status__in=['hold', 'deleted']).aggregate(comp_count=Count(
                    'l4_status', Q(l4_status='completed')), cur_count=Count('l4_status', Q(l4_status='not_picked')), total_count=Count('l1_l2_accuracy', Q(l1_l2_accuracy='pass')))
                getdata_for_target = QA_queue.objects.filter(queue_batch_id=BaseID).aggregate(
                    queue=Sum(Cast('queue_percentage', models.IntegerField())))
                target_percentage = int(getdata_for_target['queue'])

                queue = int(target_percentage / 100 *
                            int(filecount['total_count']))

                print("Total :", int(filecount['total_count']), "Queue :", queue,
                      "Competed :", filecount['comp_count'], "Target % :", getdata_for_target)
                # print(filecount['comp_count'] <= queue)
                if filecount['comp_count'] < queue and int(filecount['cur_count']) >= 0 and int(queue) >= 0:
                    with transaction.atomic():
                        rawData = raw_data.objects.select_for_update(skip_locked=True).filter(Q(l1_status='completed') & Q(l2_status='completed') & query, (Q(l4_status='not_picked') & Q(l4_emp_id__isnull=True) | Q(l4_status='picked') & Q(l4_emp_id=EmpID)),
                                                                                              (Q(l1_l2_accuracy__isnull=True) | Q(l1_l2_accuracy='pass')), baseid_id=BaseID).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two').exclude(status__in=['hold', 'deleted']).exclude(l1_l2_accuracy='fail').exclude(l1_emp_id=EmpID).exclude(l2_emp_id=EmpID).order_by('-l4_status').first()

                        if rawData:
                            l4comp = l1_l2Comparison(rawData['id'])
                            if l4comp:
                                l4input = l4comp['result']

                                if 'Not Matched' in l4input['Comparison'].values:
                                    l1_l2_accuracy = 'fail'
                                    raw_data.objects.filter(id=rawData['id']).update(
                                        l1_l2_accuracy=l1_l2_accuracy)
                                    return redirect('/api/v1/productionl4/')
                                else:
                                    l1_l2_accuracy = 'pass'

                                    l4prod = l4_production.objects
                                    if l4prod.filter(qid_id=rawData['id']).exists():
                                        l4_production.objects.filter(qid_id=rawData['id']).update(
                                            start_time=timezone.now())
                                        raw_data.objects.filter(id=rawData['id']).update(
                                            l4_status='picked', l4_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy)
                                    else:
                                        prodid = l4_production.objects.create(
                                            qid_id=rawData['id'], start_time=timezone.now())

                                        raw_data.objects.filter(id=rawData['id']).update(
                                            l4_status='picked', l4_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy, l4_prod_id=prodid.id)
                                    l4dict = json.dumps(
                                        l4input.to_dict(orient='records'))
                                    return render(request, 'pages/l4_production.html', {'htmlfields':htmlfields, 'l4_count': l4_count, 'result': rawData, 'status': l4dict, 'l1_prod_link': l4comp['l1_prod_link'], 'l2_prod_link': l4comp['l2_prod_link']})
                return render(request, 'pages/l4_production.html', {'filenames': filenames, 'l4_count': l4_count, 'result': []})
            except Exception as er:
                print(er)
                # , 'l4count':l4count l4count = raw_data.objects.filter(Q(l4_status='completed', l4_emp_id=EmpID)).values('baseid__batch_name').annotate(l4count=Count('baseid__batch_name')).exclude(status__in=['hold', 'deleted']).order_by('-baseid__batch_name')
        rawData = []
        return render(request, 'pages/l4_production.html', {'filenames': filenames, 'l4_count': l4_count, 'result': rawData})


# @custom_token_login_required
@loginrequired
def outputDownload(request):
    # EmpLoc = request.session.get('empLoc') Location/area wise filter
    # ,Q(created_by_id__location = EmpLoc)
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')

    if request.method == 'POST':
        key = request.POST.get('key')

        filename = request.POST.get('filename')
        fromdate = request.POST.get('fromDate')
        todate = request.POST.get('toDate')
        reporttype = request.POST.get('reporttype')
        language = request.POST.get('language')
        # location = request.POST.get('location')

        if language == 'All':
            query = Q()
        else:
            query = Q(baseid_id__language=language)

        if filename == 'All':
            query1 = Q()
        else:
            query1 = Q(baseid_id__filename=filename)

        try:
            if fromdate and todate:
                conditions1 = Q(l1_prod_id__end_time__range=(fromdate, todate))
                conditions2 = Q(l2_prod_id__end_time__range=(fromdate, todate))
                conditions3 = Q(l3_prod_id__end_time__range=(fromdate, todate))
                conditions4 = Q(l4_prod_id__end_time__range=(fromdate, todate))
            else:
                conditions1 = Q()
                conditions2 = Q()
                conditions3 = Q()
                conditions4 = Q()

            dL1raw = raw_data.objects.filter(conditions1 & query & query1, l1_status='completed').annotate(timtakn=Sum(F('l1_prod_id__end_time') - F('l1_prod_id__start_time'))).values('id', 'l1_prod_id__end_time__date', 'id_value', 'l1_prod_id', 'l1_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l1_prod_id__start_time', 'l1_prod_id__end_time',
                                                                                                                                                                                        'l1_emp_id__employeeName', 'l1_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l1_status', 'timtakn',
                                                                                                                                                                                        'l1_prod_id__que1',
                                                                                                                                                                                        'l1_prod_id__que1a',

                                                                                                                                                                                        'l1_prod_id__que2_ans1',
                                                                                                                                                                                        'l1_prod_id__que2a_ans1',
                                                                                                                                                                                        'l1_prod_id__que3_ans1',
                                                                                                                                                                                        'l1_prod_id__que4_ans1',
                                                                                                                                                                                        'l1_prod_id__que4a_ans1',
                                                                                                                                                                                        'l1_prod_id__que4b_ans1',
                                                                                                                                                                                        'l1_prod_id__que4c_ans1',
                                                                                                                                                                                        'l1_prod_id__que4d_ans1',
                                                                                                                                                                                        'l1_prod_id__que4e_ans1',
                                                                                                                                                                                        'l1_prod_id__que4f_ans1',
                                                                                                                                                                                        'l1_prod_id__que5_ans1',
                                                                                                                                                                                        'l1_prod_id__que5a_ans1',
                                                                                                                                                                                        'l1_prod_id__que6_ans1',
                                                                                                                                                                                        'l1_prod_id__que6a_ans1',
                                                                                                                                                                                        'l1_prod_id__que7_ans1',
                                                                                                                                                                                        'l1_prod_id__que8_ans1',
                                                                                                                                                                                        'l1_prod_id__que8a_ans1',
                                                                                                                                                                                        'l1_prod_id__que8b_ans1',

                                                                                                                                                                                        'l1_prod_id__que2_ans2',
                                                                                                                                                                                        'l1_prod_id__que2a_ans2',
                                                                                                                                                                                        'l1_prod_id__que3_ans2',
                                                                                                                                                                                        'l1_prod_id__que4_ans2',
                                                                                                                                                                                        'l1_prod_id__que4a_ans2',
                                                                                                                                                                                        'l1_prod_id__que4b_ans2',
                                                                                                                                                                                        'l1_prod_id__que4c_ans2',
                                                                                                                                                                                        'l1_prod_id__que4d_ans2',
                                                                                                                                                                                        'l1_prod_id__que4e_ans2',
                                                                                                                                                                                        'l1_prod_id__que4f_ans2',
                                                                                                                                                                                        'l1_prod_id__que5_ans2',
                                                                                                                                                                                        'l1_prod_id__que5a_ans2',
                                                                                                                                                                                        'l1_prod_id__que6_ans2',
                                                                                                                                                                                        'l1_prod_id__que6a_ans2',
                                                                                                                                                                                        'l1_prod_id__que7_ans2',
                                                                                                                                                                                        'l1_prod_id__que8_ans2',
                                                                                                                                                                                        'l1_prod_id__que8a_ans2',
                                                                                                                                                                                        'l1_prod_id__que8b_ans2',
                                                                                                                                                                                        'l1_prod_id__annotation_comment').exclude(status__in=['hold', 'deleted'])
            l1prodid = dL1raw.values_list('l1_prod_id', flat=True)

            dL2raw = raw_data.objects.filter(conditions2 & query & query1, l2_status='completed').annotate(timtakn=Sum(F('l2_prod_id__end_time') - F('l2_prod_id__start_time'))).values('id', 'l2_prod_id__end_time__date', 'id_value', 'l2_prod_id', 'l2_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l2_prod_id__start_time', 'l2_prod_id__end_time',
                                                                                                                                                                                        'l2_emp_id__employeeName', 'l2_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l2_status', 'timtakn',
                                                                                                                                                                                        'l2_prod_id__que1',
                                                                                                                                                                                        'l2_prod_id__que1a',

                                                                                                                                                                                        'l2_prod_id__que2_ans1',
                                                                                                                                                                                        'l2_prod_id__que2a_ans1',
                                                                                                                                                                                        'l2_prod_id__que3_ans1',
                                                                                                                                                                                        'l2_prod_id__que4_ans1',
                                                                                                                                                                                        'l2_prod_id__que4a_ans1',
                                                                                                                                                                                        'l2_prod_id__que4b_ans1',
                                                                                                                                                                                        'l2_prod_id__que4c_ans1',
                                                                                                                                                                                        'l2_prod_id__que4d_ans1',
                                                                                                                                                                                        'l2_prod_id__que4e_ans1',
                                                                                                                                                                                        'l2_prod_id__que4f_ans1',
                                                                                                                                                                                        'l2_prod_id__que5_ans1',
                                                                                                                                                                                        'l2_prod_id__que5a_ans1',
                                                                                                                                                                                        'l2_prod_id__que6_ans1',
                                                                                                                                                                                        'l2_prod_id__que6a_ans1',
                                                                                                                                                                                        'l2_prod_id__que7_ans1',
                                                                                                                                                                                        'l2_prod_id__que8_ans1',
                                                                                                                                                                                        'l2_prod_id__que8a_ans1',
                                                                                                                                                                                        'l2_prod_id__que8b_ans1',

                                                                                                                                                                                        'l2_prod_id__que2_ans2',
                                                                                                                                                                                        'l2_prod_id__que2a_ans2',
                                                                                                                                                                                        'l2_prod_id__que3_ans2',
                                                                                                                                                                                        'l2_prod_id__que4_ans2',
                                                                                                                                                                                        'l2_prod_id__que4a_ans2',
                                                                                                                                                                                        'l2_prod_id__que4b_ans2',
                                                                                                                                                                                        'l2_prod_id__que4c_ans2',
                                                                                                                                                                                        'l2_prod_id__que4d_ans2',
                                                                                                                                                                                        'l2_prod_id__que4e_ans2',
                                                                                                                                                                                        'l2_prod_id__que4f_ans2',
                                                                                                                                                                                        'l2_prod_id__que5_ans2',
                                                                                                                                                                                        'l2_prod_id__que5a_ans2',
                                                                                                                                                                                        'l2_prod_id__que6_ans2',
                                                                                                                                                                                        'l2_prod_id__que6a_ans2',
                                                                                                                                                                                        'l2_prod_id__que7_ans2',
                                                                                                                                                                                        'l2_prod_id__que8_ans2',
                                                                                                                                                                                        'l2_prod_id__que8a_ans2',
                                                                                                                                                                                        'l2_prod_id__que8b_ans2',
                                                                                                                                                                                        'l2_prod_id__annotation_comment').exclude(status__in=['hold', 'deleted'])
            l2prodid = dL2raw.values_list('l2_prod_id', flat=True)

            dL3raw = raw_data.objects.filter(conditions3 & query & query1, l3_status='completed').annotate(timtakn=Sum(F('l3_prod_id__end_time') - F('l3_prod_id__start_time'))).values('id', 'l3_prod_id__end_time__date', 'id_value', 'l3_prod_id', 'l3_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l3_prod_id__start_time', 'l3_prod_id__end_time',
                                                                                                                                                                                        'l3_emp_id__employeeName', 'l3_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l3_status', 'timtakn',
                                                                                                                                                                                        'l3_prod_id__que1',
                                                                                                                                                                                        'l3_prod_id__que1a',

                                                                                                                                                                                        'l3_prod_id__que2_ans1',
                                                                                                                                                                                        'l3_prod_id__que2a_ans1',
                                                                                                                                                                                        'l3_prod_id__que3_ans1',
                                                                                                                                                                                        'l3_prod_id__que4_ans1',
                                                                                                                                                                                        'l3_prod_id__que4a_ans1',
                                                                                                                                                                                        'l3_prod_id__que4b_ans1',
                                                                                                                                                                                        'l3_prod_id__que4c_ans1',
                                                                                                                                                                                        'l3_prod_id__que4d_ans1',
                                                                                                                                                                                        'l3_prod_id__que4e_ans1',
                                                                                                                                                                                        'l3_prod_id__que4f_ans1',
                                                                                                                                                                                        'l3_prod_id__que5_ans1',
                                                                                                                                                                                        'l3_prod_id__que5a_ans1',
                                                                                                                                                                                        'l3_prod_id__que6_ans1',
                                                                                                                                                                                        'l3_prod_id__que6a_ans1',
                                                                                                                                                                                        'l3_prod_id__que7_ans1',
                                                                                                                                                                                        'l3_prod_id__que8_ans1',
                                                                                                                                                                                        'l3_prod_id__que8a_ans1',
                                                                                                                                                                                        'l3_prod_id__que8b_ans1',

                                                                                                                                                                                        'l3_prod_id__que2_ans2',
                                                                                                                                                                                        'l3_prod_id__que2a_ans2',
                                                                                                                                                                                        'l3_prod_id__que3_ans2',
                                                                                                                                                                                        'l3_prod_id__que4_ans2',
                                                                                                                                                                                        'l3_prod_id__que4a_ans2',
                                                                                                                                                                                        'l3_prod_id__que4b_ans2',
                                                                                                                                                                                        'l3_prod_id__que4c_ans2',
                                                                                                                                                                                        'l3_prod_id__que4d_ans2',
                                                                                                                                                                                        'l3_prod_id__que4e_ans2',
                                                                                                                                                                                        'l3_prod_id__que4f_ans2',
                                                                                                                                                                                        'l3_prod_id__que5_ans2',
                                                                                                                                                                                        'l3_prod_id__que5a_ans2',
                                                                                                                                                                                        'l3_prod_id__que6_ans2',
                                                                                                                                                                                        'l3_prod_id__que6a_ans2',
                                                                                                                                                                                        'l3_prod_id__que7_ans2',
                                                                                                                                                                                        'l3_prod_id__que8_ans2',
                                                                                                                                                                                        'l3_prod_id__que8a_ans2',
                                                                                                                                                                                        'l3_prod_id__que8b_ans2',
                                                                                                                                                                                        'l3_prod_id__annotation_comment').exclude(status__in=['hold', 'deleted'])
            l3prodid = dL3raw.values_list('l3_prod_id', flat=True)

            dL4raw = raw_data.objects.filter(conditions4 & query & query1, l1_l2_accuracy='pass').annotate(timtakn=Sum(F('l4_prod_id__end_time') - F('l4_prod_id__start_time'))).values('id', 'l4_prod_id__end_time__date', 'id_value', 'l4_prod_id', 'l4_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l4_prod_id__start_time', 'l4_prod_id__end_time',
                                                                                                                                                                                        'l4_emp_id__employeeName', 'l4_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l4_status', 'timtakn',
                                                                                                                                                                                        'l4_prod_id__que1',
                                                                                                                                                                                        'l4_prod_id__que1a',

                                                                                                                                                                                        'l4_prod_id__que2_ans1',
                                                                                                                                                                                        'l4_prod_id__que2a_ans1',
                                                                                                                                                                                        'l4_prod_id__que3_ans1',
                                                                                                                                                                                        'l4_prod_id__que4_ans1',
                                                                                                                                                                                        'l4_prod_id__que4a_ans1',
                                                                                                                                                                                        'l4_prod_id__que4b_ans1',
                                                                                                                                                                                        'l4_prod_id__que4c_ans1',
                                                                                                                                                                                        'l4_prod_id__que4d_ans1',
                                                                                                                                                                                        'l4_prod_id__que4e_ans1',
                                                                                                                                                                                        'l4_prod_id__que4f_ans1',
                                                                                                                                                                                        'l4_prod_id__que5_ans1',
                                                                                                                                                                                        'l4_prod_id__que5a_ans1',
                                                                                                                                                                                        'l4_prod_id__que6_ans1',
                                                                                                                                                                                        'l4_prod_id__que6a_ans1',
                                                                                                                                                                                        'l4_prod_id__que7_ans1',
                                                                                                                                                                                        'l4_prod_id__que8_ans1',
                                                                                                                                                                                        'l4_prod_id__que8a_ans1',
                                                                                                                                                                                        'l4_prod_id__que8b_ans1',

                                                                                                                                                                                        'l4_prod_id__que2_ans2',
                                                                                                                                                                                        'l4_prod_id__que2a_ans2',
                                                                                                                                                                                        'l4_prod_id__que3_ans2',
                                                                                                                                                                                        'l4_prod_id__que4_ans2',
                                                                                                                                                                                        'l4_prod_id__que4a_ans2',
                                                                                                                                                                                        'l4_prod_id__que4b_ans2',
                                                                                                                                                                                        'l4_prod_id__que4c_ans2',
                                                                                                                                                                                        'l4_prod_id__que4d_ans2',
                                                                                                                                                                                        'l4_prod_id__que4e_ans2',
                                                                                                                                                                                        'l4_prod_id__que4f_ans2',
                                                                                                                                                                                        'l4_prod_id__que5_ans2',
                                                                                                                                                                                        'l4_prod_id__que5a_ans2',
                                                                                                                                                                                        'l4_prod_id__que6_ans2',
                                                                                                                                                                                        'l4_prod_id__que6a_ans2',
                                                                                                                                                                                        'l4_prod_id__que7_ans2',
                                                                                                                                                                                        'l4_prod_id__que8_ans2',
                                                                                                                                                                                        'l4_prod_id__que8a_ans2',
                                                                                                                                                                                        'l4_prod_id__que8b_ans2',
                                                                                                                                                                                        'l4_prod_id__annotation_comment'
                                                                                                                                                                                        ).exclude(status__in=['hold', 'deleted'])
            l4prodid = dL4raw.values_list('l4_prod_id', flat=True)

            if key == 'Download':
                response = HttpResponse(
                    content_type='text/csv;charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + \
                    reporttype+"|"+str(timezone.now().date())+'".csv"'
                writer = csv.writer(response)

                if reporttype in ['DA1', 'DA2', 'QC/QA']:
                    writer.writerow(title)

                if reporttype == 'DA1':
                    for v in dL1raw:
                        records = [
                            'DA1',
                            v['baseid_id__batch_name'],
                            v['baseid_id__filename'],
                            v['id_value'],
                            v['asin'],
                            v['product_url'],
                            v['title'],
                            v['evidence'],
                            v['imagepath'],
                            v['question'],
                            v['answer_one'],
                            v['answer_two'],

                            v['l1_prod_id__que1'],
                            v['l1_prod_id__que1a'],

                            v['l1_prod_id__que2_ans1'],
                            v['l1_prod_id__que2a_ans1'],
                            v['l1_prod_id__que3_ans1'],
                            v['l1_prod_id__que4_ans1'],
                            v['l1_prod_id__que4a_ans1'],
                            v['l1_prod_id__que4b_ans1'],
                            v['l1_prod_id__que4c_ans1'],
                            v['l1_prod_id__que4d_ans1'],
                            v['l1_prod_id__que4e_ans1'],
                            v['l1_prod_id__que4f_ans1'],
                            v['l1_prod_id__que5_ans1'],
                            v['l1_prod_id__que5a_ans1'],
                            v['l1_prod_id__que6_ans1'],
                            v['l1_prod_id__que6a_ans1'],
                            v['l1_prod_id__que7_ans1'],
                            v['l1_prod_id__que8_ans1'],
                            v['l1_prod_id__que8a_ans1'],
                            v['l1_prod_id__que8b_ans1'],

                            v['l1_prod_id__que2_ans2'],
                            v['l1_prod_id__que2a_ans2'],
                            v['l1_prod_id__que3_ans2'],
                            v['l1_prod_id__que4_ans2'],
                            v['l1_prod_id__que4a_ans2'],
                            v['l1_prod_id__que4b_ans2'],
                            v['l1_prod_id__que4c_ans2'],
                            v['l1_prod_id__que4d_ans2'],
                            v['l1_prod_id__que4e_ans2'],
                            v['l1_prod_id__que4f_ans2'],
                            v['l1_prod_id__que5_ans2'],
                            v['l1_prod_id__que5a_ans2'],
                            v['l1_prod_id__que6_ans2'],
                            v['l1_prod_id__que6a_ans2'],
                            v['l1_prod_id__que7_ans2'],
                            v['l1_prod_id__que8_ans2'],
                            v['l1_prod_id__que8a_ans2'],
                            v['l1_prod_id__que8b_ans2'],

                            v['l1_emp_id__employeeID'],
                            v['l1_emp_id__employeeName'],
                            v['l1_emp_id__location'],
                            v['l1_prod_id__start_time'],
                            v['l1_prod_id__end_time'],
                            v['timtakn'],
                            v['l1_prod_id__end_time__date']
                        ]
                        writer.writerow(records)

                if reporttype == 'DA2':
                    for v in dL2raw:
                        records = [
                            'DA2',
                            v['baseid_id__batch_name'],
                            v['baseid_id__filename'],
                            v['id_value'],
                            v['asin'],
                            v['product_url'],
                            v['title'],
                            v['evidence'],
                            v['imagepath'],
                            v['question'],
                            v['answer_one'],
                            v['answer_two'],

                            v['l2_prod_id__que1'],
                            v['l2_prod_id__que1a'],

                            v['l2_prod_id__que2_ans1'],
                            v['l2_prod_id__que2a_ans1'],
                            v['l2_prod_id__que3_ans1'],
                            v['l2_prod_id__que4_ans1'],
                            v['l2_prod_id__que4a_ans1'],
                            v['l2_prod_id__que4b_ans1'],
                            v['l2_prod_id__que4c_ans1'],
                            v['l2_prod_id__que4d_ans1'],
                            v['l2_prod_id__que4e_ans1'],
                            v['l2_prod_id__que4f_ans1'],
                            v['l2_prod_id__que5_ans1'],
                            v['l2_prod_id__que5a_ans1'],
                            v['l2_prod_id__que6_ans1'],
                            v['l2_prod_id__que6a_ans1'],
                            v['l2_prod_id__que7_ans1'],
                            v['l2_prod_id__que8_ans1'],
                            v['l2_prod_id__que8a_ans1'],
                            v['l2_prod_id__que8b_ans1'],

                            v['l2_prod_id__que2_ans2'],
                            v['l2_prod_id__que2a_ans2'],
                            v['l2_prod_id__que3_ans2'],
                            v['l2_prod_id__que4_ans2'],
                            v['l2_prod_id__que4a_ans2'],
                            v['l2_prod_id__que4b_ans2'],
                            v['l2_prod_id__que4c_ans2'],
                            v['l2_prod_id__que4d_ans2'],
                            v['l2_prod_id__que4e_ans2'],
                            v['l2_prod_id__que4f_ans2'],
                            v['l2_prod_id__que5_ans2'],
                            v['l2_prod_id__que5a_ans2'],
                            v['l2_prod_id__que6_ans2'],
                            v['l2_prod_id__que6a_ans2'],
                            v['l2_prod_id__que7_ans2'],
                            v['l2_prod_id__que8_ans2'],
                            v['l2_prod_id__que8a_ans2'],
                            v['l2_prod_id__que8b_ans2'],

                            v['l2_emp_id__employeeID'],
                            v['l2_emp_id__employeeName'],
                            v['l2_emp_id__location'],
                            v['l2_prod_id__start_time'],
                            v['l2_prod_id__end_time'],
                            v['timtakn'],
                            v['l2_prod_id__end_time__date']
                        ]
                        writer.writerow(records)

                if reporttype == 'QC/QA':
                    for v in dL3raw:
                        records = [
                            'QC',
                            v['baseid_id__batch_name'],
                            v['baseid_id__filename'],
                            v['id_value'],
                            v['asin'],
                            v['product_url'],
                            v['title'],
                            v['evidence'],
                            v['imagepath'],
                            v['question'],
                            v['answer_one'],
                            v['answer_two'],

                            v['l3_prod_id__que1'],
                            v['l3_prod_id__que1a'],

                            v['l3_prod_id__que2_ans1'],
                            v['l3_prod_id__que2a_ans1'],
                            v['l3_prod_id__que3_ans1'],
                            v['l3_prod_id__que4_ans1'],
                            v['l3_prod_id__que4a_ans1'],
                            v['l3_prod_id__que4b_ans1'],
                            v['l3_prod_id__que4c_ans1'],
                            v['l3_prod_id__que4d_ans1'],
                            v['l3_prod_id__que4e_ans1'],
                            v['l3_prod_id__que4f_ans1'],
                            v['l3_prod_id__que5_ans1'],
                            v['l3_prod_id__que5a_ans1'],
                            v['l3_prod_id__que6_ans1'],
                            v['l3_prod_id__que6a_ans1'],
                            v['l3_prod_id__que7_ans1'],
                            v['l3_prod_id__que8_ans1'],
                            v['l3_prod_id__que8a_ans1'],
                            v['l3_prod_id__que8b_ans1'],

                            v['l3_prod_id__que2_ans2'],
                            v['l3_prod_id__que2a_ans2'],
                            v['l3_prod_id__que3_ans2'],
                            v['l3_prod_id__que4_ans2'],
                            v['l3_prod_id__que4a_ans2'],
                            v['l3_prod_id__que4b_ans2'],
                            v['l3_prod_id__que4c_ans2'],
                            v['l3_prod_id__que4d_ans2'],
                            v['l3_prod_id__que4e_ans2'],
                            v['l3_prod_id__que4f_ans2'],
                            v['l3_prod_id__que5_ans2'],
                            v['l3_prod_id__que5a_ans2'],
                            v['l3_prod_id__que6_ans2'],
                            v['l3_prod_id__que6a_ans2'],
                            v['l3_prod_id__que7_ans2'],
                            v['l3_prod_id__que8_ans2'],
                            v['l3_prod_id__que8a_ans2'],
                            v['l3_prod_id__que8b_ans2'],

                            v['l3_emp_id__employeeID'],
                            v['l3_emp_id__employeeName'],
                            v['l3_emp_id__location'],
                            v['l3_prod_id__start_time'],
                            v['l3_prod_id__end_time'],
                            v['timtakn'],
                            v['l3_prod_id__end_time__date']
                        ]
                        writer.writerow(records)
                    for mv in dL1raw:
                        for v in dL4raw:
                            records = []
                            if mv['id_value'] == v['id_value'] and v['l4_emp_id__employeeID'] != None and v['l4_prod_id__start_time'] != None and v['l4_prod_id__end_time'] != None:
                                records.extend([
                                    'QA',
                                    v['baseid_id__batch_name'],
                                    v['baseid_id__filename'],
                                    v['id_value'],
                                    v['asin'],
                                    v['product_url'],
                                    v['title'],
                                    v['evidence'],
                                    v['imagepath'],
                                    v['question'],
                                    v['answer_one'],
                                    v['answer_two'],

                                    v['l4_prod_id__que1'],
                                    v['l4_prod_id__que1a'],

                                    v['l4_prod_id__que2_ans1'],
                                    v['l4_prod_id__que2a_ans1'],
                                    v['l4_prod_id__que3_ans1'],
                                    v['l4_prod_id__que4_ans1'],
                                    v['l4_prod_id__que4a_ans1'],
                                    v['l4_prod_id__que4b_ans1'],
                                    v['l4_prod_id__que4c_ans1'],
                                    v['l4_prod_id__que4d_ans1'],
                                    v['l4_prod_id__que4e_ans1'],
                                    v['l4_prod_id__que4f_ans1'],
                                    v['l4_prod_id__que5_ans1'],
                                    v['l4_prod_id__que5a_ans1'],
                                    v['l4_prod_id__que6_ans1'],
                                    v['l4_prod_id__que6a_ans1'],
                                    v['l4_prod_id__que7_ans1'],
                                    v['l4_prod_id__que8_ans1'],
                                    v['l4_prod_id__que8a_ans1'],
                                    v['l4_prod_id__que8b_ans1'],

                                    v['l4_prod_id__que2_ans2'],
                                    v['l4_prod_id__que2a_ans2'],
                                    v['l4_prod_id__que3_ans2'],
                                    v['l4_prod_id__que4_ans2'],
                                    v['l4_prod_id__que4a_ans2'],
                                    v['l4_prod_id__que4b_ans2'],
                                    v['l4_prod_id__que4c_ans2'],
                                    v['l4_prod_id__que4d_ans2'],
                                    v['l4_prod_id__que4e_ans2'],
                                    v['l4_prod_id__que4f_ans2'],
                                    v['l4_prod_id__que5_ans2'],
                                    v['l4_prod_id__que5a_ans2'],
                                    v['l4_prod_id__que6_ans2'],
                                    v['l4_prod_id__que6a_ans2'],
                                    v['l4_prod_id__que7_ans2'],
                                    v['l4_prod_id__que8_ans2'],
                                    v['l4_prod_id__que8a_ans2'],
                                    v['l4_prod_id__que8b_ans2'],

                                    v['l4_emp_id__employeeID'],
                                    v['l4_emp_id__employeeName'],
                                    v['l4_emp_id__location'],
                                    v['l4_prod_id__start_time'],
                                    v['l4_prod_id__end_time'],
                                    v['timtakn'],
                                    v['l4_prod_id__end_time__date']
                                ])
                            elif mv['id_value'] == v['id_value']:
                                records.extend([
                                    'QA',
                                    mv['baseid_id__batch_name'],
                                    mv['baseid_id__filename'],
                                    mv['id_value'],
                                    mv['asin'],
                                    mv['product_url'],
                                    mv['title'],
                                    mv['evidence'],
                                    mv['imagepath'],
                                    mv['question'],
                                    mv['answer_one'],
                                    mv['answer_two'],

                                    mv['l1_prod_id__que1'],
                                    mv['l1_prod_id__que1a'],

                                    mv['l1_prod_id__que2_ans1'],
                                    mv['l1_prod_id__que2a_ans1'],
                                    mv['l1_prod_id__que3_ans1'],
                                    mv['l1_prod_id__que4_ans1'],
                                    mv['l1_prod_id__que4a_ans1'],
                                    mv['l1_prod_id__que4b_ans1'],
                                    mv['l1_prod_id__que4c_ans1'],
                                    mv['l1_prod_id__que4d_ans1'],
                                    mv['l1_prod_id__que4e_ans1'],
                                    mv['l1_prod_id__que4f_ans1'],
                                    mv['l1_prod_id__que5_ans1'],
                                    mv['l1_prod_id__que5a_ans1'],
                                    mv['l1_prod_id__que6_ans1'],
                                    mv['l1_prod_id__que6a_ans1'],
                                    mv['l1_prod_id__que7_ans1'],
                                    mv['l1_prod_id__que8_ans1'],
                                    mv['l1_prod_id__que8a_ans1'],
                                    mv['l1_prod_id__que8b_ans1'],

                                    mv['l1_prod_id__que2_ans2'],
                                    mv['l1_prod_id__que2a_ans2'],
                                    mv['l1_prod_id__que3_ans2'],
                                    mv['l1_prod_id__que4_ans2'],
                                    mv['l1_prod_id__que4a_ans2'],
                                    mv['l1_prod_id__que4b_ans2'],
                                    mv['l1_prod_id__que4c_ans2'],
                                    mv['l1_prod_id__que4d_ans2'],
                                    mv['l1_prod_id__que4e_ans2'],
                                    mv['l1_prod_id__que4f_ans2'],
                                    mv['l1_prod_id__que5_ans2'],
                                    mv['l1_prod_id__que5a_ans2'],
                                    mv['l1_prod_id__que6_ans2'],
                                    mv['l1_prod_id__que6a_ans2'],
                                    mv['l1_prod_id__que7_ans2'],
                                    mv['l1_prod_id__que8_ans2'],
                                    mv['l1_prod_id__que8a_ans2'],
                                    mv['l1_prod_id__que8b_ans2'],

                                    mv['l1_emp_id__employeeID'],
                                    mv['l1_emp_id__employeeName'],
                                    mv['l1_emp_id__location'],
                                    mv['l1_prod_id__start_time'],
                                    mv['l1_prod_id__end_time'],
                                    mv['timtakn'],
                                    mv['l1_prod_id__end_time__date']
                                ])
                            if records and len(records) != 0:
                                writer.writerow(records)

                return response
        except Exception as er:
            print(er)
        return render(request, 'pages/outputDownload.html', {'langs': langs, 'filenames': filenames, 'dL1raw': dL1raw, 'dL2raw': dL2raw, 'dL3raw': dL3raw, 'dL4raw': dL4raw, 'fromdate': fromdate, 'toDate': todate, 'language': language, 'filename': filename})
    else:
        return render(request, 'pages/outputDownload.html', {'filenames': filenames, 'langs': langs})

# @custom_token_login_required


@loginrequired
def ConsolidateOutput(request):
    filename = request.POST.get('filename')
    fromdate = request.POST.get('fromDate')
    todate = request.POST.get('toDate')
    language = request.POST.get('language')
    key = request.POST.get('key')

    if filename == 'All':
        query1 = Q()
    else:
        query1 = Q(baseid_id__filename=filename)

    if language == 'All':
        query = Q()
    else:
        query = Q(baseid_id__language=language)

    if fromdate and todate:
        conditions1 = Q(l1_prod_id__end_time__range=(fromdate, todate))
        conditions2 = Q(l2_prod_id__end_time__range=(fromdate, todate))
        conditions3 = Q(l3_prod_id__end_time__range=(fromdate, todate))
        conditions4 = Q(l4_prod_id__end_time__range=(fromdate, todate))
    else:
        conditions1 = Q()
        conditions2 = Q()
        conditions3 = Q()
        conditions4 = Q()
    try:
        status = Q()
        status &= Q(l1_status="completed")
        status &= Q(l2_status="completed")
        status |= Q(l3_status="completed")
        status |= Q(l1_l2_accuracy="pass")

        rawtable = raw_data.objects
        cons = rawtable.filter(conditions1 | conditions2 | conditions3 | conditions4 & status, query, query1).values(
            'id_value',
            'baseid_id__batch_name',
            'baseid_id__filename',
            'question',
            'asin',
            'product_url',
            'imagepath',
            'evidence',
            'answer_one',
            'answer_two',
            *l1list if rawtable.filter(conditions1 & Q(l1_status='completed') & query & query1) else [],
            *l2list if rawtable.filter(conditions2 & Q(l2_status='completed') & query & query1) else [],
            *l3list if rawtable.filter(conditions3 & Q(l3_status='completed') & query & query1) else [],
            *l4list if rawtable.filter(conditions4 & Q(l1_l2_accuracy="pass") & query & query1) else []
        ).exclude(status__in=['hold', 'deleted'])

        cnstable = pd.DataFrame(cons)
        cnstable.fillna('')

        if not cnstable.empty:
            df_cleaned = cnstable.dropna(axis=1, how='all')
            df_cleaned['DA1-Total Time Taken'] = df_cleaned['l1_prod_id__end_time'] - df_cleaned['l1_prod_id__start_time'] if all(
                col in df_cleaned.columns for col in ['l1_prod_id__start_time', 'l1_prod_id__end_time']) else None
            df_cleaned['DA2-Total Time Taken'] = df_cleaned['l2_prod_id__end_time'] - df_cleaned['l2_prod_id__start_time'] if all(
                col in df_cleaned.columns for col in ['l2_prod_id__start_time', 'l2_prod_id__end_time']) else None
            df_cleaned['QC-Total Time Taken'] = df_cleaned['l3_prod_id__end_time'] - df_cleaned['l3_prod_id__start_time'] if all(
                col in df_cleaned.columns for col in ['l3_prod_id__start_time', 'l3_prod_id__end_time']) else None
            df_cleaned['QA-Total Time Taken'] = df_cleaned['l4_prod_id__end_time'] - df_cleaned['l4_prod_id__start_time'] if all(
                col in df_cleaned.columns for col in ['l4_prod_id__start_time', 'l4_prod_id__end_time']) else None
            # print(df_cleaned['l1_prod_id__start_time'],"==",  df_cleaned['l1_prod_id__end_time'],df_cleaned['l1_prod_id__end_time'] - df_cleaned['l1_prod_id__start_time'])
            mrgd = df_cleaned

        if not cnstable.empty:
            columns_to_drop = [
                col for col in mrgd.columns if col.endswith(('_y', '_x', '_z'))]
            mrgd = mrgd.drop(columns=columns_to_drop)
            # mrgd = mrgd.drop(columns=stat)

            df_cleaned = mrgd.dropna(axis=1, how='all')
            mrgd = df_cleaned.drop_duplicates()

            mrgd.rename(columns=ColumnName, inplace=True)

            existing_columns = [col for col in order if col in mrgd.columns]
            mrgd = mrgd[existing_columns]

            if key == "withoutdata":
                mrgd = mrgd.drop(
                    columns=[col for col in without if col in mrgd.columns])
                lable = str(key)+'"OverallReport"'
            else:
                lable = '"OverallReport"'

            if not mrgd.empty:
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + lable + \
                    str(timezone.now().date())+'".csv"'

                mrgd.to_csv(path_or_buf=response,
                            index=False, encoding='utf-8-sig')

                return response
        else:
            return render(request, 'pages/outputDownload.html', {'Alert': {'type': 'info', 'message': 'No Records'}})
    except Exception as er:
        print(er)
        return render(request, 'pages/outputDownload.html', {'Alert': 'Error'})

# @custom_token_login_required


@loginrequired
def target(request):
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    filenames = raw_data.objects.filter().values('baseid_id', filename=F('baseid__filename')).exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    EmpID = request.session.get('empId')

    qa_queue_view = QA_queue.objects.values('queue_date', 'queue_batch__batch_name', 'queue_batch__filename', 'queue_percentage', 'created_by__employeeID').annotate(
        created_at=TruncMinute('created_at')).exclude(queue_batch__filename__contains='Deleted')

    # Default values for variables
    scope = ""
    targetfor = ""
    file = ""
    date = ""
    queue = ""
    location = []

    if request.method == 'POST':
        scope = request.POST.get('scope')
        targetfor = request.POST.get('targetfor')

        if targetfor == 'Queue':
            file = request.POST.get('batch')
            date = request.POST.get('date')
            queue = request.POST.get('queuev')

            queueObj = QA_queue.objects

            if queueObj.filter(queue_batch_id=file, queue_date=date).exists():
                if date and targetfor and not queue:
                    try:
                        fordate = QA_queue.objects.filter(queue_batch_id=file, queue_date=date).values(
                            'queue_percentage')[0]
                        prcet = fordate['queue_percentage']
                    except:
                        prcet = 0
                    return JsonResponse({'status': 'Success', 'code': 200, 'fordate': prcet})

                queueObj.filter(queue_batch_id=file, queue_date=date).update(queue_batch_id=file, queue_date=date,
                                                                             queue_percentage=queue, created_by_id=EmpID)
            else:
                queueObj.create(queue_batch_id=file, queue_date=date,
                                queue_percentage=queue, created_by_id=EmpID)

            # Redirect to the same view after form submission
            return redirect('/api/v1/target/')

        else:
            scope = request.POST.get('scope')
            location = request.POST.get('location')
            date = request.POST.get('date')
            # print(scope, location, date)

            if 'All' in location:
                query = Q()
            else:
                query = Q(userprofile_id__location=location)

            if 'All' in scope:
                query1 = ~Q(role='Admin') & ~Q(role='Super Admin')
                query3 = Q()
            else:
                query1 = Q(role=scope)
                query3 = Q(targetfor=scope)

            tdatas = Roles.objects.filter(query, query1)
            targetusers = tdatas.values(
                'id',
                'userprofile_id__employeeName',
                'role',
                'userprofile_id__location',
                'userprofile_id__employeeName',
                empid=F('userprofile_id'),
            )

            existing_targetdata = targetsetting.objects.filter(query3, target_date=date,
                                                               targetempid_id__in=tdatas.values_list('userprofile_id')).values('target', 'targetfor', empid=F('targetempid_id'))

            mlist = []
            for d in targetusers:
                for d2 in existing_targetdata:
                    if d['empid'] == d2['empid'] and d['role'] == d2['targetfor']:
                        d.update(d2)
                mlist.append(d)

            datais = bool(targetusers)

            return render(request, 'pages/targetsetpage.html', {
                'datais': datais,
                'targetusers': mlist,
                'locations': locations,
                'filenames': filenames,
                'selected_scope': scope,
                'selected_targetfor': targetfor,
                'selected_file': file,
                'selected_date': date,
                'selected_queuev': queue,
                'selected_location': location
            })

    else:
        return render(request, 'pages/targetsetpage.html', {
            'datais': False,
            'qa_queue_view': qa_queue_view,
            'locations': locations,
            'filenames': filenames,
            'selected_scope': scope,
            'selected_targetfor': targetfor,
            'selected_file': file,
            'selected_date': date,
            'selected_queuev': queue,
            'selected_location': location,
        })

# @custom_token_login_required


@loginrequired
def save_table_data(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        try:
            table_data = json.loads(request.POST.get('tableData'))
            target_date = request.POST.get('target_date')

            for row_data in table_data:
                employee_id = row_data['employeeID']
                targetfor = row_data['role']
                percentage_val = row_data['percentageval']

                if percentage_val != '':
                    if int(percentage_val) != 0 and int(percentage_val) != None:
                        targetsetting.objects.update_or_create(
                            targetempid_id=employee_id,
                            targetfor=targetfor,
                            target_date=target_date,
                            defaults={
                                'target': percentage_val,
                                'created_by_id': EmpID
                            }
                        )
            response_data = {'message': 'Data saved successfully'}
            return JsonResponse(response_data)
        except Exception as er:
            print(er)
            response_data = {'message': f'Error: {str(er)}'}
            return JsonResponse(response_data, status=500)


# @custom_token_login_required
@loginrequired
def batchwisetracking(request):
    queue()
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        location = request.POST.get('location')
        filename = request.POST.get('filename')

        # Convert string dates to datetime objects
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

        # Q(baseid_id__created_at__date__range = (from_date,to_date)) #

        if 'All' == location:
            l1_count_filter = Q(
                l1_status='completed', l1_prod_id__end_time__date__range=(from_date, to_date))
            l2_count_filter = Q(
                l2_status='completed', l2_prod_id__end_time__date__range=(from_date, to_date))
            l3_count_filter = Q(
                l3_status='completed', l3_prod_id__end_time__date__range=(from_date, to_date))
            l4_count_filter = Q(
                l4_status='completed', l4_prod_id__end_time__date__range=(from_date, to_date))
        else:
            l1_count_filter = Q(l1_status='completed', l1_emp__location=location,
                                l1_prod_id__end_time__date__range=(from_date, to_date))
            l2_count_filter = Q(l2_status='completed', l2_emp__location=location,
                                l2_prod_id__end_time__date__range=(from_date, to_date))
            l3_count_filter = Q(l3_status='completed', l3_emp__location=location,
                                l3_prod_id__end_time__date__range=(from_date, to_date))
            l4_count_filter = Q(l4_status='completed', l4_emp__location=location,
                                l4_prod_id__end_time__date__range=(from_date, to_date))

        if 'All' == filename:
            filename_filter = Q()
        else:
            filename_filter = Q(baseid_id__filename=filename)

        trackdata = raw_data.objects.filter(filename_filter).values(
            'baseid_id__created_at__date',
            'baseid_id__batch_name',
            'baseid_id__filename',
            'baseid_id__created_by_id__location'
        ).annotate(
            inputcount=Count('baseid_id__batch_name'),
            da1_count=Count('l1_status', l1_count_filter),
            da2_count=Count('l2_status', l2_count_filter),
            qc_queue=Count('l1_l2_accuracy', Q(l1_l2_accuracy='fail')),
            qc_count=Count('l3_status', l3_count_filter),
            qa_queue=Count('l1_l2_accuracy', Q(l1_l2_accuracy='pass')),
            qa_count=Count('l4_status', l4_count_filter)
        ).exclude(status__in=['hold', 'deleted'])

        return render(request, 'pages/batchwisetracking.html', {'trackdata': trackdata, 'locations': locations, 'filenames': filenames, 'from_date': from_date, 'to_date': to_date, 'location': location, 'filename': filename})
    else:
        return render(request, 'pages/batchwisetracking.html', {'locations': locations, 'filenames': filenames})

# @custom_token_login_required


@loginrequired
def userwisetracking(request):
    queue()
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    scopes = Roles.objects.filter(Q(role__isnull=False) & ~Q(role='')).values(
        'role').exclude(role__in=['Admin', 'Super Admin']).distinct()
    if request.method == 'POST':
        key = request.POST.get('key')
        date = request.POST.get('date')
        location = request.POST.get('location')
        scope = request.POST.get('scope')

        userid = Roles.objects.filter(role=scope).values_list(
            'userprofile_id', flat=True)
        qscopes = Q()
        if 'DA1' in userid:
            qscopes = Q(l1_emp_id__in=userid)
        elif 'DA2' in userid:
            qscopes = Q(l2_emp_id__in=userid)
        elif 'QC' in userid:
            qscopes = Q(l3_emp_id__in=userid)
        elif 'QA' in userid:
            qscopes = Q(l4_emp_id__in=userid)

        if scope == 'DA1':
            trackdata = raw_data.objects.filter(qscopes,
                                                baseid_id__created_at__date=date,
                                                l1_emp_id__location=location
                                                ).values(empid=F('l1_emp_id')).annotate(
                count=Count('l1_status', Q(l1_status='completed'))
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'DA2':
            trackdata = raw_data.objects.filter(qscopes,
                                                baseid_id__created_at__date=date,
                                                l2_emp_id__location=location
                                                ).values(empid=F('l2_emp_id')).annotate(
                count=Count('l2_status', Q(l2_status='completed')),
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'QC':
            trackdata = raw_data.objects.filter(qscopes,
                                                baseid_id__created_at__date=date,
                                                l3_emp_id__location=location
                                                ).values(empid=F('l3_emp_id')).annotate(
                count=Count('l3_status', Q(l3_status='completed')),
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'QA':
            trackdata = raw_data.objects.filter(qscopes,
                                                baseid_id__created_at__date=date,
                                                l4_emp_id__location=location
                                                ).values(empid=F('l4_emp_id')).annotate(
                count=Count('l4_status', Q(l4_status='completed'))
            ).exclude(status__in=['hold', 'deleted'])

        targetdata = targetsetting.objects.filter(targetempid_id__in=userid, targetempid__location=location, target_date__date=date).values(
            'targetempid_id__employeeID', 'target', 'targetempid__location', empid=F('targetempid_id'))

        df_trackdata = pd.DataFrame(trackdata)
        df_targetdata = pd.DataFrame(targetdata)
        datais = False
        if not df_targetdata.empty and not df_trackdata.empty:
            mrgd = pd.merge(df_trackdata, df_targetdata,
                            on='empid', how='right')
            if not mrgd.empty:
                mrgd.fillna(0, inplace=True)
                mrgd['Achieved %'] = mrgd.apply(lambda row: round(
                    (int(row['count']) / int(row['target'])) * 100, 2) if not pd.isna(row['count']) else 0, axis=1)
                mrgd['Completed Count'] = mrgd['count'].astype(int)
                mrgd.index = np.arange(1, len(mrgd) + 1)
                mrgd = mrgd.drop(columns=['empid'])
                mrgd = mrgd.rename(columns={'targetempid_id__employeeID': 'Employee Id',
                                   'targetempid__location': 'Location', 'target': 'Target Count'})
                # mrgd.reset_index(drop=True, inplace=True)
                ord = ['Employee Id', 'Location', 'Target Count',
                       'Completed Count', 'Achieved %']
                mrgd = mrgd[ord]
                if key == 'Download':
                    lable = 'UserwiseTracking_Report'
                    response = HttpResponse(
                        content_type='text/csv; charset=utf-8-sig')
                    response['Content-Disposition'] = 'attachment; filename="' + lable + \
                        str(timezone.now().date())+'".csv"'
                    mrgd.to_csv(path_or_buf=response,
                                index=False, encoding='utf-8-sig')

                    return response
                else:
                    mrgd = mrgd.to_html().replace('<table border="1" class="dataframe">', '<table class="table table-hover">').replace('<thead>',
                                                                                                                                       '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                    datais = True
                    return render(request, 'pages/userwisetracking.html', {'datais': datais, 'mrgd': mrgd, 'locations': locations, 'scopes': scopes, 'date': date, 'location': location, 'scope': scope})
        return render(request, 'pages/userwisetracking.html', {'datais': datais, 'locations': locations, 'scopes': scopes, 'date': date, 'location': location, 'scope': scope, 'Alert': {'type': 'Info', 'message': 'Agents have No Target'}})
    else:
        return render(request, 'pages/userwisetracking.html', {'datais': False, 'locations': locations, 'scopes': scopes})


# @custom_token_login_required
@loginrequired
def hourlytarget(request):
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    if request.method == 'POST':
        scope = request.POST.get('scope')
        location = request.POST.get('location')
        date = request.POST.get('date')
        key = request.POST.get('key')

        role = Q()
        if not scope == 'All':
            role = Q(targetfor=scope)

        locprod = Q()
        loctarget = Q()
        if not location == 'All':
            locprod = Q(created_by__location=location)
            loctarget = Q(targetempid__location=location)

        prod_Date = Q(end_time__date=date)

        table_names = []
        if scope == 'DA1' or scope == 'All':
            table_names.extend(['l1_production'])
        if scope == 'DA2' or scope == 'All':
            table_names.extend(['l2_production'])
        if scope == 'QC' or scope == 'All':
            table_names.extend(['l3_production'])
        if scope == 'QA' or scope == 'All':
            table_names.extend(['l4_production'])

        def getcount(filename):
            if filename:
                count = raw_data.objects.filter(
                    baseid__filename=filename).count()
                return count
            else:
                return 0

        querysets = []
        for table_name in table_names:
            queryset = globals()[table_name].objects.filter(prod_Date, locprod).values(
                date=F('created_at__date'),
                empid=F('created_by__employeeID'),
                empname=F('created_by__employeeName')
            ).annotate(
                source_table=Value(str(table_name), output_field=CharField()),
                crtdhr=ExtractHour('end_time'),
                count=Count('created_by_id'),
                filename=F('qid__baseid__filename'),
            ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productionhourly = list(chain(*querysets))

        targetdata = targetsetting.objects.filter(role, loctarget, target_date__date=date).values(
            'target', 'targetempid__location', empid=F('targetempid_id__employeeID'), empname=F('targetempid__employeeName'))
        qsifttime = ShiftTime.objects.filter(created_at__date=date).annotate(
            shifttime=ExtractHour(Sum(F('endtime') - F('starttime')))
        ).values('shifttime', empid=F('userprofile__employeeID'))

        df_prodhoure = pd.DataFrame(productionhourly)
        df_targetdata = pd.DataFrame(targetdata)
        df_sifttime = pd.DataFrame(qsifttime)
        if not df_prodhoure.empty and not df_targetdata.empty:
            mrgd = pd.merge(df_prodhoure, df_targetdata, on=[
                            'empid', 'empname'], how='outer')
            mrgd = mrgd.pivot_table(index=['empid', 'empname', 'filename', 'targetempid__location', 'target'],
                                    columns='crtdhr',
                                    values='count',
                                    fill_value=0).reset_index()

            if not df_sifttime.empty:
                droplist = ['houretarget', 'shifttime']
                mrgd = pd.merge(mrgd, df_sifttime, on='empid',
                                how='left').fillna(0)

                mrgd['houretarget'] = mrgd.apply(lambda row: round(
                    int(row['target']) / 8, 2), axis=1).astype(int)

                # mrgd['houretarget'] = mrgd.apply(lambda row: round((int(row['target']) * getcount(row['filename'])) / 100,2), axis=1)
                # mrgd['houretarget'] = mrgd.apply(lambda row: round(int(row['houretarget']) / int(row['shifttime']) if int(row['shifttime']) != 0 else int(11),1), axis=1)
            else:
                droplist = ['houretarget']
                mrgd['houretarget'] = mrgd.apply(lambda row: round(
                    int(row['target']) / 8, 2), axis=1).astype(int)

                # mrgd['houretarget'] = mrgd.apply(lambda row: round((int(row['target']) * getcount(row['filename'])) / 100,2), axis=1)
                # mrgd['houretarget'] = mrgd.apply(lambda row: round(int(row['houretarget']) / int(11),1), axis=1)

            tablecolumn = ['empid', 'filename', 'empname',
                           'targetempid__location', 'target', 'Hourly Target']
            mrgd = mrgd.rename(columns=lambda x: str(
                x) if x not in tablecolumn else x)
            mrgd = mrgd.fillna(0)
            mrgd.insert(mrgd.columns.get_loc('target') + 1,
                        'Hourly Target', mrgd['houretarget'])
            mrgd = mrgd.drop(columns=droplist)

            # mrgd = mrgd[tablecolumn]
            mrgd = mrgd.rename(columns=rnmhourlycolumn)
            mrgd.index = np.arange(1, len(mrgd) + 1)

            if key == 'Download':
                lable = 'Hourly_Report'
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + lable + \
                    str(timezone.now().date())+'".csv"'
                mrgd.to_csv(path_or_buf=response,
                            index=False, encoding='utf-8-sig')

                return response
            else:
                mrgd = mrgd.to_html().replace('<table border="1" class="dataframe">', '<table id="dftable" class="table table-hover">').replace('<thead>',
                                                                                                                                                '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                return render(request, 'pages/hourly_target.html', {'houretarget': mrgd, 'locations': locations,  'scope': scope, 'location': location, 'date': date, 'key': key})
        else:
            return render(request, 'pages/hourly_target.html', {'locations': locations, 'date': date, 'scope': scope, 'location': location, 'Alert': json.dumps({'type': 'Info', 'message': 'No records'})})
    else:
        return render(request, 'pages/hourly_target.html', {'locations': locations})

# @custom_token_login_required


@loginrequired
def resetuser(request):
    filenames = raw_data.objects.filter().values(
        'baseid_id', 'baseid__filename').exclude(status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    if request.method == 'POST':
        keyval = request.POST.get('keyval')
        key = request.POST.get('key')
        if key == 'GetItem':
            batch_name = request.POST.get('batch_name')
            id_vals = request.POST.get('id_value')
            targetusers = raw_data.objects.filter(baseid_id=batch_name, id_value=id_vals).values(
                'id',
                'baseid__batch_name',
                'id_value',
                'asin',
                'l1_emp__employeeID',
                'l1_status',
                'l2_emp__employeeID',
                'l2_status',
                'l3_emp__employeeID',
                'l3_status',
                'l4_emp__employeeID',
                'l4_status'
            )
            return render(request, 'pages/filebaseduserchech.html', {'filenames': filenames, 'targetusers': targetusers, 'batch_name': batch_name})

        if key == "userassign":
            batch_name = request.POST.get('batch_name1')
            scope = request.POST.get('scope1')
            # production_staus = request.POST.get('production_staus')
            status_data = request.POST.get('hold_unhold')
            assignuser_id = Roles.objects.filter(role=scope).values(
                'id', 'role', 'userprofile__employeeID', 'userprofile_id')

            if status_data == 'hold':
                if scope == "DA1":
                    query1 = Q(l1_status=status_data)
                if scope == "DA2":
                    query2 = Q(l2_status=status_data)
                if scope == "QC":
                    query3 = Q(l3_status=status_data)
                if scope == "QA":
                    query4 = Q(l4_status=status_data)
                exc = Q()

            elif status_data == 'picked':
                if scope == "DA1":
                    query1 = Q(l1_status='picked')
                if scope == "DA2":
                    query2 = Q(l2_status='picked')
                if scope == "QC":
                    query3 = Q(l3_status='picked')
                if scope == "QA":
                    query4 = Q(l4_status='picked')
                exc = Q()
            else:
                if scope == "DA1":
                    query1 = Q(l1_status='not_picked')
                    exc = Q(l1_status='completed') | Q(l1_status='picked')
                if scope == "DA2":
                    query2 = Q(l2_status='not_picked')
                    exc = Q(l2_status='completed') | Q(l2_status='picked')
                if scope == "QC":
                    query3 = Q(l3_status='not_moved') & Q(l1_status='completed') & Q(
                        l2_status='completed') & Q(l1_l2_accuracy='fail')
                    exc = Q(l3_status='completed') | Q(l3_status='picked')
                if scope == "QA":
                    query4 = Q(l4_status='not_picked') & Q(l1_status='completed') & Q(
                        l2_status='completed') & Q(l1_l2_accuracy='pass')
                    exc = Q(l4_status='completed') | Q(l4_status='picked')

            if scope == "DA1":
                asignuser = raw_data.objects.filter(query1,
                                                    baseid_id=batch_name
                                                    ).values(
                    'id',
                    'id_value',
                    'l1_emp__employeeID',
                    'l1_status',
                    'l2_emp__employeeID',
                    'l2_status',
                    'l3_emp__employeeID',
                    'l3_status',
                    'l4_emp__employeeID',
                    'l4_status',
                    'status'
                ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "DA2":
                asignuser = raw_data.objects.filter(query2,
                                                    baseid_id=batch_name,
                                                    ).values(
                    'id',
                    'id_value',
                    'l1_emp__employeeID',
                    'l1_status',
                    'l2_emp__employeeID',
                    'l2_status',
                    'l3_emp__employeeID',
                    'l3_status',
                    'l4_emp__employeeID',
                    'l4_status',
                    'status'
                ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "QC":
                asignuser = raw_data.objects.filter(query3,
                                                    baseid_id=batch_name,
                                                    ).values(
                    'id',
                    'id_value',
                    'l1_emp__employeeID',
                    'l1_status',
                    'l2_emp__employeeID',
                    'l2_status',
                    'l3_emp__employeeID',
                    'l3_status',
                    'l4_emp__employeeID',
                    'l4_status',
                    'status'
                ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "QA":
                asignuser = raw_data.objects.filter(query4,
                                                    baseid_id=batch_name,
                                                    ).values(
                    'id',
                    'id_value',
                    'l1_emp__employeeID',
                    'l1_status',
                    'l2_emp__employeeID',
                    'l2_status',
                    'l3_emp__employeeID',
                    'l3_status',
                    'l4_emp__employeeID',
                    'l4_status',
                    'status'
                ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            return render(request, 'pages/filebaseduserchech.html', {'assignuser_id': assignuser_id, 'batch_name1': batch_name, 'status_data': status_data, 'scope': scope, 'asignuser': asignuser, 'filenames': filenames})

        if keyval == 'assignuser':
            id_values = request.POST.getlist('idval[]')
            filename = request.POST.get('filename')
            assigemployee = request.POST.get('assigningemployee_id')
            assigning_for = request.POST.get('assigning_for')
            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l1_emp_id=assigemployee, l1_status='picked')
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l2_emp_id=assigemployee, l2_status='picked')
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l3_emp_id=assigemployee, l3_status='picked')
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l4_emp_id=assigemployee, l4_status='picked')
        if keyval == 'hold':
            id_values = request.POST.getlist('idval[]')
            filename = request.POST.get('filename')
            assigning_for = request.POST.get('assigning_for')

            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(
                        baseid_id=filename, id_value=id_value).update(l1_status='picked')
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(
                        baseid_id=filename, id_value=id_value).update(l2_status='picked')
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(
                        baseid_id=filename, id_value=id_value).update(l3_status='picked')
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(
                        baseid_id=filename, id_value=id_value).update(l4_status='picked')
        if keyval == 'reset':
            id_values = request.POST.getlist('idval[]')
            filename = request.POST.get('filename')
            assigning_for = request.POST.get('assigning_for')

            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l1_status='not_picked', l1_loc=None, l1_emp=None)
                    # raw_data.objects.filter(baseid_id = filename, id_value=id_value).delete()
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l2_status='not_picked', l2_loc=None, l2_emp=None)
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l3_status='not_moved', l3_emp=None)
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l4_status='not_picked', l4_emp=None)
        return JsonResponse({'status': 'success', 'code': 200})
    else:
        queue()
        return render(request, 'pages/filebaseduserchech.html', {'datais': False, 'filenames': filenames})

# @custom_token_login_required


@loginrequired
def ut_report(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')
    locations = Location.objects.values('location')
    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        filename = request.POST.get('filename')
        location = request.POST.get('location')
        language = request.POST.get('language')

        query = Q()
        if fromdate and todate:
            query &= Q(end_time__date__range=(fromdate, todate))
        if not 'All' == location:
            query &= Q(created_by__location=location)

        if not 'All' == filename:
            query &= Q(qid__baseid__filename=filename)

        if not 'All' == language:
            query &= Q(qid__baseid__language=language)

        querysets = []
        for table_name in ['l1_production', 'l2_production', 'l3_production', 'l4_production']:
            queryset = globals()[table_name].objects.filter(query).values(
                date=F('created_at__date'),
                empid=F('created_by__employeeID'),
                filename=F('qid__baseid__filename'),
                language=F('qid__baseid__language'),
                location=F('created_by__location'),
                empname=F('created_by__employeeName')
            ).annotate(
                productiontime=Sum(F('end_time') - F('start_time')),
            ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productions = list(chain(*querysets))
        df_production = pd.DataFrame(productions)
        if not df_production.empty:
            df_production['Percentage %'] = round(
                df_production['productiontime'] / timedelta(hours=9) * 100, 2)
            df_production['productiontime'] = pd.to_timedelta(
                df_production['productiontime']).astype(str).str.split().str[-1].str[:8]
            df_production.rename(columns=utcolumns, inplace=True)
            utord = ['Date', 'Employee ID', 'Employee Name', 'Filename',
                     'Location', 'Language', 'Production Time', 'Percentage %']
            df_production = df_production[utord]
            df_production.index = np.arange(1, len(df_production) + 1)
            if key == 'Download':
                lable = 'UT_Report'
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + lable + \
                    str(timezone.now().date())+'".csv"'
                df_production.to_csv(path_or_buf=response,
                                     index=False, encoding='utf-8-sig')

                return response
            else:
                df_production = df_production.to_html().replace('<table border="1" class="dataframe">', '<table id="dftable" class="table table-hover">').replace('<thead>',
                                                                                                                                                                  '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                return render(request, 'pages/ut_report.html', {'langs': langs, 'locations': locations, 'ut_report': df_production, 'filenames': filenames, 'fromdate': fromdate, 'todate': todate, 'filename': filename, 'location': location, 'language': language})
        else:
            # df_production.loc['Total'] = df_production.iloc[:, 3:-1].sum()
            # df_production.loc['Total','Utilization %'] =
            return render(request, 'pages/ut_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames, 'fromdate': fromdate, 'todate': todate, 'filename': filename, 'location': location, 'language': language})
    else:
        return render(request, 'pages/ut_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames})

# @custom_token_login_required


@loginrequired
def aht_report(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')
    locations = Location.objects.values('location')
    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        filename = request.POST.get('filename')
        location = request.POST.get('location')
        language = request.POST.get('language')
        scope = request.POST.get('scope')

        query = Q()
        if fromdate and todate:
            query &= Q(end_time__date__range=(fromdate, todate))
        if not 'All' in location:
            query &= Q(created_by__location=location)

        if not 'All' in filename:
            query &= Q(qid__baseid__filename=filename)

        if not 'All' in language:
            query &= Q(qid__baseid__language=language)

        table_names = []
        if scope == 'DA1' or scope == 'All':
            table_names.extend(['l1_production'])
        if scope == 'DA2' or scope == 'All':
            table_names.extend(['l2_production'])
        if scope == 'QC' or scope == 'All':
            table_names.extend(['l3_production'])
        if scope == 'QA' or scope == 'All':
            table_names.extend(['l4_production'])

        querysets = []
        for table_name in table_names:
            queryset = globals()[table_name].objects.filter(query).values(
                date=F('created_at__date'),
                empid=F('created_by__employeeID'),
                filename=F('qid__baseid__filename'),
                language=F('qid__baseid__language'),
                location=F('created_by__location'),
                empname=F('created_by__employeeName')
            ).annotate(
                productiontime=Sum(F('end_time') - F('start_time')),
                prodcount=Count('created_by__employeeID')
            ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productions = list(chain(*querysets))
        df_production = pd.DataFrame(productions)
        if not df_production.empty:
            df_production['AHT'] = (df_production['productiontime'] / df_production['prodcount']).apply(lambda x: '{:02}:{:02}:{:.2f}'.format(
                int(x.seconds // 3600), int((x.seconds % 3600) // 60), x.seconds % 60 + x.microseconds / 1e6))  # ().astype(str).str.split().str[-1]
            df_production['productiontime'] = pd.to_timedelta(
                df_production['productiontime']).astype(str).str.split().str[-1].str[:8]
            utcolumns.update({'prodcount': 'Production Count'})
            df_production.rename(columns=utcolumns, inplace=True)
            utord = ['Date', 'Employee ID', 'Employee Name', 'Filename',
                     'Location', 'Language', 'Production Time', 'Production Count', 'AHT']
            df_production = df_production[utord]
            df_production.index = np.arange(1, len(df_production) + 1)
            if key == 'Download':
                lable = 'AHT_Report'
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + lable + \
                    str(timezone.now().date())+'".csv"'
                df_production.to_csv(path_or_buf=response,
                                     index=False, encoding='utf-8-sig')
                return response
            else:
                df_production = df_production.to_html().replace('<table border="1" class="dataframe">', '<table id="dftable" class="table table-hover">').replace('<thead>',
                                                                                                                                                                  '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                return render(request, 'pages/aht_report.html', {'langs': langs, 'locations': locations, 'aht_report': df_production, 'filenames': filenames, 'fromdate': fromdate, 'todate': todate, 'filename': filename, 'location': location, 'language': language, 'scope': scope})
        else:
            return render(request, 'pages/aht_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames, 'fromdate': fromdate, 'todate': todate, 'filename': filename, 'location': location, 'language': language, 'scope': scope})
    else:
        return render(request, 'pages/aht_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames})

# @custom_token_login_required


@loginrequired
def ck_report(request):
    filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
        status__in=['hole', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')
    locations = Location.objects.values('location')
    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        baseID = request.POST.get('batch')
        location = request.POST.get('location')
        language = request.POST.get('language')

        query = Q()
        if fromdate and todate:
            query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
            query &= Q(l2_prod__end_time__date__range=(fromdate, todate))
        if not 'All' in location:
            query &= Q(l1_loc=location)
            query &= Q(l2_loc=location)

        if not 'All' in baseID:
            query &= Q(baseid_id=baseID)

        if not 'All' in language:
            query &= Q(baseid__language=language)

        datas = raw_data.objects.filter(query, l1_status='completed', l2_status='completed').values(
            'id_value', 'l1_prod_id__general_ques1', 'l2_prod_id__general_ques1').exclude(status__in=['hole', 'deleted'])  # ,'baseid__batch_name'
        df_datas = pd.DataFrame(datas)
        if not df_datas.empty:
            df_datas.replace('', pd.NA, inplace=True)

            df_datas = df_datas[df_datas['l1_prod_id__general_ques1'].isin(
                df_datas['l2_prod_id__general_ques1'])]
            df_datas = df_datas[df_datas['l2_prod_id__general_ques1'].isin(
                df_datas['l1_prod_id__general_ques1'])]

            # df_datas = df_datas.dropna(
            #     subset=['l1_prod_id__general_ques1', 'l2_prod_id__general_ques1'], how='any')

            # 'baseid__batch_name':'Batch Name',
            df_datas = df_datas.rename(
                columns={'l1_prod_id__general_ques1': 'DA1', 'l2_prod_id__general_ques1': 'DA2'})
            pivot_table = pd.pivot_table(df_datas, values='id_value', index=[
                                         'DA1'], columns='DA2', aggfunc='count', fill_value=0, margins=True, margins_name='Total')  # 'Batch Name',

            try:
                answer1 = pivot_table.loc['A is better than B',
                                          'A is better than B']
            except:
                answer1 = 0
            try:
                answer2 = pivot_table.loc['B is better than A',
                                          'B is better than A']
            except:
                answer2 = 0
            try:
                both = pivot_table.loc['A and B are equally good',
                                       'A and B are equally good']
            except:
                both = 0
            try:
                neither = pivot_table.loc['A and B are both unacceptable to present in front of a customer',
                                          'A and B are both unacceptable to present in front of a customer']
            except:
                neither = 0

            pivotsum = answer1 + answer2 + both + neither

            total = int(pivot_table.loc['Total', 'Total'])

            # Total Row Values
            rowtotal = np.array(pivot_table.loc['Total'].values.flatten())
            # Total Column Values
            coltotal = np.array(pivot_table['Total'].values)

            main_list = np.array(
                ['A is better than B', 'B is better than A', 'A and B are equally good', 'A and B are both unacceptable to present in front of a customer', 'Total'])

            onel_list = np.array(pivot_table.columns.values)  # Column Names

            onel_missing_values = np.setdiff1d(main_list, onel_list)
            onel_missing_indices = np.where(
                np.isin(main_list, onel_missing_values))[0]

            for index in onel_missing_indices:
                rowtotal = np.insert(rowtotal, index, 0)
            # print(rowtotal,"rowtotal")

            two_list = np.array(pivot_table.index.values)  # Row Values

            two_missing_values = np.setdiff1d(main_list, two_list)
            two_missing_indices = np.where(
                np.isin(main_list, two_missing_values))[0]

            for index in two_missing_indices:
                coltotal = np.insert(coltotal, index, 0)
            # print(coltotal,"coltotal")

            rowtotal = rowtotal[(rowtotal != total)]
            coltotal = coltotal[(coltotal != total)]

            try:
                npdot = np.dot(rowtotal, coltotal)
            except:
                npdot = 0

            sqtotal = total ** 2

            new_df = {}
            new_df['P0'] = round((pivotsum / total)*100, 2)
            new_df['Pe'] = round((npdot / sqtotal) * 100, 2)
            new_df['1- Pe'] = round((1 - (npdot / sqtotal)) * 100, 2)
            new_df['P0 - Pe'] = round(((new_df['P0'] -
                                      new_df['Pe']) / 100)*100, 2)
            new_df['k'] = round((new_df['P0 - Pe'] / new_df['1- Pe']) * 100, 2)

            ck_report = pivot_table.to_html()
            final_ck = new_df

            return render(request, 'pages/ck_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames, 'ck_report': ck_report, 'final_ck': final_ck, 'batch': baseID, 'fromdate': fromdate, 'todate': todate, 'location': location, 'language': language})
        return render(request, 'pages/ck_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames, 'Alert': {'message': 'No Records'}})
    else:
        return render(request, 'pages/ck_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames})


@loginrequired
def qualityreport(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    language = userProfile.objects.filter(
        Q(language__isnull=False) & ~Q(language='')).values('language').distinct()

    language_list = []
    for item in language:
        language_list.extend(ast.literal_eval(item['language']))
    language_list = list(set(language_list))

    if request.method == 'POST':
        try:

            fromdate = request.POST.get('fromdate')
            todate = request.POST.get('todate')
            filename = request.POST.get('filename')
            location = request.POST.get('location')
            scope = request.POST.get('scope')
            key = request.POST.get('key')
            language_sl = request.POST.get('language')
            options = request.POST.get('options')

            # print(fromdate,todate,filename,location,scope,key,language_sl,options)
            totalcount = Q()

            raw_data_query = Q(l1_status="completed",
                               l2_status="completed", l3_status="completed")

            if filename != "ALL":
                totalcount &= Q(baseid__filename=filename)
                raw_data_query &= Q(baseid__filename=filename)
            total_data_count = raw_data.objects.filter(totalcount).count()
            if location != "ALL":

                raw_data_query &= Q(Q(l1_loc=location) | Q(l2_loc=location))

            if language_sl != "ALL":

                raw_data_query &= Q(baseid__language=[language_sl])

            raw_data_query &= Q(
                l1_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(
                l2_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(
                l3_prod__end_time__date__range=(fromdate, todate))

            qc_ount = raw_data.objects.filter(raw_data_query).count()

            print("Total number of data after filtering : ",
                  total_data_count, "qc_count : ", qc_ount)

            raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                                                                             'baseid__batch_name',
                                                                             'l1_emp__employeeName',
                                                                             'l1_emp__employeeID',
                                                                             'l2_emp__employeeID',
                                                                             'l1_loc',
                                                                             'l2_emp__employeeName',
                                                                             'l2_loc',
                                                                             'id_value',
                                                                             'question',
                                                                             'asin',
                                                                             'title',
                                                                             'product_url',
                                                                             'imagepath',
                                                                             'evidence',
                                                                             'answer_one',
                                                                             'answer_two',
                                                                             'l1_status',
                                                                             'l2_status',
                                                                             'l4_status',
                                                                             'l3_status',
                                                                             'l1_l2_accuracy',
                                                                            'l1_prod__que1',
                                                                            'l1_prod__que1a',
                                                                            'l1_prod__que2_ans1',
                                                                            'l1_prod__que2a_ans1',
                                                                            'l1_prod__que3_ans1',
                                                                            'l1_prod__que4_ans1',
                                                                            'l1_prod__que4a_ans1',
                                                                            'l1_prod__que4b_ans1',
                                                                            'l1_prod__que4c_ans1',
                                                                            'l1_prod__que4d_ans1',
                                                                            'l1_prod__que4e_ans1',
                                                                            'l1_prod__que4f_ans1',
                                                                            'l1_prod__que5a_ans1',
                                                                            'l1_prod__que6_ans1',
                                                                            'l1_prod__que6a_ans1',
                                                                            'l1_prod__que7_ans1',
                                                                            'l1_prod__que8_ans1',
                                                                            'l1_prod__que8a_ans1',
                                                                            'l1_prod__que8b_ans1',
                                                                            'l1_prod__que2_ans2',
                                                                            'l1_prod__que2a_ans2',
                                                                            'l1_prod__que3_ans2',
                                                                            'l1_prod__que4_ans2',
                                                                            'l1_prod__que4a_ans2',
                                                                            'l1_prod__que4b_ans2',
                                                                            'l1_prod__que4c_ans2',
                                                                            'l1_prod__que4d_ans2',
                                                                            'l1_prod__que4e_ans2',
                                                                            'l1_prod__que4f_ans2',
                                                                            'l1_prod__que5a_ans2',
                                                                            'l1_prod__que6_ans2',
                                                                            'l1_prod__que6a_ans2',
                                                                            'l1_prod__que7_ans2',
                                                                            'l1_prod__que8_ans2',
                                                                            'l1_prod__que8a_ans2',
                                                                            'l1_prod__que8b_ans2',
                                                                            'l2_prod__que1',
                                                                            'l2_prod__que1a',
                                                                            'l2_prod__que2_ans1',
                                                                            'l2_prod__que2a_ans1',
                                                                            'l2_prod__que3_ans1',
                                                                            'l2_prod__que4_ans1',
                                                                            'l2_prod__que4a_ans1',
                                                                            'l2_prod__que4b_ans1',
                                                                            'l2_prod__que4c_ans1',
                                                                            'l2_prod__que4d_ans1',
                                                                            'l2_prod__que4e_ans1',
                                                                            'l2_prod__que4f_ans1',
                                                                            'l2_prod__que5a_ans1',
                                                                            'l2_prod__que6_ans1',
                                                                            'l2_prod__que6a_ans1',
                                                                            'l2_prod__que7_ans1',
                                                                            'l2_prod__que8_ans1',
                                                                            'l2_prod__que8a_ans1',
                                                                            'l2_prod__que8b_ans1',
                                                                            'l2_prod__que2_ans2',
                                                                            'l2_prod__que2a_ans2',
                                                                            'l2_prod__que3_ans2',
                                                                            'l2_prod__que4_ans2',
                                                                            'l2_prod__que4a_ans2',
                                                                            'l2_prod__que4b_ans2',
                                                                            'l2_prod__que4c_ans2',
                                                                            'l2_prod__que4d_ans2',
                                                                            'l2_prod__que4e_ans2',
                                                                            'l2_prod__que4f_ans2',
                                                                            'l2_prod__que5a_ans2',
                                                                            'l2_prod__que6_ans2',
                                                                            'l2_prod__que6a_ans2',
                                                                            'l2_prod__que7_ans2',
                                                                            'l2_prod__que8_ans2',
                                                                            'l2_prod__que8a_ans2',
                                                                            'l2_prod__que8b_ans2',
                                                                            'l3_prod__que1',
                                                                            'l3_prod__que1a',
                                                                            'l3_prod__que2_ans1',
                                                                            'l3_prod__que2a_ans1',
                                                                            'l3_prod__que3_ans1',
                                                                            'l3_prod__que4_ans1',
                                                                            'l3_prod__que4a_ans1',
                                                                            'l3_prod__que4b_ans1',
                                                                            'l3_prod__que4c_ans1',
                                                                            'l3_prod__que4d_ans1',
                                                                            'l3_prod__que4e_ans1',
                                                                            'l3_prod__que4f_ans1',
                                                                            'l3_prod__que5a_ans1',
                                                                            'l3_prod__que6_ans1',
                                                                            'l3_prod__que6a_ans1',
                                                                            'l3_prod__que7_ans1',
                                                                            'l3_prod__que8_ans1',
                                                                            'l3_prod__que8a_ans1',
                                                                            'l3_prod__que8b_ans1',
                                                                            'l3_prod__que2_ans2',
                                                                            'l3_prod__que2a_ans2',
                                                                            'l3_prod__que3_ans2',
                                                                            'l3_prod__que4_ans2',
                                                                            'l3_prod__que4a_ans2',
                                                                            'l3_prod__que4b_ans2',
                                                                            'l3_prod__que4c_ans2',
                                                                            'l3_prod__que4d_ans2',
                                                                            'l3_prod__que4e_ans2',
                                                                            'l3_prod__que4f_ans2',
                                                                            'l3_prod__que5a_ans2',
                                                                            'l3_prod__que6_ans2',
                                                                            'l3_prod__que6a_ans2',
                                                                            'l3_prod__que7_ans2',
                                                                            'l3_prod__que8_ans2',
                                                                            'l3_prod__que8a_ans2',
                                                                            'l3_prod__que8b_ans2')

            # changed by(Prasanth)
            ##################### New Code #############################
            raw_data_values_df = pd.DataFrame(raw_data_values)

            if scope == 'DA1':
                result_df = userwisequalityreportDA1(raw_data_values_df)
            if scope == 'DA2':
                result_df = userwisequalityreportDA2(raw_data_values_df)
            if scope == 'ALL':
                fromfun1 = userwisequalityreportDA1(raw_data_values_df)
                fromfun2 = userwisequalityreportDA2(raw_data_values_df)
                result_df = pd.concat([fromfun1, fromfun2], ignore_index=True)
            ##########################################################################

            # result_df = pd.DataFrame()

            # for row in raw_data_values:

            #     if scope == 'DA1':

            #         fromfun = userwisequalityreportDA1(row)

            #         result_df = pd.concat(
            #             [result_df, fromfun], ignore_index=True)

            #     elif scope == 'DA2':

            #         fromfun = userwisequalityreportDA2(row)

            #         result_df = pd.concat(
            #             [result_df, fromfun], ignore_index=True)

            #     elif scope == 'ALL':

            #         fromfun1 = userwisequalityreportDA1(row)

            #         result_df = pd.concat(
            #             [result_df, fromfun1], ignore_index=True)

            #         fromfun2 = userwisequalityreportDA2(row)

            #         result_df = pd.concat(
            #             [result_df, fromfun2], ignore_index=True)

            error_counts = []

            # Loop through columns 15 to 38 (inclusive)
            for i in range(15, 38):
                # Count the number of False values in the current column
                count = (result_df.iloc[:, i] == False).sum()
                # Append the count to the error_counts list
                error_counts.append(count)

            if key == 'Download':
                if options == 'USER':

                    csv_buffer = StringIO()
                    result_df.to_csv(csv_buffer, index=True, encoding='utf-8')

                    # Set up the response
                    response = HttpResponse(
                        csv_buffer.getvalue(), content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'

                    return response

                elif options == 'FIELD':
                    rows = [
                        'Q1: Are the context and query valid?',
                        'Q1A: Why is the context or query invalid?',
                        'Q2: Does consistency evaluation apply to this answer? Answer 1',
                        'Q2A: Why does consistency evaluation not apply to this answer? Answer 1',
                        'Q3: Select all types of evidence that you referred to for confirming consistency? Answer 1',
                        'Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 1',
                        'Q4.1: Are the statements in the answer consistent with details in the product page? Answer 1',
                        'Q4.2: Does the answer provide complete information based on the product page? Answer 1',
                        'Q4.3: Is the answer consistent with customer reviews? Answer 1',
                        'Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 1',
                        'Q4.5: Does the answer correctly reference the source of the information? Answer 1',
                        'Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 1',
                        'Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 1',
                        'Q6: Is the answer consistent with common sense or your own knowledge? Answer 1',
                        'Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 1',
                        'Q7: Which statements lack supporting evidence? Answer 1',
                        'Q8: Overall, is the answer consistent? Answer 1',
                        'Q8A: If you are unsure about consistency, then what is the reason? Answer 1',
                        'Q8B: Please enter any comment? Answer 1',
                        'Q2: Does consistency evaluation apply to this answer? Answer 2',
                        'Q2A: Why does consistency evaluation not apply to this answer? Answer 2',
                        'Q3: Select all types of evidence that you referred to for confirming consistency? Answer 2',
                        'Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 2',
                        'Q4.1: Are the statements in the answer consistent with details in the product page? Answer 2',
                        'Q4.2: Does the answer provide complete information based on the product page? Answer 2',
                        'Q4.3: Is the answer consistent with customer reviews? Answer 2',
                        'Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 2',
                        'Q4.5: Does the answer correctly reference the source of the information? Answer 2',
                        'Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 2',
                        'Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 2',
                        'Q6: Is the answer consistent with common sense or your own knowledge? Answer 2',
                        'Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 2',
                        'Q7: Which statements lack supporting evidence? Answer 2',
                        'Q8: Overall, is the answer consistent? Answer 2',
                        'Q8A: If you are unsure about consistency, then what is the reason? Answer 2',
                        'Q8B: Please enter any comment? Answer 2',
                        'Over All'
                    ]

                    new_df = pd.DataFrame(rows, columns=['PRODUCTION'])
                    new_df['Total_Input_count'] = total_data_count
                    new_df['processed_count'] = qc_ount
                    new_df['Total_error'] = result_df.iloc[:, 14:39].apply(
                        lambda col: (col == False).sum(), axis=1)
                    for index, count in enumerate(error_counts):
                        new_df.at[index, 'Total_error'] = count
                    new_df['Accuracy__on_total_input'] = round(
                        ((1 - (new_df['Total_error'] / new_df['Total_Input_count'])) * 100), 2)
                    new_df['Disagreement__on_total_input'] = round(
                        ((new_df['Total_error'] / new_df['Total_Input_count']))*100, 2)
                    new_df['Accuracy__on_processed_count'] = round(
                        ((1 - (new_df['Total_error'] / new_df['processed_count'])) * 100), 2)
                    new_df['Disagreement__on_processed_count'] = round(
                        ((new_df['Total_error'] / new_df['processed_count']))*100, 2)
                    total_input_count_sum = new_df['Total_Input_count'].iloc[:-1].sum()
                    processed_count_sum = new_df['processed_count'].iloc[:-1].sum()
                    Total_error_sum = new_df['Total_error'].iloc[:-1].sum()
                    Accuracy__on_total_input_sum = new_df['Accuracy__on_total_input'].sum(
                    )
                    Disagreement__on_total_input_sum = new_df['Disagreement__on_total_input'].sum(
                    )

                    new_df.iloc[-1, 1] = total_input_count_sum
                    new_df.iloc[-1, 2] = processed_count_sum
                    new_df.iloc[-1, 3] = Total_error_sum
                    new_df.iloc[-1, 4] = round((1-Total_error_sum /
                                               total_input_count_sum)*100, 2)
                    new_df.iloc[-1, 5] = round((Total_error_sum /
                                               total_input_count_sum)*100, 2)
                    new_df.iloc[-1,
                                6] = round((1-Total_error_sum/processed_count_sum)*100, 2)
                    new_df.iloc[-1,
                                7] = round((Total_error_sum/processed_count_sum)*100, 2)

                    new_df['Accuracy__on_total_input'] = new_df['Accuracy__on_total_input'].map(
                        lambda x: f"{x}%")
                    new_df['Disagreement__on_total_input'] = new_df['Disagreement__on_total_input'].map(
                        lambda x: f"{x}%")
                    new_df['Accuracy__on_processed_count'] = new_df['Accuracy__on_processed_count'].map(
                        lambda x: f"{x}%")
                    new_df['Disagreement__on_processed_count'] = new_df['Disagreement__on_processed_count'].map(
                        lambda x: f"{x}%")

                    csv_data = new_df.to_csv(index=True, encoding='utf-8')

                    response = HttpResponse(csv_data, content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'
                    return response

            else:

                if options == 'USER':

                    result_df['audit_count_ft'] = result_df.groupby(['PRODUCTION', 'Employee_id'])[
                        'Employee_Name'].transform('count')
                    result_df['total_error_ft'] = result_df.groupby(['PRODUCTION', 'Employee_id'])[
                        'Total_error'].transform('sum')

                    result_df = result_df.drop_duplicates(
                        subset=['PRODUCTION', 'Employee_id'], keep='first')

                    result_df['field_count_ft'] = result_df['audit_count_ft'] * 25

                    result_df['field_wise_accuracy_ft'] = round(
                        (1 - (result_df['total_error_ft'] / result_df['field_count_ft']))*100)

                    data_list = result_df.to_dict(orient='records')

                    return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames, 'language': language_list, 'response_data_list': data_list})

                elif options == 'FIELD':
                    rows = [
                        'Q1: Are the context and query valid?',
                        'Q1A: Why is the context or query invalid?',
                        'Q2: Does consistency evaluation apply to this answer? Answer 1',
                        'Q2A: Why does consistency evaluation not apply to this answer? Answer 1',
                        'Q3: Select all types of evidence that you referred to for confirming consistency? Answer 1',
                        'Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 1',
                        'Q4.1: Are the statements in the answer consistent with details in the product page? Answer 1',
                        'Q4.2: Does the answer provide complete information based on the product page? Answer 1',
                        'Q4.3: Is the answer consistent with customer reviews? Answer 1',
                        'Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 1',
                        'Q4.5: Does the answer correctly reference the source of the information? Answer 1',
                        'Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 1',
                        'Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 1',
                        'Q6: Is the answer consistent with common sense or your own knowledge? Answer 1',
                        'Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 1',
                        'Q7: Which statements lack supporting evidence? Answer 1',
                        'Q8: Overall, is the answer consistent? Answer 1',
                        'Q8A: If you are unsure about consistency, then what is the reason? Answer 1',
                        'Q8B: Please enter any comment? Answer 1',
                        'Q2: Does consistency evaluation apply to this answer? Answer 2',
                        'Q2A: Why does consistency evaluation not apply to this answer? Answer 2',
                        'Q3: Select all types of evidence that you referred to for confirming consistency? Answer 2',
                        'Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 2',
                        'Q4.1: Are the statements in the answer consistent with details in the product page? Answer 2',
                        'Q4.2: Does the answer provide complete information based on the product page? Answer 2',
                        'Q4.3: Is the answer consistent with customer reviews? Answer 2',
                        'Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 2',
                        'Q4.5: Does the answer correctly reference the source of the information? Answer 2',
                        'Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 2',
                        'Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 2',
                        'Q6: Is the answer consistent with common sense or your own knowledge? Answer 2',
                        'Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 2',
                        'Q7: Which statements lack supporting evidence? Answer 2',
                        'Q8: Overall, is the answer consistent? Answer 2',
                        'Q8A: If you are unsure about consistency, then what is the reason? Answer 2',
                        'Q8B: Please enter any comment? Answer 2',
                        'Over All'
                    ]

                    new_df = pd.DataFrame(rows, columns=['PRODUCTION'])
                    new_df['Total_Input_count'] = total_data_count
                    new_df['processed_count'] = qc_ount
                    new_df['Total_error'] = result_df.iloc[:, 14:39].apply(
                        lambda col: (col == False).sum(), axis=1)
                    for index, count in enumerate(error_counts):
                        new_df.at[index, 'Total_error'] = count
                    new_df['Accuracy__on_total_input'] = round(
                        ((1 - (new_df['Total_error'] / new_df['Total_Input_count'])) * 100), 2)
                    new_df['Disagreement__on_total_input'] = round(
                        ((new_df['Total_error'] / new_df['Total_Input_count']))*100, 2)
                    new_df['Accuracy__on_processed_count'] = round(
                        ((1 - (new_df['Total_error'] / new_df['processed_count'])) * 100), 2)
                    new_df['Disagreement__on_processed_count'] = round(
                        ((new_df['Total_error'] / new_df['processed_count']))*100, 2)
                    total_input_count_sum = new_df['Total_Input_count'].iloc[:-1].sum()
                    processed_count_sum = new_df['processed_count'].iloc[:-1].sum()
                    Total_error_sum = new_df['Total_error'].iloc[:-1].sum()
                    Accuracy__on_total_input_sum = new_df['Accuracy__on_total_input'].sum(
                    )
                    Disagreement__on_total_input_sum = new_df['Disagreement__on_total_input'].sum(
                    )

                    new_df.iloc[-1, 1] = total_input_count_sum
                    new_df.iloc[-1, 2] = processed_count_sum
                    new_df.iloc[-1, 3] = Total_error_sum
                    new_df.iloc[-1, 4] = round((1-Total_error_sum /
                                               total_input_count_sum)*100, 2)
                    new_df.iloc[-1, 5] = round((Total_error_sum /
                                               total_input_count_sum)*100, 2)
                    new_df.iloc[-1,
                                6] = round((1-Total_error_sum/processed_count_sum)*100, 2)
                    new_df.iloc[-1,
                                7] = round((Total_error_sum/processed_count_sum)*100, 2)

                    new_df['Accuracy__on_total_input'] = new_df['Accuracy__on_total_input'].map(
                        lambda x: f"{x}%")
                    new_df['Disagreement__on_total_input'] = new_df['Disagreement__on_total_input'].map(
                        lambda x: f"{x}%")
                    new_df['Accuracy__on_processed_count'] = new_df['Accuracy__on_processed_count'].map(
                        lambda x: f"{x}%")
                    new_df['Disagreement__on_processed_count'] = new_df['Disagreement__on_processed_count'].map(
                        lambda x: f"{x}%")

                    # print(new_df)

                    # new_df['Audited_count'] = result_df.apply(lambda row: row[:-2].eq(True).sum(), axis=1)

                    # new_df['Field_count'] = new_df['Audited_count'] * 25
                    # new_df['Audited_count_wise_accuracy'] = round((1 - (new_df['Total_error'] / new_df['Audited_count'])) * 100)
                    # new_df['field_count_wise_accuracy'] = round((1 - (new_df['Total_error'] / new_df['Field_count'])) * 100)
                    data_list = new_df.to_dict(orient='records')
                    return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames, 'language': language_list, 'data_list2': data_list})

        except Exception as e:
            return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames, 'language': language_list})

    return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames, 'language': language_list})


def userwisequalityreportDA1(userid):

    # pd.DataFrame([userid])   changed by(Prasanth) old code after "#"
    df_report = userid

    df_report['PRODUCTION'] = 'DA1'

    the_audit_count = 27



    if (df_report['l1_prod__que1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que1a'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que2_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que2a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que3_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4b_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4c_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4d_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4e_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4f_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que5a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que6_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que6a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que7_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que8_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que8a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que8b_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que2_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que2a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que3_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4b_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4c_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4d_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4e_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4f_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que5a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que6_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que6a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que7_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que8_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que8a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que8b_ans2'].empty):
        the_audit_count = the_audit_count-1

    df_report['Q1: Are the context and query valid?',] = (df_report[    'l1_prod__que1'] == df_report[    'l3_prod__que1'])
    df_report['Q1A: Why is the context or query invalid?',] = (df_report[    'l1_prod__que1a'] == df_report[    'l3_prod__que1a'])
    df_report['Q2: Does consistency evaluation apply to this answer? Answer 1',] = (df_report[    'l1_prod__que2_ans1'] == df_report[    'l3_prod__que2_ans1'])
    df_report['Q2A: Why does consistency evaluation not apply to this answer? Answer 1',] = (df_report[    'l1_prod__que2a_ans1'] == df_report[    'l3_prod__que2a_ans1'])
    df_report['Q3: Select all types of evidence that you referred to for confirming consistency? Answer 1',] = (df_report[    'l1_prod__que3_ans1'] == df_report[    'l3_prod__que3_ans1'])
    df_report['Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 1',] = (df_report[    'l1_prod__que4_ans1'] == df_report[    'l3_prod__que4_ans1'])
    df_report['Q4.1: Are the statements in the answer consistent with details in the product page? Answer 1',] = (df_report[    'l1_prod__que4a_ans1'] == df_report[    'l3_prod__que4a_ans1'])
    df_report['Q4.2: Does the answer provide complete information based on the product page? Answer 1',] = (df_report[    'l1_prod__que4b_ans1'] == df_report[    'l3_prod__que4b_ans1'])
    df_report['Q4.3: Is the answer consistent with customer reviews? Answer 1',] = (df_report[    'l1_prod__que4c_ans1'] == df_report[    'l3_prod__que4c_ans1'])
    df_report['Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 1',] = (df_report[    'l1_prod__que4d_ans1'] == df_report[    'l3_prod__que4d_ans1'])
    df_report['Q4.5: Does the answer correctly reference the source of the information? Answer 1',] = (df_report[    'l1_prod__que4e_ans1'] == df_report[    'l3_prod__que4e_ans1'])
    df_report['Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 1',] = (df_report[    'l1_prod__que4f_ans1'] == df_report[    'l3_prod__que4f_ans1'])
    df_report['Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 1',] = (df_report[    'l1_prod__que5a_ans1'] == df_report[    'l3_prod__que5a_ans1'])
    df_report['Q6: Is the answer consistent with common sense or your own knowledge? Answer 1',] = (df_report[    'l1_prod__que6_ans1'] == df_report[    'l3_prod__que6_ans1'])
    df_report['Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 1',] = (df_report[    'l1_prod__que6a_ans1'] == df_report[    'l3_prod__que6a_ans1'])
    df_report['Q7: Which statements lack supporting evidence? Answer 1',] = (df_report[    'l1_prod__que7_ans1'] == df_report[    'l3_prod__que7_ans1'])
    df_report['Q8: Overall, is the answer consistent? Answer 1',] = (df_report[    'l1_prod__que8_ans1'] == df_report[    'l3_prod__que8_ans1'])
    df_report['Q8A: If you are unsure about consistency, then what is the reason? Answer 1',] = (df_report[    'l1_prod__que8a_ans1'] == df_report[    'l3_prod__que8a_ans1'])
    df_report['Q8B: Please enter any comment? Answer 1',] = (df_report[    'l1_prod__que8b_ans1'] == df_report[    'l3_prod__que8b_ans1'])
    df_report['Q2: Does consistency evaluation apply to this answer? Answer 2',] = (df_report[    'l1_prod__que2_ans2'] == df_report[    'l3_prod__que2_ans2'])
    df_report['Q2A: Why does consistency evaluation not apply to this answer? Answer 2',] = (df_report[    'l1_prod__que2a_ans2'] == df_report[    'l3_prod__que2a_ans2'])
    df_report['Q3: Select all types of evidence that you referred to for confirming consistency? Answer 2',] = (df_report[    'l1_prod__que3_ans2'] == df_report[    'l3_prod__que3_ans2'])
    df_report['Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 2',] = (df_report[    'l1_prod__que4_ans2'] == df_report[    'l3_prod__que4_ans2'])
    df_report['Q4.1: Are the statements in the answer consistent with details in the product page? Answer 2',] = (df_report[    'l1_prod__que4a_ans2'] == df_report[    'l3_prod__que4a_ans2'])
    df_report['Q4.2: Does the answer provide complete information based on the product page? Answer 2',] = (df_report[    'l1_prod__que4b_ans2'] == df_report[    'l3_prod__que4b_ans2'])
    df_report['Q4.3: Is the answer consistent with customer reviews? Answer 2',] = (df_report[    'l1_prod__que4c_ans2'] == df_report[    'l3_prod__que4c_ans2'])
    df_report['Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 2',] = (df_report[    'l1_prod__que4d_ans2'] == df_report[    'l3_prod__que4d_ans2'])
    df_report['Q4.5: Does the answer correctly reference the source of the information? Answer 2',] = (df_report[    'l1_prod__que4e_ans2'] == df_report[    'l3_prod__que4e_ans2'])
    df_report['Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 2',] = (df_report[    'l1_prod__que4f_ans2'] == df_report[    'l3_prod__que4f_ans2'])
    df_report['Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 2',] = (df_report[    'l1_prod__que5a_ans2'] == df_report[    'l3_prod__que5a_ans2'])
    df_report['Q6: Is the answer consistent with common sense or your own knowledge? Answer 2',] = (df_report[    'l1_prod__que6_ans2'] == df_report[    'l3_prod__que6_ans2'])
    df_report['Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 2',] = (df_report[    'l1_prod__que6a_ans2'] == df_report[    'l3_prod__que6a_ans2'])
    df_report['Q7: Which statements lack supporting evidence? Answer 2',] = (df_report[    'l1_prod__que7_ans2'] == df_report[    'l3_prod__que7_ans2'])
    df_report['Q8: Overall, is the answer consistent? Answer 2',] = (df_report[    'l1_prod__que8_ans2'] == df_report[    'l3_prod__que8_ans2'])
    df_report['Q8A: If you are unsure about consistency, then what is the reason? Answer 2',] = (df_report[    'l1_prod__que8a_ans2'] == df_report[    'l3_prod__que8a_ans2'])
    df_report['Q8B: Please enter any comment? Answer 2',] = (df_report[    'l1_prod__que8b_ans2'] == df_report[    'l3_prod__que8b_ans2'])

    columns_to_remove = [
        'l1_status',
        'l2_status',
        'l4_status',
        'l3_status',
        'l1_l2_accuracy',
        'l1_prod__que1',
        'l1_prod__que1a',
        'l1_prod__que2_ans1',
        'l1_prod__que2a_ans1',
        'l1_prod__que3_ans1',
        'l1_prod__que4_ans1',
        'l1_prod__que4a_ans1',
        'l1_prod__que4b_ans1',
        'l1_prod__que4c_ans1',
        'l1_prod__que4d_ans1',
        'l1_prod__que4e_ans1',
        'l1_prod__que4f_ans1',
        'l1_prod__que5a_ans1',
        'l1_prod__que6_ans1',
        'l1_prod__que6a_ans1',
        'l1_prod__que7_ans1',
        'l1_prod__que8_ans1',
        'l1_prod__que8a_ans1',
        'l1_prod__que8b_ans1',
        'l1_prod__que2_ans2',
        'l1_prod__que2a_ans2',
        'l1_prod__que3_ans2',
        'l1_prod__que4_ans2',
        'l1_prod__que4a_ans2',
        'l1_prod__que4b_ans2',
        'l1_prod__que4c_ans2',
        'l1_prod__que4d_ans2',
        'l1_prod__que4e_ans2',
        'l1_prod__que4f_ans2',
        'l1_prod__que5a_ans2',
        'l1_prod__que6_ans2',
        'l1_prod__que6a_ans2',
        'l1_prod__que7_ans2',
        'l1_prod__que8_ans2',
        'l1_prod__que8a_ans2',
        'l1_prod__que8b_ans2',
        'l2_prod__que1',
        'l2_prod__que1a',
        'l2_prod__que2_ans1',
        'l2_prod__que2a_ans1',
        'l2_prod__que3_ans1',
        'l2_prod__que4_ans1',
        'l2_prod__que4a_ans1',
        'l2_prod__que4b_ans1',
        'l2_prod__que4c_ans1',
        'l2_prod__que4d_ans1',
        'l2_prod__que4e_ans1',
        'l2_prod__que4f_ans1',
        'l2_prod__que5a_ans1',
        'l2_prod__que6_ans1',
        'l2_prod__que6a_ans1',
        'l2_prod__que7_ans1',
        'l2_prod__que8_ans1',
        'l2_prod__que8a_ans1',
        'l2_prod__que8b_ans1',
        'l2_prod__que2_ans2',
        'l2_prod__que2a_ans2',
        'l2_prod__que3_ans2',
        'l2_prod__que4_ans2',
        'l2_prod__que4a_ans2',
        'l2_prod__que4b_ans2',
        'l2_prod__que4c_ans2',
        'l2_prod__que4d_ans2',
        'l2_prod__que4e_ans2',
        'l2_prod__que4f_ans2',
        'l2_prod__que5a_ans2',
        'l2_prod__que6_ans2',
        'l2_prod__que6a_ans2',
        'l2_prod__que7_ans2',
        'l2_prod__que8_ans2',
        'l2_prod__que8a_ans2',
        'l2_prod__que8b_ans2',
        'l3_prod__que1',
        'l3_prod__que1a',
        'l3_prod__que2_ans1',
        'l3_prod__que2a_ans1',
        'l3_prod__que3_ans1',
        'l3_prod__que4_ans1',
        'l3_prod__que4a_ans1',
        'l3_prod__que4b_ans1',
        'l3_prod__que4c_ans1',
        'l3_prod__que4d_ans1',
        'l3_prod__que4e_ans1',
        'l3_prod__que4f_ans1',
        'l3_prod__que5a_ans1',
        'l3_prod__que6_ans1',
        'l3_prod__que6a_ans1',
        'l3_prod__que7_ans1',
        'l3_prod__que8_ans1',
        'l3_prod__que8a_ans1',
        'l3_prod__que8b_ans1',
        'l3_prod__que2_ans2',
        'l3_prod__que2a_ans2',
        'l3_prod__que3_ans2',
        'l3_prod__que4_ans2',
        'l3_prod__que4a_ans2',
        'l3_prod__que4b_ans2',
        'l3_prod__que4c_ans2',
        'l3_prod__que4d_ans2',
        'l3_prod__que4e_ans2',
        'l3_prod__que4f_ans2',
        'l3_prod__que5a_ans2',
        'l3_prod__que6_ans2',
        'l3_prod__que6a_ans2',
        'l3_prod__que7_ans2',
        'l3_prod__que8_ans2',
        'l3_prod__que8a_ans2',
        'l3_prod__que8b_ans2'
    ]

    df_report = df_report.drop(columns=columns_to_remove)

    new_column_names = {'l1_emp__employeeID': 'Employee_id',
                        'l1_emp__employeeName': 'Employee_Name', 'l1_loc': 'Location'}

    df_report.rename(columns=new_column_names, inplace=True)

    df_report['Audited_count'] = the_audit_count

    df_report['Total_error'] = df_report.apply(
        lambda row: row[:-2].eq(False).sum(), axis=1)

    df_report['Field_count'] = df_report['Audited_count']*25

    df_report['Audited_count_wise_accuracy'] = round(
        (1 - (df_report['Total_error'] / df_report['Audited_count']))*100)

    df_report['field_count_wise_accuracy'] = round(
        (1 - (df_report['Total_error'] / df_report['Field_count']))*100)

    return df_report


def userwisequalityreportDA2(userid):

    # pd.DataFrame([userid])   changed by(Prasanth) old code after "#"
    df_report = userid

    # comparing l2 == l3
    df_report['PRODUCTION'] = 'DA2'

    the_audit_count = 27




    if (df_report['l2_prod__que1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que1a'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que2_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que2a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que3_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4b_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4c_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4d_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4e_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4f_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que5a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que6_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que6a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que7_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que8_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que8a_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que8b_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que2_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que2a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que3_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4b_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4c_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4d_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4e_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4f_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que5a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que6_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que6a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que7_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que8_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que8a_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que8b_ans2'].empty):
        the_audit_count = the_audit_count-1


    df_report['Q1: Are the context and query valid?',] = (df_report[    'l2_prod__que1'] == df_report[    'l3_prod__que1'])
    df_report['Q1A: Why is the context or query invalid?',] = (df_report[    'l2_prod__que1a'] == df_report[    'l3_prod__que1a'])
    df_report['Q2: Does consistency evaluation apply to this answer? Answer 1',] = (df_report[    'l2_prod__que2_ans1'] == df_report[    'l3_prod__que2_ans1'])
    df_report['Q2A: Why does consistency evaluation not apply to this answer? Answer 1',] = (df_report[    'l2_prod__que2a_ans1'] == df_report[    'l3_prod__que2a_ans1'])
    df_report['Q3: Select all types of evidence that you referred to for confirming consistency? Answer 1',] = (df_report[    'l2_prod__que3_ans1'] == df_report[    'l3_prod__que3_ans1'])
    df_report['Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 1',] = (df_report[    'l2_prod__que4_ans1'] == df_report[    'l3_prod__que4_ans1'])
    df_report['Q4.1: Are the statements in the answer consistent with details in the product page? Answer 1',] = (df_report[    'l2_prod__que4a_ans1'] == df_report[    'l3_prod__que4a_ans1'])
    df_report['Q4.2: Does the answer provide complete information based on the product page? Answer 1',] = (df_report[    'l2_prod__que4b_ans1'] == df_report[    'l3_prod__que4b_ans1'])
    df_report['Q4.3: Is the answer consistent with customer reviews? Answer 1',] = (df_report[    'l2_prod__que4c_ans1'] == df_report[    'l3_prod__que4c_ans1'])
    df_report['Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 1',] = (df_report[    'l2_prod__que4d_ans1'] == df_report[    'l3_prod__que4d_ans1'])
    df_report['Q4.5: Does the answer correctly reference the source of the information? Answer 1',] = (df_report[    'l2_prod__que4e_ans1'] == df_report[    'l3_prod__que4e_ans1'])
    df_report['Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 1',] = (df_report[    'l2_prod__que4f_ans1'] == df_report[    'l3_prod__que4f_ans1'])
    df_report['Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 1',] = (df_report[    'l2_prod__que5a_ans1'] == df_report[    'l3_prod__que5a_ans1'])
    df_report['Q6: Is the answer consistent with common sense or your own knowledge? Answer 1',] = (df_report[    'l2_prod__que6_ans1'] == df_report[    'l3_prod__que6_ans1'])
    df_report['Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 1',] = (df_report[    'l2_prod__que6a_ans1'] == df_report[    'l3_prod__que6a_ans1'])
    df_report['Q7: Which statements lack supporting evidence? Answer 1',] = (df_report[    'l2_prod__que7_ans1'] == df_report[    'l3_prod__que7_ans1'])
    df_report['Q8: Overall, is the answer consistent? Answer 1',] = (df_report[    'l2_prod__que8_ans1'] == df_report[    'l3_prod__que8_ans1'])
    df_report['Q8A: If you are unsure about consistency, then what is the reason? Answer 1',] = (df_report[    'l2_prod__que8a_ans1'] == df_report[    'l3_prod__que8a_ans1'])
    df_report['Q8B: Please enter any comment? Answer 1',] = (df_report[    'l2_prod__que8b_ans1'] == df_report[    'l3_prod__que8b_ans1'])
    df_report['Q2: Does consistency evaluation apply to this answer? Answer 2',] = (df_report[    'l2_prod__que2_ans2'] == df_report[    'l3_prod__que2_ans2'])
    df_report['Q2A: Why does consistency evaluation not apply to this answer? Answer 2',] = (df_report[    'l2_prod__que2a_ans2'] == df_report[    'l3_prod__que2a_ans2'])
    df_report['Q3: Select all types of evidence that you referred to for confirming consistency? Answer 2',] = (df_report[    'l2_prod__que3_ans2'] == df_report[    'l3_prod__que3_ans2'])
    df_report['Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 2',] = (df_report[    'l2_prod__que4_ans2'] == df_report[    'l3_prod__que4_ans2'])
    df_report['Q4.1: Are the statements in the answer consistent with details in the product page? Answer 2',] = (df_report[    'l2_prod__que4a_ans2'] == df_report[    'l3_prod__que4a_ans2'])
    df_report['Q4.2: Does the answer provide complete information based on the product page? Answer 2',] = (df_report[    'l2_prod__que4b_ans2'] == df_report[    'l3_prod__que4b_ans2'])
    df_report['Q4.3: Is the answer consistent with customer reviews? Answer 2',] = (df_report[    'l2_prod__que4c_ans2'] == df_report[    'l3_prod__que4c_ans2'])
    df_report['Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 2',] = (df_report[    'l2_prod__que4d_ans2'] == df_report[    'l3_prod__que4d_ans2'])
    df_report['Q4.5: Does the answer correctly reference the source of the information? Answer 2',] = (df_report[    'l2_prod__que4e_ans2'] == df_report[    'l3_prod__que4e_ans2'])
    df_report['Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 2',] = (df_report[    'l2_prod__que4f_ans2'] == df_report[    'l3_prod__que4f_ans2'])
    df_report['Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 2',] = (df_report[    'l2_prod__que5a_ans2'] == df_report[    'l3_prod__que5a_ans2'])
    df_report['Q6: Is the answer consistent with common sense or your own knowledge? Answer 2',] = (df_report[    'l2_prod__que6_ans2'] == df_report[    'l3_prod__que6_ans2'])
    df_report['Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 2',] = (df_report[    'l2_prod__que6a_ans2'] == df_report[    'l3_prod__que6a_ans2'])
    df_report['Q7: Which statements lack supporting evidence? Answer 2',] = (df_report[    'l2_prod__que7_ans2'] == df_report[    'l3_prod__que7_ans2'])
    df_report['Q8: Overall, is the answer consistent? Answer 2',] = (df_report[    'l2_prod__que8_ans2'] == df_report[    'l3_prod__que8_ans2'])
    df_report['Q8A: If you are unsure about consistency, then what is the reason? Answer 2',] = (df_report[    'l2_prod__que8a_ans2'] == df_report[    'l3_prod__que8a_ans2'])
    df_report['Q8B: Please enter any comment? Answer 2',] = (df_report[    'l2_prod__que8b_ans2'] == df_report[    'l3_prod__que8b_ans2'])


    columns_to_remove = [
        'l1_status',
        'l2_status',
        'l4_status',
        'l3_status',
        'l1_l2_accuracy',
        'l1_prod__que1',
        'l1_prod__que1a',
        'l1_prod__que2_ans1',
        'l1_prod__que2a_ans1',
        'l1_prod__que3_ans1',
        'l1_prod__que4_ans1',
        'l1_prod__que4a_ans1',
        'l1_prod__que4b_ans1',
        'l1_prod__que4c_ans1',
        'l1_prod__que4d_ans1',
        'l1_prod__que4e_ans1',
        'l1_prod__que4f_ans1',
        'l1_prod__que5a_ans1',
        'l1_prod__que6_ans1',
        'l1_prod__que6a_ans1',
        'l1_prod__que7_ans1',
        'l1_prod__que8_ans1',
        'l1_prod__que8a_ans1',
        'l1_prod__que8b_ans1',
        'l1_prod__que2_ans2',
        'l1_prod__que2a_ans2',
        'l1_prod__que3_ans2',
        'l1_prod__que4_ans2',
        'l1_prod__que4a_ans2',
        'l1_prod__que4b_ans2',
        'l1_prod__que4c_ans2',
        'l1_prod__que4d_ans2',
        'l1_prod__que4e_ans2',
        'l1_prod__que4f_ans2',
        'l1_prod__que5a_ans2',
        'l1_prod__que6_ans2',
        'l1_prod__que6a_ans2',
        'l1_prod__que7_ans2',
        'l1_prod__que8_ans2',
        'l1_prod__que8a_ans2',
        'l1_prod__que8b_ans2',
        'l2_prod__que1',
        'l2_prod__que1a',
        'l2_prod__que2_ans1',
        'l2_prod__que2a_ans1',
        'l2_prod__que3_ans1',
        'l2_prod__que4_ans1',
        'l2_prod__que4a_ans1',
        'l2_prod__que4b_ans1',
        'l2_prod__que4c_ans1',
        'l2_prod__que4d_ans1',
        'l2_prod__que4e_ans1',
        'l2_prod__que4f_ans1',
        'l2_prod__que5a_ans1',
        'l2_prod__que6_ans1',
        'l2_prod__que6a_ans1',
        'l2_prod__que7_ans1',
        'l2_prod__que8_ans1',
        'l2_prod__que8a_ans1',
        'l2_prod__que8b_ans1',
        'l2_prod__que2_ans2',
        'l2_prod__que2a_ans2',
        'l2_prod__que3_ans2',
        'l2_prod__que4_ans2',
        'l2_prod__que4a_ans2',
        'l2_prod__que4b_ans2',
        'l2_prod__que4c_ans2',
        'l2_prod__que4d_ans2',
        'l2_prod__que4e_ans2',
        'l2_prod__que4f_ans2',
        'l2_prod__que5a_ans2',
        'l2_prod__que6_ans2',
        'l2_prod__que6a_ans2',
        'l2_prod__que7_ans2',
        'l2_prod__que8_ans2',
        'l2_prod__que8a_ans2',
        'l2_prod__que8b_ans2',
        'l3_prod__que1',
        'l3_prod__que1a',
        'l3_prod__que2_ans1',
        'l3_prod__que2a_ans1',
        'l3_prod__que3_ans1',
        'l3_prod__que4_ans1',
        'l3_prod__que4a_ans1',
        'l3_prod__que4b_ans1',
        'l3_prod__que4c_ans1',
        'l3_prod__que4d_ans1',
        'l3_prod__que4e_ans1',
        'l3_prod__que4f_ans1',
        'l3_prod__que5a_ans1',
        'l3_prod__que6_ans1',
        'l3_prod__que6a_ans1',
        'l3_prod__que7_ans1',
        'l3_prod__que8_ans1',
        'l3_prod__que8a_ans1',
        'l3_prod__que8b_ans1',
        'l3_prod__que2_ans2',
        'l3_prod__que2a_ans2',
        'l3_prod__que3_ans2',
        'l3_prod__que4_ans2',
        'l3_prod__que4a_ans2',
        'l3_prod__que4b_ans2',
        'l3_prod__que4c_ans2',
        'l3_prod__que4d_ans2',
        'l3_prod__que4e_ans2',
        'l3_prod__que4f_ans2',
        'l3_prod__que5a_ans2',
        'l3_prod__que6_ans2',
        'l3_prod__que6a_ans2',
        'l3_prod__que7_ans2',
        'l3_prod__que8_ans2',
        'l3_prod__que8a_ans2',
        'l3_prod__que8b_ans2'
    ]

    df_report = df_report.drop(columns=columns_to_remove)

    new_column_names = {'l2_emp__employeeID': 'Employee_id',
                        'l2_emp__employeeName': 'Employee_Name', 'l2_loc': 'Location'}

    df_report.rename(columns=new_column_names, inplace=True)

    df_report['Audited_count'] = the_audit_count

    df_report['Total_error'] = df_report.apply(
        lambda row: row[:-2].eq(False).sum(), axis=1)

    df_report['Field_count'] = df_report['Audited_count']*25

    df_report['Audited_count_wise_accuracy'] = round(
        (1 - (df_report['Total_error'] / df_report['Audited_count']))*100)

    df_report['field_count_wise_accuracy'] = round(
        (1 - (df_report['Total_error'] / df_report['Field_count']))*100)

    return df_report


def format_columns(col):
    if col.name != 'Questions':
        return col.astype(str) + '%'
    return col


@loginrequired
def iaa(request):
    batchname = basefile.objects.filter(Q(filename__isnull=False) & ~Q(
        filename='')).values('filename').order_by('-id').distinct()

    if request.method == 'POST':
        try:
            totaldata = pd.DataFrame()

            fromdate = request.POST.get('fromdate')
            todate = request.POST.get('todate')
            batchname_filter = request.POST.get('batchname')
            key = request.POST.get('key')

            from datetime import datetime, timedelta

            fromdates = datetime.strptime(fromdate, '%Y-%m-%d')
            todates = datetime.strptime(todate, '%Y-%m-%d')

            date_difference = (todates - fromdates).days

            list_of_dates = [
                fromdates + timedelta(days=i) for i in range(date_difference + 1)]

            formatted_dates = [date.strftime('%Y-%m-%d')
                               for date in list_of_dates]

            question_list = [
                'Questions',
                'Q1: Are the context and query valid?',
                'Q1A: Why is the context or query invalid?',
                'Q2: Does consistency evaluation apply to this answer? Answer 1',
                'Q2A: Why does consistency evaluation not apply to this answer? Answer 1',
                'Q3: Select all types of evidence that you referred to for confirming consistency? Answer 1',
                'Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 1',
                'Q4.1: Are the statements in the answer consistent with details in the product page? Answer 1',
                'Q4.2: Does the answer provide complete information based on the product page? Answer 1',
                'Q4.3: Is the answer consistent with customer reviews? Answer 1',
                'Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 1',
                'Q4.5: Does the answer correctly reference the source of the information? Answer 1',
                'Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 1',
                'Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 1',
                'Q6: Is the answer consistent with common sense or your own knowledge? Answer 1',
                'Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 1',
                'Q7: Which statements lack supporting evidence? Answer 1',
                'Q8: Overall, is the answer consistent? Answer 1',
                'Q8A: If you are unsure about consistency, then what is the reason? Answer 1',
                'Q8B: Please enter any comment? Answer 1',
                'Q2: Does consistency evaluation apply to this answer? Answer 2',
                'Q2A: Why does consistency evaluation not apply to this answer? Answer 2',
                'Q3: Select all types of evidence that you referred to for confirming consistency? Answer 2',
                'Q4: Which sections of the product page did you refer to as evidence for your evaluation? Answer 2',
                'Q4.1: Are the statements in the answer consistent with details in the product page? Answer 2',
                'Q4.2: Does the answer provide complete information based on the product page? Answer 2',
                'Q4.3: Is the answer consistent with customer reviews? Answer 2',
                'Q4.4: Does the answer extract product attribute information from the product page accurately? Answer 2',
                'Q4.5: Does the answer correctly reference the source of the information? Answer 2',
                'Q4.6: Are the summaries for ASINs in the answer consistent with the product pages? Answer 2',
                'Q5.1: Are the statements in the answer consistent with the external sources that you found? Answer 2',
                'Q6: Is the answer consistent with common sense or your own knowledge? Answer 2',
                'Q6.1: Describe the common sense or personal knowledge that applies to this answer? Answer 2',
                'Q7: Which statements lack supporting evidence? Answer 2',
                'Q8: Overall, is the answer consistent? Answer 2',
                'Q8A: If you are unsure about consistency, then what is the reason? Answer 2',
                'Q8B: Please enter any comment? Answer 2'
            ]

            for formatted_date in formatted_dates:
                # iterating for date wise data
                dayvalues = iaa_date_wise(
                    formatted_date, formatted_date, batchname_filter)

                if not dayvalues.empty:

                    totaldata = pd.merge(
                        totaldata, dayvalues, left_index=True, right_index=True, how='right')

            raw_data_query = Q(l1_status="completed",
                               l2_status="completed", l3_status="completed")

            if batchname_filter != "ALL":

                raw_data_query &= Q(baseid__filename=batchname_filter)

            raw_data_query &= Q(
                l1_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(
                l2_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(
                l3_prod__end_time__date__range=(fromdate, todate))

            raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                                                                             'baseid__batch_name',
                                                                             'l1_emp__employeeName',
                                                                             'l1_emp__employeeID',
                                                                             'l2_emp__employeeID',
                                                                             'l1_loc',
                                                                             'l2_emp__employeeName',
                                                                             'l2_loc',
                                                                             'id_value',
                                                                             'question',
                                                                             'asin',
                                                                             'title',
                                                                             'product_url',
                                                                             'imagepath',
                                                                             'evidence',
                                                                             'answer_one',
                                                                             'answer_two',
                                                                             'l1_status',
                                                                             'l2_status',
                                                                             'l4_status',
                                                                             'l3_status',
                                                                             'l1_l2_accuracy',
                                                                            'l1_prod__que1',
                                                                            'l1_prod__que1a',
                                                                            'l1_prod__que2_ans1',
                                                                            'l1_prod__que2a_ans1',
                                                                            'l1_prod__que3_ans1',
                                                                            'l1_prod__que4_ans1',
                                                                            'l1_prod__que4a_ans1',
                                                                            'l1_prod__que4b_ans1',
                                                                            'l1_prod__que4c_ans1',
                                                                            'l1_prod__que4d_ans1',
                                                                            'l1_prod__que4e_ans1',
                                                                            'l1_prod__que4f_ans1',
                                                                            'l1_prod__que5a_ans1',
                                                                            'l1_prod__que6_ans1',
                                                                            'l1_prod__que6a_ans1',
                                                                            'l1_prod__que7_ans1',
                                                                            'l1_prod__que8_ans1',
                                                                            'l1_prod__que8a_ans1',
                                                                            'l1_prod__que8b_ans1',
                                                                            'l1_prod__que2_ans2',
                                                                            'l1_prod__que2a_ans2',
                                                                            'l1_prod__que3_ans2',
                                                                            'l1_prod__que4_ans2',
                                                                            'l1_prod__que4a_ans2',
                                                                            'l1_prod__que4b_ans2',
                                                                            'l1_prod__que4c_ans2',
                                                                            'l1_prod__que4d_ans2',
                                                                            'l1_prod__que4e_ans2',
                                                                            'l1_prod__que4f_ans2',
                                                                            'l1_prod__que5a_ans2',
                                                                            'l1_prod__que6_ans2',
                                                                            'l1_prod__que6a_ans2',
                                                                            'l1_prod__que7_ans2',
                                                                            'l1_prod__que8_ans2',
                                                                            'l1_prod__que8a_ans2',
                                                                            'l1_prod__que8b_ans2',
                                                                            'l2_prod__que1',
                                                                            'l2_prod__que1a',
                                                                            'l2_prod__que2_ans1',
                                                                            'l2_prod__que2a_ans1',
                                                                            'l2_prod__que3_ans1',
                                                                            'l2_prod__que4_ans1',
                                                                            'l2_prod__que4a_ans1',
                                                                            'l2_prod__que4b_ans1',
                                                                            'l2_prod__que4c_ans1',
                                                                            'l2_prod__que4d_ans1',
                                                                            'l2_prod__que4e_ans1',
                                                                            'l2_prod__que4f_ans1',
                                                                            'l2_prod__que5a_ans1',
                                                                            'l2_prod__que6_ans1',
                                                                            'l2_prod__que6a_ans1',
                                                                            'l2_prod__que7_ans1',
                                                                            'l2_prod__que8_ans1',
                                                                            'l2_prod__que8a_ans1',
                                                                            'l2_prod__que8b_ans1',
                                                                            'l2_prod__que2_ans2',
                                                                            'l2_prod__que2a_ans2',
                                                                            'l2_prod__que3_ans2',
                                                                            'l2_prod__que4_ans2',
                                                                            'l2_prod__que4a_ans2',
                                                                            'l2_prod__que4b_ans2',
                                                                            'l2_prod__que4c_ans2',
                                                                            'l2_prod__que4d_ans2',
                                                                            'l2_prod__que4e_ans2',
                                                                            'l2_prod__que4f_ans2',
                                                                            'l2_prod__que5a_ans2',
                                                                            'l2_prod__que6_ans2',
                                                                            'l2_prod__que6a_ans2',
                                                                            'l2_prod__que7_ans2',
                                                                            'l2_prod__que8_ans2',
                                                                            'l2_prod__que8a_ans2',
                                                                            'l2_prod__que8b_ans2',
                                                                            'l3_prod__que1',
                                                                            'l3_prod__que1a',
                                                                            'l3_prod__que2_ans1',
                                                                            'l3_prod__que2a_ans1',
                                                                            'l3_prod__que3_ans1',
                                                                            'l3_prod__que4_ans1',
                                                                            'l3_prod__que4a_ans1',
                                                                            'l3_prod__que4b_ans1',
                                                                            'l3_prod__que4c_ans1',
                                                                            'l3_prod__que4d_ans1',
                                                                            'l3_prod__que4e_ans1',
                                                                            'l3_prod__que4f_ans1',
                                                                            'l3_prod__que5a_ans1',
                                                                            'l3_prod__que6_ans1',
                                                                            'l3_prod__que6a_ans1',
                                                                            'l3_prod__que7_ans1',
                                                                            'l3_prod__que8_ans1',
                                                                            'l3_prod__que8a_ans1',
                                                                            'l3_prod__que8b_ans1',
                                                                            'l3_prod__que2_ans2',
                                                                            'l3_prod__que2a_ans2',
                                                                            'l3_prod__que3_ans2',
                                                                            'l3_prod__que4_ans2',
                                                                            'l3_prod__que4a_ans2',
                                                                            'l3_prod__que4b_ans2',
                                                                            'l3_prod__que4c_ans2',
                                                                            'l3_prod__que4d_ans2',
                                                                            'l3_prod__que4e_ans2',
                                                                            'l3_prod__que4f_ans2',
                                                                            'l3_prod__que5a_ans2',
                                                                            'l3_prod__que6_ans2',
                                                                            'l3_prod__que6a_ans2',
                                                                            'l3_prod__que7_ans2',
                                                                            'l3_prod__que8_ans2',
                                                                            'l3_prod__que8a_ans2',
                                                                            'l3_prod__que8b_ans2')

            result_df = pd.DataFrame(raw_data_values)

            new_columns_list = []

            columns_to_compare = [
                    ( 'l1_prod__que1',    'l2_prod__que1',     'l3_prod__que1' ),
                    ( 'l1_prod__que1a',    'l2_prod__que1a',     'l3_prod__que1a' ),
                    ( 'l1_prod__que2_ans1',    'l2_prod__que2_ans1',     'l3_prod__que2_ans1' ),
                    ( 'l1_prod__que2a_ans1',    'l2_prod__que2a_ans1',     'l3_prod__que2a_ans1' ),
                    ( 'l1_prod__que3_ans1',    'l2_prod__que3_ans1',     'l3_prod__que3_ans1' ),
                    ( 'l1_prod__que4_ans1',    'l2_prod__que4_ans1',     'l3_prod__que4_ans1' ),
                    ( 'l1_prod__que4a_ans1',    'l2_prod__que4a_ans1',     'l3_prod__que4a_ans1' ),
                    ( 'l1_prod__que4b_ans1',    'l2_prod__que4b_ans1',     'l3_prod__que4b_ans1' ),
                    ( 'l1_prod__que4c_ans1',    'l2_prod__que4c_ans1',     'l3_prod__que4c_ans1' ),
                    ( 'l1_prod__que4d_ans1',    'l2_prod__que4d_ans1',     'l3_prod__que4d_ans1' ),
                    ( 'l1_prod__que4e_ans1',    'l2_prod__que4e_ans1',     'l3_prod__que4e_ans1' ),
                    ( 'l1_prod__que4f_ans1',    'l2_prod__que4f_ans1',     'l3_prod__que4f_ans1' ),
                    ( 'l1_prod__que5a_ans1',    'l2_prod__que5a_ans1',     'l3_prod__que5a_ans1' ),
                    ( 'l1_prod__que6_ans1',    'l2_prod__que6_ans1',     'l3_prod__que6_ans1' ),
                    ( 'l1_prod__que6a_ans1',    'l2_prod__que6a_ans1',     'l3_prod__que6a_ans1' ),
                    ( 'l1_prod__que7_ans1',    'l2_prod__que7_ans1',     'l3_prod__que7_ans1' ),
                    ( 'l1_prod__que8_ans1',    'l2_prod__que8_ans1',     'l3_prod__que8_ans1' ),
                    ( 'l1_prod__que8a_ans1',    'l2_prod__que8a_ans1',     'l3_prod__que8a_ans1' ),
                    ( 'l1_prod__que8b_ans1',    'l2_prod__que8b_ans1',     'l3_prod__que8b_ans1' ),
                    ( 'l1_prod__que2_ans2',    'l2_prod__que2_ans2',     'l3_prod__que2_ans2' ),
                    ( 'l1_prod__que2a_ans2',    'l2_prod__que2a_ans2',     'l3_prod__que2a_ans2' ),
                    ( 'l1_prod__que3_ans2',    'l2_prod__que3_ans2',     'l3_prod__que3_ans2' ),
                    ( 'l1_prod__que4_ans2',    'l2_prod__que4_ans2',     'l3_prod__que4_ans2' ),
                    ( 'l1_prod__que4a_ans2',    'l2_prod__que4a_ans2',     'l3_prod__que4a_ans2' ),
                    ( 'l1_prod__que4b_ans2',    'l2_prod__que4b_ans2',     'l3_prod__que4b_ans2' ),
                    ( 'l1_prod__que4c_ans2',    'l2_prod__que4c_ans2',     'l3_prod__que4c_ans2' ),
                    ( 'l1_prod__que4d_ans2',    'l2_prod__que4d_ans2',     'l3_prod__que4d_ans2' ),
                    ( 'l1_prod__que4e_ans2',    'l2_prod__que4e_ans2',     'l3_prod__que4e_ans2' ),
                    ( 'l1_prod__que4f_ans2',    'l2_prod__que4f_ans2',     'l3_prod__que4f_ans2' ),
                    ( 'l1_prod__que5a_ans2',    'l2_prod__que5a_ans2',     'l3_prod__que5a_ans2' ),
                    ( 'l1_prod__que6_ans2',    'l2_prod__que6_ans2',     'l3_prod__que6_ans2' ),
                    ( 'l1_prod__que6a_ans2',    'l2_prod__que6a_ans2',     'l3_prod__que6a_ans2' ),
                    ( 'l1_prod__que7_ans2',    'l2_prod__que7_ans2',     'l3_prod__que7_ans2' ),
                    ( 'l1_prod__que8_ans2',    'l2_prod__que8_ans2',     'l3_prod__que8_ans2' ),
                    ( 'l1_prod__que8a_ans2',    'l2_prod__que8a_ans2',     'l3_prod__que8a_ans2' ),
                    ( 'l1_prod__que8b_ans2',    'l2_prod__que8b_ans2',     'l3_prod__que8b_ans2' )
            ]

            # Loop through each set of three columns and perform the comparison
            for i, (col1, col2, col3) in enumerate(columns_to_compare):
                result_df[f'compare_{i}_l1_l2'] = result_df[col1] == result_df[col2]
                result_df[f'compare_{i}_l1_l3'] = result_df[col1] == result_df[col3]
                result_df[f'compare_{i}_l2_l3'] = result_df[col2] == result_df[col3]
                new_column_col = f'new_column_{i}'
                new_columns_list.append(new_column_col)
                # Add the values
                result_df[f'new_column_{i}'] = (
                    result_df[f'compare_{i}_l1_l2'].astype(int) +
                    result_df[f'compare_{i}_l1_l3'].astype(int) +
                    result_df[f'compare_{i}_l2_l3'].astype(int)
                )

            # Drop the intermediate comparison columns if needed
            result_df = result_df.drop(columns=[f'compare_{i}_l1_l2' for i in range(len(columns_to_compare))] +
                                       [f'compare_{i}_l1_l3' for i in range(len(columns_to_compare))] +
                                       [f'compare_{i}_l2_l3' for i in range(len(columns_to_compare))])

            result_df.loc['Total number of zeros'] = result_df[new_columns_list].eq(
                0).sum()
            result_df.loc['Total number of ones'] = result_df[new_columns_list].eq(
                1).sum()
            result_df.loc['Total number of threes'] = result_df[new_columns_list].eq(
                3).sum()

            result_df.loc['Total of above three'] = result_df.loc['Total number of zeros'] + \
                result_df.loc['Total number of ones'] + \
                result_df.loc['Total number of threes']

            result_df.loc['percentage for '+str(fromdate)+' to '+str(todate)] = (
                (result_df.loc['Total number of ones'] + result_df.loc['Total number of threes']) / result_df.loc['Total of above three']) * 100

            percentage_df = pd.DataFrame(
                result_df.loc['percentage for '+str(fromdate)+' to '+str(todate)]).transpose()

            columns_to_remove = [
                        'l1_status',
                        'l2_status',
                        'l4_status',
                        'l3_status',
                        'l1_l2_accuracy',
                        'l1_prod__que1',
                        'l1_prod__que1a',
                        'l1_prod__que2_ans1',
                        'l1_prod__que2a_ans1',
                        'l1_prod__que3_ans1',
                        'l1_prod__que4_ans1',
                        'l1_prod__que4a_ans1',
                        'l1_prod__que4b_ans1',
                        'l1_prod__que4c_ans1',
                        'l1_prod__que4d_ans1',
                        'l1_prod__que4e_ans1',
                        'l1_prod__que4f_ans1',
                        'l1_prod__que5a_ans1',
                        'l1_prod__que6_ans1',
                        'l1_prod__que6a_ans1',
                        'l1_prod__que7_ans1',
                        'l1_prod__que8_ans1',
                        'l1_prod__que8a_ans1',
                        'l1_prod__que8b_ans1',
                        'l1_prod__que2_ans2',
                        'l1_prod__que2a_ans2',
                        'l1_prod__que3_ans2',
                        'l1_prod__que4_ans2',
                        'l1_prod__que4a_ans2',
                        'l1_prod__que4b_ans2',
                        'l1_prod__que4c_ans2',
                        'l1_prod__que4d_ans2',
                        'l1_prod__que4e_ans2',
                        'l1_prod__que4f_ans2',
                        'l1_prod__que5a_ans2',
                        'l1_prod__que6_ans2',
                        'l1_prod__que6a_ans2',
                        'l1_prod__que7_ans2',
                        'l1_prod__que8_ans2',
                        'l1_prod__que8a_ans2',
                        'l1_prod__que8b_ans2',
                        'l2_prod__que1',
                        'l2_prod__que1a',
                        'l2_prod__que2_ans1',
                        'l2_prod__que2a_ans1',
                        'l2_prod__que3_ans1',
                        'l2_prod__que4_ans1',
                        'l2_prod__que4a_ans1',
                        'l2_prod__que4b_ans1',
                        'l2_prod__que4c_ans1',
                        'l2_prod__que4d_ans1',
                        'l2_prod__que4e_ans1',
                        'l2_prod__que4f_ans1',
                        'l2_prod__que5a_ans1',
                        'l2_prod__que6_ans1',
                        'l2_prod__que6a_ans1',
                        'l2_prod__que7_ans1',
                        'l2_prod__que8_ans1',
                        'l2_prod__que8a_ans1',
                        'l2_prod__que8b_ans1',
                        'l2_prod__que2_ans2',
                        'l2_prod__que2a_ans2',
                        'l2_prod__que3_ans2',
                        'l2_prod__que4_ans2',
                        'l2_prod__que4a_ans2',
                        'l2_prod__que4b_ans2',
                        'l2_prod__que4c_ans2',
                        'l2_prod__que4d_ans2',
                        'l2_prod__que4e_ans2',
                        'l2_prod__que4f_ans2',
                        'l2_prod__que5a_ans2',
                        'l2_prod__que6_ans2',
                        'l2_prod__que6a_ans2',
                        'l2_prod__que7_ans2',
                        'l2_prod__que8_ans2',
                        'l2_prod__que8a_ans2',
                        'l2_prod__que8b_ans2',
                        'l3_prod__que1',
                        'l3_prod__que1a',
                        'l3_prod__que2_ans1',
                        'l3_prod__que2a_ans1',
                        'l3_prod__que3_ans1',
                        'l3_prod__que4_ans1',
                        'l3_prod__que4a_ans1',
                        'l3_prod__que4b_ans1',
                        'l3_prod__que4c_ans1',
                        'l3_prod__que4d_ans1',
                        'l3_prod__que4e_ans1',
                        'l3_prod__que4f_ans1',
                        'l3_prod__que5a_ans1',
                        'l3_prod__que6_ans1',
                        'l3_prod__que6a_ans1',
                        'l3_prod__que7_ans1',
                        'l3_prod__que8_ans1',
                        'l3_prod__que8a_ans1',
                        'l3_prod__que8b_ans1',
                        'l3_prod__que2_ans2',
                        'l3_prod__que2a_ans2',
                        'l3_prod__que3_ans2',
                        'l3_prod__que4_ans2',
                        'l3_prod__que4a_ans2',
                        'l3_prod__que4b_ans2',
                        'l3_prod__que4c_ans2',
                        'l3_prod__que4d_ans2',
                        'l3_prod__que4e_ans2',
                        'l3_prod__que4f_ans2',
                        'l3_prod__que5a_ans2',
                        'l3_prod__que6_ans2',
                        'l3_prod__que6a_ans2',
                        'l3_prod__que7_ans2',
                        'l3_prod__que8_ans2',
                        'l3_prod__que8a_ans2',
                        'l3_prod__que8b_ans2'
            ]

            percentage_df = percentage_df.drop(columns=columns_to_remove)

            percentage_df.reset_index(inplace=True)

            melted_percentage_df = pd.melt(percentage_df)

            totaldata = pd.merge(
                totaldata, melted_percentage_df['value'], left_index=True, right_index=True, how='right')

            totaldata['questions'] = question_list[:len(totaldata)]

            totaldata.columns = totaldata.iloc[0]

            totaldata = totaldata[1:].reset_index(drop=True)

            totaldata.index = np.arange(1, len(totaldata) + 1)

            totaldata = totaldata[[
                'Questions'] + [col for col in totaldata.columns if col != 'Questions']]

            # Convert all decimal values to floats with 2 decimal places
            totaldata.iloc[:, 1:] = totaldata.iloc[:,
                                                   1:].astype(float).round(2)

            # Assuming your DataFrame is named df
            num_columns = totaldata.shape[1]

            totaldata.loc['OVER ALL'] = None

            # print(f"The number of columns in the DataFrame is: {num_columns}")

            for i in range(1, num_columns):  # Loop from 1 to 10
                average_value = round(totaldata.iloc[:, i].mean(), 2)
                print(
                    f"The average value of column {totaldata.columns[i]} is: {average_value}")
                totaldata.loc['OVER ALL', totaldata.columns[i]] = average_value

            totaldata = totaldata.apply(format_columns, axis=0)

            if key == 'Download':

                csv_data = totaldata.to_csv(index=True, encoding='utf-8')

                response = HttpResponse(csv_data, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'
                return response

            else:
                # print(totaldata)
                tabledata = totaldata.to_html().replace('<table border="1" class="dataframe">', '<table id="dftable" class="table table-hover">').replace('<thead>',
                                                                                                                                                          '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                return render(request, 'pages/iaa.html', {'batchname': batchname, 'tabledata': tabledata})
        except Exception as e:
            return render(request, 'pages/iaa.html', {'batchname': batchname})

    return render(request, 'pages/iaa.html', {'batchname': batchname})


def iaa_date_wise(fromdate, todate, batchname_filter):
    raw_data_query = Q(l1_status="completed",
                       l2_status="completed", l3_status="completed")

    if batchname_filter != "ALL":

        raw_data_query &= Q(baseid__filename=batchname_filter)

    raw_data_query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
    raw_data_query &= Q(l2_prod__end_time__date__range=(fromdate, todate))
    raw_data_query &= Q(l3_prod__end_time__date__range=(fromdate, todate))

    raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                                                                             'baseid__batch_name',
                                                                             'l1_emp__employeeName',
                                                                             'l1_emp__employeeID',
                                                                             'l2_emp__employeeID',
                                                                             'l1_loc',
                                                                             'l2_emp__employeeName',
                                                                             'l2_loc',
                                                                             'id_value',
                                                                             'question',
                                                                             'asin',
                                                                             'title',
                                                                             'product_url',
                                                                             'imagepath',
                                                                             'evidence',
                                                                             'answer_one',
                                                                             'answer_two',
                                                                             'l1_status',
                                                                             'l2_status',
                                                                             'l4_status',
                                                                             'l3_status',
                                                                             'l1_l2_accuracy',
                                                                            'l1_prod__que1',
                                                                            'l1_prod__que1a',
                                                                            'l1_prod__que2_ans1',
                                                                            'l1_prod__que2a_ans1',
                                                                            'l1_prod__que3_ans1',
                                                                            'l1_prod__que4_ans1',
                                                                            'l1_prod__que4a_ans1',
                                                                            'l1_prod__que4b_ans1',
                                                                            'l1_prod__que4c_ans1',
                                                                            'l1_prod__que4d_ans1',
                                                                            'l1_prod__que4e_ans1',
                                                                            'l1_prod__que4f_ans1',
                                                                            'l1_prod__que5a_ans1',
                                                                            'l1_prod__que6_ans1',
                                                                            'l1_prod__que6a_ans1',
                                                                            'l1_prod__que7_ans1',
                                                                            'l1_prod__que8_ans1',
                                                                            'l1_prod__que8a_ans1',
                                                                            'l1_prod__que8b_ans1',
                                                                            'l1_prod__que2_ans2',
                                                                            'l1_prod__que2a_ans2',
                                                                            'l1_prod__que3_ans2',
                                                                            'l1_prod__que4_ans2',
                                                                            'l1_prod__que4a_ans2',
                                                                            'l1_prod__que4b_ans2',
                                                                            'l1_prod__que4c_ans2',
                                                                            'l1_prod__que4d_ans2',
                                                                            'l1_prod__que4e_ans2',
                                                                            'l1_prod__que4f_ans2',
                                                                            'l1_prod__que5a_ans2',
                                                                            'l1_prod__que6_ans2',
                                                                            'l1_prod__que6a_ans2',
                                                                            'l1_prod__que7_ans2',
                                                                            'l1_prod__que8_ans2',
                                                                            'l1_prod__que8a_ans2',
                                                                            'l1_prod__que8b_ans2',
                                                                            'l2_prod__que1',
                                                                            'l2_prod__que1a',
                                                                            'l2_prod__que2_ans1',
                                                                            'l2_prod__que2a_ans1',
                                                                            'l2_prod__que3_ans1',
                                                                            'l2_prod__que4_ans1',
                                                                            'l2_prod__que4a_ans1',
                                                                            'l2_prod__que4b_ans1',
                                                                            'l2_prod__que4c_ans1',
                                                                            'l2_prod__que4d_ans1',
                                                                            'l2_prod__que4e_ans1',
                                                                            'l2_prod__que4f_ans1',
                                                                            'l2_prod__que5a_ans1',
                                                                            'l2_prod__que6_ans1',
                                                                            'l2_prod__que6a_ans1',
                                                                            'l2_prod__que7_ans1',
                                                                            'l2_prod__que8_ans1',
                                                                            'l2_prod__que8a_ans1',
                                                                            'l2_prod__que8b_ans1',
                                                                            'l2_prod__que2_ans2',
                                                                            'l2_prod__que2a_ans2',
                                                                            'l2_prod__que3_ans2',
                                                                            'l2_prod__que4_ans2',
                                                                            'l2_prod__que4a_ans2',
                                                                            'l2_prod__que4b_ans2',
                                                                            'l2_prod__que4c_ans2',
                                                                            'l2_prod__que4d_ans2',
                                                                            'l2_prod__que4e_ans2',
                                                                            'l2_prod__que4f_ans2',
                                                                            'l2_prod__que5a_ans2',
                                                                            'l2_prod__que6_ans2',
                                                                            'l2_prod__que6a_ans2',
                                                                            'l2_prod__que7_ans2',
                                                                            'l2_prod__que8_ans2',
                                                                            'l2_prod__que8a_ans2',
                                                                            'l2_prod__que8b_ans2',
                                                                            'l3_prod__que1',
                                                                            'l3_prod__que1a',
                                                                            'l3_prod__que2_ans1',
                                                                            'l3_prod__que2a_ans1',
                                                                            'l3_prod__que3_ans1',
                                                                            'l3_prod__que4_ans1',
                                                                            'l3_prod__que4a_ans1',
                                                                            'l3_prod__que4b_ans1',
                                                                            'l3_prod__que4c_ans1',
                                                                            'l3_prod__que4d_ans1',
                                                                            'l3_prod__que4e_ans1',
                                                                            'l3_prod__que4f_ans1',
                                                                            'l3_prod__que5a_ans1',
                                                                            'l3_prod__que6_ans1',
                                                                            'l3_prod__que6a_ans1',
                                                                            'l3_prod__que7_ans1',
                                                                            'l3_prod__que8_ans1',
                                                                            'l3_prod__que8a_ans1',
                                                                            'l3_prod__que8b_ans1',
                                                                            'l3_prod__que2_ans2',
                                                                            'l3_prod__que2a_ans2',
                                                                            'l3_prod__que3_ans2',
                                                                            'l3_prod__que4_ans2',
                                                                            'l3_prod__que4a_ans2',
                                                                            'l3_prod__que4b_ans2',
                                                                            'l3_prod__que4c_ans2',
                                                                            'l3_prod__que4d_ans2',
                                                                            'l3_prod__que4e_ans2',
                                                                            'l3_prod__que4f_ans2',
                                                                            'l3_prod__que5a_ans2',
                                                                            'l3_prod__que6_ans2',
                                                                            'l3_prod__que6a_ans2',
                                                                            'l3_prod__que7_ans2',
                                                                            'l3_prod__que8_ans2',
                                                                            'l3_prod__que8a_ans2',
                                                                            'l3_prod__que8b_ans2')


    result_df = pd.DataFrame(raw_data_values)

    if result_df.empty:

        return result_df

    new_columns_list = []

    columns_to_compare = [
                    ( 'l1_prod__que1',    'l2_prod__que1',     'l3_prod__que1' ),
                    ( 'l1_prod__que1a',    'l2_prod__que1a',     'l3_prod__que1a' ),
                    ( 'l1_prod__que2_ans1',    'l2_prod__que2_ans1',     'l3_prod__que2_ans1' ),
                    ( 'l1_prod__que2a_ans1',    'l2_prod__que2a_ans1',     'l3_prod__que2a_ans1' ),
                    ( 'l1_prod__que3_ans1',    'l2_prod__que3_ans1',     'l3_prod__que3_ans1' ),
                    ( 'l1_prod__que4_ans1',    'l2_prod__que4_ans1',     'l3_prod__que4_ans1' ),
                    ( 'l1_prod__que4a_ans1',    'l2_prod__que4a_ans1',     'l3_prod__que4a_ans1' ),
                    ( 'l1_prod__que4b_ans1',    'l2_prod__que4b_ans1',     'l3_prod__que4b_ans1' ),
                    ( 'l1_prod__que4c_ans1',    'l2_prod__que4c_ans1',     'l3_prod__que4c_ans1' ),
                    ( 'l1_prod__que4d_ans1',    'l2_prod__que4d_ans1',     'l3_prod__que4d_ans1' ),
                    ( 'l1_prod__que4e_ans1',    'l2_prod__que4e_ans1',     'l3_prod__que4e_ans1' ),
                    ( 'l1_prod__que4f_ans1',    'l2_prod__que4f_ans1',     'l3_prod__que4f_ans1' ),
                    ( 'l1_prod__que5a_ans1',    'l2_prod__que5a_ans1',     'l3_prod__que5a_ans1' ),
                    ( 'l1_prod__que6_ans1',    'l2_prod__que6_ans1',     'l3_prod__que6_ans1' ),
                    ( 'l1_prod__que6a_ans1',    'l2_prod__que6a_ans1',     'l3_prod__que6a_ans1' ),
                    ( 'l1_prod__que7_ans1',    'l2_prod__que7_ans1',     'l3_prod__que7_ans1' ),
                    ( 'l1_prod__que8_ans1',    'l2_prod__que8_ans1',     'l3_prod__que8_ans1' ),
                    ( 'l1_prod__que8a_ans1',    'l2_prod__que8a_ans1',     'l3_prod__que8a_ans1' ),
                    ( 'l1_prod__que8b_ans1',    'l2_prod__que8b_ans1',     'l3_prod__que8b_ans1' ),
                    ( 'l1_prod__que2_ans2',    'l2_prod__que2_ans2',     'l3_prod__que2_ans2' ),
                    ( 'l1_prod__que2a_ans2',    'l2_prod__que2a_ans2',     'l3_prod__que2a_ans2' ),
                    ( 'l1_prod__que3_ans2',    'l2_prod__que3_ans2',     'l3_prod__que3_ans2' ),
                    ( 'l1_prod__que4_ans2',    'l2_prod__que4_ans2',     'l3_prod__que4_ans2' ),
                    ( 'l1_prod__que4a_ans2',    'l2_prod__que4a_ans2',     'l3_prod__que4a_ans2' ),
                    ( 'l1_prod__que4b_ans2',    'l2_prod__que4b_ans2',     'l3_prod__que4b_ans2' ),
                    ( 'l1_prod__que4c_ans2',    'l2_prod__que4c_ans2',     'l3_prod__que4c_ans2' ),
                    ( 'l1_prod__que4d_ans2',    'l2_prod__que4d_ans2',     'l3_prod__que4d_ans2' ),
                    ( 'l1_prod__que4e_ans2',    'l2_prod__que4e_ans2',     'l3_prod__que4e_ans2' ),
                    ( 'l1_prod__que4f_ans2',    'l2_prod__que4f_ans2',     'l3_prod__que4f_ans2' ),
                    ( 'l1_prod__que5a_ans2',    'l2_prod__que5a_ans2',     'l3_prod__que5a_ans2' ),
                    ( 'l1_prod__que6_ans2',    'l2_prod__que6_ans2',     'l3_prod__que6_ans2' ),
                    ( 'l1_prod__que6a_ans2',    'l2_prod__que6a_ans2',     'l3_prod__que6a_ans2' ),
                    ( 'l1_prod__que7_ans2',    'l2_prod__que7_ans2',     'l3_prod__que7_ans2' ),
                    ( 'l1_prod__que8_ans2',    'l2_prod__que8_ans2',     'l3_prod__que8_ans2' ),
                    ( 'l1_prod__que8a_ans2',    'l2_prod__que8a_ans2',     'l3_prod__que8a_ans2' ),
                    ( 'l1_prod__que8b_ans2',    'l2_prod__que8b_ans2',     'l3_prod__que8b_ans2' )
    ]

    # Loop through each set of three columns and perform the comparison
    for i, (col1, col2, col3) in enumerate(columns_to_compare):
        result_df[f'compare_{i}_l1_l2'] = result_df[col1] == result_df[col2]
        result_df[f'compare_{i}_l1_l3'] = result_df[col1] == result_df[col3]
        result_df[f'compare_{i}_l2_l3'] = result_df[col2] == result_df[col3]
        new_column_col = f'new_column_{i}'
        new_columns_list.append(new_column_col)
        # Add the values
        result_df[f'new_column_{i}'] = (
            result_df[f'compare_{i}_l1_l2'].astype(int) +
            result_df[f'compare_{i}_l1_l3'].astype(int) +
            result_df[f'compare_{i}_l2_l3'].astype(int)
        )

    # Drop the intermediate comparison columns if needed
    result_df = result_df.drop(columns=[f'compare_{i}_l1_l2' for i in range(len(columns_to_compare))] +
                               [f'compare_{i}_l1_l3' for i in range(len(columns_to_compare))] +
                               [f'compare_{i}_l2_l3' for i in range(len(columns_to_compare))])

    result_df.loc['Total number of zeros'] = result_df[new_columns_list].eq(
        0).sum()
    result_df.loc['Total number of ones'] = result_df[new_columns_list].eq(
        1).sum()
    result_df.loc['Total number of threes'] = result_df[new_columns_list].eq(
        3).sum()

    result_df.loc['Total of above three'] = result_df.loc['Total number of zeros'] + \
        result_df.loc['Total number of ones'] + \
        result_df.loc['Total number of threes']

    result_df.loc['percentage for '+str(fromdate)] = ((result_df.loc['Total number of ones'] +
                                                       result_df.loc['Total number of threes']) / result_df.loc['Total of above three']) * 100

    percentage_df = pd.DataFrame(
        result_df.loc['percentage for '+str(fromdate)]).transpose()

    columns_to_remove = [
                        'l1_status',
                        'l2_status',
                        'l4_status',
                        'l3_status',
                        'l1_l2_accuracy',
                        'l1_prod__que1',
                        'l1_prod__que1a',
                        'l1_prod__que2_ans1',
                        'l1_prod__que2a_ans1',
                        'l1_prod__que3_ans1',
                        'l1_prod__que4_ans1',
                        'l1_prod__que4a_ans1',
                        'l1_prod__que4b_ans1',
                        'l1_prod__que4c_ans1',
                        'l1_prod__que4d_ans1',
                        'l1_prod__que4e_ans1',
                        'l1_prod__que4f_ans1',
                        'l1_prod__que5a_ans1',
                        'l1_prod__que6_ans1',
                        'l1_prod__que6a_ans1',
                        'l1_prod__que7_ans1',
                        'l1_prod__que8_ans1',
                        'l1_prod__que8a_ans1',
                        'l1_prod__que8b_ans1',
                        'l1_prod__que2_ans2',
                        'l1_prod__que2a_ans2',
                        'l1_prod__que3_ans2',
                        'l1_prod__que4_ans2',
                        'l1_prod__que4a_ans2',
                        'l1_prod__que4b_ans2',
                        'l1_prod__que4c_ans2',
                        'l1_prod__que4d_ans2',
                        'l1_prod__que4e_ans2',
                        'l1_prod__que4f_ans2',
                        'l1_prod__que5a_ans2',
                        'l1_prod__que6_ans2',
                        'l1_prod__que6a_ans2',
                        'l1_prod__que7_ans2',
                        'l1_prod__que8_ans2',
                        'l1_prod__que8a_ans2',
                        'l1_prod__que8b_ans2',
                        'l2_prod__que1',
                        'l2_prod__que1a',
                        'l2_prod__que2_ans1',
                        'l2_prod__que2a_ans1',
                        'l2_prod__que3_ans1',
                        'l2_prod__que4_ans1',
                        'l2_prod__que4a_ans1',
                        'l2_prod__que4b_ans1',
                        'l2_prod__que4c_ans1',
                        'l2_prod__que4d_ans1',
                        'l2_prod__que4e_ans1',
                        'l2_prod__que4f_ans1',
                        'l2_prod__que5a_ans1',
                        'l2_prod__que6_ans1',
                        'l2_prod__que6a_ans1',
                        'l2_prod__que7_ans1',
                        'l2_prod__que8_ans1',
                        'l2_prod__que8a_ans1',
                        'l2_prod__que8b_ans1',
                        'l2_prod__que2_ans2',
                        'l2_prod__que2a_ans2',
                        'l2_prod__que3_ans2',
                        'l2_prod__que4_ans2',
                        'l2_prod__que4a_ans2',
                        'l2_prod__que4b_ans2',
                        'l2_prod__que4c_ans2',
                        'l2_prod__que4d_ans2',
                        'l2_prod__que4e_ans2',
                        'l2_prod__que4f_ans2',
                        'l2_prod__que5a_ans2',
                        'l2_prod__que6_ans2',
                        'l2_prod__que6a_ans2',
                        'l2_prod__que7_ans2',
                        'l2_prod__que8_ans2',
                        'l2_prod__que8a_ans2',
                        'l2_prod__que8b_ans2',
                        'l3_prod__que1',
                        'l3_prod__que1a',
                        'l3_prod__que2_ans1',
                        'l3_prod__que2a_ans1',
                        'l3_prod__que3_ans1',
                        'l3_prod__que4_ans1',
                        'l3_prod__que4a_ans1',
                        'l3_prod__que4b_ans1',
                        'l3_prod__que4c_ans1',
                        'l3_prod__que4d_ans1',
                        'l3_prod__que4e_ans1',
                        'l3_prod__que4f_ans1',
                        'l3_prod__que5a_ans1',
                        'l3_prod__que6_ans1',
                        'l3_prod__que6a_ans1',
                        'l3_prod__que7_ans1',
                        'l3_prod__que8_ans1',
                        'l3_prod__que8a_ans1',
                        'l3_prod__que8b_ans1',
                        'l3_prod__que2_ans2',
                        'l3_prod__que2a_ans2',
                        'l3_prod__que3_ans2',
                        'l3_prod__que4_ans2',
                        'l3_prod__que4a_ans2',
                        'l3_prod__que4b_ans2',
                        'l3_prod__que4c_ans2',
                        'l3_prod__que4d_ans2',
                        'l3_prod__que4e_ans2',
                        'l3_prod__que4f_ans2',
                        'l3_prod__que5a_ans2',
                        'l3_prod__que6_ans2',
                        'l3_prod__que6a_ans2',
                        'l3_prod__que7_ans2',
                        'l3_prod__que8_ans2',
                        'l3_prod__que8a_ans2',
                        'l3_prod__que8b_ans2'
    ]

    percentage_df = percentage_df.drop(columns=columns_to_remove)

    percentage_df.reset_index(inplace=True)

    melted_percentage_df = pd.melt(percentage_df)

    return melted_percentage_df['value']


