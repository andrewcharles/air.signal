Notes for automating earth engine

1. Run a task on schedule
2. React to new data in Cloud Storage
3. Monitoring and send a text

Cloud Scheduler
Cloud Functions
- 5 minutes max, but it's a controller
- 2 million free invocations per month

 no pub/sub on ee: can have a secondary monitoring job


REMOTE SENSING

Since 2017 the sentinel 2 satellite, run by Euro space agency,
images everywhere on the planet at a frequency of approx every 5 days
at a resolution of 10x10m 

At the same time, drone imagery is more readily available and cheaper, which means high resolution imagery can be generated easier than ever before.

By integrating the different types of data we can maximise the potential of the free imagery.

e.g. we might have lidar for a small part of a site, which enables us to build a model to classify vegetation over the whole site using satellite.

This Skywave slide gives a sense of how to do this.




