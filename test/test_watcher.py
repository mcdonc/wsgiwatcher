import os
import time


def test_pidapp_responds_with_200_status(pidapp):
    pidapp.get('/', status=200)


def test_pidapp_reloads_after_file_changed(
        pidapp_file, pidapp, wait_for_response):
    pid1 = pidapp.get('/', status=200).body
    with open(pidapp_file, 'a') as fh:
        fh.write('\n')
    resp = wait_for_response(
        lambda r: r.body != pid1, retries=10, interval=0.2)
    assert resp.body != pid1


def test_kills_worker_processes(pidapp_process, wait_for_response):
    """Shutting down monitor master process kills worker processes."""
    pidapp_process.terminate()
    # Terminate() just sends SIGTERM, now we wait for it to actually terminate
    pidapp_process.wait()
    # Parent is gone, wait a "poll interval" time for child to notice
    time.sleep(1)

    assert pidapp_process.returncode is not None

    resp = wait_for_response(
        lambda r: r.status_code == 502)

    assert resp.status_code == 502
