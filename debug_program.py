import argparse
import querier
import debugging
from functools import partial

class HandlerClass:
	def __init__(self, modelQuerier):
		self.modelQuerier = modelQuerier
	
	def on_stop(self, debug_session):
		success, output = debug_session.execute_command("bt")
		print(output)		

def main():
	parser = argparse.ArgumentParser(description="Run specified phases of the grading process.")
	parser.add_argument('--executable', required=True, help=f"The executable to run.")
	parser.add_argument('--model', required=True, help=f"The model(s) to use debugging the program. The following model names can be queried through the OpenAI API: {querier.OpenAIModelQuerier.supported_model_names()}")
	args = parser.parse_args()

	modelQuerier = querier.AIModelQuerier.resolve_queriers([args.model])[0]	
	handler = HandlerClass(modelQuerier)

	session = debugging.DebuggingSession(args.executable, stop_handler=handler.on_stop)
	print(session)

if __name__ == "__main__":
	main()
