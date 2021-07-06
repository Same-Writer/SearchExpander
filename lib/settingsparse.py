import yaml

class SettingsParser:

    settings_path = ""

    smtp_addr = ""
    smtp_pw = ""
    smtp_test = True

    rosetta_path = ""
    log_results = True
    results_path = ""
    verbose = True
    search_delay = 0

    run = True
    open_browser = True
    notify_email = True
    email_recipients = []
    cities = []
    states = []
    search_urls = []


    def __init__(self, settingsfile):

        _import = True

        self.settings_path = settingsfile


    def parse_settings(self):

        stream = self._open_yaml(self.settings_path)

        smtp = stream["SMTP Client"]
        self.smtp_addr = smtp['address']
        self.smtp_pw = smtp['password']
        self.smtp_test = smtp['send test']

        app_settings = stream["App Settings"]
        self.rosetta_path = app_settings['rosetta path']
        self.log_results = app_settings['log results']
        self.results_path = app_settings['results path']
        self.verbose = app_settings['verbose']
        self.search_delay = app_settings["search delay"]

        search_parameters = stream["Search Parameters"]
        self.run = search_parameters['run']
        self.open_browser = search_parameters['openbrowser']
        self.notify_email = search_parameters['notifyemail']
        self.email_recipients = search_parameters['email']
        self.cities = search_parameters['cities']
        self.states = search_parameters['states']
        self.search_urls = search_parameters['searchURLs']

        return None


    def _open_yaml(self, yamlpath):
        with open(yamlpath, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

