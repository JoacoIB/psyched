from psyched.dag import DAG


dag = DAG()

a = dag.new_task("First", task_type='shell', command=['sleep', '1'])
b = dag.new_task("Second 1", task_type='shell', command=['sleep', '1'])
c = dag.new_task("Second 2", task_type='shell', command=['sleep', '1'])
d = dag.new_task("Last", task_type='shell', command=['sleep', '1'])

a >> [b, c] >> d

dag.run()
