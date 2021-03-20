from src.run_utils import RunningJob, Task, run

class TestJob(RunningJob):

    def __init__(self, funcs_params: dict):
        super(TestJob, self).__init__("test", "test", 1)
        self.funcs_params = {}
        for f, p in funcs_params.items():
            self.funcs_params[f] = p

    def finalize(self, outdir):
        pass

    def generate_tasks(self, outdir, stop_early=None):
        return [Task(f, p) for f, p in self.funcs_params.items()]


def test_paper_8_bug():
    funcs_params = {}
    jobs = TestJob(funcs_params)

    run(jobs, with_population_caching=False)