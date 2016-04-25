#!/usr/bin/python
#needs pip install schedule
import json
import sys
import threading
import os
import subprocess
import signal
import commands
import collections
import logging
from or_class import *
import MySQLdb
import argparse
import fnmatch
import syslog
#Global definitions
global configfile
global databasefile

global ctrl_obj
global probe_obj
global database_obj
global startuplist
global msg
global controllercounter
global probecounter
global dbcounter
global dbcondition


#controller
ctrl_obj = []
probe_obj = []
database_obj = []
startuplist = {}
dirtmp="/tmp/"
dbcondition=0





# progressbar
def progressbar(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s -->%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben

def cls():
    os.system('cls' if os.name=='nt' else 'clear')



def banner():

    print " ___         _              ___             _   _              ___         _           _ _    "
    print "| _ \__ _ __| |__ _ _ _ ___| _ \___ __ _ __| |_(_)_ _____ ___ / __|___ _ _| |_ _ _ ___| | |___ _ _"
    print "|   / _` / _` / _` | '_|___|   / -_) _` / _|  _| \ V / -_)___| (__/ _ \ ' \  _| '_/ _ \ | / -_) '_|"
    print "|_|_\__,_\__,_\__,_|_|     |_|_\___\__,_\__|\__|_|\_/\___|    \___\___/_||_\__|_| \___/_|_\___|_|"






# loadconfig
def loadconfig( jsonfile ):

        #In-ram configuration
        global inram_configuration

        try:


           with open(jsonfile) as data_file:
               inram_configuration = json.load(data_file)

        except IOError as e:

            print "\nno go:We got a probelm..I'm looking for "+jsonfile+" but I can't find th file for please check.\n"

        except:

            print "\nno go:The "+jsonfile+" file is not correct , please check the syntax and/or file logic\n"
            raise

        return True






def checkduplicatescontroller(cid):

    d=0

    for k in range(0,controllercounter):



        if cid == ctrl_obj[k].controllername_id:

                d+=1
                if d > 1:
                    print "\n\nnogo: The controllername_id must be unique , I have found some duplicates on "+ctrl_obj[k].controllername_id
                    return True
    k +=1


def checkduplicatesprobe(pid):

    d=0

    for k in range(0,probecounter):



        if pid == probe_obj[k].probename_id:

                d+=1
                if d > 1:
                    print "\n\nnogo: The probename_id must be unique , I have found some duplicates on "+probe_obj[k].probename_id
                    return True
    k +=1


def checkduplicatesdatabase(did):

    d=0

    for k in range(0,dbcounter):



        if did == database_obj[k].database_id:

                d+=1
                if d > 1:
                    print "\n\nnogo: The database_id must be unique , I have found some duplicates on "+database_obj[k].database_id
                    return True
    k +=1



# buildobcject
def objectbuilder():
    global controllercounter
    global probecounter
    controllercounter = 0
    probecounter = 0
    abs_probeindex=0
    lastresult=""
    try:

        #check for controller

        for row_ctrl in inram_configuration['controllerset']:

            #Creating controller object totalprobes will be update leater now is 1
             #Setting total number of probe


            totalprobes=json.dumps(row_ctrl['probeset']).count("probename_id")

            ctrl_obj.append(Controller(
            row_ctrl['controllername_id'],
            row_ctrl['condition'],
            row_ctrl['expected_value'],
            parsecommand(row_ctrl['ifsatisfied_action']),
            parsecommand(row_ctrl['ifnotsatisfied_action']),
            row_ctrl['repeat_ifsatisfied_action'],
            row_ctrl['repeat_ifnotsatisfied_action'],
            row_ctrl['rearm_after'],
            parsecommand(row_ctrl['rearm_action']),
            totalprobes,controllercounter,lastresult))

            controllercounter +=1
            pbindex=0
            lastresult=""
            for pbindex in range(0,totalprobes):

                probe_obj.append(Probe(
                row_ctrl['probeset'][pbindex]['probename_id'],
                row_ctrl['probeset'][pbindex]['sql'],
                row_ctrl['probeset'][pbindex]['sqlengine'],
                parsecommand(row_ctrl['probeset'][pbindex]['probefile']),
                controllercounter-1,pbindex,abs_probeindex,lastresult))
                pbindex +=1
                probecounter +=1
                abs_probeindex +=1

                #Go to the next probe

        #Public value


        return True
    except KeyError:

            print "\n\nnogo: The configuration file "+configfile+" seem has logical corrupted prbably some fields are disappeared\n"

    except:

            print "\n\nnogo: oops some problem occured during validation checking process\n"
    raise


    return True




def dbobjectbuilder():
    global dbcounter

    dbcounter = 0

    try:



        for row_ctrl in inram_configuration['databases']:


            database_obj.append(Dbengine(
            row_ctrl['database_id'],
            row_ctrl['dbengine'],
            row_ctrl['host'],
            row_ctrl['database'],
            row_ctrl['username'],
            row_ctrl['password']
            ,dbcounter))

            dbcounter +=1


        return True
    except KeyError:

            print "\n\nnogo: The configuration file "+databasefile+" seem has logical corrupted prbably some fields are disappeared\n"

    except:

            print "\n\nnogo: oops some problem occured during validation checking process\n"
    raise


    return True



def chkrange(c,val,min,max,attribute):
    if (val >= min) and (val <= max) :
        return True
    else:
        print "\n\nnogo: The "+attribute+"is set to "+str(val)+" on "+ctrl_obj[c].controllername_id+" but must be => "+str(min)+" and <= "+str(max)+" secons\n"

        return False

def chkoptions(c,val,options,attribute):
    if "null" in options and val == "":
        return True
    else:
        if (val in options) and val:
            return True
        else:
            print "\n\nnogo: The "+attribute+" needs to be "+options+"\n"

            return False




def chkfile(filename,section):
    #ignoring paramenters


        filename =filename.split(' ',1)[0].replace("\"","")
        if ((os.path.exists(filename) and os.access(filename, os.X_OK)) and (filename.find("/") != -1)) or filename =="" :

            return True

        else:

            print "\n\nnogo: The file named "+filename+" definend on "+section+" must meet three requirements:"
            print "nogo: Existent executable and needs absolute path\n"


            return False



def checklogiccontroller(c):

    if not (ctrl_obj[c].controllername_id):
        print "\n\nnogo: The controllername_id must be set"
        return False

    else:

        #Check for dup licates

        if checkduplicatescontroller(ctrl_obj[c].controllername_id) == True:
            return False
        else:
            if (ctrl_obj[c].condition) == False:
                print "\nno go: All conditions must be set"
                return False
            else:
                if (ctrl_obj[c].expected_value) == False:
                    print "\nno go: All expected_value must be set"
                    return False
                else:
                    if chkfile(ctrl_obj[c].ifsatisfied_action,ctrl_obj[c].controllername_id) == False:
                        return False
                    else:
                        if chkfile(ctrl_obj[c].ifnotsatisfied_action,ctrl_obj[c].controllername_id) == False:
                            return False
                        else:
                            if chkrange(c,ctrl_obj[c].rearm_after,0,31536000,'Rearm') == False:
                                return False
                            else:
                                if chkfile(ctrl_obj[c].rearm_action,ctrl_obj[c].controllername_id) == False:
                                    return False
                                else:
                                    if chkfile(ctrl_obj[c].rearm_action,ctrl_obj[c].controllername_id) == False:
                                        return False
                                    else:
                                        options="once,ever,null"
                                        if ctrl_obj[c].ifsatisfied_action and chkoptions(c,ctrl_obj[c].repeat_ifsatisfied_action,options,'repeat_ifsatisfied_action') == False:
                                            return False
                                        else:
                                            if ctrl_obj[c].ifnotsatisfied_action and chkoptions(c,ctrl_obj[c].repeat_ifnotsatisfied_action,options,'repeat_ifnotsatisfied_action') == False:
                                                return False
                                            else:
                                                    return True


def checklogicprobe(i):
        if not (probe_obj[i].probename_id):

            print "\n\nnogo: The probename_id must be set"
            return False

        else:

            if checkduplicatesprobe(probe_obj[i].probename_id) == True:
                return False
            else:

                if (probe_obj[i].sql,probe_obj[i].probename_id) == False:
                    return False
                else:

                    if  (probe_obj[i].sql) and (probe_obj[i].probefile):
                        print "\n\nno go:Can not use dirctive sql and probefile togheter on "+probe_obj[i].probename_id;
                        print

                        return False
                    else:

                        if  (probe_obj[i].sql) == False :
                            print"\n\n"
                            print "Sql experssion must be set on "+probe_obj[i].probename_id;
                            print
                            return False
                        else:

                            if (probe_obj[i].sql) and not (probe_obj[i].sqlengine)  :
                                print"\n\n"
                                print "Sql engine must be set on "+probe_obj[i].probename_id;
                                print
                                return False
                            else:

                                if  chkfile(probe_obj[i].probefile,probe_obj[i].probename_id) == False :

                                    return False
                                else:

                                    i +=1


                                return True


def checklogicdatabase(i):

        if not(database_obj[i].database_id):

            print "\n\nnogo: The database_id  must be set"
            return False

        else:

            if checkduplicatesdatabase(database_obj[i].database_id) == True:
                return False
            else:
                options="mysql,postgres,oracle,mssql"
                if chkoptions(i,database_obj[i].dbengine,options,'dbengine') == False:
                    return False
                else:
                    if database_obj[i].dbengine == "mysql":

                            if not(database_obj[i].host)  or not(database_obj[i].database)  or not(database_obj[i].username)  or not(database_obj[i].password):

                                print
                                print
                                print"no go:All database paramenters are necessary"
                                return False

                            else:
                                return True
                    else:
                            print
                            print
                            print"no go:Only mysql is supported ad the moment, we are at work for others please fork me on https://github.com/ottacom/Radar-Reactive-Controller"

                            return False




def checkdbconnection(index):

    try:
        db = MySQLdb.connect(host=database_obj[index].host,
                     user=database_obj[index].username,
                     passwd=database_obj[index].password,
                     db=database_obj[index].database)


        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()

        # Check if anything at all is returned
        if results:

            return True
        else:

            return False

    except MySQLdb.Error:
        print"\n\nno go: Connection database problem "+database_obj[index].host+" plese check user password and access to the database"
        print
        print
        return False



def checkzombie(name,max_process):
    chkps=commands.getstatusoutput("ps -ef |grep "+name+" |grep -v grep |wc -l")
    #chkps=commands.getstatusoutput("ps -ef |grep "+name+"| grep -v grep ")

    #Pay attention the list give it back status and arguments
    #1 process = process +1

    if int(chkps[1]) < max_process+1:
        #Found some zombie process
        return True

    else:

        return False


def jobsimulation(job,startprobe):


    try:

        print "--->Starting Radar Controller simulation for:"+ctrl_obj[job].controllername_id
        i=0



        for i in range(startprobe, startprobe+ctrl_obj[job].totalprobes):


            print "------>Starting probe "+probe_obj[i].probename_id

            if (probe_obj[i].sql) :
                print "--------->Executing SQL "+probe_obj[i].sql
                dbindex=0
                while (probe_obj[i].sqlengine == database_obj[dbindex].dbengine):

                    dbindex+=1

                probe_obj[i].lastresult=executesql(probe_obj[i].sql,dbindex)
                print "--------->Sql on "+probe_obj[i].probename_id+" has returns "+str(probe_obj[i].lastresult)
                #Condition valorizing
                ctrl_obj[job].condition=ctrl_obj[job].condition.replace(str(probe_obj[i].probename_id),str(probe_obj[i].lastresult))

            else:


                print "-------->Executing Command "+probe_obj[i].probefile
                #split parameters


                probe_obj[i].lastresult=os.system(probe_obj[i].probefile+"> /dev/null")
                print "-------->Command on "+probe_obj[i].probename_id+" has returns "+str(probe_obj[i].lastresult)
                #Condition valorizing
                ctrl_obj[job].condition=ctrl_obj[job].condition.replace(str(probe_obj[i].probename_id),str(probe_obj[i].lastresult))

        i =+1



        print "--->Verifing conditions "+ctrl_obj[job].condition
        ctrl_obj[job].lastresult=executesql(ctrl_obj[job].condition,dbcondition)

        if str(ctrl_obj[job].lastresult) == str(ctrl_obj[job].expected_value):

            print "--->Condition is satisfied_action we got "+str(ctrl_obj[job].lastresult)+" and we expected "+str(ctrl_obj[job].expected_value)
            if (ctrl_obj[job].ifsatisfied_action):
                print "--->This is a simulation and I don't start "+str(ctrl_obj[job].ifsatisfied_action)+",I will do that outside the simulation"
        else :
            print "--->Condition is not satisfied_action we got "+str(ctrl_obj[job].lastresult)+" but we expected "+str(ctrl_obj[job].expected_value)
            if (ctrl_obj[job].ifnotsatisfied_action):
                print "--->This is a simulation and I don't start "+ctrl_obj[job].ifnotsatisfied_action+",I will do that outside the simulation"
                #open(dirtmp+, ctrl_obj[job].controllername_id.false).close()

        if (ctrl_obj[job].rearm_after):
            print "--->Rearm after "+str(ctrl_obj[job].rearm_after)+" times satisfied_action"

        if (ctrl_obj[job].rearm_action):
            print "--->The rearm is set but this is a simulation and I don't start "+ctrl_obj[job].rearm_action+",I will do that outside the simulation"
        print
        print


    except:

        print "\n\n!!!!!!!!!!!!Unrecovable problem occured: Ouch... something is going wrong please check your scripts and sql query"
        print
        print



def executesql (sql,dbindex):


        try:

            db = MySQLdb.connect(host=database_obj[dbindex].host,
                         user=database_obj[dbindex].username,
                         passwd=database_obj[dbindex].password,
                         db=database_obj[dbindex].database)


            cursor = db.cursor()
            cursor.execute(sql)
            results = cursor.fetchone()[0]

            # Check if anything at all is returned
            if results:

                return results

            else:

                return False

        except MySQLdb.Error:
            print
            print "!!!!!!!!!!!!!"
            print "Ouch.. We have a database problem during SQL execution on "+database_obj[dbindex].host+"\nThe sql query \""+sql+"\" has returned an unexpected Error\nplease check sql sintax user password and if you have access to the database"
            print
            return False





# now, to clear the screen
def simulation():
    cls()
    banner()
    print "\n\nRadar-Reactive-controller go-nogo for syntax check control\n"


    #if checkzombie('start.py',1) == False:
    #    progressbar(0,100,'Check for another instance......        ')
    #    print "\n\nnogo: Another instace of observium-radar still running  something wrong before, please check around and try again\n"
    #    quit()
    #else:

    if loadconfig(configfile) == True:

            progressbar(5,100,'Load file......        ')
    else:
        quit()

    #Second stage
    if objectbuilder() == True:
        progressbar(10,100,'Check config........                 ')
    else:
        quit()


    #Third stage
    i=0
    lastbar=10

    for i in range(0,controllercounter):

        if checklogiccontroller(i) == True:
            lastbar=lastbar+20/controllercounter;
            progressbar(lastbar+(20/controllercounter)*i,100,'Check logic & relations.......          ')
        else:
            quit()
    i +=1


    i=0

    for i in range(0, probecounter):
        if checklogicprobe(i) == True:
            lastbar=lastbar+20/probecounter;
            progressbar(lastbar+(20/probecounter)*i,100,'Check logic & relations probe.......         ')

        else:
            quit()
    i +=1

    #Configuring database
    if loadconfig(databasefile) == True:
            lastbar=lastbar+5;
            progressbar(lastbar,100,'Loading database congfig file......        ')
    else:
        quit()

    if dbobjectbuilder() == True:
        lastbar=lastbar+5;
        progressbar(lastbar+5,100,'Configuring database......             ')
    else:
        quit()

    i=0

    for i in range(0,dbcounter):

        if checklogicdatabase(i) == True:
            lastbar=lastbar+5/dbcounter;
            progressbar(lastbar+(20/dbcounter)*i,100,'Check logic database.......          ')
        else:
            quit()
    i +=1


    i=0

    progressbar(lastbar+(20/dbcounter)*i,100,'Check database connectivities.......          ')
    for i in range(0,dbcounter):

        if checkdbconnection(i) == True:

            lastbar=lastbar+25/dbcounter;
            progressbar(lastbar+(20/dbcounter)*i,100,'Check database connectivities.......          ')

        else:
            quit()
    i +=1




    progressbar(100,100,'Check complete!!!!                                  ')
    print
    print
    print "Radar Reactive Controller syntax is OK , we are ready to simulating the Radar"
    print "\n\n"

    i=0

    startprobe=0
    for i in range(0,controllercounter):
        p=0
        while (probe_obj[p].controllerindex != i):
            p +=1
        startprobe=probe_obj[p].abs_probeindex


        jobsimulation(i,startprobe)
    i +=1




def production(silent):
    defaultmsg="Something is going wrong.. please check you configuration using -m simulation"
    if silent == False:
        logger ("Starting RRC","alert")

        if loadconfig(configfile) == True:

            logger ("Inizializing....","alert")
        else:
            logger (defaultmsg,"err")
            quit()

        if objectbuilder() == True:
            logger ("Workflow created..","alert")
        else:
            logger (defaultmsg,"err")
            quit()

        if loadconfig(databasefile) == True:
            logger ("Inizializing database","alert")
        else:
            logger (defaultmsg,"err")
            quit()

        if dbobjectbuilder() == True:
            logger ("Database Connection created....","alert")
        else:
            logger (defaultmsg,"err")
            quit()


        logger ("RRC has been started","alert")
        startprobe=0
        for i in range(0,controllercounter):
            p=0
            while (probe_obj[p].controllerindex != i):
                p +=1
            startprobe=probe_obj[p].abs_probeindex


            jobexecute(i,startprobe)

        i +=1

        logger ("RRC is terminated","alert")

    else:

        if loadconfig(configfile) == False:
            print defaultmsg
            quit()

        if objectbuilder() == False:
            print defaultmsg
            quit()

        if loadconfig(databasefile) == False:
            print defaultmsg
            quit()

        if dbobjectbuilder() == False:
            print defaultmsg
            quit()
        startprobe=0
        for i in range(0,controllercounter):
            p=0
            while (probe_obj[p].controllerindex != i):
                p +=1
            startprobe=probe_obj[p].abs_probeindex


            jobexecutesilent(i,startprobe)


        i +=1



def jobexecute(job,startprobe):
   try:
        executefile =""
        par=""

        tmpfile=ctrl_obj[job].controllername_id.replace(" ", "_")

        i=0


        for i in range(startprobe, ctrl_obj[job].totalprobes+startprobe):



            if (probe_obj[i].sql) :

                dbindex=0
                while (probe_obj[i].sqlengine == database_obj[dbindex].dbengine):

                    dbindex+=1
                probe_obj[i].lastresult=executesql(probe_obj[i].sql,dbindex)

                #Condition valorizing
                ctrl_obj[job].condition=ctrl_obj[job].condition.replace(str(probe_obj[i].probename_id),str(probe_obj[i].lastresult))

            else:



                probe_obj[i].lastresult=os.system(probe_obj[i].probefile)

                #Condition valorizing
                ctrl_obj[job].condition=ctrl_obj[job].condition.replace(str(probe_obj[i].probename_id),str(probe_obj[i].lastresult))

        i =+1


        ctrl_obj[job].lastresult=executesql(ctrl_obj[job].condition,dbcondition)

        #Condition satisfied
        if str(ctrl_obj[job].lastresult) == str(ctrl_obj[job].expected_value):

            logger("Controller "+ctrl_obj[job].controllername_id+" is satisfied","alert")
            if ctrl_obj[job].rearm_after == 0:
                if (ctrl_obj[job].ifsatisfied_action) and not(os.path.exists(dirtmp+'OK_'+tmpfile)) and  (ctrl_obj[job].repeat_ifsatisfied_action=="once"):
                        logger ("Controller "+ctrl_obj[job].controllername_id+" has started the ifsatisfied_action in "+ctrl_obj[job].repeat_ifsatisfied_action,"alert")
                        logger ("Action: "+ctrl_obj[job].ifsatisfied_action,"alert")
                        os.system(ctrl_obj[job].ifsatisfied_action+"> /dev/null")
                        if (os.path.exists(dirtmp+'KO_'+tmpfile)):
                            os.remove(dirtmp+'KO_'+tmpfile)
                        touch(dirtmp+'OK_'+tmpfile)

                if (ctrl_obj[job].ifsatisfied_action) and  (ctrl_obj[job].repeat_ifsatisfied_action=="ever"):
                        logger ("Controller "+ctrl_obj[job].controllername_id+" has started the ifsatisfied_action , in "+ctrl_obj[job].repeat_ifsatisfied_action,"alert")
                        logger ("Action: "+ctrl_obj[job].ifsatisfied_action,"alert")
                        os.system(ctrl_obj[job].ifsatisfied_action+" > /dev/null")
                        if (os.path.exists(dirtmp+'OK_'+tmpfile)):
                            os.remove(dirtmp+'OK_'+tmpfile)
                        touch(dirtmp+'KO_'+tmpfile)
            else:


                #REARM
                if str(ctrl_obj[job].lastresult) == str(ctrl_obj[job].expected_value) and ctrl_obj[job].rearm_after > 0 and (os.path.exists(dirtmp+'KO_'+tmpfile)):
                    totalfile=""
                    logger ("Rearm after "+str(ctrl_obj[job].rearm_after)+" times satisfied_action","alert")
                    totalfile=len(fnmatch.filter(os.listdir(dirtmp), '*.'+tmpfile))
                    tfile=int(totalfile)+1
                    touch(dirtmp+str(tfile)+'.'+tmpfile)
                    toleft=ctrl_obj[job].rearm_after-tfile
                    logger ("Controller "+ctrl_obj[job].controllername_id+" has been rearmed after "+str(ctrl_obj[job].rearm_after)+" times satisfied "+str(toleft)+" left","alert")
                    if (tfile >=ctrl_obj[job].rearm_after):


                            os.system(ctrl_obj[job].rearm_action+"> /dev/null")
                            logger ("Controller "+ctrl_obj[job].controllername_id+" has been rearmed!","alert")
                            logger ("Controller "+ctrl_obj[job].controllername_id+" has started the rearm action ","alert")
                            logger ("Action:"+ctrl_obj[job].rearm_action,"notice")
                            logger ("Controller "+ctrl_obj[job].controllername_id+" has started the ifsatisfied_action in "+ctrl_obj[job].repeat_ifsatisfied_action,"alert")
                            logger ("Action: "+ctrl_obj[job].ifsatisfied_action,"alert")
                            files = os.listdir(dirtmp)
                            for f in files:

                              if not os.path.isdir(f) and tmpfile in f:
                                print dirtmp+f
                                os.remove(dirtmp+f)




                    touch(dirtmp+'OK_'+tmpfile)


        #Condition Unsatisfied
        if str(ctrl_obj[job].lastresult) != str(ctrl_obj[job].expected_value):

            print "Controller "+ctrl_obj[job].controllername_id+" is not satisfied"

            if (ctrl_obj[job].ifnotsatisfied_action) and not(os.path.exists(dirtmp+'KO_'+tmpfile)) and  (ctrl_obj[job].repeat_ifnotsatisfied_action=="once"):
                    logger ("Controller "+ctrl_obj[job].controllername_id+" has started the ifnotsatisfied_action , in "+ctrl_obj[job].repeat_ifnotsatisfied_action,"alert")
                    logger ("Action: "+ctrl_obj[job].ifnotsatisfied_action,"alert")
                    os.system(ctrl_obj[job].ifnotsatisfied_action+"> /dev/null")
                    if (os.path.exists(dirtmp+'OK_'+tmpfile)):
                        os.remove(dirtmp+'OK_'+tmpfile)
                    touch(dirtmp+'KO_'+tmpfile)

            if (ctrl_obj[job].ifnotsatisfied_action)  and  (ctrl_obj[job].repeat_ifnotsatisfied_action=="ever"):
                    logger ("Controller "+ctrl_obj[job].controllername_id+" has started has started the ifnotsatisfied_action, in "+ctrl_obj[job].repeat_ifnotsatisfied_action,"alert")
                    logger ("Action: "+ctrl_obj[job].ifnotsatisfied_action,"alert")
                    os.system(ctrl_obj[job].ifnotsatisfied_action+"> /dev/null")
                    if (os.path.exists(dirtmp+'OK_'+tmpfile)):
                        os.remove(dirtmp+'OK_'+tmpfile)
                    touch(dirtmp+'KO_'+tmpfile)







   except:
        logger ("Unrecovable problem occured: Ouch... something is going wrong please check your scripts and sql query","crit")
        print "\n\n!!!!!!!!!!!!Unrecovable problem occured: Ouch... something is going wrong please check your scripts and sql query"
        print
        print



def jobexecutesilent(job,startprobe):
   try:
        executefile =""
        par=""

        tmpfile=ctrl_obj[job].controllername_id.replace(" ", "_")

        i=0

        for i in range(startprobe, ctrl_obj[job].totalprobes+startprobe):


            if (probe_obj[i].sql) :

                dbindex=0
                while (probe_obj[i].sqlengine == database_obj[dbindex].dbengine):

                    dbindex+=1
                probe_obj[i].lastresult=executesql(probe_obj[i].sql,dbindex)

                #Condition valorizing
                ctrl_obj[job].condition=ctrl_obj[job].condition.replace(str(probe_obj[i].probename_id),str(probe_obj[i].lastresult))

            else:



                probe_obj[i].lastresult=os.system(probe_obj[i].probefile+" > /dev/null")

                #Condition valorizing
                ctrl_obj[job].condition=ctrl_obj[job].condition.replace(str(probe_obj[i].probename_id),str(probe_obj[i].lastresult))

        i =+1


        ctrl_obj[job].lastresult=executesql(ctrl_obj[job].condition,dbcondition)

        #Condition satisfied
        if str(ctrl_obj[job].lastresult) == str(ctrl_obj[job].expected_value):


            if ctrl_obj[job].rearm_after == 0:
                if (ctrl_obj[job].ifsatisfied_action) and not(os.path.exists(dirtmp+'OK_'+tmpfile)) and  (ctrl_obj[job].repeat_ifsatisfied_action=="once"):
                        os.system(ctrl_obj[job].ifsatisfied_action+" > /dev/null")
                        if (os.path.exists(dirtmp+'KO_'+tmpfile)):
                            os.remove(dirtmp+'KO_'+tmpfile)
                        touch(dirtmp+'OK_'+tmpfile)

                if (ctrl_obj[job].ifsatisfied_action) and  (ctrl_obj[job].repeat_ifsatisfied_action=="ever"):
                        os.system(ctrl_obj[job].ifsatisfied_action+" > /dev/null")
                        if (os.path.exists(dirtmp+'OK_'+tmpfile)):
                            os.remove(dirtmp+'OK_'+tmpfile)
                        touch(dirtmp+'KO_'+tmpfile)
            else:


                #REARM
                if str(ctrl_obj[job].lastresult) == str(ctrl_obj[job].expected_value) and ctrl_obj[job].rearm_after > 0 and (os.path.exists(dirtmp+'KO_'+tmpfile)):
                    totalfile=""

                    totalfile=len(fnmatch.filter(os.listdir(dirtmp), '*.'+tmpfile))
                    tfile=int(totalfile)+1
                    touch(dirtmp+str(tfile)+'.'+tmpfile)
                    toleft=ctrl_obj[job].rearm_after-tfile

                    if (tfile >=ctrl_obj[job].rearm_after):


                            os.system(ctrl_obj[job].rearm_action+" > /dev/null")
                            files = os.listdir(dirtmp)
                            for f in files:

                              if not os.path.isdir(f) and tmpfile in f:

                                os.remove(dirtmp+f)




                    touch(dirtmp+'OK_'+tmpfile)


        #Condition Unsatisfied
        if str(ctrl_obj[job].lastresult) != str(ctrl_obj[job].expected_value):



            if (ctrl_obj[job].ifnotsatisfied_action) and not(os.path.exists(dirtmp+'KO_'+tmpfile)) and  (ctrl_obj[job].repeat_ifnotsatisfied_action=="once"):
                    os.system(ctrl_obj[job].ifnotsatisfied_action+" > /dev/null")
                    if (os.path.exists(dirtmp+'OK_'+tmpfile)):
                        os.remove(dirtmp+'OK_'+tmpfile)
                    touch(dirtmp+'KO_'+tmpfile)

            if (ctrl_obj[job].ifnotsatisfied_action)  and  (ctrl_obj[job].repeat_ifnotsatisfied_action=="ever"):
                    os.system(ctrl_obj[job].ifnotsatisfied_action+" > /dev/null")
                    if (os.path.exists(dirtmp+'OK_'+tmpfile)):
                        os.remove(dirtmp+'OK_'+tmpfile)
                    touch(dirtmp+'KO_'+tmpfile)




   except:

        print "\n\n!!!!!!!!!!!!Unrecovable problem occured: Ouch... something is going wrong please check your scripts and sql query"
        print



def touch(fname, times=None):
    fhandle = open(fname, 'a')
    try:
        os.utime(fname, times)
    finally:
        fhandle.close()

def logger(message,priority):
        print message
        os.system("logger -i -p "+priority+" "+message)

def parsecommand(command):

        if (command):
            command=command.replace(",","\" \"")
            command="\""+command+"\""
            return command

        else:

            return command



##############################################################



if __name__ == "__main__":

    functions = [simulation,production]
    functions = { function.__name__ : function for function in functions}
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--mode',
                  choices=list(functions.keys()),
                  required=True,
                  help="""Start RRC in simulation or production mode, absolutely no reaction will be performed in simulation """)
    parser.add_argument('-d', '--databasefile',
                  required=True,
                  help="""Database configuration file ex database.json""")
    parser.add_argument('-c', '--controllerfile',
                  required=True,
                  help="""Controller configuration file controller.json""")
    parser.add_argument('-s', '--silent',
                  action='store_true',
                  help="""No output on screen""")


    args = parser.parse_args()
    databasefile=args.databasefile
    configfile=args.controllerfile

    if (not(os.path.exists(databasefile)) or not(os.access(databasefile, os.R_OK)) or not(os.path.exists(configfile)) or not(os.access(configfile, os.R_OK)))== True:
        print "Problem during access to conotrollerfile and databasefile, please chek if they are and their permission"
        quit()

    if args.mode =='simulation':
        simulation()
    if args.mode =='production' and args.silent == False:
        production(False)
    if args.mode =='production' and args.silent == True:
        production(True)
