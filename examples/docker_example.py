from psyched.dag import DAG
from psyched.image import Image

ubuntu = Image('ubuntu', '16.04')
dag = DAG()

a = dag.new_task("First", task_type='docker', image=ubuntu, command="sleep 1")
b = dag.new_task("Second 1", task_type='docker', image=ubuntu, command="sleep 1")
c = dag.new_task("Second 2", task_type='docker', image=ubuntu, command="sleep 1")
d = dag.new_task("Last", task_type='docker', image=ubuntu, command="sleep 1")

a >> [b, c] >> d

dag.run()
