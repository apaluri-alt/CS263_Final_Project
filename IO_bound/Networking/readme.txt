Notes

- Baseline: sends requests synchronously and waits for each one before eventually processing them and sorting a list of 1000 random floats

- Async: sends requests and allows event loop to execute sorting while requests are being processed by server. Added bonus, since requests are sent without waiting for a response, we have additional concurrency to take advantage of if the server implements concurrency

- Threading/Multiprocessing: handles requests in chunks based on concurrency size, where threads are waiting for their own requests to respond back before sending new request. Allows for concurrency on server side. 

- Server: set up is very simple. One endpoint that waits for 10 ms and returns either tcp or udp randomly as a JSON field (done as a simple simulation)

