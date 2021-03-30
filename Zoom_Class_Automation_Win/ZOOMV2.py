##zoommtg://zoom.us/join?confno=5507412297&pwd=011990
from datetime import datetime
import subprocess
from time import sleep
import pyodbc
import sys
drv=r"{Microsoft Access Driver (*.mdb, *.accdb)}"
path=r".\ZOOM.accdb;"
conn = pyodbc.connect(driver=drv,dbq=path,autocommit=True)
cursor = conn.cursor()

DELAY=180

def isMeetingOpen():
    nm1="Zoom Meeting 40-Minutes*"
    nm2="Zoom Meeting"
    err="INFO: No tasks are running which match the specified criteria.\n"
    cmd=r'tasklist /FI "WiNDOWTITLE eq {}"'
    cmd2=r'''for /f "tokens=10 delims=," %F in ('tasklist /v /fi "imagename eq zoom.exe" /fo csv') do @echo %~F'''
    r1=subprocess.run(cmd.format(nm1), shell=True, capture_output=True, text=True).stdout
    r2=subprocess.run(cmd.format(nm2), shell=True, capture_output=True, text=True).stdout
    r3=subprocess.run(cmd2, shell=True, capture_output=True, text=True).stdout
    if(r1==err and r2==err):
        print(r3)
    return not (r1==err and r2==err)

def GetID(sub):
    cursor.execute("SELECT * FROM IDS WHERE SUB='{}'".format(sub))
    return cursor.fetchall()[0]


def JoinMeeting(sub):
    data=GetID(sub)
    print("Joining "+data[0]+" Class, "+data[3])
    cmd='start %zoom% --url="zoommtg://zoom.us/join?confno={0}&pwd={1}"'.format(data[1],data[2])
    subprocess.run(cmd, shell=True)
    

def GetSub(day,time):
    sql='''
        SELECT TOP 1 *
        FROM {0}
        WHERE TME>'{1}'
        ORDER BY TME
    '''
    cursor.execute(sql.format(day,time))
    data=cursor.fetchall()
    if(len(data)):
        return data[0]
    return data

def GetOverride():
    a=[]
    try:
        file = open(r".\ZOOM.txt","r")
        a=file.read().split()
        file.close()
        if(a[0]!='P' and a[0]!='F' and len(a)!=2):
            a=[]
    except:
        print(end="")
    return a

def GetTime(frmt):
    return datetime.now().strftime(frmt)

def ChkMeeting():
    print('Checking if meeting is open')
    if(not isMeetingOpen()):
        print("No meeting is open!!")
        print("Checking for overrides")
        override=GetOverride()
        flag=False
        if(len(override)==2):
            if(override[0]=='F'):
                print("Forced override found!")
                return GetTime("%H%M"), override[1]
            elif(override[0]=='P'):
                print("Passive override found!")
                flag=True
        else:
            print("No override found!")
        print("Checking Schedule...")
        Subject=GetSub(GetTime("%a"),GetTime("%H%M"))
        if(len(Subject)==0):
            print("No more meetings!! exiting program.")
            sys.exit("NO MEETINGS FOUND")
        if(flag):
            if(override[1]=="Free"):
                return Subject[1],override[1]
            return Subject[0],override[1]
        if(Subject[2]=="Free"):
            return Subject[1],Subject[2]
        return Subject[0],Subject[2]
    else:
        print("Meeting already running!!")
        return "0000","Delay"

def timeDiff(T1,T2):
    STT=datetime.strptime
    tdiff=STT(T2,"%H%M")-STT(T1,"%H%M%S")
    return tdiff.total_seconds()

while(1):
    print("[ LOG "+datetime.now().strftime("%x %X")+" ]")
    time,cls=ChkMeeting()
    if(cls!="Delay"):
        if(time>GetTime("%H%M")):
            freedelay=timeDiff(GetTime("%H%M%S"),time)
            print("Free period, delaying until next class, ("+str(freedelay)+" seconds)...")
            sleep(freedelay)
            print()
            if(cls=="Free"):
               continue
            print("[ LOG "+datetime.now().strftime("%x %X")+" ]")
        JoinMeeting(cls)
    print("Delaying for "+str(DELAY)+" seconds")
    sleep(DELAY)
    print()
