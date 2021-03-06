#Created by Felix Sterzelmaier, Concat AG
#2019-11
#tested on Python 3.7.4 and 3.7.5rc1
#run with "run.bat" or "python3 ./convert.py" or "python ./convert.py"

#imports
import xlrd
import os
import sys
from datetime import datetime
from datetime import time
from pytz import timezone
from datetime import timezone, datetime, timedelta
import tzlocal
import string
import re

############################################################################
############ Only Change Variables below this line #########################
############################################################################

filename_prefix = ""
filename_sufix = ".yml"
columnNames = "A"
config_prefx = ""
config_sufix = "_oneview_config.json"
inputfilename = "wip_checkliste_gesamt.xlsx"
exceltabmgmt = "Synergy-MGMT"
exceltabsubnets = "Synergy-Subnets"
exceltabnets = "Synergy-Networks"
exceltabstorage = "Nimble"
exceltabhypervisor = "Synergy-VMware"
exceltabnimble = "Synergy-Nimble"
exceltabgeneral = "Umgebung allgemein"
outputfolder = "output"
restApiVersion = "1000"
restDomain = "LOCAL"

############################################################################
############## Only change Variables above this line #######################
############################################################################

variablesAll = []
variablesNimbleAll = {}
variablesSynergyNimbleAll = {}
variablesHypervisorAll = {}
variablesClustersAll = []
variableHVCPserverpassword = ""
variableHVCPmgmtNet = ""
variablesMgmtNet = {}
variablesClusterHosts = []
variablesGeneral = {}

#change working directory to script path/xlsx path
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

############################################################################
############## Small helper functions ######################################
############################################################################

#A->0, B->1, ...
def columnCharToInt(c):
	c = c.lower()
	return string.ascii_lowercase.index(c)

#string to lowercase, space to _, - to _, remove everything except ascii-letters and _
def convertToAnsibleVariableName(n):
	n = str(n)
	n = n.lower().replace(" ","_").replace("-","_")
	n = re.sub(r'\W+', '', n)
	return n

############################################################################
############## Parse Excel functions #######################################
############################################################################

def findFrames():
	global variablesAll
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabmgmt)

	columnNamesInt = columnCharToInt(columnNames)
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,columnNamesInt))
		
		if(name==""):
			continue
			
		if(name=="OneView Hostname"):
			
			for col in range(columnCharToInt(columnNames)+1,worksheet.ncols):
				data = str(worksheet.cell_value(row,col))
				if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
					continue
					
				tmp = {"name":data,"column":col,"letter":data[0]}
				variablesAll.append(tmp)
			break
	
	#ehemals fillvariables
	for frame in variablesAll:
		variables = {}
		infocount = 0
		foundGateway = False
		for row in range(worksheet.nrows):
			name = str(worksheet.cell_value(row,columnNamesInt))
			
			if(name==""):
				continue
				
			if(name=="Infos"):
				infocount = infocount + 1
				continue

			if(infocount!=1):
				continue
			
			#found valid line
			columnDataInt = frame["column"]
			data = str(worksheet.cell_value(row,columnDataInt))
			if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
				continue
			
			if(data.find("#TODO") != -1):
				pos = data.find("#TODO")
				data = data[:pos-1]
			
			name = convertToAnsibleVariableName(name)			
			if(name=="gateway"):
				if(foundGateway):
					continue
				foundGateway = True
			
			variables[name] = data
		frame["variables"] = variables

def findNimbles():
	global variablesNimbleAll
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabstorage)

	columnNamesInt = columnCharToInt(columnNames)
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,columnNamesInt))
		
		if(name==""):
			continue
			
		if(name=="Storage System Name"):
			
			for col in range(columnCharToInt(columnNames)+1,worksheet.ncols):
				data = str(worksheet.cell_value(row,col))
				if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO") or str(worksheet.cell_value(row-1,col))=="Bemerkungen"):
					continue
					
				tmp = {"name":data,"column":col,"letter":data[0]}
				variablesNimbleAll[data[0]] = tmp
			break
	
	#ehemals fillvariablesnimble
	for l in variablesNimbleAll:
		nimble = variablesNimbleAll[l]
		variables = {}
		start = False
		end = False
		for row in range(worksheet.nrows):
			name = str(worksheet.cell_value(row,columnNamesInt))
			
			if(name==""):
				continue
				
			if(name=="Group name"):
				start = True
				
			if(not start):
				continue
				
			if(end):
				continue
				
			if(name=="NTP (time) server IP address"):
				end = True
			
			#found valid line
			columnDataInt = nimble["column"]
			data = str(worksheet.cell_value(row,columnDataInt))
			if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
				continue
			
			if(data.find("#TODO") != -1):
				pos = data.find("#TODO")
				data = data[:pos-1]
			
			name = convertToAnsibleVariableName(name)			
			
			variables[name] = data
		nimble["variables"] = variables

def findSynergyNimbles():
	global variablesSynergyNimbleAll
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabnimble)
	
	columnNamesInt = columnCharToInt(columnNames)
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,columnNamesInt))
		
		if(name==""):
			continue
			
		if(name=="Zone"):
			
			for col in range(columnCharToInt(columnNames)+1,worksheet.ncols):
				data = str(worksheet.cell_value(row,col))
				if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO") or str(worksheet.cell_value(row-1,col))=="Bemerkungen"):
					continue
				
				tmp = {"column":col,"letter":data[0]}
				variablesSynergyNimbleAll[data[0]] = tmp
			break
	
	#ehemals fillvariablesnimble
	for l in variablesSynergyNimbleAll:
		nimble = variablesSynergyNimbleAll[l]
		variables = {}
		start = False
		for row in range(worksheet.nrows):
			name = str(worksheet.cell_value(row,columnNamesInt))
			
			if(name==""):
				continue
				
			if(name=="Storage system type"):
				start = True
				
			if(not start):
				continue
			
			#found valid line
			columnDataInt = nimble["column"]
			data = str(worksheet.cell_value(row,columnDataInt))
			if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
				continue
			
			if(data.find("#TODO") != -1):
				pos = data.find("#TODO")
				data = data[:pos-1]
			
			name = convertToAnsibleVariableName(name)			

			variables[name] = data
		nimble["variables"] = variables

def findHypervisor():
	global variablesHypervisorAll,variablesClustersAll,variableHVCPserverpassword,variableHVCPmgmtNet
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabhypervisor)

	start = False
	end = False
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,0))
		
		if(name==""):
			continue
			
		if(name=="Type"):
			start = True
			
		if(not start):
			continue
			
		if(end):
			continue
			
		if(name=="High availability"):
			end = True
		
		#found valid line
		data = worksheet.cell_value(row,1)
		if(isinstance(data,float)):
			data = str(int(data))
		
		if(data=="" or data=="#TODO" or data=="n/a" or data.startswith("#TODO")):
			continue
		
		if(data.find("#TODO") != -1):
			pos = data.find("#TODO")
			data = data[:pos-1]
		
		name = convertToAnsibleVariableName(name)			
		variablesHypervisorAll[name] = data
		
	#clusters
	start = False
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,3))
		
		if(name==""):
			continue
			
		if(name=="Cluster"):
			start = True
			continue
			
		if(not start):
			continue
		
		#found valid line
		if(not name in variablesClustersAll):
			variablesClustersAll.append(name)
			
	#serverpassword
	start = False
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,5))
		
		if(name==""):
			continue
			
		if(name=="serverPassword"):
			start = True
			continue
			
		if(not start):
			continue
		
		variableHVCPserverpassword = name
		break
		
	#variableHVCPmgmtNet
	start = False
	for row in range(worksheet.nrows):
		name = str(worksheet.cell_value(row,4))
		
		if(name==""):
			continue
			
		if(name=="Management Network"):
			start = True
			continue
			
		if(not start):
			continue
		
		variableHVCPmgmtNet = name
		break
			
def findVariablesMgmtNet():
	global variablesMgmtNet
	#get MGMT Net Variables
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabsubnets)
	
	variablesHead = []
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	
	for row in range(1,worksheet.nrows):
		variablesOneNet = {}
		for col in range(worksheet.ncols):
			val = worksheet.cell_value(row,col)
			
			if(isinstance(val,float)):
				val = str(int(val))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			if(val!=""):
				variablesOneNet[variablesHead[col]] = val
		
		if(variablesOneNet["name"]==variableHVCPmgmtNet):
			variablesMgmtNet = variablesOneNet
						
def findHostsPerCluster():
	global variablesClusterHosts 
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabhypervisor)
	
	started = False
	headLine = 0
	for row in range(0,worksheet.nrows):
		name = convertToAnsibleVariableName(worksheet.cell_value(row,0))
		if(name=="hypervisors"):
			started = True
			headLine = row+1
			continue
			
		if(not started):
			continue
			
		if(row==headLine):
			variablesHead = []
			for col in range(worksheet.ncols):
				name = convertToAnsibleVariableName(worksheet.cell_value(row,col))
				variablesHead.append(name)
			continue
	
		variablesOneClusterHost = {}
		for col in range(worksheet.ncols):
			val = worksheet.cell_value(row,col)
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			if(val!=""):
				variablesOneClusterHost[variablesHead[col]] = val
		
		variablesClusterHosts.append(variablesOneClusterHost)
		
						
def findGeneral():
	global variablesGeneral
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabgeneral)
	
	started = False
	headColumn = 6
	for row in range(0,worksheet.nrows):
	
		name = worksheet.cell_value(row,headColumn)
		if(name=="SNMP Trap Receiver & Manager"):
			name = convertToAnsibleVariableName(name)
			value = worksheet.cell_value(row,headColumn+1).split("\n")[0]
			variablesGeneral[name] = value
			
		if(name=="Community Name"):
			name = convertToAnsibleVariableName(name)
			value = worksheet.cell_value(row,headColumn+1)
			variablesGeneral[name] = value

############################################################################
############## Write Config and Fileheaders functions ######################
############################################################################

def writeConfigs():
	for frame in variablesAll:
		configFile = outputfolder+"/"+config_prefx+frame["letter"]+config_sufix
		outfile = open(configFile,'w')
		outfile.write("{"+"\n")
		outfile.write("    \"ip\": \""+frame["variables"]["oneview_hostname"].lower()+"."+frame["variables"]["domain_name"]+"\","+"\n")
		outfile.write("    \"credentials\": {"+"\n")
		outfile.write("        \"userName\": \"Administrator\","+"\n")
		outfile.write("        \"password\": \""+frame["variables"]["administrator_passwort"]+"\""+"\n")
		outfile.write("    },"+"\n")
		outfile.write("    \"image_streamer_ip\": \"\","+"\n") #bleibt leer. Folgene Tasks lesen die IP live aus
		outfile.write('    "api_version": "'+restApiVersion+'"\n')
		outfile.write("}"+"\n")
		outfile.close()

def writeFileheader(outfile,configFileName,writeConfigPart=True,writeTaskPart=True):
	filename = os.path.basename(outfile.name)
	print("now: "+filename)
	outfile.write("###\n")
	outfile.write("# created by python script convert.py\n")
	outfile.write("# Felix Sterzelmaier, Concat AG\n")
	outfile.write("# Created: "+datetime.now(tzlocal.get_localzone()).strftime("%Y-%m-%d %H:%M:%S %Z(%z)")+"\n")
	outfile.write("# Dependencies: pip install --upgrade pip\n")
	outfile.write("# Dependencies: pip install pyvmomi\n")
	outfile.write("# Run with: ansible-playbook -c local -i localhost, "+filename+"\n")
	outfile.write("# Run on: 10.10.5.239/olant-ansible as user olant in path /home/olant/synergy-ansible/feste-script/output\n")
	outfile.write("# Before reading this playbook please read the README.txt and the sourcecode of convert.py first!\n")
	outfile.write("###\n")
	outfile.write("---\n")
	outfile.write("- hosts: localhost\n")
	if(writeConfigPart):
		outfile.write("  vars:\n")
		outfile.write('    config: "{{ playbook_dir }}/'+configFileName+'"\n')
	if(writeTaskPart):
		outfile.write("  tasks:\n")
	outfile.write("\n")
		
def writeFilepartRESTAPILogin(outfile,host,username,password):
	outfile.write('  - name: Login to API and retrieve AUTH-Token\n')
	outfile.write('    uri:\n')
	outfile.write('      validate_certs: yes\n')
	outfile.write('      headers:\n')
	outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
	outfile.write('        Content-Type: application/json\n')
	outfile.write('      url: https://'+host+'/rest/login-sessions\n')
	outfile.write('      method: POST\n')
	outfile.write('      body_format: json\n')
	outfile.write('      body:\n')
	outfile.write('        authLoginDomain: "'+restDomain+'"\n')
	outfile.write('        password: "'+password+'"\n')
	outfile.write('        userName: "'+username+'"\n')
	outfile.write('        loginMsgAck: "true"\n')
	outfile.write('    register: var_this\n')
	outfile.write('  - set_fact: var_token=\'{{ var_this["json"]["sessionID"] }}\'\n')
	outfile.write('\n')
	
def writeFilepartGetImageStreamerIp(outfile,configpath):
	outfile.write('    - name: Gather facts about all OS Deployment Servers\n')
	outfile.write('      oneview_os_deployment_server_facts:\n')
	outfile.write('        config: "{{ playbook_dir }}/'+configpath+'"\n')
	outfile.write('    - set_fact:\n')
	outfile.write('        var_image_streamer_ip="{{ os_deployment_servers[0].primaryIPV4 }}"\n')
	outfile.write('\n')

def writeFilepartGetConfig(outfile,configpath):		
	outfile.write('    - name: load var from file\n')
	outfile.write('      include_vars:\n')
	outfile.write('        file: "{{ playbook_dir }}/'+configpath+'"\n')
	outfile.write('        name: var_imported_config\n')

def writeFilepartConfigvariablesInline(outfile,spaces):	
	outfile.write(spaces+'hostname: "{{ var_imported_config[\'ip\'] }}"\n')
	outfile.write(spaces+'username: "{{ var_imported_config[\'credentials\'][\'userName\'] }}"\n')
	outfile.write(spaces+'password: "{{ var_imported_config[\'credentials\'][\'password\'] }}"\n')
	outfile.write(spaces+'api_version: "{{ var_imported_config[\'api_version\'] }}"\n')
	
def waitAndOutputTask(outfile,clusterlist,urllist):
	for i in range(len(clusterlist)):
		cluster = clusterlist[i]
		url = urllist[i]

		outfile.write('  - name: Wait for '+cluster+'\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "1000"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: "{{ '+url+' }}"\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    no_log: False\n')
		outfile.write('    register: var_return_task_'+convertToAnsibleVariableName(cluster)+'\n')
		outfile.write('    until: var_return_task_'+convertToAnsibleVariableName(cluster)+'.json.taskState != "New" and var_return_task_'+convertToAnsibleVariableName(cluster)+'.json.taskState != "Pending" and var_return_task_'+convertToAnsibleVariableName(cluster)+'.json.taskState != "Running" and var_return_task_'+convertToAnsibleVariableName(cluster)+'.json.taskState != "Starting" and var_return_task_'+convertToAnsibleVariableName(cluster)+'.json.taskState != "Unknown"\n')
		outfile.write('    delay: 60\n')
		outfile.write('    retries: 60\n')
		outfile.write('\n')
		
	#output last Taskoutput per Cluster
	outfile.write('#full output for each cluster\n')
	for i in range(len(clusterlist)):
		cluster = clusterlist[i]
		outfile.write('  - debug: var=var_return_task_'+convertToAnsibleVariableName(cluster)+'.json\n')
	outfile.write('\n')
	
	#output last TaskoutputState per Cluster
	outfile.write('#taskstate for each Cluster\n')
	for i in range(len(clusterlist)):
		cluster = clusterlist[i]
		outfile.write('  - debug: var=var_return_task_'+convertToAnsibleVariableName(cluster)+'.json.taskState\n')
	outfile.write('\n')

############################################################################
############## Create Playbooks functions ##################################
############################################################################

#105 ehemals #19
def writeRenameEnclosures(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		outfile.write('    - name: Gather facts about all Enclosures\n')
		outfile.write('      oneview_enclosure_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: enc_m1="{{ item }}"\n')
		outfile.write('      loop: "{{ enclosures }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      when: item.applianceBays.0.model is match "Synergy Composer" and item.applianceBays.1.model is none\n')
		outfile.write('\n')
		outfile.write('    - set_fact: enc_m2="{{ item }}"\n')
		outfile.write('      loop: "{{ enclosures }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      when: item.applianceBays.0.model is match "Synergy Composer" and item.applianceBays.1.model is match "Synergy Image Streamer"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: enc_sl="{{ item }}"\n')
		outfile.write('      loop: "{{ enclosures }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      when: item.applianceBays.0.model is none and item.applianceBays.1.model is match "Synergy Image Streamer"\n')
		outfile.write('\n')
		outfile.write('    - name: Rename Enclosure Master-1\n')
		outfile.write('      oneview_enclosure:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        validate_etag: False\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ enc_m1.name }}"\n')
		outfile.write('          newName: "'+frame["letter"]+'-Master1"\n')
		outfile.write('\n')
		outfile.write('    - name: Rename Enclosure Master-2\n')
		outfile.write('      oneview_enclosure:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        validate_etag: False\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ enc_m2.name }}"\n')
		outfile.write('          newName: "'+frame["letter"]+'-Master2"\n')
		outfile.write('\n')
		outfile.write('    - name: Rename Enclosure Slave\n')
		outfile.write('      oneview_enclosure:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        validate_etag: False\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ enc_sl.name }}"\n')
		outfile.write('          newName: "'+frame["letter"]+'-Slave"\n')
		outfile.write('\n')
		#END
		outfile.close()
	
#110 ehemals #16
def writeRenameServerHardwareTypes(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		outfile.write('    - name: Gather facts about all Server Hardware Types\n')
		outfile.write('      oneview_server_hardware_type_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - set_fact: var_one="{{ item }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{server_hardware_types}}"\n')
		outfile.write('      when: item["adapters"]|length==1\n')
		outfile.write('\n')
		outfile.write('    - set_fact: var_two="{{ item }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{server_hardware_types}}"\n')
		outfile.write('      when: item["adapters"]|length==2\n')
		outfile.write('\n')
		outfile.write('    - debug: msg="{{ var_one[\'name\'] }}"\n')
		outfile.write('    - debug: msg="{{ var_two[\'name\'] }}"\n')
		outfile.write('\n')
		outfile.write('    - name: Rename the Server Hardware Type\n')
		outfile.write('      oneview_server_hardware_type:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ var_one[\'name\'] }}"\n')
		outfile.write('          newName: "HypervisorNode"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - name: Rename the Server Hardware Type\n')
		outfile.write('      oneview_server_hardware_type:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          name: "{{ var_two[\'name\'] }}"\n')
		outfile.write('          newName: "StorageNode"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - name: Gather facts about all Server Hardware Types\n')
		outfile.write('      oneview_server_hardware_type_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - set_fact: var_one="{{ item }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{server_hardware_types}}"\n')
		outfile.write('      when: item["adapters"]|length==1\n')
		outfile.write('\n')
		outfile.write('    - set_fact: var_two="{{ item }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{server_hardware_types}}"\n')
		outfile.write('      when: item["adapters"]|length==2\n')
		outfile.write('\n')
		outfile.write('    - debug: msg="{{ var_one[\'name\'] }}"\n')
		outfile.write('    - debug: msg="{{ var_two[\'name\'] }}"\n')
		outfile.write('\n')
		#END
		outfile.close()

#210 ehemals #01
def writeTimelocale(nr,name):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+name+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		outfile.write("     - name: Configure time locale in en_US.UTF-8\n")
		outfile.write("       oneview_appliance_time_and_locale_configuration:\n")
		outfile.write("         config: \"{{ config }}\"\n")
		outfile.write("         state: present\n")
		outfile.write("         data:\n")
		outfile.write("             locale: en_US.UTF-8\n")
		outfile.write("             timezone: UTC\n")
		outfile.write("             ntpServers:\n")
		outfile.write("                 - "+frame["variables"]["gateway"]+"\n")
		outfile.write("       delegate_to: localhost\n")
		outfile.write("\n")
		outfile.close()		

#215
def writeConfigureSNMP(nr,name):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+name+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		outfile.write('    - name: Set Appliance Device Read Community String\n')
		outfile.write('      oneview_appliance_device_read_community:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          communityString: "'+variablesGeneral["community_name"]+'"\n')
		outfile.write('\n')
		outfile.write('    - name: Set Appliance Device SNMPv1 Trap Destination\n')
		outfile.write('      oneview_appliance_device_snmp_v1_trap_destinations:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          communityString: "'+variablesGeneral["community_name"]+'"\n')
		outfile.write('          destination: "'+variablesGeneral["snmp_trap_receiver__manager"]+'"\n')
		outfile.write('          port: 162\n')
		outfile.write('\n')

#270 ehemals #11
def writeAddFirmwareBundle(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('    - name: Ensure that a firmware bundle is present\n')
		outfile.write('      oneview_firmware_bundle:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        file_path: "{{ playbook_dir }}/files/'+frame["variables"]["synergy_spp"]+'"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('    - debug: var=firmware_bundle\n')
		outfile.write('\n')
		#END
		outfile.close()

#280 ehemals #02
def writeAddresspoolsubnet(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		outfile.close()
		
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabsubnets)
	variablesHead = []
	
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	
	for row in range(1,worksheet.nrows):
		variablesOneSubnet = {}
		for col in range(worksheet.ncols):
			val = str(worksheet.cell_value(row,col))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			if(val!=""):
				variablesOneSubnet[variablesHead[col]] = val
		writeAddresspoolsubnetOne(nr,filenamepart,variablesOneSubnet)
		
#280 ehemals #02 helper
def writeAddresspoolsubnetOne(nr,filenamepart,variablesOneSubnet):	
	if(not "zone" in variablesOneSubnet):
		print("variablesOneSubnet missing zone!")
		return
		
	if(not "name" in variablesOneSubnet):
		print("variablesOneSubnet missing name!")
		return
		
	if(not "type" in variablesOneSubnet):
		print("variablesOneSubnet missing typ!")
		return

	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'a')

		if(variablesOneSubnet["zone"].find(frame["letter"]) != -1):
			if(variablesOneSubnet["type"]=="Subnet"):
				if(not "subnetid" in variablesOneSubnet):
					print("variablesOneSubnet missing subnetid!")
					return
					
				if(not "subnetmask" in variablesOneSubnet):
					print("variablesOneSubnet missing subnetmask!")
					return

				outfile.write("     - name: Create subnet "+variablesOneSubnet["subnetid"]+"\n")
				outfile.write("       oneview_id_pools_ipv4_subnet:\n")
				outfile.write("         config: \"{{ config }}\"\n")
				outfile.write("         state: present\n")
				outfile.write("         data:\n")
				outfile.write("             name: "+variablesOneSubnet["subnetid"]+"_Subnet\n")
				outfile.write("             type: Subnet\n")
				outfile.write("             networkId: "+variablesOneSubnet["subnetid"]+"\n")
				outfile.write("             subnetmask: "+variablesOneSubnet["subnetmask"]+"\n")
				
				if("gateway" in variablesOneSubnet):
					outfile.write("             gateway: "+variablesOneSubnet["gateway"]+"\n")
				if("domain" in variablesOneSubnet):
					outfile.write("             domain: "+variablesOneSubnet["domain"]+"\n")
				if("dnsserver1" in variablesOneSubnet):
					outfile.write("             dnsServers:\n")
					outfile.write("                 - "+variablesOneSubnet["dnsserver1"]+"\n")
				if("dnsserver2" in variablesOneSubnet):
					outfile.write("                 - "+variablesOneSubnet["dnsserver2"]+"\n")
				if("dnsserver3" in variablesOneSubnet):
					outfile.write("                 - "+variablesOneSubnet["dnsserver3"]+"\n")
				outfile.write("       delegate_to: localhost\n")
				outfile.write("\n")
					
			if(variablesOneSubnet["type"]=="Range"):
				if(not "rangestart" in variablesOneSubnet):
					print("variablesOneSubnet "+variablesOneSubnet["name"]+" missing rangestart!")
					return
					
				if(not "rangeend" in variablesOneSubnet):
					print("variablesOneSubnet "+variablesOneSubnet["name"]+" missing rangeend!")
					return

				outfile.write("     - set_fact: subnet_uri=\"{{ id_pools_ipv4_subnet[\"uri\"] }}\" \n")
				outfile.write("     - name: Create IPV4 range "+variablesOneSubnet["name"]+"\n")
				outfile.write("       oneview_id_pools_ipv4_range:\n")
				outfile.write("         config: \"{{ config }}\"\n")
				outfile.write("         state: present\n")
				outfile.write("         data:\n")
				outfile.write("             name: "+variablesOneSubnet["name"]+"\n")
				outfile.write("             subnetUri: \"{{ subnet_uri }}\" \n")
				outfile.write("             type: Range\n")
				outfile.write("             rangeCategory: Custom\n")
				outfile.write("             startAddress: "+variablesOneSubnet["rangestart"]+"\n")
				outfile.write("             endAddress: "+variablesOneSubnet["rangeend"]+"\n")
				outfile.write("       delegate_to: localhost\n")
				outfile.write("\n")
		outfile.close()

#290 ehemals #04
def writeCreatenetwork(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		outfile.close()

	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabnets)
	
	variablesHead = []
	
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	
	for row in range(1,worksheet.nrows):
		variablesOneNet = {}
		for col in range(worksheet.ncols):
			val = worksheet.cell_value(row,col)
			
			if(isinstance(val,float)):
				val = str(int(val))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			if(val!=""):
				variablesOneNet[variablesHead[col]] = val
		writeCreatenetworkOne(nr,filenamepart,variablesOneNet)

#290 ehemals #04 helper
def writeCreatenetworkOne(nr,filenamepart,variablesOneNet):	
	if(not "zone" in variablesOneNet):
		print("variablesOneNet missing zone!")
		return
	
	if(not "ipv4subnet" in variablesOneNet):
		print("variablesOneNet missing ipv4subnet!")
		return
		
	if(not "name" in variablesOneNet):
		print("variablesOneNet missing name!")
		return
		
	if(not "vlanid" in variablesOneNet):
		print("variablesOneNet missing vlanid!")
		return

	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'a')
		
		if(variablesOneNet["zone"].find(frame["letter"]) != -1):
			
			if(variablesOneNet["ipv4subnet"]!="None"):
				outfile.write("    - name: Gather facts about ID Pools IPV4 Subnets by name\n")
				outfile.write("      oneview_id_pools_ipv4_subnet_facts:\n")
				outfile.write("        config: \"{{ config }}\"\n")
				outfile.write("        name: '"+variablesOneNet["ipv4subnet"]+"_Subnet'\n")
				outfile.write("      delegate_to: localhost\n")
				outfile.write("\n")
				outfile.write("    - set_fact: subnet_uri=\"{{ id_pools_ipv4_subnets[0].uri }}\"\n")
				outfile.write("    - debug: var=subnet_uri\n")
				outfile.write("\n")
			
			outfile.write("    - name: Create an Ethernet Network\n")
			outfile.write("      oneview_ethernet_network:\n")
			outfile.write("        config: \"{{ config }}\"\n")
			outfile.write("        state: present\n")
			outfile.write("        data:\n")
			outfile.write("            name:                   \""+variablesOneNet["name"]+"\"\n")
			outfile.write("            ethernetNetworkType:    "+variablesOneNet["type"]+"\n")
			outfile.write("            type:    ethernet-networkV4\n")
			outfile.write("            purpose:                \""+variablesOneNet["purpose"]+"\"\n")
			outfile.write("            smartLink:              "+variablesOneNet["smartlink"].lower()+"\n")
			outfile.write("            privateNetwork:         "+variablesOneNet["privatenetwork"].lower()+"\n")
			outfile.write("            vlanId:                 "+variablesOneNet["vlanid"]+"\n")
			if(variablesOneNet["ipv4subnet"]!="None"):
				outfile.write("            subnetUri:              \"{{ subnet_uri }}\"\n")
			outfile.write("            bandwidth:\n")
			outfile.write("               typicalBandwidth: "+variablesOneNet["preferredbandwidth"]+"\n")
			outfile.write("               maximumBandwidth: "+variablesOneNet["maxbandwidth"]+"\n")
			outfile.write("      delegate_to: localhost\n")
			outfile.write("\n")
		
		outfile.close()

#310 ehemals #05
def writeOSdeploymentServer(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('    - name: Ensure that the Deployment Server is present'+"\n")
		outfile.write('      oneview_os_deployment_server:'+"\n")
		outfile.write('        config: "{{ config }}"'+"\n")
		outfile.write('        state: present'+"\n")
		outfile.write('        data:'+"\n")
		outfile.write('          name: "'+frame["variables"]["oneview_hostname"]+'_OSDS"'+"\n")
		outfile.write('          mgmtNetworkName: "oob-mgmt"'+"\n")
		outfile.write('          applianceName: "'+frame["letter"]+'-Master2, appliance 2"'+"\n")
		outfile.write('          deplManagersType: "Image Streamer"'+"\n")
		outfile.write(''+"\n")
		outfile.write('    - debug: var=os_deployment_server'+"\n")
		outfile.write("\n")
		#END
		outfile.close()

#320 ehemals #06
def writeNetworkset(nr,filenamepart):
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabnets)
	
	variablesHead = []
	variables = []
	networksets = []
	
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	
	for row in range(1,worksheet.nrows):
		variablesOneNet = {}
		for col in range(worksheet.ncols):
			val = worksheet.cell_value(row,col)
			
			if(isinstance(val,float)):
				val = str(int(val))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			variablesOneNet[variablesHead[col]] = val
			
			if(variablesHead[col]=="networkset"):
				if(val!=""):
					if(not val in networksets):
						networksets.append(val)
			
		variables.append(variablesOneNet)
	
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)

		#BEGIN
		for networkset in networksets:
			outfile.write('    - name: Create Network Set '+networkset+"\n")
			outfile.write('      oneview_network_set:'+"\n")
			outfile.write('        config: "{{ config }}"'+"\n")
			outfile.write('        state: present'+"\n")
			outfile.write('        data:'+"\n")
			outfile.write('          type: "network-setV4"'+"\n")
			outfile.write('          name: "'+networkset+'"'+"\n")
			outfile.write('          networkUris:'+"\n") # it is possible to pass names instead of URIs
			for v in variables:
				if(v["networkset"] == networkset):
					if(frame["letter"] in v["zone"]):
						outfile.write('            - '+v["name"]+"\n")
			outfile.write('      delegate_to: localhost'+"\n")
			outfile.write("\n")
		#END
		outfile.close()

#330 ehemals #10
def writeStoragesystem(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		writeFilepartRESTAPILogin(outfile,hostname,"Administrator",frame["variables"]["administrator_passwort"])

		#BEGIN
		networks = variablesSynergyNimbleAll[frame["letter"]]["variables"]["networks"].split(",")
		for i in range(len(networks)):
			outfile.write('  - name: Find '+networks[i]+' Network URI\n')	
			outfile.write('    oneview_ethernet_network_facts:\n')	
			outfile.write('      config: "{{ config }}"\n')	
			outfile.write('      name: "'+networks[i]+'"\n')	
			outfile.write('  - set_fact: var_iscsi_'+str(i)+'_network_uri="{{ ethernet_networks.uri }}"\n')	
			outfile.write('\n')	
			
		#extensionstring = ""
		#for i in range(len(networks)):
		#	extensionstring = extensionstring+' | assign_nimble_port("'+networks[i]+'",var_iscsi_'+str(i)+'_network_uri)'
		
		outfile.write('  - name: Add Nimble Storage System\n')	
		outfile.write('    oneview_storage_system:\n')	
		outfile.write('      config: "{{ config }}"\n')	
		outfile.write('      state: present\n')	
		outfile.write('      data:\n')	
		outfile.write('        hostname: "'+variablesSynergyNimbleAll[frame["letter"]]["variables"]["group_management_ip_or_host_name"]+'"\n')	
		outfile.write('        family: Nimble\n')	
		outfile.write('        credentials:\n')	
		outfile.write('          username: "'+variablesSynergyNimbleAll[frame["letter"]]["variables"]["username"]+'"\n')	
		outfile.write('          password: "'+variablesSynergyNimbleAll[frame["letter"]]["variables"]["password"]+'"\n')	
		outfile.write('    register: result\n')	
		outfile.write('  - set_fact: storage_system_uri="{{ result.ansible_facts.storage_system.uri }}"\n')	
		outfile.write('\n')	
		outfile.write('  - name: Manage Nimble Storage Pool\n')	
		outfile.write('    oneview_storage_pool:\n')	
		outfile.write('      config: "{{ config }}"\n')	
		outfile.write('      state: present\n')	
		outfile.write('      data:\n')	
		outfile.write('        storageSystemUri: "{{ storage_system_uri }}"\n')	
		outfile.write('        name: "'+variablesSynergyNimbleAll[frame["letter"]]["variables"]["storage_pool_name"]+'"\n')	
		outfile.write('        isManaged: true\n')	
		outfile.write('\n')
		outfile.write('  - name: Retrieve Nimble System as JSON\n')
		outfile.write('    uri:\n')
		outfile.write('      headers:\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('      url: "https://'+hostname+'/{{ storage_system_uri }}"\n')
		outfile.write('      method: GET\n')
		outfile.write('    register: nimble\n')
		outfile.write('\n')			
		#outfile.write('  - name: Populate Nimble Ports with Network URIs\n')
		#outfile.write('    set_fact:\n')
		#outfile.write('      nimble_with_ports: \'{{ nimble.json'+extensionstring+' }}\'\n')
		#outfile.write('\n')
		
		strings1 = []
		strings2 = []
		for i in range(len(networks)):
			varname = "var_list_"+convertToAnsibleVariableName(networks[i])
			strings1.append(varname)
			strings2.append('item.name != "'+networks[i]+'"')
			
			outfile.write('  - set_fact:\n')
			outfile.write('      '+varname+': "{{ [] }}"\n')
			outfile.write('  - name: set fact\n')
			outfile.write('    set_fact:\n')
			outfile.write('      '+varname+': "{{ '+varname+' + [item | combine({\'expectedNetworkUri\':var_iscsi_'+str(i)+'_network_uri,\'mode\':\'Managed\'})] }}"\n')
			outfile.write('    when: item.name == "'+networks[i]+'"\n')
			outfile.write('    loop: "{{ nimble.json.ports }}"\n')
			#outfile.write('  - debug: var='+varname+'\n')
			outfile.write('\n')

		outfile.write('  - set_fact:\n')
		if(len(strings1)==0):
			outfile.write('      var_ports: "{{ [] }}"\n')
		else:
			outfile.write('      var_ports: "{{ [] + '+' + '.join(strings1)+'}}"\n')
		outfile.write('  - set_fact:\n')
		outfile.write('      var_ports: "{{ var_ports + [item] }}"\n')
		if(len(strings2)!=0):
			outfile.write('    when: '+' and '.join(strings2)+'\n')
		outfile.write('    loop: "{{ nimble.json.ports }}"\n')
		#outfile.write('  - debug: var=var_ports\n')
		outfile.write('\n')
		outfile.write('  - name: Populate Nimble Ports with Network URIs\n')
		outfile.write('    set_fact:\n')
		outfile.write('      nimble_with_ports: \'{{ nimble.json |combine({"ports":var_ports})}}\'\n')
		outfile.write('  - debug: var=nimble_with_ports\n')
		outfile.write('\n')
		
		
		outfile.write('  - name: Update Nimble System \n')
		outfile.write('    uri:\n')
		outfile.write('      headers:\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('      url: "https://'+hostname+'/{{ storage_system_uri }}"\n')
		outfile.write('      method: PUT\n')
		outfile.write('      body: "{{ nimble_with_ports }}"\n')
		outfile.write('      body_format: json\n')
		outfile.write('      status_code: 202\n')
		outfile.write('    register: nimble\n')
		outfile.write('\n')
		waitAndOutputTask(outfile,["one"],["nimble['location']"])
		#END
		outfile.close()
		
#334 ehemals #20
def writeCreateVolumeTemplate(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]
		writeFilepartRESTAPILogin(outfile,hostname,"Administrator",frame["variables"]["administrator_passwort"])

		#BEGIN
		outfile.write('  - name: Find Storage System URI\n')
		outfile.write('    oneview_storage_system_facts:\n')
		outfile.write('      config: "{{ config }}"\n')
		outfile.write('      storage_hostname: "'+variablesSynergyNimbleAll[frame["letter"]]["variables"]["group_management_ip_or_host_name"]+'"\n')
		outfile.write('  - set_fact: storage_system_uri="{{ storage_systems.uri }}"\n')
		outfile.write('\n')
		outfile.write('  - set_fact: nimble_performance_policy="{{ item.id }}"\n')
		outfile.write('    when: item.name == "VMware ESX 5"\n')
		outfile.write('    with_items: "{{storage_systems.deviceSpecificAttributes.performancePolicies }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: Find Storage Pool URI\n')
		outfile.write('    oneview_storage_pool_facts:\n')
		outfile.write('      config: "{{ config }}"\n')
		outfile.write('  - set_fact: storage_pool_uri="{{ storage_pools.0.uri }}"\n')
		outfile.write('\n')
		outfile.write('  - name: Retrieve Nimble root Volume Template URI\n')
		outfile.write('    uri:\n')
		outfile.write('      headers:\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('      url: "https://'+hostname+'/{{ storage_system_uri }}/templates?query=isRoot%20EQ%20true"\n')
		outfile.write('      method: GET\n')
		outfile.write('    register: root_template\n')
		outfile.write('  - set_fact: root_template_uri="{{ root_template.json.members[0].uri }}"\n')
		outfile.write('\n')
		outfile.write('  - name: Create a Storage Volume Template\n')
		outfile.write('    oneview_storage_volume_template:\n')
		outfile.write('      config: "{{ config }}"\n')
		outfile.write('      state: present\n')
		outfile.write('      data:\n')
		outfile.write('        rootTemplateUri: "{{ root_template_uri }}"\n')
		outfile.write('        properties:\n')
		outfile.write('          name:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: false\n')
		outfile.write('            type: string\n')
		outfile.write('            title: Volume name\n')
		outfile.write('            required: true\n')
		outfile.write('            maxLength: 100\n')
		outfile.write('            minLength: 1\n')
		outfile.write('            description: A volume name between 1 and 100 characters\n')
		outfile.write('          size:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: false\n')
		outfile.write('              semanticType: capacity\n')
		outfile.write('            type: integer\n')
		outfile.write('            title: Capacity\n')
		outfile.write('            default: 8796093022208\n')
		outfile.write('            maximum: 139637976727552\n')
		outfile.write('            minimum: 1048576\n')
		outfile.write('            required: true\n')
		outfile.write('            description: Capacity of the volume in bytes\n')
		outfile.write('          folder:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('              semanticType: device-folder\n')
		outfile.write('            type: string\n')
		outfile.write('            title: Folder\n')
		outfile.write('            default: \n')
		outfile.write('            required: false\n')
		outfile.write('            description: Nimble identifier of the folder which will contain the volume\n')
		outfile.write('          isPinned:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('            type: boolean\n')
		outfile.write('            title: Is Volume Cache Pinning enabled\n')
		outfile.write('            default: false\n')
		outfile.write('            required: false\n')
		outfile.write('            description: Enables or disables volume cache pinning for the volume\n')
		outfile.write('          iopsLimit:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('            type: integer\n')
		outfile.write('            title: Maximum Input/Output Operations per Second\n')
		outfile.write('            default: \n')
		outfile.write('            maximum: 4294967294\n')
		outfile.write('            minimum: 256\n')
		outfile.write('            required: false\n')
		outfile.write('            description: Specifies the maximum input/output operations per second for the\n')
		outfile.write('              volume\n')
		outfile.write('          volumeSet:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('              semanticType: device-volume-collection\n')
		outfile.write('            type: string\n')
		outfile.write('            title: Volume Set\n')
		outfile.write('            format: x-uri-reference\n')
		outfile.write('            default: \n')
		outfile.write('            required: false\n')
		outfile.write('            description: URI of the volume set to associate with the volume\n')
		outfile.write('          description:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: false\n')
		outfile.write('            type: string\n')
		outfile.write('            title: Description\n')
		outfile.write('            default: ""\n')
		outfile.write('            required: false\n')
		outfile.write('            maxLength: 2000\n')
		outfile.write('            minLength: 0\n')
		outfile.write('            description: A description for the volume\n')
		outfile.write('          isEncrypted:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('              createOnly: true\n')
		outfile.write('            type: boolean\n')
		outfile.write('            title: Is Encryption enabled\n')
		outfile.write('            default: false\n')
		outfile.write('            required: false\n')
		outfile.write('            description: Enables or disables encryption of the volume\n')
		outfile.write('          isShareable:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: false\n')
		outfile.write('            type: boolean\n')
		outfile.write('            title: Is Shareable\n')
		outfile.write('            default: true\n')
		outfile.write('            required: false\n')
		outfile.write('            description: The shareability of the volume\n')
		outfile.write('          storagePool:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: false\n')
		outfile.write('              createOnly: true\n')
		outfile.write('              semanticType: device-storage-pool\n')
		outfile.write('            type: string\n')
		outfile.write('            title: Storage Pool\n')
		outfile.write('            format: x-uri-reference\n')
		outfile.write('            required: true\n')
		outfile.write('            description: URI of the Storage Pool the volume should be added to\n')
		outfile.write('            default: "{{ storage_pool_uri }}"\n')
		outfile.write('          isDeduplicated:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('            type: boolean\n')
		outfile.write('            title: Is Deduplication enabled\n')
		outfile.write('            default: true\n')
		outfile.write('            required: false\n')
		outfile.write('            description: Enables or disables deduplication of the volume\n')
		outfile.write('          templateVersion:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('            type: string\n')
		outfile.write('            title: Template version\n')
		outfile.write('            default: "1.0"\n')
		outfile.write('            required: true\n')
		outfile.write('            description: Version of the template\n')
		outfile.write('          provisioningType:\n')
		outfile.write('            enum:\n')
		outfile.write('            - Thin\n')
		outfile.write('            - Full\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('              createOnly: true\n')
		outfile.write('              semanticType: device-provisioningType\n')
		outfile.write('            type: string\n')
		outfile.write('            title: Provisioning Type\n')
		outfile.write('            default: Thin\n')
		outfile.write('            required: false\n')
		outfile.write('            description: The provisioning type for the volume\n')
		outfile.write('          dataTransferLimit:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('            type: integer\n')
		outfile.write('            title: Data Transfer Limit Maximum in mebibytes\n')
		outfile.write('            default: \n')
		outfile.write('            maximum: 4294967294\n')
		outfile.write('            minimum: 1\n')
		outfile.write('            required: false\n')
		outfile.write('            description: Specifies the maximum data transfer limit for the volume\n')
		outfile.write('          performancePolicy:\n')
		outfile.write('            meta:\n')
		outfile.write('              locked: true\n')
		outfile.write('              semanticType: device-performancePolicy\n')
		outfile.write('            type: string\n')
		outfile.write('            title: Performance Policy\n')
		outfile.write('            required: true\n')
		outfile.write('            description: Nimble identifier of the performance policy to associate with the volume\n')
		outfile.write('            default: "{{ nimble_performance_policy }}"\n')
		outfile.write('        name: "'+variablesSynergyNimbleAll[frame["letter"]]["variables"]["template_name"]+'"\n')
		outfile.write('        description: ""\n')
		outfile.write('\n')
		#END
		outfile.close()

#336 ehemals #21
def writeCreateVolumes(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
				
		#BEGIN
		outfile.write('    - name: Find Storage Volume Template by name\n')
		outfile.write('      oneview_storage_volume_template_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        name: "'+variablesSynergyNimbleAll[frame["letter"]]["variables"]["template_name"]+'"\n')
		outfile.write('    - set_fact: storage_volume_template_uri="{{ storage_volume_templates.0.uri }}"\n')
		outfile.write('    - set_fact: storage_pool_uri="{{ storage_volume_templates.0.storagePoolUri }}"\n')
		outfile.write('    - set_fact: performance_policy="{{ storage_volume_templates.0.properties.performancePolicy.default }}"\n')
		outfile.write('\n')
		
		for cluster in variablesClustersAll:
			if(cluster[0]!=frame["letter"]):
				continue
			for i in range(1,3):
				storagevolumename = cluster+"-"+str(i).zfill(4)
				outfile.write('    - name: Create Volume '+storagevolumename+' based on a Storage Volume Template\n')
				outfile.write('      oneview_volume:\n')
				outfile.write('        config: "{{ config }}"\n')
				outfile.write('        state: present\n')
				outfile.write('        data:\n')
				outfile.write('          properties:\n')
				outfile.write('            name: "'+storagevolumename+'"\n')
				outfile.write('            description: ""\n')
				outfile.write('            storagePool: "{{ storage_pool_uri }}"\n')
				outfile.write('            size: 8796093022208\n')
				outfile.write('            provisioningType: Thin\n')
				outfile.write('            isShareable: true\n')
				outfile.write('            templateVersion: "1.0"\n')
				outfile.write('            isDeduplicated: true\n')
				outfile.write('            performancePolicy: "{{ performance_policy }}"\n')
				outfile.write('            folder:\n')
				outfile.write('            volumeSet:\n')
				outfile.write('            isEncrypted: false\n')
				outfile.write('            isPinned: false\n')
				outfile.write('            iopsLimit:\n')
				outfile.write('            dataTransferLimit:\n')
				outfile.write('          templateUri: "{{ storage_volume_template_uri }}"\n')
				outfile.write('          isPermanent: true\n')
				outfile.write('          initialScopeUris: \n')
				outfile.write('\n')
		#END
		outfile.close()

#340 ehemals #07
def writeLogicalInterconnectGroup(nr,filenamepart):
	#open workbook and worksheet
	workbook = xlrd.open_workbook(inputfilename)
	worksheet = workbook.sheet_by_name(exceltabnets)
	
	variablesHead = []
	variables = []
	
	for col in range(worksheet.ncols):
		name = convertToAnsibleVariableName(worksheet.cell_value(0,col))
		variablesHead.append(name)
	
	for row in range(1,worksheet.nrows):
		variablesOneNet = {}
		for col in range(worksheet.ncols):
			val = worksheet.cell_value(row,col)
			
			if(isinstance(val,float)):
				val = str(int(val))
			
			if(val=="#TODO" or val=="n/a" or val.startswith("#TODO")):
				val = ""
			
			if(val.find("#TODO") != -1):
				pos = val.find("#TODO")
				val = val[:pos-1]
			
			variablesOneNet[variablesHead[col]] = val
		variables.append(variablesOneNet)
	
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('#---------------------------- Logical Interconnect Group lig_sas'+"\n")
		outfile.write('     - name: Create logical Interconnect Group lig_sas'+"\n")
		outfile.write('       oneview_sas_logical_interconnect_group:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         state: present'+"\n")
		outfile.write('         data:'+"\n")
		outfile.write('             name:                   "lig_sas"'+"\n")
		outfile.write('             enclosureType:          "SY12000"'+"\n")
		outfile.write('             redundancyType:         ""'+"\n")
		outfile.write('             type:                   "sas-logical-interconnect-groupV2"'+"\n")
		outfile.write('             interconnectBaySet:     1'+"\n")
		outfile.write('             enclosureIndexes:'+"\n")
		outfile.write('                 - 1'+"\n")
		outfile.write('             interconnectMapTemplate:'+"\n")
		outfile.write('                 interconnectMapEntryTemplates:'+"\n")
		outfile.write('                     - permittedInterconnectTypeUri: "/rest/sas-interconnect-types/Synergy12GbSASConnectionModule"'+"\n")
		outfile.write('                       enclosureIndex:               "1"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    4'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeUri: "/rest/sas-interconnect-types/Synergy12GbSASConnectionModule"'+"\n")
		outfile.write('                       enclosureIndex:               "1"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write(' '+"\n")
		outfile.write('#---------------------------- Logical Interconnect Group lig_vc'+"\n")
		
		for v in variables:
			if(frame["letter"] in v["zone"]):
				outfile.write('     - name: Get uri for network '+v["name"]+"\n")
				outfile.write('       oneview_ethernet_network_facts:'+"\n")
				outfile.write('         config:         "{{ config }}"'+"\n")
				outfile.write('         name:           "'+v["name"]+'"'+"\n")
				outfile.write('     - set_fact:         var_'+convertToAnsibleVariableName(v["name"])+'="{{ethernet_networks.uri}}"'+"\n")
				outfile.write("\n")

		outfile.write('     - name: Create logical Interconnect Group lig_vc'+"\n")
		outfile.write('       oneview_logical_interconnect_group:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         state: present'+"\n")
		outfile.write('         data:'+"\n")
		outfile.write('             name:                   "lig_vc"'+"\n")
		outfile.write('             enclosureType:          "SY12000"'+"\n")
		outfile.write('             type:                   "logical-interconnect-groupV6"'+"\n")
		outfile.write('             redundancyType:         "HighlyAvailable"'+"\n")
		outfile.write('             interconnectBaySet:     3'+"\n")
		outfile.write('             ethernetSettings:           '+"\n")
		outfile.write('                 type:                           "EthernetInterconnectSettingsV5"'+"\n")
		outfile.write('                 enableIgmpSnooping:             false'+"\n")
		outfile.write('                 igmpIdleTimeoutInterval:        260'+"\n")
		outfile.write('                 enableNetworkLoopProtection:    true'+"\n")
		outfile.write('                 enablePauseFloodProtection:     true'+"\n")
		outfile.write('                 enableRichTLV:                  false'+"\n")
		outfile.write('                 enableTaggedLldp:               true'+"\n")
		outfile.write('                 enableStormControl:             false'+"\n")
		outfile.write('                 stormControlThreshold:          0'+"\n")
		outfile.write('                 enableFastMacCacheFailover:     true'+"\n")
		outfile.write('                 macRefreshInterval:             5'+"\n")
		outfile.write('             enclosureIndexes:'+"\n")
		outfile.write('                 - 1'+"\n")
		outfile.write('                 - 2'+"\n")
		outfile.write('                 - 3'+"\n")
		outfile.write('             interconnectMapTemplate:'+"\n")
		outfile.write('                 interconnectMapEntryTemplates:'+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Synergy 20Gb Interconnect Link Module"'+"\n")
		outfile.write('                       enclosureIndex:               "2"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    2'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Synergy 20Gb Interconnect Link Module"'+"\n")
		outfile.write('                       enclosureIndex:               "3"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    6'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Synergy 20Gb Interconnect Link Module"'+"\n")
		outfile.write('                       enclosureIndex:               "3"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Synergy 20Gb Interconnect Link Module"'+"\n")
		outfile.write('                       enclosureIndex:               "1"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                             - relativeValue:    6'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Virtual Connect SE 40Gb F8 Module for Synergy"'+"\n")
		outfile.write('                       enclosureIndex:               "2"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    6'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('                             - relativeValue:    2'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                     - permittedInterconnectTypeName: "Virtual Connect SE 40Gb F8 Module for Synergy"'+"\n")
		outfile.write('                       enclosureIndex:               "1"'+"\n")
		outfile.write('                       logicalLocation: '+"\n")
		outfile.write('                         locationEntries: '+"\n")
		outfile.write('                             - relativeValue:    1'+"\n")
		outfile.write('                               type:             "Enclosure" '+"\n")
		outfile.write('                             - relativeValue:    3'+"\n")
		outfile.write('                               type:             "Bay" '+"\n")
		outfile.write('             internalNetworkUris:'+"\n")
		
		for v in variables:
			if(frame["letter"] in v["zone"] and v["uplinkset"]=="Internal"):
				outfile.write('                - "{{var_'+convertToAnsibleVariableName(v["name"])+'}}"    # networkName: '+v["name"]+' '+"\n")

		outfile.write('             uplinkSets:'+"\n")
		outfile.write('                 - name:                  "iSCSI-Deployment"'+"\n")
		outfile.write('                   networkType:           "Ethernet"'+"\n")
		outfile.write('                   ethernetNetworkType:   "ImageStreamer"'+"\n")
		outfile.write('                   mode:                  "Auto"'+"\n")
		outfile.write('                   networkUris:'+"\n")

		for v in variables:
			if(frame["letter"] in v["zone"] and v["uplinkset"]=="iSCSI-Deployment"):
				outfile.write('                         - "{{var_'+convertToAnsibleVariableName(v["name"])+'}}"    # networkName: '+v["name"]+' '+"\n")

		outfile.write('                   logicalPortConfigInfos:'+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 63'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 6'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 2'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 1'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 62'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 3'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 62'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 6'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 2'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 1'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 63'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 3'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                 - name:             "Uplink_Prod"'+"\n")
		outfile.write('                   networkType:      "Ethernet"'+"\n")
		outfile.write('                   mode:             "Auto"'+"\n")
		outfile.write('                   lacpTimer:        "Long"'+"\n")
		outfile.write('                   networkUris:'+"\n")
		
		for v in variables:
			if(frame["letter"] in v["zone"] and v["uplinkset"]=="Uplink_Prod"):
				outfile.write('                         - "{{var_'+convertToAnsibleVariableName(v["name"])+'}}"    # networkName: '+v["name"]+' '+"\n")

		outfile.write('                   logicalPortConfigInfos:'+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 6'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 2'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 71'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 1'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 3'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 71'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 1'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('                             - relativeValue: 66'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 3'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                     - desiredSpeed: "Auto"'+"\n")
		outfile.write('                       logicalLocation:'+"\n")
		outfile.write('                         locationEntries:'+"\n")
		outfile.write('                             - relativeValue: 6'+"\n")
		outfile.write('                               type: "Bay" '+"\n")
		outfile.write('                             - relativeValue: 66'+"\n")
		outfile.write('                               type: "Port" '+"\n")
		outfile.write('                             - relativeValue: 2'+"\n")
		outfile.write('                               type: "Enclosure" '+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write(''+"\n")
		#END
		
		outfile.close()

#342 ehemals #08
def writeEnclosureGroup(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('#---------------------------- Enclosure Group '+frame["variables"]["enclosure_group_name"]+''+"\n")
		outfile.write('     - name: Get uri for LIG lig_sas'+"\n")
		outfile.write('       oneview_sas_logical_interconnect_group_facts:'+"\n")
		outfile.write('         config:         "{{ config }}"'+"\n")
		outfile.write('         name:           "lig_sas"'+"\n")
		outfile.write('     - set_fact:         var_lig_sas="{{sas_logical_interconnect_groups[0].uri}}"'+"\n")
		outfile.write(' '+"\n")
		outfile.write('     - name: Get uri for LIG lig_vc'+"\n")
		outfile.write('       oneview_logical_interconnect_group_facts:'+"\n")
		outfile.write('         config:         "{{ config }}"'+"\n")
		outfile.write('         name:           "lig_vc"'+"\n")
		outfile.write('     - set_fact:         var_lig_vc="{{logical_interconnect_groups[0].uri}}"'+"\n")
		outfile.write(''+"\n")
		outfile.write('     - name: Get uri for oobm-mgmt Pool'+"\n")
		outfile.write('       oneview_ethernet_network_facts:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         name: "oob-mgmt"'+"\n")
		outfile.write('     - set_fact:         var_oob_mgmt_subnet="{{ ethernet_networks.subnetUri }}"'+"\n")
		outfile.write(''+"\n")
		outfile.write('     - name: Get uri for oob-mgmt_Range'+"\n")
		outfile.write('       oneview_id_pools_ipv4_range_facts:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         subnetUri: "{{ var_oob_mgmt_subnet }}"'+"\n")
		outfile.write('     - set_fact: var_oob_mgmt_subnet_range="{{ id_pools_ipv4_ranges[0].uri }}"'+"\n")
		outfile.write(' '+"\n")
		outfile.write('     - name: Create Enclosure Group '+frame["variables"]["enclosure_group_name"]+''+"\n")
		outfile.write('       oneview_enclosure_group:'+"\n")
		outfile.write('         config: "{{ config }}"'+"\n")
		outfile.write('         state: present'+"\n")
		outfile.write('         data:'+"\n")
		outfile.write('             name:                                   "'+frame["variables"]["enclosure_group_name"]+'"'+"\n")
		outfile.write('             ipAddressingMode:                       "IpPool"'+"\n")
		outfile.write('             ipRangeUris:'+"\n")
		outfile.write('               - "{{ var_oob_mgmt_subnet_range }}"'+"\n")
		outfile.write('             osDeploymentSettings:'+"\n")
		outfile.write('               manageOSDeployment: true'+"\n")
		outfile.write('               deploymentModeSettings:'+"\n")
		outfile.write('                 deploymentMode: Internal'+"\n")
		outfile.write('             enclosureCount:                         3'+"\n")
		outfile.write('             powerMode:                              RedundantPowerFeed'+"\n")
		outfile.write('             interconnectBayMappings:'+"\n")
		outfile.write('                 - interconnectBay:                  1'+"\n")
		outfile.write('                   enclosureIndex:                   1'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  1'+"\n")
		outfile.write('                   enclosureIndex:                   2'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  1'+"\n")
		outfile.write('                   enclosureIndex:                   3'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  3'+"\n")
		outfile.write('                   enclosureIndex:                   1'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  3'+"\n")
		outfile.write('                   enclosureIndex:                   2'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  3'+"\n")
		outfile.write('                   enclosureIndex:                   3'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  4'+"\n")
		outfile.write('                   enclosureIndex:                   1'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  4'+"\n")
		outfile.write('                   enclosureIndex:                   2'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  4'+"\n")
		outfile.write('                   enclosureIndex:                   3'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_sas}}"  # lig name  lig_sas '+"\n")
		outfile.write('                 - interconnectBay:                  6'+"\n")
		outfile.write('                   enclosureIndex:                   1'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  6'+"\n")
		outfile.write('                   enclosureIndex:                   2'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('                 - interconnectBay:                  6'+"\n")
		outfile.write('                   enclosureIndex:                   3'+"\n")
		outfile.write('                   logicalInterconnectGroupUri:      "{{var_lig_vc}}"  # lig name  lig_vc '+"\n")
		outfile.write('       delegate_to: localhost'+"\n")
		outfile.write("\n")
		#END
		outfile.close()

#344 ehemals #09
def writeLogicalEnclosure(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('  - name: Gather facts about SPP\n')
		outfile.write('    oneview_firmware_driver_facts:\n')
		outfile.write('      config: "{{ config }}"\n')
		outfile.write('    no_log: true\n')
		outfile.write('    delegate_to: localhost\n')
		outfile.write('    register: result\n')
		outfile.write('\n')
		outfile.write('  - set_fact:\n')
		outfile.write('      firmware_baseline_uri="{{ result.ansible_facts.firmware_drivers[0].uri }}"\n')
		outfile.write("\n")
		outfile.write('  - name: Gather information about Enclosure '+frame["letter"]+'-Master1'+"\n")
		outfile.write('    oneview_enclosure_info:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      name: "'+frame["letter"]+'-Master1"'+"\n")
		outfile.write('    no_log: true'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('    register: result'+"\n")
		outfile.write("\n")
		outfile.write('  - set_fact:'+"\n")
		outfile.write('      var_master1uri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('  - name: Gather information about Enclosure '+frame["letter"]+'-Master2'+"\n")
		outfile.write('    oneview_enclosure_info:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      name: "'+frame["letter"]+'-Master2"'+"\n")
		outfile.write('    no_log: true'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('    register: result'+"\n")
		outfile.write("\n")
		outfile.write('  - set_fact:'+"\n")
		outfile.write('      var_master2uri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('  - name: Gather information about Enclosure '+frame["letter"]+'-Slave'+"\n")
		outfile.write('    oneview_enclosure_info:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      name: "'+frame["letter"]+'-Slave"'+"\n")
		outfile.write('    no_log: true'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('    register: result'+"\n")
		outfile.write("\n")
		outfile.write('  - set_fact:'+"\n")
		outfile.write('      var_slaveuri="{{ result.enclosures[0].uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('  - name: Gather facts about Enclosure Groups'+"\n")
		outfile.write('    oneview_enclosure_group_facts:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      name: "'+frame["variables"]["enclosure_group_name"]+'"'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('  - set_fact: var_enclosure_group_uri="{{ enclosure_groups.uri }}"'+"\n")
		outfile.write("\n")
		outfile.write('  - name: Create a Logical Enclosure (available only on HPE Synergy)'+"\n")
		outfile.write('    oneview_logical_enclosure:'+"\n")
		outfile.write('      config: "{{ config }}"'+"\n")
		outfile.write('      state: present'+"\n")
		outfile.write('      data:'+"\n")
		outfile.write('        name: "ComputeBlock'+frame["letter"]+'"'+"\n")
		outfile.write('        enclosureUris:'+"\n")
		outfile.write('          - "{{ var_master1uri }}"'+"\n")
		outfile.write('          - "{{ var_master2uri }}"'+"\n")
		outfile.write('          - "{{ var_slaveuri }}"'+"\n")
		outfile.write('        enclosureGroupUri: "{{ var_enclosure_group_uri }}"'+"\n")
		outfile.write('        firmwareBaselineUri: "{{ firmware_baseline_uri }}"'+"\n")
		outfile.write('    delegate_to: localhost'+"\n")
		outfile.write('\n')
		#END
		outfile.close()
		
#346 ehemals #17
def writeCreateServerProfileTemplate(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]

		#BEGIN
		outfile.write('    - name: Gather facts about all Os Deployment Plans\n')
		outfile.write('      oneview_os_deployment_plan_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('    - set_fact:         var_os_deployment_plans_0_name="{{os_deployment_plans[0]["name"]}}"\n')
		outfile.write('\n')
		outfile.write('    - name: Find Deployment Plan URI\n')
		outfile.write('      oneview_os_deployment_plan_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        name: "{{ var_os_deployment_plans_0_name }}"\n')
		outfile.write('    - set_fact: deployment_plan_uri="{{ os_deployment_plans[0].uri }}"\n')
		outfile.write('\n')
		outfile.write('    - name: Find Firmware Baseline URI\n')
		outfile.write('      oneview_firmware_driver_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('    - set_fact: firmware_baseline_uri="{{ firmware_drivers[0].uri }}"\n')
		outfile.write('\n')
		outfile.write('    - name: Find Network Set URI\n')
		outfile.write('      oneview_network_set_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: prod_netset_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ network_sets }}"\n')
		outfile.write('      when: item.name is match "set_Prod"\n')
		outfile.write('\n')
		outfile.write('    - name: Gather network URIs\n')
		outfile.write('      oneview_ethernet_network_facts:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: deploy_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "iSCSI-Deployment"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: management_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "ib-mgmt"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: vmotion_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "vSphereVMotion"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: iscsi_a_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "iSCSI-A"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: iscsi_b_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "iSCSI-B"\n')
		outfile.write('\n')
		outfile.write('    - set_fact: ft_network_uri="{{ item.uri }}"\n')
		outfile.write('      no_log: True\n')
		outfile.write('      loop: "{{ ethernet_networks }}"\n')
		outfile.write('      when: item.name is match "vSphereFT"\n')
		outfile.write('\n')
		outfile.write('    - name: Create Server Profile Template\n')
		outfile.write('      oneview_server_profile_template:\n')
		outfile.write('        config: "{{ config }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          type: ServerProfileTemplateV6\n')
		outfile.write('          name: "Nublar_ESXi"\n')
		outfile.write('          description: "ESXi 6.7 Update 2 Build 13981272 mit NCM 6.1 und iSUT 2.4"\n')
		outfile.write('          serverProfileDescription: ""\n')
		outfile.write('          serverHardwareTypeName: "HypervisorNode"\n')
		outfile.write('          enclosureGroupName: "'+frame["variables"]["enclosure_group_name"]+'"\n')
		outfile.write('          affinity: Bay\n')
		outfile.write('          hideUnusedFlexNics: true\n')
		outfile.write('          macType: Virtual\n')
		outfile.write('          wwnType: Virtual\n')
		outfile.write('          serialNumberType: Virtual\n')
		outfile.write('          iscsiInitiatorNameType: AutoGenerated\n')
		outfile.write('          osDeploymentSettings:\n')
		outfile.write('            osDeploymentPlanUri: "{{ deployment_plan_uri }}"\n')
		outfile.write('            osCustomAttributes:\n')
		outfile.write('            - name: DomainName\n')
		outfile.write('              value: ad.nublar.de\n')
		outfile.write('              constraints: \'{"helpText":""}\'\n')
		outfile.write('              type: fqdn\n')
		outfile.write('            - name: Hostname\n')
		outfile.write('              value: ""\n')
		outfile.write('              constraints: \'{"helpText":""}\'\n')
		outfile.write('              type: hostname\n')
		outfile.write('            - name: ManagementNIC.connectionid\n')
		outfile.write('              value: "3"\n')
		outfile.write('            - name: ManagementNIC.dns1\n')
		outfile.write('              value: 10.40.72.10\n')
		outfile.write('            - name: ManagementNIC.dns2\n')
		outfile.write('              value: 10.40.72.11\n')
		outfile.write('            - name: ManagementNIC.gateway\n')
		outfile.write('              value: 10.40.195.254\n')
		outfile.write('            - name: ManagementNIC.ipaddress\n')
		outfile.write('              value: ""\n')
		outfile.write('            - name: ManagementNIC.netmask\n')
		outfile.write('              value: 255.255.254.0\n')
		outfile.write('            - name: ManagementNIC.networkuri\n')
		outfile.write('              value: "{{ management_network_uri }}"\n')
		outfile.write('            - name: ManagementNIC.constraint\n')
		outfile.write('              value: userspecified\n')
		outfile.write('            - name: ManagementNIC.vlanid\n')
		outfile.write('              value: "0"\n')
		outfile.write('            - name: ManagementNIC2.connectionid\n')
		outfile.write('              value: "4"\n')
		outfile.write('            - name: ManagementNIC2.networkuri\n')
		outfile.write('              value: "{{ management_network_uri }}"\n')
		outfile.write('            - name: ManagementNIC2.constraint\n')
		outfile.write('              value: userspecified\n')
		outfile.write('            - name: ManagementNIC2.vlanid\n')
		outfile.write('              value: "0"\n')
		outfile.write('            - name: Password\n')
		outfile.write('              value: ""\n')
		outfile.write('            - name: SSH\n')
		outfile.write('              value: enabled\n')
		outfile.write('              constraints: \'{"options":["enabled","disabled"]}\'\n')
		outfile.write('              type: option\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          firmware:\n')
		outfile.write('            manageFirmware: true\n')
		outfile.write('            firmwareBaselineUri: "{{ firmware_baseline_uri }}"\n')
		outfile.write('            forceInstallFirmware: false\n')
		outfile.write('            firmwareInstallType: FirmwareOnlyOfflineMode\n')
		outfile.write('            firmwareActivationType: Immediate\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          connectionSettings:\n')
		outfile.write('            connections:\n')
		outfile.write('            - id: 1\n')
		outfile.write('              name: Deployment Network A\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Mezz 3:1-a\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ deploy_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: Auto\n')
		outfile.write('              ipv4:\n')
		outfile.write('                ipAddressSource: SubnetPool\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: Primary\n')
		outfile.write('                bootVlanId: \n')
		outfile.write('                ethernetBootType: iSCSI\n')
		outfile.write('                bootVolumeSource: UserDefined\n')
		outfile.write('                iscsi:\n')
		outfile.write('                  initiatorNameSource: ProfileInitiatorName\n')
		outfile.write('                  secondBootTargetIp: ""\n')
		outfile.write('                  chapLevel: None\n')
		outfile.write('            - id: 2\n')
		outfile.write('              name: Deployment Network B\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Mezz 3:2-a\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ deploy_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: Auto\n')
		outfile.write('              ipv4:\n')
		outfile.write('                ipAddressSource: SubnetPool\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: Secondary\n')
		outfile.write('                bootVlanId: \n')
		outfile.write('                ethernetBootType: iSCSI\n')
		outfile.write('                bootVolumeSource: UserDefined\n')
		outfile.write('                iscsi:\n')
		outfile.write('                  initiatorNameSource: ProfileInitiatorName\n')
		outfile.write('                  secondBootTargetIp: ""\n')
		outfile.write('                  chapLevel: None\n')
		outfile.write('            - id: 3\n')
		outfile.write('              name: mgmt-1\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Mezz 3:1-d\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ management_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 4\n')
		outfile.write('              name: mgmt-2\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Mezz 3:2-d\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ management_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 5\n')
		outfile.write('              name: vmotion-1\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ vmotion_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 6\n')
		outfile.write('              name: vmotion-2\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ vmotion_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 7\n')
		outfile.write('              name: prod-1\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ prod_netset_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 8\n')
		outfile.write('              name: prod-2\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ prod_netset_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 9\n')
		outfile.write('              name: iSCSI-A\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ iscsi_a_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 10\n')
		outfile.write('              name: iSCSI-B\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ iscsi_b_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 11\n')
		outfile.write('              name: ft-1\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ ft_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            - id: 12\n')
		outfile.write('              name: ft-2\n')
		outfile.write('              functionType: Ethernet\n')
		outfile.write('              portId: Auto\n')
		outfile.write('              requestedMbps: "2500"\n')
		outfile.write('              networkUri: "{{ ft_network_uri }}"\n')
		outfile.write('              lagName: \n')
		outfile.write('              isolatedTrunk: false\n')
		outfile.write('              requestedVFs: "0"\n')
		outfile.write('              ipv4: {}\n')
		outfile.write('              boot:\n')
		outfile.write('                priority: NotBootable\n')
		outfile.write('                iscsi: {}\n')
		outfile.write('            manageConnections: true\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          bootMode:\n')
		outfile.write('            manageMode: true\n')
		outfile.write('            mode: UEFIOptimized\n')
		outfile.write('            secureBoot: Unmanaged\n')
		outfile.write('            pxeBootPolicy: Auto\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          boot:\n')
		outfile.write('            manageBoot: true\n')
		outfile.write('            order:\n')
		outfile.write('            - HardDisk\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          bios:\n')
		outfile.write('            manageBios: true\n')
		outfile.write('            overriddenSettings:\n')
		outfile.write('            - id: IntelUpiPowerManagement\n')
		outfile.write('              value: Disabled\n')
		outfile.write('            - id: UncoreFreqScaling\n')
		outfile.write('              value: Maximum\n')
		outfile.write('            - id: EnergyEfficientTurbo\n')
		outfile.write('              value: Disabled\n')
		outfile.write('            - id: MinProcIdlePkgState\n')
		outfile.write('              value: NoState\n')
		outfile.write('            - id: PowerRegulator\n')
		outfile.write('              value: StaticHighPerf\n')
		outfile.write('            - id: MinProcIdlePower\n')
		outfile.write('              value: NoCStates\n')
		outfile.write('            - id: SubNumaClustering\n')
		outfile.write('              value: Enabled\n')
		outfile.write('            - id: EnergyPerfBias\n')
		outfile.write('              value: MaxPerf\n')
		outfile.write('            - id: CollabPowerControl\n')
		outfile.write('              value: Disabled\n')
		outfile.write('            - id: WorkloadProfile\n')
		outfile.write('              value: Virtualization-MaxPerformance\n')
		outfile.write('            - id: NumaGroupSizeOpt\n')
		outfile.write('              value: Clustered\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('          managementProcessor:\n')
		outfile.write('            manageMp: false\n')
		outfile.write('            mpSettings: []\n')
		outfile.write('            complianceControl: Unchecked\n')
		outfile.write('          localStorage:\n')
		outfile.write('            complianceControl: Checked\n')
		outfile.write('            sasLogicalJBODs: []\n')
		outfile.write('            controllers:\n')
		outfile.write('            - logicalDrives:\n')
		outfile.write('              - name: local-raid1\n')
		outfile.write('                raidLevel: RAID1\n')
		outfile.write('                bootable: false\n')
		outfile.write('                numPhysicalDrives: 2\n')
		outfile.write('                driveTechnology: \n')
		outfile.write('                sasLogicalJBODId: \n')
		outfile.write('                accelerator: Unmanaged\n')
		outfile.write('              deviceSlot: Embedded\n')
		outfile.write('              mode: Mixed\n')
		outfile.write('              initialize: True\n')
		outfile.write('              driveWriteCache: Unmanaged\n')
		outfile.write('          sanStorage:\n')
		outfile.write('            manageSanStorage: true\n')
		outfile.write('            hostOSType: VMware (ESXi)\n')
		outfile.write('            volumeAttachments: []\n')
		outfile.write('            sanSystemCredentials: []\n')
		outfile.write('            complianceControl: CheckedMinimum\n')
		outfile.write('\n')
		outfile.write('    - debug: var=server_profile_template\n')
		outfile.write('\n')
		#END
		outfile.close()
		
#350 ehemals #13
def writeUploadAndExtractIsArtifact(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix,False)
		writeFilepartGetImageStreamerIp(outfile,config_prefx+frame["letter"]+config_sufix)
		writeFilepartGetConfig(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('\n')
		outfile.write('    - name: Upload an Artifact Bundle\n')
		outfile.write('      image_streamer_artifact_bundle:\n')
		#outfile.write('        config: "{{ config }}"\n')
		writeFilepartConfigvariablesInline(outfile,"        ")
		outfile.write('        image_streamer_hostname: "{{ var_image_streamer_ip }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          localArtifactBundleFilePath: "{{ playbook_dir }}/files/'+frame["variables"]["artifact_bundle"]+'"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		outfile.write('    - name: Extract an Artifact Bundle\n')
		outfile.write('      image_streamer_artifact_bundle:\n')
		#outfile.write('        config: "{{ config }}"\n')
		writeFilepartConfigvariablesInline(outfile,"        ")
		outfile.write('        image_streamer_hostname: "{{ var_image_streamer_ip }}"\n')
		outfile.write('        state: extracted\n')
		outfile.write('        data:\n')
		outfile.write('          name: "'+frame["variables"]["artifact_bundle"].replace(".zip","")+'"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		#END
		outfile.close()
		
#352 ehemals #14
def writeUploadGI(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix,False)
		writeFilepartGetImageStreamerIp(outfile,config_prefx+frame["letter"]+config_sufix)
		writeFilepartGetConfig(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('    - name: Upload a Golden Image\n')
		outfile.write('      image_streamer_golden_image:\n')
		#outfile.write('        config: "{{ config }}"\n')
		writeFilepartConfigvariablesInline(outfile,"        ")
		outfile.write('        image_streamer_hostname: "{{ var_image_streamer_ip }}"\n')
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          name: "'+frame["variables"]["golden_image"].replace(".zip","")+'"\n')
		outfile.write('          description: "Release Build mit SUT und NCM"\n')
		outfile.write('          localImageFilePath: "{{ playbook_dir }}/files/'+frame["variables"]["golden_image"]+'"\n')
		outfile.write('      delegate_to: localhost\n')
		outfile.write('\n')
		#END
		outfile.close()	

#354 ehemals #15
def writeCreatedeploymentplan(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix,False)
		writeFilepartGetImageStreamerIp(outfile,config_prefx+frame["letter"]+config_sufix)
		writeFilepartGetConfig(outfile,config_prefx+frame["letter"]+config_sufix)
		
		#BEGIN
		outfile.write('    - name: Retrieve GoldenImage URI\n')
		outfile.write('      image_streamer_golden_image_facts:\n')
		#outfile.write('        config: "{{ config }}"\n')
		writeFilepartConfigvariablesInline(outfile,"        ")
		outfile.write('        image_streamer_hostname: "{{ var_image_streamer_ip }}"\n')
		outfile.write('        name: "'+frame["variables"]["golden_image"].replace(".zip","")+'"\n')
		outfile.write('      register: result\n')
		outfile.write('\n')
		outfile.write('    - name: Create a Deployment Plan\n')
		outfile.write('      image_streamer_deployment_plan:\n')
		#outfile.write('        config: "{{ config }}"\n')
		writeFilepartConfigvariablesInline(outfile,"        ")
		outfile.write('        state: present\n')
		outfile.write('        data:\n')
		outfile.write('          description: "Release Build mit SUT und NCM"\n')
		outfile.write('          name: "nublarEsxiUpdated"\n')
		outfile.write('          hpProvided: "false"\n')
		outfile.write('          oeBuildPlanName: "HPE - ESXi 6.7 - deploy with multiple management NIC HA config - 2019-07-24"\n')
		outfile.write('          goldenImageURI: "{{ golden_images[0].uri }}"\n')
		outfile.write('          type: "OEDeploymentPlanV5"\n')
		outfile.write('          customAttributes:\n')
		outfile.write('            - name: ManagementNIC\n')
		outfile.write('              constraints: "{\\"ipv4static\\":true,\\"ipv4dhcp\\":true,\\"ipv4disable\\":false,\\"parameters\\":[\\"dns1\\",\\"dns2\\",\\"gateway\\",\\"ipaddress\\",\\"mac\\",\\"netmask\\",\\"vlanid\\"]}"\n')
		outfile.write('              description: "Configuring first NIC for Teaming in ESXi"\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "edc74bf8-d469-470f-a3e2-107e5c45e750"\n')
		outfile.write('              type: nic\n')
		outfile.write('              value: null\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: DomainName\n')
		outfile.write('              constraints: "{\\"helpText\\":\\"\\"}"\n')
		outfile.write('              description: "Fully Qualified Domain Name for ESXi host"\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "55704650-ce70-4f45-85f1-f3ff4dfeaf04"\n')
		outfile.write('              type: fqdn\n')
		outfile.write('              value: "ad.nublar.de"\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: SSH\n')
		outfile.write('              constraints: "{\\"options\\":[\\"enabled\\",\\"disabled\\"]}"\n')
		outfile.write('              description: "To enable/disable and start/stop SSH in ESXi"\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "99c9c40d-1f83-48a2-9367-1028ed55513f"\n')
		outfile.write('              type: option\n')
		outfile.write('              value: enabled\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: Hostname\n')
		outfile.write('              constraints: "{\\"helpText\\":\\"\\"}"\n')
		outfile.write('              description: "Hostname for VMware ESXi host. The hostname value can be defined manually or by using the tokens. This value must conform to valid hostname requirement defined by Internet standards."\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "8b11e853-e49a-49f0-9a0d-fbd80805758f"\n')
		outfile.write('              type: hostname\n')
		outfile.write('              value: ""\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: ManagementNIC2\n')
		outfile.write('              constraints: "{\\"ipv4static\\":true,\\"ipv4dhcp\\":false,\\"ipv4disable\\":false,\\"parameters\\":[\\"mac\\",\\"vlanid\\"]}"\n')
		outfile.write('              description: "Configuring second NIC for Teaming in ESXi"\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "46c75ab3-6da7-4a2b-a575-ef18dab2d458"\n')
		outfile.write('              type: nic\n')
		outfile.write('              value: null\n')
		outfile.write('              visible: true\n')
		outfile.write('            - name: Password\n')
		outfile.write('              constraints: "{\\"options\\":[\\"\\"]}"\n')
		outfile.write('              description: "Password value must meet password complexity and minimum length requirements defined for ESXi 5.x, ESXi 6.x appropriately."\n')
		outfile.write('              editable: true\n')
		outfile.write('              id: "e6709ead-e111-4b3e-8039-0cc97f2c0120"\n')
		outfile.write('              type: password\n')
		outfile.write('              value: ""\n')
		outfile.write('              visible: true\n')
		outfile.write('\n')
		#END
		outfile.close()

#360 ehemals #03
def writeAddHypervisorManager(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		writeFilepartRESTAPILogin(outfile,frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"],"Administrator",frame["variables"]["administrator_passwort"])
		
		
		#BEGIN
		outfile.write('  - name: Initiate asynchronous registration of an external hypervisor manager with the appliance. (Using AUTH-Token) (Statuscode should be 202)\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]+'/rest/hypervisor-managers\n')
		outfile.write('      method: POST\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('        type: "HypervisorManagerV2"\n')
		outfile.write('        name: "'+variablesHypervisorAll["hostname"]+'"\n')
		outfile.write('        username: "'+variablesHypervisorAll["username"]+'"\n')
		outfile.write('        password: "'+variablesHypervisorAll["password"]+'"\n')
		outfile.write('        hypervisorType: "Vmware"\n')
		outfile.write('        preferences:\n')
		outfile.write('          type: "Vmware"\n')
		outfile.write('          drsEnabled: '+("true" if (variablesHypervisorAll["distributed_resource_scheduler"]=="Enabled") else "false")+'\n')
		outfile.write('          haEnabled: '+("true" if (variablesHypervisorAll["high_availability"]=="Enabled") else "false")+'\n')
		outfile.write('          distributedSwitchVersion: "'+variablesHypervisorAll["distributed_vswitch_version"]+'"\n')
		outfile.write('          distributedSwitchUsage: "'+variablesHypervisorAll["use_distributed_vswitch_for"]+'"\n')
		outfile.write('          multiNicVMotion: '+("true" if (variablesHypervisorAll["multi_nic_vmotion"]=="Enabled") else "false")+'\n')
		outfile.write('          virtualSwitchType: "'+variablesHypervisorAll["vswitch_type"]+'"\n')
		outfile.write('      status_code: 202\n')
		outfile.write('    register: var_return\n')
		outfile.write('\n')
		waitAndOutputTask(outfile,["one"],["var_return['location']"])
		#END
		outfile.close()
		
#362 ehemals #18
def writeAddHypervisorClusterProfile(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]
		writeFilepartRESTAPILogin(outfile,hostname,"Administrator",frame["variables"]["administrator_passwort"])
		
		#BEGIN get Facts
		outfile.write('  - name: get Hypervisor manager uri\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+hostname+'/rest/hypervisor-managers\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_hypervisor_managers\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: var_hypervisor_manager_uri="{{var_hypervisor_managers["json"]["members"][0]["uri"]}}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: Gather Server Profile Template Nublar_ESXi uri\n')
		outfile.write('    oneview_server_profile_template_facts:\n')
		outfile.write('      config: "{{ config }}"\n')
		outfile.write('      name: "Nublar_ESXi"\n')
		outfile.write('    delegate_to: localhost\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: var_server_profile_template_uri="{{server_profile_templates[0]["uri"]}}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		
		#get standardswitchesUri and distributedswitchesUri
		outfile.write('  - set_fact: var_standardswitches_uris={{[]}}\n')
		outfile.write('  - set_fact: var_standardswitches_uris="{{var_standardswitches_uris + [item[\'networkUri\']]}}"\n')
		outfile.write('    when: item[\'networkUri\'] not in var_standardswitches_uris and item[\'networkUri\'] is search("/ethernet-networks/")\n')
		outfile.write('    with_items: \'{{ server_profile_templates[0]["connectionSettings"]["connections"] }}\'\n')
		outfile.write('    no_log: True\n')
		#outfile.write('  - debug: var=var_standardswitches_uris\n')
		outfile.write('\n')
		outfile.write('  - set_fact: var_distributedswitches_uris={{[]}}\n')
		outfile.write('  - set_fact: var_distributedswitches_uris="{{var_distributedswitches_uris + [item[\'networkUri\']]}}"\n')
		outfile.write('    when: item[\'networkUri\'] not in var_distributedswitches_uris and item[\'networkUri\'] is search("/network-sets/")\n')
		outfile.write('    with_items: \'{{ server_profile_templates[0]["connectionSettings"]["connections"] }}\'\n')
		outfile.write('    no_log: True\n')
		#outfile.write('  - debug: var=var_distributedswitches_uris\n')
		outfile.write('\n')
		
		#2x URI to names
		outfile.write('  - name: uri to name standardswitches\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: "https://'+hostname+'{{ item }}"\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_standardswitches_names_raw\n')
		outfile.write('    with_items: "{{ var_standardswitches_uris }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: uri to name distributedswitches\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: "https://'+hostname+'{{ item }}"\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_distributedswitches_names_raw\n')
		outfile.write('    with_items: "{{ var_distributedswitches_uris }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: uri to name distributedswitches\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: "https://'+hostname+'{{ item }}"\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_distributedswitches_networks_raw\n')
		outfile.write('    with_items: \'{{ var_distributedswitches_names_raw["results"][0]["json"]["networkUris"] }}\'\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - set_fact: var_switchesrequest="{{lookup(\'switchesrequest\',server_profile_templates[0]["connectionSettings"]["connections"],var_standardswitches_names_raw,var_distributedswitches_names_raw,"'+frame["letter"]+'",var_distributedswitches_networks_raw["results"])}}"\n')
		#outfile.write('  - debug: var=var_switchesrequest\n')
		outfile.write('\n')	
		
		#outfile.write('  - meta: end_play\n')
		#outfile.write('  - pause:\n')

		clusterlist = []
		urllist = [] #ansible variable to url
		for cluster in variablesClustersAll:
			if(cluster[0]!=frame["letter"]):
				continue
			clusterlist.append(cluster)
			urllist.append('var_return_'+convertToAnsibleVariableName(cluster)+'[\'location\']')
			#BEGIN SET
			outfile.write('  - name: Initiate asynchronous registration of an Hypervisor-Cluster-Profile (Using AUTH-Token) (Statuscode should be 202)\n')
			outfile.write('    uri:\n')
			outfile.write('      validate_certs: yes\n')
			outfile.write('      headers:\n')
			outfile.write('        Auth: "{{ var_token }}"\n')
			outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
			outfile.write('        Content-Type: application/json\n')
			outfile.write('      url: https://'+hostname+'/rest/hypervisor-cluster-profiles\n')
			outfile.write('      method: POST\n')
			outfile.write('      body_format: json\n')
			outfile.write('      body:\n')
			outfile.write('        type: HypervisorClusterProfileV3\n')
			outfile.write('        description: ""\n')
			outfile.write('        hypervisorType: Vmware\n')
			outfile.write('        hypervisorClusterSettings:\n')
			outfile.write('          type: "Vmware"\n')
			outfile.write('          drsEnabled: '+("true" if (variablesHypervisorAll["distributed_resource_scheduler"]=="Enabled") else "false")+'\n')
			outfile.write('          haEnabled: '+("true" if (variablesHypervisorAll["high_availability"]=="Enabled") else "false")+'\n')
			outfile.write('          distributedSwitchVersion: "'+variablesHypervisorAll["distributed_vswitch_version"]+'"\n')
			outfile.write('          distributedSwitchUsage: "'+variablesHypervisorAll["use_distributed_vswitch_for"]+'"\n')
			outfile.write('          multiNicVMotion: '+("true" if (variablesHypervisorAll["multi_nic_vmotion"]=="Enabled") else "false")+'\n')
			outfile.write('          virtualSwitchType: "'+variablesHypervisorAll["vswitch_type"]+'"\n')
			outfile.write('        hypervisorHostProfileTemplate:\n')
			outfile.write('          serverProfileTemplateUri: "{{ var_server_profile_template_uri }}"\n')
			outfile.write('          deploymentPlan:\n')
			outfile.write('            serverPassword: "'+variableHVCPserverpassword+'"\n')
			outfile.write('            deploymentCustomArgs: []\n')
			outfile.write('          hostprefix: "'+cluster+'"\n')
			outfile.write('          hostConfigPolicy:\n')
			outfile.write('            leaveHostInMaintenance: false\n')
			outfile.write('            useHostnameToRegister: true\n')
			outfile.write('          virtualSwitchConfigPolicy:\n')
			outfile.write('            manageVirtualSwitches: true\n')
			outfile.write('            configurePortGroups: true\n')
			outfile.write('          virtualSwitches: "{{var_switchesrequest}}"\n')
			outfile.write('        name: "'+cluster+'"\n')
			outfile.write('        mgmtIpSettingsOverride:\n')
			outfile.write('          netmask: "'+variablesMgmtNet["subnetmask"]+'"\n')
			outfile.write('          gateway: "'+variablesMgmtNet["gateway"]+'"\n')
			outfile.write('          dnsDomain: "'+variablesMgmtNet["domain"]+'"\n')
			outfile.write('          primaryDns: "'+variablesMgmtNet["dnsserver1"]+'"\n')
			outfile.write('          secondaryDns: "'+variablesMgmtNet["dnsserver2"]+'"\n')
			outfile.write('        hypervisorManagerUri: "{{ var_hypervisor_manager_uri }}"\n')
			outfile.write('        path: "FFM-'+frame["letter"]+'"\n')
			outfile.write('        initialScopeUris: []\n')
			outfile.write('      status_code: 202\n')
			outfile.write('    register: var_return_'+convertToAnsibleVariableName(cluster)+'\n')
			outfile.write('\n')
			
		waitAndOutputTask(outfile,clusterlist,urllist)
		#END
		outfile.close()

#364 ehemals #22
def writeAddVolumesToHypervisorClusterProfile(nr,filenamepart):		
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]
		writeFilepartRESTAPILogin(outfile,hostname,"Administrator",frame["variables"]["administrator_passwort"])
		
		#BEGIN
		outfile.write('  - name: Retrieve HVCP as name:uri dict\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "1000"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+hostname+'/rest/hypervisor-cluster-profiles\n')
		outfile.write('      method: GET\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_hvcp\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: hvcp={{{}}}\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: hvcp="{{ hvcp | combine({item[\'name\']:item[\'uri\']}) }}"\n')
		outfile.write('    loop: "{{ var_hvcp.json.members }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: Retrieve Volumes for HVCP (registers storage_volumes)\n')
		outfile.write('    oneview_volume_facts:\n')
		outfile.write('      config: "{{ config }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')

		clusterlist = []
		urllist = [] #ansible variable to url
		for cluster in variablesClustersAll:
			if(cluster[0]!=frame["letter"]):
				continue
			clusterlist.append(cluster)
			urllist.append('var_return_'+convertToAnsibleVariableName(cluster)+'[\'location\']')
			
			outfile.write('#get var_current_hvcp_for_this_cluster\n')
			outfile.write('  - name: get HVCP for '+cluster+'\n')
			outfile.write('    uri:\n')
			outfile.write('      validate_certs: yes\n')
			outfile.write('      headers:\n')
			outfile.write('        Auth: "{{ var_token }}"\n')
			outfile.write('        X-Api-Version: "1000"\n')
			outfile.write('        Content-Type: application/json\n')
			outfile.write('      url: "https://'+hostname+'{{ hvcp[\''+cluster+'\'] }}"\n')
			outfile.write('      method: GET\n')
			outfile.write('      status_code: 200\n')
			outfile.write('    no_log: True\n')
			outfile.write('    register: var_current_hvcp_for_this_cluster\n')
			outfile.write('\n')
			outfile.write('#move JSON in var_current_hvcp_for_this_cluster one up, remove eTag\n')
			outfile.write('  - set_fact: var_current_hvcp_for_this_cluster="{{ var_current_hvcp_for_this_cluster["json"] }}"\n')
			outfile.write('    no_log: True\n')
			outfile.write('  - set_fact: var_current_hvcp_for_this_cluster="{{ var_current_hvcp_for_this_cluster|combine({\'eTag\':None},recursive=True) }}"\n')
			outfile.write('    no_log: True\n')
			outfile.write('\n')
			outfile.write('#build temporary Array with all storageVolumeUris to attach. this is item[\'uri\'] from storage_volumes where item[\'name\']=cluster\n')
			outfile.write('  - set_fact: tmpArray={{[]}}\n')
			outfile.write('    no_log: True\n')
			outfile.write('  - set_fact: tmpArray="{{ tmpArray + [{\'storageVolumeUri\':item[\'uri\'],\'volumeFileSystemType\':\'VMFS\'}] }}"\n')
			outfile.write('    when: item[\'name\'] is search("'+cluster+'-")\n')
			outfile.write('    loop: "{{ storage_volumes }}"\n')
			outfile.write('    no_log: True\n')
			outfile.write('\n')
			outfile.write('#do attach call via REST-API. Body is var_current_hvcp_for_this_cluster combined with sharedStorageVolumes which contains our temp Array\n')
			outfile.write('  - name: Attach Volumes to Cluster '+cluster+'\n')
			outfile.write('    uri:\n')
			outfile.write('      validate_certs: yes\n')
			outfile.write('      headers:\n')
			outfile.write('        Auth: "{{ var_token }}"\n')
			outfile.write('        X-Api-Version: "1000"\n')
			outfile.write('        Content-Type: application/json\n')
			outfile.write('      url: "https://'+hostname+'{{ hvcp[\''+cluster+'\'] }}"\n')
			outfile.write('      method: PUT\n')
			outfile.write('      body_format: json\n')
			outfile.write('      body: "{{ var_current_hvcp_for_this_cluster|combine({\'sharedStorageVolumes\':tmpArray},recursive=True) }}"\n')
			outfile.write('      status_code: 202\n')
			outfile.write('    no_log: True\n')
			outfile.write('    register: var_return_'+convertToAnsibleVariableName(cluster)+'\n')
			outfile.write('\n')
			outfile.write('\n')
			outfile.write('\n')
			outfile.write('\n')
			outfile.write('\n')
		waitAndOutputTask(outfile,clusterlist,urllist)
		#END
		outfile.close()
		
#366
def writeAddHypervisorsToHVCP(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]
		writeFilepartRESTAPILogin(outfile,hostname,"Administrator",frame["variables"]["administrator_passwort"])
		
		#BEGIN
		#gather facts for all clusters
		outfile.write('  - name: get Server Hardware\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+hostname+'/rest/server-hardware\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_server_hardware\n')
		outfile.write('    no_log: True\n')		
		outfile.write('  - set_fact: var_serverhardware_name_to_uri={{{}}}\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: var_serverhardware_name_to_uri="{{ var_serverhardware_name_to_uri | combine({item[\'name\']:item[\'uri\']}) }}"\n')
		outfile.write('    loop: "{{ var_server_hardware[\'json\'][\'members\'] }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: get Hypervisor manager uri\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "'+restApiVersion+'"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+hostname+'/rest/hypervisor-managers\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body:\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_hypervisor_managers\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: var_hypervisor_manager_uri="{{var_hypervisor_managers["json"]["members"][0]["uri"]}}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: Gather Server Profile Template Nublar_ESXi uri\n')
		outfile.write('    oneview_server_profile_template_facts:\n')
		outfile.write('      config: "{{ config }}"\n')
		outfile.write('      name: "Nublar_ESXi"\n')
		outfile.write('    delegate_to: localhost\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: var_server_profile_template_uri="{{server_profile_templates[0]["uri"]}}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: Retrieve HVCP as name:uri dict\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "1000"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://'+hostname+'/rest/hypervisor-cluster-profiles\n')
		outfile.write('      method: GET\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_hvcp\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: hvcp={{{}}}\n')
		outfile.write('    no_log: True\n')
		outfile.write('  - set_fact: hvcp="{{ hvcp | combine({item[\'name\']:item[\'uri\']}) }}"\n')
		outfile.write('    loop: "{{ var_hvcp.json.members }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		outfile.write('\n')
		
		
		clusterlist = []
		urllist = [] #ansible variable to url
		#CREATE
		#foreach cluster in this Zone (A or B)
		for cluster in variablesClustersAll:
			if(cluster[0]!=frame["letter"]):
				continue

			clusterlist.append(cluster)
			urllist.append('var_return_'+convertToAnsibleVariableName(cluster)+'[\'location\']')
			
			outfile.write('#get var_current_hvcp_for_this_cluster\n')
			outfile.write('  - name: get HVCP for '+cluster+'\n')
			outfile.write('    uri:\n')
			outfile.write('      validate_certs: yes\n')
			outfile.write('      headers:\n')
			outfile.write('        Auth: "{{ var_token }}"\n')
			outfile.write('        X-Api-Version: "1000"\n')
			outfile.write('        Content-Type: application/json\n')
			outfile.write('      url: "https://'+hostname+'{{ hvcp[\''+cluster+'\'] }}"\n')
			outfile.write('      method: GET\n')
			outfile.write('      status_code: 200\n')
			outfile.write('    no_log: True\n')
			outfile.write('    register: var_current_hvcp_for_this_cluster\n')
			outfile.write('\n')
			outfile.write('#move JSON in var_current_hvcp_for_this_cluster one up, remove eTag\n')
			outfile.write('  - set_fact: var_current_hvcp_for_this_cluster="{{ var_current_hvcp_for_this_cluster["json"] }}"\n')
			outfile.write('    no_log: True\n')
			outfile.write('  - set_fact: var_current_hvcp_for_this_cluster="{{ var_current_hvcp_for_this_cluster|combine({\'eTag\':None},recursive=True) }}"\n')
			outfile.write('    no_log: True\n')
			outfile.write('\n')
			
			
			outfile.write('#build temporary Array with all variablesClusterHosts(from python convert.py/excel) to attach.\n')
			outfile.write('  - set_fact: tmpArray="{{[]}}"\n')
			outfile.write('    no_log: True\n')

			for clusterHost in variablesClusterHosts:
				if(clusterHost["cluster"]!=cluster):
					continue
					
				outfile.write('  - set_fact:\n')
				outfile.write('      t:\n')
				outfile.write('        serverHardwareUri: "{{ var_serverhardware_name_to_uri[\''+clusterHost["server_hardware"]+'\'] }}"\n')
				outfile.write('        deploymentCustomArgs:\n')
				outfile.write('         - argumentName: "Hostname"\n')
				outfile.write('           argumentValue: "'+clusterHost["hostname"]+'"\n')
				outfile.write('        mgmtIp:\n')
				outfile.write('          ip: "'+clusterHost["management_ipv4_address"]+'"\n')
				outfile.write('  - set_fact: tmpArray="{{ tmpArray + [t] }}"\n')
				outfile.write('    no_log: True\n')
				
			outfile.write('\n')
			outfile.write('#do attach call via REST-API. Body is var_current_hvcp_for_this_cluster combined with addHostRequests which contains our temp Array\n')
			outfile.write('  - name: Add Hypervisor Hosts to Cluster '+cluster+'\n')
			outfile.write('    uri:\n')
			outfile.write('      validate_certs: yes\n')
			outfile.write('      headers:\n')
			outfile.write('        Auth: "{{ var_token }}"\n')
			outfile.write('        X-Api-Version: "1000"\n')
			outfile.write('        Content-Type: application/json\n')
			outfile.write('      url: "https://'+hostname+'{{ hvcp[\''+cluster+'\'] }}"\n')
			outfile.write('      method: PUT\n')
			outfile.write('      body_format: json\n')
			outfile.write('      body: "{{ var_current_hvcp_for_this_cluster|combine({\'addHostRequests\':tmpArray},recursive=True) }}"\n')
			outfile.write('      status_code: 202\n')
			outfile.write('    no_log: True\n')
			outfile.write('    register: var_return_'+convertToAnsibleVariableName(cluster)+'\n')
			outfile.write('\n')
			outfile.write('\n')
			outfile.write('\n')
			outfile.write('\n')
			outfile.write('\n')
			
			
		#Wait for each Cluster
		outfile.write('#wait for each cluster\n')
		#foreach cluster in this Zone
		waitAndOutputTask(outfile,clusterlist,urllist)

		#END
		outfile.close()
		
#810
def writeRemediateHypervisorProfiles(nr,filenamepart):
	for frame in variablesAll:
		filePath = outputfolder+"/"+filename_prefix+frame["letter"]+"_"+nr+"_"+filenamepart+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix)
		hostname = frame["variables"]["oneview_hostname"].lower()+'.'+frame["variables"]["domain_name"]
		writeFilepartRESTAPILogin(outfile,hostname,"Administrator",frame["variables"]["administrator_passwort"])
		
		#BEGIN
		outfile.write('  - name: Retrieve HVP as name:uri dict\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "1000"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: https://a-dcb-syn0001.ad.nublar.de/rest/hypervisor-host-profiles\n')
		outfile.write('      method: GET\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    register: var_hvp\n')
		outfile.write('  - set_fact: hvp={{[]}}\n')
		outfile.write('  - set_fact: hvp="{{ hvp + [item] }}"\n')
		outfile.write('    when: item.refreshState is match \'NotRefreshing\' and item.state is not match \'Configuring\' and item.status is not match \'OK\'\n')
		outfile.write('    loop: "{{ var_hvp.json.members }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - set_fact: hvp2remediate={{[]}}\n')
		outfile.write('  - set_fact: hvp2remediate="{{ hvp2remediate + [ item|combine({\'complianceState\':\'Remediate\'},recursive=True) ] }}"\n')
		outfile.write('    loop: "{{ hvp }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('  - name: Remediate HVPs\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "1000"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: "https://a-dcb-syn0001.ad.nublar.de/{{ item.uri }}"\n')
		outfile.write('      method: PUT\n')
		outfile.write('      status_code: 202\n')
		outfile.write('      body_format: json\n')
		outfile.write('      body: "{{ item }}"\n')
		outfile.write('    register: var_result\n')
		outfile.write('    loop: "{{ hvp2remediate }}"\n')
		outfile.write('    no_log: True\n')
		outfile.write('\n')
		outfile.write('#url for each task\n')
		outfile.write('  - debug: var=item[\'location\']\n')
		outfile.write('    loop: "{{ var_result.results }}"\n')
		outfile.write('    loop_control:\n')
		outfile.write('      label: "mylabel"\n')
		outfile.write('      extended: yes\n')
		outfile.write('\n')	
		#outfile.write('  - debug: var=var_result\n')
		outfile.write('\n')
		outfile.write('#If this task works correctly is not 100 percent verified!\n')
		outfile.write('  - name: Wait for completing Tasks...\n')
		outfile.write('    uri:\n')
		outfile.write('      validate_certs: yes\n')
		outfile.write('      headers:\n')
		outfile.write('        Auth: "{{ var_token }}"\n')
		outfile.write('        X-Api-Version: "1000"\n')
		outfile.write('        Content-Type: application/json\n')
		outfile.write('      url: "{{ item[\'location\'] }}"\n')
		outfile.write('      method: GET\n')
		outfile.write('      body_format: json\n')
		outfile.write('      status_code: 200\n')
		outfile.write('    no_log: True\n')
		outfile.write('    register: var_result2\n')
		outfile.write('    until: var_result2.json.taskState != "New" and var_result2.json.taskState != "Pending" and var_result2.json.taskState != "Running" and var_result2.json.taskState != "Starting" and var_result2.json.taskState != "Unknown"\n')
		outfile.write('    delay: 60\n')
		outfile.write('    retries: 60\n')
		outfile.write('    loop: "{{ var_result.results }}"\n')
		outfile.write('    loop_control:\n')
		outfile.write('      label: "mylabel"\n')
		outfile.write('      extended: yes\n')
		outfile.write('\n')
		outfile.write('#taskstate for each Cluster\n')
		outfile.write('  - debug: var=item.json.taskState\n')
		outfile.write('    loop: "{{ var_result2.results }}"\n')
		outfile.write('    loop_control:\n')
		outfile.write('      label: "mylabel"\n')
		outfile.write('      extended: yes\n')
		outfile.write('\n')	
		

		#END
		outfile.close()
		
		
#Masterplaybook (one per zone)
def writeMasterPlaybook():
	for frame in variablesAll:
		filePath = outputfolder+"/"+frame["letter"]+filename_sufix
		outfile = open(filePath,'w')
		writeFileheader(outfile,config_prefx+frame["letter"]+config_sufix,False,False)

		#BEGIN
		outfile.write('\n')
		for fileVariables in playbooks:
			outfile.write('- import_playbook: "'+frame["letter"]+'_'+str(fileVariables["nr"])+'_'+fileVariables["name"]+'.yml"\n')
		outfile.write('\n')
		#END
		outfile.close()
	

############################################################################
############## Playbooks definition ########################################
############################################################################

playbooks = []
playbooks.append({"nr":105,"name":"renameEnclosures","function":writeRenameEnclosures})
playbooks.append({"nr":110,"name":"renameServerHardwareTypes","function":writeRenameServerHardwareTypes})
playbooks.append({"nr":210,"name":"setDateTime","function":writeTimelocale})
playbooks.append({"nr":215,"name":"ConfigureSNMP","function":writeConfigureSNMP})
playbooks.append({"nr":270,"name":"addFirmwareBundle","function":writeAddFirmwareBundle})
playbooks.append({"nr":280,"name":"createSubnetsAndRanges","function":writeAddresspoolsubnet})
playbooks.append({"nr":290,"name":"createEthernetNetworks","function":writeCreatenetwork})
playbooks.append({"nr":310,"name":"createOSDeploymentServer","function":writeOSdeploymentServer})
playbooks.append({"nr":320,"name":"createNetworkSets","function":writeNetworkset})
playbooks.append({"nr":330,"name":"addStorageSystem","function":writeStoragesystem})
playbooks.append({"nr":334,"name":"createStorageVolumeTemplate","function":writeCreateVolumeTemplate})
playbooks.append({"nr":336,"name":"createStorageVolumes","function":writeCreateVolumes})
playbooks.append({"nr":340,"name":"createLogicalInterconnectGroups","function":writeLogicalInterconnectGroup})
playbooks.append({"nr":342,"name":"createEnclosureGroup","function":writeEnclosureGroup})
playbooks.append({"nr":344,"name":"createLogicalEnclosure","function":writeLogicalEnclosure})
playbooks.append({"nr":346,"name":"createServerProfileTemplate","function":writeCreateServerProfileTemplate})
playbooks.append({"nr":350,"name":"uploadAndExtractImageStreamerArtifact","function":writeUploadAndExtractIsArtifact})
playbooks.append({"nr":352,"name":"uploadGoldenImage","function":writeUploadGI})
playbooks.append({"nr":354,"name":"createDeploymentPlan","function":writeCreatedeploymentplan})
playbooks.append({"nr":360,"name":"addHypervisorManager","function":writeAddHypervisorManager})
playbooks.append({"nr":362,"name":"addHypervisorClusterProfiles","function":writeAddHypervisorClusterProfile})
playbooks.append({"nr":364,"name":"addStoragevolumesToHypervisorClusterProfiles","function":writeAddVolumesToHypervisorClusterProfile})
playbooks.append({"nr":366,"name":"addHypervisorHostsToHypervisorClusterProfiles","function":writeAddHypervisorsToHVCP})
playbooks.append({"nr":810,"name":"remediateHyperVisorProfiles","function":writeRemediateHypervisorProfiles})
		
############################################################################
############## Main Function ###############################################
############################################################################
		
def main():
	findFrames()
	findNimbles()
	findSynergyNimbles()
	findHypervisor()
	findVariablesMgmtNet()
	findHostsPerCluster()
	findGeneral()
	writeConfigs()
	writeMasterPlaybook()
	
	for fileVariables in playbooks:
		fileVariables["function"](str(fileVariables["nr"]),fileVariables["name"])
	
#start
main()
