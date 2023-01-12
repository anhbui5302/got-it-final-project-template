class ApplicationServiceException(Exception):
    def __init__(self, status_code, message, data=None):
        super(ApplicationServiceException, self).__init__(message)

        self.status_code = status_code
        self.message = message
        self.data = data

    def __str__(self):
        return '<ApplicationServiceException - {}: {}, data={}>'.format(
            self.__class__.__name__, self.message, self.data
        )
