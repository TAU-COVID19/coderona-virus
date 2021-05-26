import os
import json

#Test the amount of the  created Immune
def test_createInfectedPersons():
    """
    #Edit config.json add extension 
    #create population with 5 people ages [9,19,29,39,49]
    #test that each day one pf them is getting immuned
    #Edit config.json remove extension
    """
    ConfigData = None
    config_path = os.path.join(os.path.dirname(__file__) ,"config.json")
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        tmpExtension = ConfigData['ExtensionsName']
        ConfigData['ExtensionsName'] = "ImmuneByAgeExtension"
    with open(config_path,'w') as json_data_file:
        json.dump(ConfigData,json_data_file)

    ages_arr = [9,19,29,39,49,59]
    pop
    
    with open(config_path) as json_data_file:
        ConfigData = json.load(json_data_file)
        ConfigData['ExtensionsName'] = tmpExtension
    with open(config_path,'w') as json_data_file:
        json.dump(ConfigData,json_data_file)
