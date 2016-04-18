#!/usr/bin/python
#needs pip install schedule
import json
import sys
import time
import threading
import os
import subprocess
import signal
import commands
import collections
import logging
from or_class import *
import MySQLdb

#Global definitions
global configfile #path of configfile
global databasefile

global ctrl_obj
global probe_obj
global database_obj
global startuplist
global msg


#Configfile
configfile="controller.json"
databasefile="database.json"
#controller
ctrl_obj = []
probe_obj = []
database_obj = []
startuplist = {}



def t_controllercounter(val):
    global controllercounter
    controllercounter=val


def t_probecounter(val):
    global probecounter
    probecounter=val




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
    try:

        #check for controller

        for row_ctrl in inram_configuration['controllerset']:

            #Creating controller object totalprobes will be update leater now is 1
             #Setting total number of probe


            totalprobes=json.dumps(row_ctrl['probeset']).count("probename_id")

            ctrl_obj.append(Controller(
            row_ctrl['controllername_id'],
            row_ctrl['logging'],
            row_ctrl['condition'],
            row_ctrl['expected_value'],
            row_ctrl['action_true'],
            row_ctrl['action_false'],
            row_ctrl['rollback_after'],
            row_ctrl['rollback_action'],
            totalprobes,controllercounter))

            controllercounter +=1
            pbindex=0

            for pbindex in range(0,totalprobes):

                probe_obj.append(Probe(
                row_ctrl['probeset'][pbindex]['probename_id'],
                row_ctrl['probeset'][pbindex]['sql'],
                row_ctrl['probeset'][pbindex]['sqlengine'],
                row_ctrl['probeset'][pbindex]['probefile'],
                controllercounter-1,pbindex))

                pbindex +=1
                probecounter +=1

                #Go to the next probe

        #Public value

        t_controllercounter(controllercounter)
        t_probecounter(probecounter)

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

            print "\n\nnogo: The configuration file "+configfile+" seem has logical corrupted prbably some fields are disappeared\n"

    except:

            print "\n\nnogo: oops some problem occured during validation checking process\n"
    raise


    return True



def chkrange(c,val,min,max):
    if (val >= min) and (val <= max) :
        return True
    else:
        print "\n\nnogo: The "+val+" of  "+ctrl_obj[c].controllername_id+" must be => "+min+" and <= "+max+" secons\n"

        return False

def chkoptions(c,val,options,attribute):
    if (val in options) and val:
        return True
    else:
        print "\n\nnogo: The "+attribute+" needs to be "+options+"\n"

        return False




def chkfile(filename,section):



    if ((os.path.exists(filename) and os.access(filename, os.X_OK)) and (filename.find("/") != -1)) or filename =="" :

        return True

    else:

        print "\n\nnogo: The file named "+filename+" definend on "+section+" must meet three requirements:"
        print "\nnogo: Existent executable and needs absolute path\n"

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
            options="yes,not"
            if chkoptions(c,ctrl_obj[c].logging,options,'logging') == False:
                return False
            else:

                if (ctrl_obj[c].condition) == False:
                    print "\nno go: All conditions mut be set"
                    return False
                else:
                    if (ctrl_obj[c].expected_value) == False:
                        print "\nno go: All expected_value must be set"
                        return False
                    else:
                        if chkfile(ctrl_obj[c].action_true,ctrl_obj[c].controllername_id) == False:
                            return False
                        else:
                            if chkfile(ctrl_obj[c].action_false,ctrl_obj[c].controllername_id) == False:
                                return False
                            else:
                                if chkrange(c,ctrl_obj[c].rollback_after,1,31536000) == False:
                                    return False
                                else:
                                    if chkfile(ctrl_obj[c].rollback_action,ctrl_obj[c].controllername_id) == False:
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

                    if  (probe_obj[i].sql) and (probe_obj[i].probefile) :
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
                     db=database_obj[i].database)


        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()
        # Check if anything at all is returned
        if results:
            return True
        else:
            return False

    except MySQLdb.Error:

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



# now, to clear the screen
def main():
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


    for i in range(0,dbcounter):

        if checkdbconnection(i) == True:

            lastbar=lastbar+5/dbcounter;
            progressbar(lastbar+(20/dbcounter)*i,100,'Check database connectivities.......          ')

        else:
            quit()
    i +=1

    print
    print
    print
    print "Radar Reactive Controller syntax is OK and ready to go"
    print "\n\n"


##############################################################

if __name__ == "__main__":
    main()
