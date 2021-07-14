import yaml

class SettingsParser:

    settings_path = ""

    smtp_addr = ""
    smtp_pw = ""
    smtp_test = True
    smtp_host = "smtp.gmail.com"
    smtp_port = 587

    rosetta_path = ""
    log_results = True
    log_level = 'INFO'
    results_path = ""
    verbose = True
    search_delay = 0

    run = True
    open_browser = True
    notify_email = True
    scrape_next = False
    email_recipients = []
    cities = []
    states = []
    search_urls = []


    def __init__(self, settingsfile):

        _import = True

        self.settings_path = settingsfile


    def parse_settings(self):

        stream = self._open_yaml(self.settings_path)

        smtp = stream["SMTP Settings"]
        self.smtp_addr = smtp['address']
        self.smtp_pw = smtp['password']
        self.smtp_test = smtp['send test']
        self.smtp_host = smtp['host']
        self.smtp_port = smtp['port']

        app_settings = stream["App Settings"]
        self.rosetta_path = app_settings['rosetta path']
        self.log_results = app_settings['save results']
        self.log_level = app_settings['debug log level']
        self.results_path = app_settings['results path']

        search_parameters = stream["Search Settings"]
        self.run = search_parameters['run']
        self.scrape_next = search_parameters['scrape all pages']
        self.search_delay = search_parameters["search delay"]
        self.cities = search_parameters['cities']
        self.states = search_parameters['states']
        self.search_urls = search_parameters['searchURLs']

        notification = stream["Notification Settings"]
        self.open_browser = notification['openbrowser']
        self.notify_email = notification['notifyemail']
        self.email_recipients = notification['email recipients']

        return None


    def _open_yaml(self, yamlpath):
        with open(yamlpath, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

