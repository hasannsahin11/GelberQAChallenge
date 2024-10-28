def before_all(context):
    # Initializing shared data storage
    context.shared_data = {}

def before_scenario(context, scenario):
    print(f"Scenario has started: {scenario}")


def after_scenario(context, scenario):
   print(f"Scenario has ended: {scenario}")
    # context.shared_data.clear()


