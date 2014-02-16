
# For tasks that can be run as background jobs.
from django_rq import job

@job
def aggregate():
    """
    Calculates a new time frame from collected Twitter data.
    """
    pass

@job
def cleanup():
    """
    Removes any tweets for time frames that have already been aggregated.
    """
    pass