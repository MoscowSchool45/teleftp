class FilesystemError(Exception):
    pass


class FilesystemAuthError(FilesystemError):
    pass


class FilesystemTimeoutError(FilesystemError):
    pass


class FilesystemDriver(object):
    FILE, DIRECTORY, ERROR = range(3)

    def connect(self, user_data, password):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def cd(self, dir):
        raise NotImplementedError()

    def cd(self):
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
    pass