import yaml

class ConfigReader():
    """
    The class reads and returns configuration settings from a configuration file
    written in YAML. For simplicity, the yaml has only two levels of hierarchy:
    (section:setting).
    
    The class forces an exit if the configuration file does not exist.
    The class also exits if a setting is not found in the file and no defaults
    are supplied in the defaults dectionary.
    The exit behaviour may be changed later to raise an exception that can be
    handled in other parts of the application.
    """
    
    defaults = {'local_host':'0.0.0.0', 'local_port': 5555}
    
    def __init__(self, cfile):
        try:
            with open(cfile,'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)
        except:
            exit("Configuration file not found!")

    def get(self, param):
        """
        The method expects the input param to be a string in the format 'section_setting'.
        If the search in the configuration file return None, the setting is
        searched in the defaults dictionary.
        """
        [section, setting] = param.split('_')
        result = self.cfg.get(section, {}).get(setting, None)
        if result is not None:
            return result
        try:
            return  self.defaults[param]
        except KeyError:
            exit("Setting {}:{} is not found".format(section, setting))
        

if __name__ == "__main__":
    # This is for testing only with the script is called as a stad alone app
    config = ConfigReader('config.yaml')

    networkport = config.getSetting("local_port")
    # you should always see this output
    print(networkport)

    logsfile = config.getSetting("logs_file")
    # you should see the output only if the log file exists
    print(logsfile) 

    gamescore = config.getSetting("game_score")
    # you shoud not see the output (unless you add this setting to the conf file
    print(gamescore)
    
