from multiprocessing import Process
from http_server import app
from worker import do_work
import os
import uvicorn
import time

num_http_workers = int(os.environ.get("http_workers", "1"))
num_job_workers = int(os.environ.get("job_workers", "1"))


def start_uvicorn():
    print("starting uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=num_http_workers)


if __name__ == "__main__":
    job_workers = []
    for i in range(num_job_workers):
        print(f"starting worker {i}")
        worker = Process(target=do_work)
        worker.start()
        job_workers.append(worker)

    uvicorn_worker = Process(target=start_uvicorn)
    uvicorn_worker.start()

    while True:
        if not uvicorn_worker.is_alive():
            print("---- Uvicorn process has died unexpectedly! Restarting service ----")
            uvicorn_worker = Process(target=start_uvicorn)
            uvicorn_worker.start()

        for worker_num, job_worker in enumerate(job_workers):
            if not job_worker.is_alive():
                print(f"---- Job worker num {worker_num} has died unexpectedly! Restarting worker ----")
                worker = Process(target=do_work)
                worker.start()
                job_workers[worker_num] = worker

        time.sleep(5)
