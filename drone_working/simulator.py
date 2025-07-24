from dronekit_sitl import SITL

sitl = SITL()
sitl.download('copter', '3.3', verbose=True)  # first time only
sitl_args = ['--model', 'quad']
sitl.launch(sitl_args, await_ready=True)
