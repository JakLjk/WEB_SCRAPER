from shared.methods.object_size import get_object_size

class Webpage:
    def __str__(self):
        try: 
            size_raw = get_object_size(self.raw_data)
        except TypeError:
            size_raw = "N/A"
        try: 
            len_details = len(self.details)
        except TypeError:
            len_details = "N/A"
        try: 
            len_equipment = len(self.equipment)
        except TypeError:
            len_equipment = "N/A"
        return (f"\nWebpage object:\n"
               f"  Offer Title: {self.offer_title}\n"
               f"  Offer ID: {self.offer_id}\n"
               f"  Added Date: {self.added_date}\n"
               f"  Price: {self.price}\n"
               f"  Currency: {self.currency}\n"
               f"  Coordiantes: {self.coordinates}\n"
               f"  Number of details: {len_details}\n"
               f"  Number of listed equipments: {len_equipment}\n"
               f"  Link: {self.link}\n"
               f"  Size of raw data: {size_raw}MB\n")
            
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

        self.details:dict = {}
        self.equipment:list = []




