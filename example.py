from psyched.image import Image
from psyched.dag import DAG


ubuntu = Image('ubuntu', '16.04')
dag = DAG()

a = dag.new_task("First", ubuntu, "sleep 1")
b = dag.new_task("Second 1", ubuntu, "sleep 1")
c = dag.new_task("Second 2", ubuntu, "sleep 1")
d = dag.new_task("Last", ubuntu, "sleep 1")

a >> [b, c] >> d

dag.run()
