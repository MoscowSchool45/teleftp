import os.path
import os
import io

from ftplib import FTP, error_perm


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

    def put(self, filename, file_path):
        raise NotImplementedError()


class FTPDriver(FilesystemDriver):
    def connect(self, user_data, password):
        self.data['ftp'] = FTP()
        self.data['ftp'].connect(self.config.ftp['host'], self.config.ftp['port'])
        try:
            self.data['ftp'].login(user_data['username'], password)
            self.data['ftp'].pwd()  # Try a command to see if we're in
        except error_perm:
            raise FilesystemAuthError("Couldn't authenticate")

    def disconnect(self):
        self.data['ftp'].quit()
        del self.data['ftp']

    def ls(self):
        return sorted(self.data['ftp'].nlst())
        # todo: errors, timeout, etc

    def pwd(self):
        return self.data['ftp'].pwd()

    def get(self, filename):
        try:
            self.data['ftp'].cwd(filename)
            return FilesystemDriver.DIRECTORY, filename
        except error_perm:
            try:
                self.data['ftp'].voidcmd("TYPE I")
                file_size = self.data['ftp'].size(filename)
                if file_size is None:
                    return FilesystemDriver.ERROR, "File not found."
                elif 'size-limit' in self.config.ftp and \
                        self.config.ftp['size-limit'] is not None and \
                        file_size > self.config.ftp['size-limit']:
                    return FilesystemDriver.ERROR, "File too large to be sent."
                io_buffer = io.BytesIO()
                self.data['ftp'].retrbinary('RETR {}'.format(filename), io_buffer.write)
                io_return_buffer = io.BytesIO(io_buffer.getvalue())
                return FilesystemDriver.FILE, io_return_buffer
            except error_perm:
                return FilesystemDriver.ERROR, "File not found or you lack permissions"

    def put(self, filename, file_path):
        try:
            with open(file_path, 'rb') as f:
                self.data['ftp'].storbinary("STOR {}".format(filename), f)
        except error_perm:
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
            return FilesystemDriver.ERROR, "Working directory disappeared."
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
            return FilesystemDriver.ERROR, "File not found."
        if os.path.isdir(file_path):
            self.data['cwd'] = file_path
            return FilesystemDriver.DIRECTORY, self.data['cwd']
        elif os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            if 'size-limit' in self.config.ftp and \
                    self.config.ftp['size-limit'] is not None and \
                    file_size > self.config.ftp['size-limit']:
                return FilesystemDriver.ERROR, "File too large to be sent."
            if file_size == 0:
                return FilesystemDriver.ERROR, "Empty file."
            file = open(file_path, 'rb')
            return FilesystemDriver.FILE, file
        else:
            return FilesystemDriver.ERROR, "File not found"

    def put(self, filename, file_path):
        os.rename(file_path, os.path.join(self.data['cwd'], filename))