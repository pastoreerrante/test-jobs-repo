"""Throwaway jobs to exercise the job_event_webhook broker: one per completion path."""

import time

from nautobot.apps.jobs import BooleanVar, IntegerVar, Job, register_jobs

name = "Webhook Broker Tests"


class PassingJob(Job):
    """Completes normally: expect a POST with job_output and no einfo."""

    class Meta:
        name = "Webhook test - success"

    def run(self):
        self.logger.info("Doing nothing, successfully.")
        return "ok"


class FailCalledJob(Job):
    """Calls self.fail(): JobResult is FAILURE, but the payload looks like a success."""

    class Meta:
        name = "Webhook test - self.fail()"

    def run(self):
        self.fail("Deliberate failure via self.fail().")
        return "failed softly"


class RaisingJob(Job):
    """Raises: expect a POST that includes einfo."""

    class Meta:
        name = "Webhook test - exception"

    def run(self):
        raise RuntimeError("Deliberate exception from test job.")


class LongExceptionJob(Job):
    """Raises with a long message: the Job Result summary should wrap exc_message, not overflow the page."""

    length = IntegerVar(default=400, min_value=1, max_value=5000)
    with_spaces = BooleanVar(default=False, description="Use a long sentence instead of one unbroken token.")

    class Meta:
        name = "Long exception message"

    def run(self, length, with_spaces):
        if with_spaces:
            message = ("This is a deliberately long exception message. " * (length // 47 + 1))[:length]
        else:
            message = "x" * length
        raise RuntimeError(message)


class SlowJob(Job):
    """Sleeps, to compare job duration with the endpoint up vs. down."""

    seconds = IntegerVar(default=2, min_value=0, max_value=60)

    class Meta:
        name = "Webhook test - sleep"

    def run(self, seconds):
        time.sleep(seconds)
        return f"slept {seconds}s"


register_jobs(PassingJob, FailCalledJob, RaisingJob, LongExceptionJob, SlowJob)
