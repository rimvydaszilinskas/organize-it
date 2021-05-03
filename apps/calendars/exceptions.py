class EventTimeValidationError(Exception):
    def __init__(self, message=None) -> None:
        self.message = message if message else 'An error occured validating event times'
        super().__init__(self, self.message)
