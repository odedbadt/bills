from infi.credentials_store import CLICredentialsStore

class ServiceCLICrdentialsStore(CLICredentialsStore):
    def _get_file_folder(self):
        return ".infi.credentials_store"

    def authenticate(self, key, credentilas):
        return True

    def ask_credentials_prompt(self, key):
        print '\nConnecting to the service ' + str(key)