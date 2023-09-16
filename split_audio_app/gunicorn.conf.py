import multiprocessing

bind = "0:5000"
workers = multiprocessing.cpu_count()
timeout = 180
