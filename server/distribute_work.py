import os
import sys
if __name__ == '__main__':
    project_name = sys.argv[1]
    script_name = sys.argv[2]
    id = sys.argv[3]
    users = sys.argv[4]
    spawn_rate = sys.argv[5]
    workers = sys.argv[6]
    host = sys.argv[7]
    time = sys.argv[8]
    results_path = f'locust/{script_name}/{id}/results'
    log_path = f'locust/{script_name}/{id}/log.log'
    time_command = f'-t {str(time)}s' if time is not None else ''
    host_command = f'--host {host}' if host is not None else ''
    command = f'cd projects/{project_name} && ../../env/{project_name}/bin/locust -f locust/{script_name}.py  {host_command} --users {users} --spawn-rate {spawn_rate} --headless {time_command} --csv {results_path} --logfile {log_path} --master --expect-workers={workers}'
    for i in range(0, int(workers)):
        worker_log_path = f'locust/{script_name}/{id}/worker_{i+1}_log.log'
        worker_command = f'cd projects/{project_name} && ../../env/{project_name}/bin/locust -f locust/{script_name}.py --logfile {worker_log_path} --worker &'
        os.system(worker_command)
    os.system(command)