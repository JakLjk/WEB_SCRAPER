class ServerNegativeResponse(Exception):
    pass

class ServerUnknownResponse(Exception):
    pass

class UnsupportedPageLayout(Exception):
    pass

class DeadOfferLink(Exception):
    pass

class NoMapElementLoaded(Exception):
    pass

class ServerResponseError(Exception):
    pass

class NoResponseFromServer(Exception):
    pass

class UnrecognizedServerResponse(Exception):
    pass

class UnrecognizedClientResponse(Exception):
    pass