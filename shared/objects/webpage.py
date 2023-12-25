


class Webpage:
    def __str__(self):
        try: 
            len_raw = len(self.raw_data)
        except TypeError:
            len_raw = "N/A"
        return (f"\nWebpage object:\n"
               f"  Offer Title: {self.offer_title}\n"
               f"  Offer ID: {self.offer_id}\n"
               f"  Added Date: {self.added_date}\n"
               f"  Price: {self.price}\n"
               f"  Currency: {self.currency}\n"
               f"  Coordiantes: {self.coordinates}\n"
               f"  Link: {self.link}\n"
               f"  Number of signs in raw data: {len_raw}\n")
            
    def __init__(self, link:str) -> None:
        self.link:str = link
        self.raw_data:str = None
        self.offer_title:str = None
        self.added_date:str = None
        self.offer_id:str = None
        self.price:str = None
        self.currency:str = None
        self.description:str = None
        self.coordinates:str = None


