from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import Device, Log
import paramiko
import time
from datetime import datetime
import os
import os.path


def home(request):
    all_device = Device.objects.all()
    cisco_device = Device.objects.filter(vendor="cisco")
    mikrotik_device = Device.objects.filter(vendor="mikrotik")
    ransnet_device = Device.objects.filter(vendor="ransnet")
    last_event = Log.objects.all().order_by('-id')[:10]

    context = {
        'all_device': len(all_device),
        'cisco_device': len(cisco_device),
        'mikrotik_device': len(mikrotik_device),
        'ransnet_device': len(ransnet_device),
        'last_event': last_event,
        'no' : 1
    }
    return render(request, 'home.html', context)

def devices(request):
    all_device = Device.objects.all()

    context = {
        'all_device': all_device
    }

    return render(request, 'devices.html', context)

def configure(request):
    if request.method == "POST":
        selected_device_id = request.POST.getlist('device')
        mikrotik_command = request.POST['mikrotik_command'].splitlines()
        cisco_command = request.POST['cisco_command'].splitlines()
        ransnet_command = request.POST['ransnet_command'].splitlines()
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)

                if dev.vendor.lower() == 'cisco':
                    conn = ssh_client.invoke_shell()
                    conn.send("conf t\n")
                    for cmd in cisco_command:
                        conn.send(cmd + "\n")
                        time.sleep(1)

                elif dev.vendor.lower() == 'ransnet':
                    conn = ssh_client.invoke_shell()
                    conn.send("enable\n")
                    time.sleep(1)
                    conn.send("Letmein99\n")
                    time.sleep(1)
                    conn.send("configure\n")
                    for cmd in ransnet_command:
                        conn.send(cmd + "\n")
                        time.sleep(1)
                else:
                    for cmd in mikrotik_command:
                        ssh_client.exec_command(cmd)
                log = Log(target=dev.ip_address, action="Configure", status="Success", time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action="Configure", status="Error", time=datetime.now(), messages=e)
                log.save()
        
        return redirect('home')

    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'Configure'
        }
        return render(request, 'config.html', context)

def verify_config(request):
    if request.method == "POST":
        result = []
        selected_device_id = request.POST.getlist('device')
        mikrotik_command = request.POST['mikrotik_command'].splitlines()
        cisco_command = request.POST['cisco_command'].splitlines()
        ransnet_command = request.POST['ransnet_command'].splitlines()
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)

                if dev.vendor.lower() == 'mikrotik':
                    for cmd in mikrotik_command:
                        stdin,stdout,stderr = ssh_client.exec_command(cmd)
                        result.append("Result on {}".format(dev.ip_address))
                        result.append(stdout.read().decode())
                
                elif dev.vendor.lower() == 'ransnet':
                    conn = ssh_client.invoke_shell()
                    conn.send("enable\n")
                    time.sleep(1)
                    conn.send("Letmein99\n")
                    time.sleep(1)
                    for cmd in ransnet_command:
                        conn.send(cmd + "\n")
                        time.sleep(1)
                        output = conn.recv(65535)
                        result.append(output.decode())

                else:
                    conn = ssh_client.invoke_shell()
                    conn.send('terminal length 0\n')
                    for cmd in cisco_command:
                        result.append("Result On {}".format(dev.ip_address))
                        conn.send(cmd + "\n")
                        time.sleep(1)
                        output = conn.recv(65535)
                        result.append(output.decode())
                log = Log(target=dev.ip_address, action="Verify Config", status="Success", time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action="Verify Config", status="Error", time=datetime.now(), messages=e)
                log.save()
        
        result = '\n'.join(result)
        return render(request, 'verify_result.html', {'result':result})

    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'verify config'
        }
        return render(request, 'config.html', context)


def log(request):
    logs = Log.objects.all().order_by('-id')[:10]

    context = {
        'logs': logs
    }

    return render(request, 'log.html', context)

def save_config(request):
    waktu = datetime.now()
    waktuku = waktu.strftime("%d-%B-%Y")
    save_path = 'backup'
    if request.method == "POST":
        selected_device_id = request.POST.getlist('device')
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)

                if dev.vendor.lower() == 'cisco':
                    conn = ssh_client.invoke_shell()
                    conn.send("terminal length 0\n")
                    time.sleep(1)
                    conn.send("show running-config\n")
                    time.sleep(1)

                    output = conn.recv(65535)
                    output_final = output.decode()
                    namafile = os.path.join(save_path, dev.ip_address+"-"+waktuku+".txt")
                    savefile = open(namafile, "w")
                    savefile.write(output_final)
                    savefile.close

                elif dev.vendor.lower() == 'ransnet':
                    conn = ssh_client.invoke_shell()
                    conn.send("enable\n")
                    time.sleep(1)
                    conn.send("Letmein99\n")
                    time.sleep(1)
                    conn.send("show running-config\n")
                    time.sleep(1)

                    output = conn.recv(65535)
                    output_final = output.decode()
                    namafile = os.path.join(save_path, dev.ip_address+"-"+waktuku+".txt")
                    savefile = open(namafile, "w")
                    savefile.write(output_final)
                    savefile.close
                    
                else:
                    stdin, stdout, stderr = ssh_client.exec_command("export")
                    output_final = stdout.readlines()
                    namafile = os.path.join(save_path, dev.ip_address+"-"+waktuku+".txt")
                    savefile = open(namafile, "w")
                    savefile.write(output_final)
                    savefile.close

                log = Log(target=dev.ip_address, action="Configure", status="Success", time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action="Configure", status="Error", time=datetime.now(), messages=e)
                log.save()
        
        return redirect('home')

    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'save config'
        }
        return render(request, 'save.html', context)
