import json
from calendar import c
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from nonebot_plugin_apscheduler import scheduler


class JobManager:
  def __init__(self, config_path: Path | str):
    self.jobs = []
    self.config_path = config_path

  def load_jobs(
    self,
  ):
    with open(self.config_path) as f:
      configs = json.load(f)
      for cf in configs:
        job = Job(**cf)
        self.add_job(job)

  def update_jobs(self, config_path: Path):
    self.remove_all_jobs()

  def add_job(self, job: "Job"):
    self.jobs.append(job)
    job.register_job()

  def remove_job(self, job_id: str):
    for job in self.jobs:
      if job.id == job_id:
        scheduler.remove_job(job_id)
        self.jobs.remove(job)
        return True
    return False

  def remove_all_jobs(self):
    for job in self.jobs:
      scheduler.remove_job(job.id)
    self.jobs.clear()

  def start_scheduler(self):
    scheduler.start()

  def stop_scheduler(self):
    scheduler.shutdown()


@dataclass
class Job:
  id: str
  name: str
  func: str
  type: str = "date"
  year: int | str | None = None
  month: int | str | None = None
  week: int | str | None = None
  day: int | str | None = None
  hour: int | str | None = None
  minute: int | str | None = None
  second: int | str | None = None

  def register_job_date(self):
    trigger_kwargs = {
      "year": self.year,
      "month": self.month,
      "week": self.week,
      "day": self.day,
      "hour": self.hour,
      "minute": self.minute,
      "second": self.second,
    }
    trigger_kwargs = {k: int(v) for k, v in trigger_kwargs.items() if v is not None}
    runtime = datetime(**trigger_kwargs, tzinfo=None)
    return {"run_date": runtime}

  def register_job_interval(self):
    trigger_kwargs = {"days": self.day, "hours": self.hour, "minutes": self.minute, "seconds": self.second}
    return {k: v for k, v in trigger_kwargs.items() if v is not None}

  def register_job_cron(self):
    trigger_kwargs = {
      "year": self.year,
      "month": self.month,
      "week": self.week,
      "day": self.day,
      "hour": self.hour,
      "minute": self.minute,
      "second": self.second,
    }
    return {k: v for k, v in trigger_kwargs.items() if v is not None}

  def register_job(self):
    if self.type == "date":
      trigger_kwargs = self.register_job_date()
    elif self.type == "interval":
      trigger_kwargs = self.register_job_interval()
    else:  # "cron"
      trigger_kwargs = self.register_job_cron()

    scheduler.add_job(
      func=globals().get(self.func),
      trigger=self.type,
      **trigger_kwargs,  # type: ignore
      id=self.id,
      name=self.name,
    )


jb = JobManager(config_path=Path("config.json"))
# def read_job():
#   with open(fileSystem.scheduler / "config.json", "r+") as f:
#     configs = json.load(f)
#     for config in configs:
#       job = Job(**config)
#       job.register_job()
#       logger.opt(colors=True).success(
#         f'Succeeded to load <cyan>scheduler unit</cyan> "<yellow>{job.name}</yellow>" from <magenta>nonebot_plugin_yuelibot.scheduler</magenta>"'
#       )


# read_job()
