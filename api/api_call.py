import threading
from ratelimiter import RateLimiter
import time

class API_Search:
    def __init__(self, names, bb_session):
        self.names = names
        self.bb_session = bb_session
        self.emails = []
        self.errors = []
        self.bad_responses = []
        self.api_calls(self.names)

    def api_calls(self, names):
        names = self.names
        # Create a list to hold the threads
        threads = []

        # Start a thread for each name in the list        
        rate_limiter = RateLimiter(max_calls=10, period=1)

        for name in names:
            with rate_limiter:
                thread = threading.Thread(target=self.search_constituent, args=(name,))
                threads.append(thread)
                thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def search_constituent(self, name):
        bb_session = self.bb_session

        # Sort out Jr. or IV or other non-name values that end up in the list.
        original = name
        name = name.strip()
        name = name.replace('  ',' ')
        name = name.split(',')[0]

        if name:
            while True:
                r = bb_session.get(f'https://api.sky.blackbaud.com/constituent/v1/constituents/search?search_text={name}&strict_search=True')
                
                # Process the response
                if r.status_code == 200:
                    count = r.json()['count']
                    if count == 1:
                        self.emails.append((r.json()['value'][0]['email'].strip(), original))
                        break
                    else:
                        self.errors.append(original)
                        break
                elif r.status_code == 429:
                    # wait for the specified retry-after time
                    time.sleep(int(r.headers["Retry-After"]))
                else:
                    self.errors.append(original)
                    break
    
    def return_data(self):
        # print(self.emails, self.errors)
        return self.emails, self.errors
