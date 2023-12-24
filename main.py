import sys
import logging

# Init logging objects
import my_loggers
from server.launch import launch_server
from client.launch import launch_client


# Arguments that were provided by user:
user_args = [arg.lower() for arg in sys.argv[1:]]
main_log = logging.getLogger("MAIN_LOG")

def main():
    if "-s" in user_args:
        main_log.info("Initialising server")
        launch_server()
    
    elif "-c" in user_args:
        main_log.info("Initialising client")
        launch_client(work_type="mineLinks")
        # launch_client(work_type="mineOffers")

    else:
        main_log.info("No proper arguments passed - quitting")
        sys.exit()

if __name__ == "__main__":
    main()

    

# TODO worker and DB connector
    
# TODO logger size limits
    
# TODO add proper password prompt (to generate hash based on it)
    
# TODO json based configs
    
# TODO separate loggers for each thread

# Client and webpage class that will be sent between client and server