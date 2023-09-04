class RedirectException(Exception):
    '''Self redirect exception'''
    def __init__(self, *args):
        self.message = 'Self redirect exception'

    def __str__(self):
        return '{0}'.format(self.message)


class StartIdStopIdException(Exception):
    '''Stop_id param lower then start_id exception'''
    def __init__(self, *args):
        self.message = '--stop_id lower then --start_id parameter'

    def __str__(self):
        return '{0}'.format(self.message)
