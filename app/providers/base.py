from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    @abstractmethod
    def initiate_payment(self, order):
        pass

    @abstractmethod
    def verify_payment(self, provider_ref):
        pass
    
    @abstractmethod
    def handle_callback(self, request):
        pass