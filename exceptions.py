class ThirdPartyApiUnavailable(Exception):
    pass


class BitfinexApiUnavailable(ThirdPartyApiUnavailable):
    pass


class BankOfCanadaApiUnavailable(ThirdPartyApiUnavailable):
    pass


class QuandlApiUnavailable(ThirdPartyApiUnavailable):
    pass


class InitDataNotFound(Exception):
    pass


class LoanDataNotFound(InitDataNotFound):
    pass


class ExchangeRateDataNotFound(InitDataNotFound):
    pass
