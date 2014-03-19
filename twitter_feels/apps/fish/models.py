from django.db import models
import random
from stream_analysis import TimedIntervalMixin

from twitter_feels.libs.twitter_analysis import TweetTimeFrame
import settings


class Emotion(models.Model):
    """
    An emotion. Yep.
    """

    # The word itself
    name = models.CharField(max_length=30)

    # Disable tracking of this word
    description = models.CharField(max_length=200, default=None, blank=True)

    def __unicode__(self):
        return self.name


class TimeFrame(TweetTimeFrame):
    """The root time frame class that calculates all the bin counts for this interval"""

    DURATION = settings.TIME_FRAME_DURATION

    total_tweets = models.PositiveIntegerField(null=True, blank=True, default=None)

    def calculate(self, stream_data):

        self.total_tweets = stream_data.count()

        emotions = Emotion.objects.all()
        emotions_by_name = {}
        for emotion in emotions:
            emotions_by_name[emotion.name] = emotion

        # Create a full complement of empty time bin counts
        time_bin_count_map = {}
        for emotion in emotions:
            for bieber in [True, False]:
                for retweet in [True, False]:
                    time_bin_count_map[(emotion, bieber, retweet)] = TimeBinCount(
                        emotion=emotion,
                        bieber=bieber,
                        retweet=retweet,
                        start_time=self.start_time,
                        frame=self,
                    )

        # Build up a list of example tweets
        example_tweets = []

        for tweet in stream_data:

            lower_text = tweet.text.lower()
            bieber = ("bieb" in lower_text or "justin" in lower_text)
            retweet = tweet.is_retweet or lower_text.startswith("rt ")

            emotion = None
            if ("thank" in lower_text
                and ("good" in lower_text
                     or "happy" in lower_text
                     or "love" in lower_text)):
                emotion = emotions_by_name["gratitude"]

            elif (("want to build" in lower_text)
                  or ("excited to build" in lower_text)
                  or ("need to build" in lower_text)):
                emotion = emotions_by_name["industriousness"]

            elif (("want love" in lower_text)
                  or ("feel lonely" in lower_text)
                  or ("want a boyfriend" in lower_text)
                  or ("want a girlfriend" in lower_text)) \
                    and not ("don't" in lower_text
                             or "dont" in lower_text
                             or "doesn't" in lower_text
                             or "doesnt" in lower_text):
                emotion = emotions_by_name["longing"]

            if emotion is not None:
                bin_count = time_bin_count_map[(emotion, bieber, retweet)]
                bin_count.count += 1

                if not retweet or random.random() < settings.PERCENT_AS_EXAMPLES:
                    example_tweets.append(ExampleTweet(
                        tweet_id=tweet.tweet_id,
                        text=tweet.text,
                        created_at=tweet.created_at,
                        frame=self,

                        emotion=emotion,
                        bieber=bieber,
                        retweet=retweet,
                    ))

        # Save it all in the database
        TimeBinCount.objects.bulk_create(time_bin_count_map.values())
        ExampleTweet.objects.bulk_create(example_tweets)

        # We are done with this data
        return stream_data


class TimeBinCount(TimedIntervalMixin, models.Model):
    """Describes the counts for 1 bin, for one time interval"""

    # We need to duplicate this variable here so that the convenience methods
    # on TimedIntervalMixin work properly
    DURATION = TimeFrame.DURATION

    # The frame this is associated with
    frame = models.ForeignKey(TimeFrame)

    # The dimensions that define the bin (plus start_time from TimeIntervalMixin)
    emotion = models.ForeignKey(Emotion)
    bieber = models.BooleanField()
    retweet = models.BooleanField()

    # The value for the bin
    count = models.PositiveIntegerField(default=0)


class ExampleTweet(models.Model):
    """Stores an example tweet"""

    # The frame this example is associated with
    frame = models.ForeignKey(TimeFrame)

    tweet_id = models.BigIntegerField()
    text = models.CharField(max_length=250)
    created_at = models.DateTimeField()

    # The dimensions of this example
    emotion = models.ForeignKey(Emotion)
    bieber = models.BooleanField()
    retweet = models.BooleanField()

