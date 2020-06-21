from psyched.dag import DAG
from psyched.image import Image

ubuntu = Image('amd64/ubuntu', '20.04')
dag = DAG()

a = dag.new_task("First", task_type='docker', image=ubuntu, command="ls -lha /")
b = dag.new_task("Second 1", task_type='docker', image=ubuntu, command="ls -lha /")
c = dag.new_task("Second 2", task_type='docker', image=ubuntu, command="ls -lha /")
d = dag.new_task("Last", task_type='docker', image=ubuntu, command="ls -lha /")

a >> [b, c] >> d

dag.serve()
