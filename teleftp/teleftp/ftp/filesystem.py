import os.path
import os


class FilesystemError(Exception):
    pass


class FilesystemAuthError(FilesystemError):
    pass


class FilesystemTimeoutError(FilesystemError):
    pass


class FilesystemDriver(object):
    FILE, DIRECTORY, ERROR = range(3)

    def __init__(self, config=None):
        self.config = config
        self.data = {}

    def connect(self, user_data, password):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def ls(self):
        raise NotImplementedError()

    def pwd(self):
        raise NotImplementedError()

    def get(self, filename):
        raise NotImplementedError()

    def put(self, filename, filedata):
        raise NotImplementedError()


class FTPDriver(FilesystemDriver):
    pass


class LocalDriver(FilesystemDriver):
    def connect(self, user_data, password):
        try:
            if not user_data['username'] in self.config.local['authentication']:
                raise FilesystemAuthError("Wrong username and password combination")
        except KeyError:
            raise FilesystemAuthError("No authentication data in server configuration")
        if self.config.local['authentication'][user_data['username']] != password:
            raise FilesystemAuthError("Wrong username and password combination")
        self.data['cwd'] = self.config.local['root_directory']

    def disconnect(self):
        del self.data['cwd']

    def ls(self):
        if os.path.exists(self.data['cwd']) and os.path.isdir(self.data['cwd']):
            return sorted(os.listdir(self.data['cwd']))
        else:
            raise FilesystemError("Current working directory disappeared. Try /logout and start over.")

    def pwd(self):
        return self.data['cwd']

    def get(self, filename):
        if not os.path.exists(self.data['cwd']) or not os.path.isdir(self.data['cwd']):
            return FilesystemDriver.ERROR, None
        if filename == '..':
            if self.data['cwd'] != self.config.local['root_directory']:
                file_path = os.path.dirname(self.data['cwd'])
            else:
                # Prevent escaping the working directory
                file_path = self.data['cwd']
        elif filename == '.':
            file_path = self.data['cwd']
        else:
            file_path = os.path.join(self.data['cwd'], filename)
        if not os.path.exists(file_path):
            return FilesystemDriver.ERROR, None
        if os.path.isdir(file_path):
            self.data['cwd'] = file_path
            return FilesystemDriver.DIRECTORY, self.data['cwd']
        elif os.path.isfile(file_path):
            file = open(file_path, 'rb')
            return FilesystemDriver.FILE, file
        else:
            return FilesystemDriver.ERROR, None