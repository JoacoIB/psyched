
from psyched.dag import DAG

dag = DAG()


def count(n):
    cnt = 0
    for i in range(n):
        cnt += 1
    return


a = dag.new_task("First", task_type='python', target=count, n=10000)
b = dag.new_task("Second 1", task_type='python', target=count, n=10000)
c = dag.new_task("Second 2", task_type='python', target=count, n=10000)
d = dag.new_task("Last", task_type='python', target=count, n=10000)

a >> [b, c] >> d

dag.run()
