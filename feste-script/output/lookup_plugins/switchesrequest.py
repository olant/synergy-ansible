from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase):
	#def run(self, tmp, connections, var_standardswitches_names_raw, var_distributedswitches_names_raw, letter, distributedswitches_networks):
	def run(self, terms, variables=None, **kwargs):

		print(terms)
		connections = terms[0]
		var_standardswitches_names_raw = terms[1]
		var_distributedswitches_names_raw = terms[2]
		letter = terms[3]
		distributedswitches_networks = terms[4]

		###############
		###############		Standard
		###############
		data = []
		uniqueNetworkNames = []
		for e in connections:
			if("ethernet-networks" in e["networkUri"]):
				tmp = {}
				tmp["networkUri"] = e["networkUri"]
				tmp["name"] = e["name"]
				tmp["id"] = e["id"]
				tmp["portId"] = e["portId"]
				data.append(tmp)

		data2 = {}
		for z in var_standardswitches_names_raw["results"]:
			tmp = {}
			z = z["json"]
			tmp["name"] = z["name"]
			tmp["uri"] = z["uri"]
			tmp["vlanId"] = z["vlanId"]
			tmp["purpose"] = z["purpose"]
			data2[z["name"]]=tmp

		ret = []
		for networkName in data2:
			vars = data2[networkName]
			if(networkName == "iSCSI-Deployment"):
				continue

			tmp =  {
				"name": networkName,
				"virtualSwitchType": "Standard",
				"version": None,
				"virtualSwitchPortGroups": [
				  {
					"name": networkName,
					"networkUris": [
					  vars["uri"]
					],
					"vlan": "0",
					"virtualSwitchPorts": [
					  {
						"virtualPortPurpose": [
						  vars["purpose"]
						],
						"ipAddress": None,
						"subnetMask": None,
						"dhcp": True,
						"action": "NONE"
					  }
					],
					"action": "NONE"
				  }
				],
				"virtualSwitchUplinks": [],
				"action": "NONE",
				"networkUris": [
				  vars["uri"]
				]
			  }

			for d in data:
				if(d["networkUri"] == vars["uri"]):
					tmp2 = {}
					tmp2["name"] = d["portId"]
					tmp2["active"] = False
					tmp2["mac"] = None
					tmp2["vmnic"] = None
					tmp2["action"] = "NONE"
					tmp["virtualSwitchUplinks"].append(tmp2)
			ret.append(tmp)


		###############
		###############		DISTRIBUTED
		###############	
		dataD = []
		data3 = {}
		for z in var_distributedswitches_names_raw["results"]:
			tmp = {}
			z = z["json"]
			tmp["name"] = z["name"]
			tmp["uri"] = z["uri"]
			tmp["networkUris"] = z["networkUris"]
			data3[z["name"]]=tmp

		for e in connections:
			if("network-set" in e["networkUri"]):
				tmp = {}
				tmp["networkUri"] = e["networkUri"]
				tmp["name"] = e["name"]
				tmp["id"] = e["id"]
				tmp["portId"] = e["portId"]
				dataD.append(tmp)

		for networkName in data3:
			vars = data3[networkName]
			tmp =  {
				"name": letter+"-Prod",
				"virtualSwitchType": "Distributed",
				"version": "6.6.0",
				"virtualSwitchPortGroups": [],
				"virtualSwitchUplinks": [],
				"action": "NONE",
				"networkUris": [
				  vars["uri"]
				]
			  }

			for d in distributedswitches_networks:
				tmp2 = {}
				d = d["json"]
				tmp2["name"] = d["name"]
				tmp2["networkUris"] = [d["uri"]]
				tmp2["vlan"] = d["vlanId"]
				tmp2["virtualSwitchPorts"] = []
				tmp2["action"] = "NONE"
				tmp["virtualSwitchPortGroups"].append(tmp2)

			names = []
			for d in dataD:
				if(d["networkUri"] == vars["uri"]):
					if(not d["name"] in names):
						names.append(d["name"])

			for c in connections:
				if(c["name"] in names):
					tmp2 = {
							"name":c["portId"],
							"active": False,
							"mac": None,
							"vmnic": None,
							"action": "NONE"
						}
					tmp["virtualSwitchUplinks"].append(tmp2)
			ret.append(tmp)
		return ret